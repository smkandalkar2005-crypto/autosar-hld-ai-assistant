import unittest
from pathlib import Path
import sys

# Ensure src is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.pdf_parser import PDFParser
from src.extractor import ArchitectureExtractor
from src.relationship_builder import RelationshipBuilder
from src.completeness_analyzer import CompletenessAnalyzer
from src.comparator import DocumentComparator
from src.vector_store import VectorStore
from src.llm_engine import LLMEngine
from src.report_generator import ReportGenerator
from src.config import SAMPLE_DOCS_DIR, OUTPUT_DIR

class TestHLDAssistantFeatures(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.pdf_ecu_v1_path = SAMPLE_DOCS_DIR / "AUTOSAR_Engine_Control_Unit_HLD.pdf"
        cls.pdf_bcm_v1_path = SAMPLE_DOCS_DIR / "AUTOSAR_Body_Control_Module_HLD.pdf"
        cls.pdf_bcm_v2_path = SAMPLE_DOCS_DIR / "AUTOSAR_Body_Control_Module_HLD_V2.pdf"

        cls.parser_ecu_v1 = PDFParser(str(cls.pdf_ecu_v1_path), fallback_version="Version 1.0")
        cls.pages_ecu_v1 = cls.parser_ecu_v1.extract_pages()
        cls.chunks_ecu_v1 = cls.parser_ecu_v1.chunk_document()

        cls.parser_bcm_v1 = PDFParser(str(cls.pdf_bcm_v1_path), fallback_version="Version 1.0")
        cls.pages_bcm_v1 = cls.parser_bcm_v1.extract_pages()
        cls.chunks_bcm_v1 = cls.parser_bcm_v1.chunk_document()

        cls.parser_bcm_v2 = PDFParser(str(cls.pdf_bcm_v2_path), fallback_version="Version 2.0")
        cls.pages_bcm_v2 = cls.parser_bcm_v2.extract_pages()
        cls.chunks_bcm_v2 = cls.parser_bcm_v2.chunk_document()

        cls.extractor = ArchitectureExtractor()
        cls.entities_ecu_v1 = cls.extractor.extract_entities(cls.pages_ecu_v1)
        cls.entities_bcm_v1 = cls.extractor.extract_entities(cls.pages_bcm_v1)
        cls.entities_bcm_v2 = cls.extractor.extract_entities(cls.pages_bcm_v2)

    def test_relationship_builder(self):
        """Test 5-tier relationship tree construction."""
        builder = RelationshipBuilder()
        tree = builder.build_tree(self.pages_ecu_v1, self.entities_ecu_v1)
        self.assertIsInstance(tree, list)
        self.assertGreater(len(tree), 0)
        self.assertIn("swc_name", tree[0])
        self.assertIn("ports", tree[0])

    def test_port_non_duplication_and_mapping(self):
        """Verify ports belong ONLY to their owner SWC and generic fallbacks are avoided."""
        builder = RelationshipBuilder()
        tree = builder.build_tree(self.pages_ecu_v1, self.entities_ecu_v1)

        all_seen_ports = []
        for swc_node in tree:
            swc_ports = [p["port_name"] for p in swc_node["ports"]]

            for port_name in swc_ports:
                self.assertNotIn(
                    port_name,
                    all_seen_ports,
                    f"Port '{port_name}' was duplicated under multiple SWCs!"
                )
                all_seen_ports.append(port_name)

            for p in swc_node["ports"]:
                self.assertNotEqual(p["mapped_interface"], "Unmapped Interface")
                self.assertNotIn("Default Payload Signal", p["mapped_signals"])
                self.assertNotEqual(p["target_component"], "RTE / BSW Gateway")

    def test_bcm_v1_vs_v2_revision_comparison(self):
        """Verify proper BCM V1 vs BCM V2 document revision comparison."""
        comparator = DocumentComparator()
        diff = comparator.compare_revisions(
            "AUTOSAR_Body_Control_Module_HLD.pdf",
            "AUTOSAR_Body_Control_Module_HLD_V2.pdf",
            self.chunks_bcm_v1,
            self.chunks_bcm_v2,
            self.entities_bcm_v1,
            self.entities_bcm_v2
        )

        # Added SWC: WindowControl_SWC
        self.assertIn("WindowControl_SWC", diff["components"]["added"])
        # Added Interface: If_WindowPosition
        self.assertIn("If_WindowPosition", diff["interfaces"]["added"])
        # Added Signal: Sig_WindowPos_pct
        self.assertIn("Sig_WindowPos_pct", diff["signals"]["added"])
        # Added BSW Module: Dem
        self.assertIn("Dem", diff["bsw_modules"]["added"])
        # Removed Interface: If_LegacyState
        self.assertIn("If_LegacyState", diff["interfaces"]["removed"])

    def test_version_aware_qa_synthesis(self):
        """Verify Version-Aware Q&A uses structured comparison results and section-specific citations."""
        comparator = DocumentComparator()
        diff = comparator.compare_revisions(
            "AUTOSAR_Body_Control_Module_HLD.pdf",
            "AUTOSAR_Body_Control_Module_HLD_V2.pdf",
            self.chunks_bcm_v1,
            self.chunks_bcm_v2,
            self.entities_bcm_v1,
            self.entities_bcm_v2
        )

        llm = LLMEngine(provider="offline")

        # 1. "What changed between HLD V1 and V2? List added components, BSW modules, and signals."
        q1 = "What changed between HLD V1 and V2? List added components, BSW modules, and signals."
        res1 = llm.generate_rag_response(q1, self.chunks_bcm_v2, comparison_results=diff)
        self.assertIn("WindowControl_SWC", res1["answer"])
        self.assertIn("Dem", res1["answer"])
        self.assertIn("Sig_WindowPos_pct", res1["answer"])
        self.assertIn("If_LegacyState", res1["answer"])
        self.assertNotIn("Interface If_WindowPosition /", res1["answer"]) # Ensure If_WindowPosition is not under Removed Elements
        self.assertGreaterEqual(len(res1["citations"]), 4)
        
        cit_elements = [c.get("element") for c in res1["citations"]]
        self.assertIn("WindowControl_SWC", cit_elements)
        self.assertIn("If_WindowPosition", cit_elements)
        self.assertIn("Sig_WindowPos_pct", cit_elements)
        self.assertIn("Dem", cit_elements)
        self.assertTrue(all(c.get("page") == 1 and "2.0" in c.get("version") and c.get("section") for c in res1["citations"]))

        # 2. "Which SWCs were modified or added in Version 2.0?"
        res2 = llm.generate_rag_response("Which SWCs were modified or added in Version 2.0?", self.chunks_bcm_v2, comparison_results=diff)
        self.assertIn("WindowControl_SWC", res2["answer"])
        self.assertEqual(res2["citations"][0]["element"], "WindowControl_SWC")
        self.assertIn("Application Components", res2["citations"][0]["section"])

        # 3. "What BSW drivers or dependencies were added in Version 2.0?"
        res3 = llm.generate_rag_response("What BSW drivers or dependencies were added in Version 2.0?", self.chunks_bcm_v2, comparison_results=diff)
        self.assertIn("Dem", res3["answer"])
        self.assertEqual(res3["citations"][0]["element"], "Dem")
        self.assertIn("Basic Software Stack", res3["citations"][0]["section"])

        # 4. "Show evidence for changes"
        res4 = llm.generate_rag_response("Show evidence for changes", self.chunks_bcm_v2, comparison_results=diff)
        self.assertIn("If_LegacyState", res4["answer"])
        self.assertIn("If_WindowPosition", res4["answer"])
        self.assertNotIn("Interface If_WindowPosition /", res4["answer"])
        self.assertGreaterEqual(len(res4["citations"]), 4)

    def test_component_detail_report_lighting_swc_no_fake_flows(self):
        """Verify component detail report for component with no documented ports (LightingControl_SWC)."""
        reporter = ReportGenerator(OUTPUT_DIR)
        builder = RelationshipBuilder()
        tree_bcm = builder.build_tree(self.pages_bcm_v1, self.entities_bcm_v1)
        analyzer = CompletenessAnalyzer()
        findings = analyzer.analyze_completeness(self.pages_bcm_v1, self.entities_bcm_v1, tree_bcm)

        lighting_node = next((n for n in tree_bcm if n["swc_name"] == "LightingControl_SWC"), {"swc_name": "LightingControl_SWC", "ports": []})
        report = reporter.export_component_detail_report("LightingControl_SWC", lighting_node, findings)

        self.assertEqual(report["component_name"], "LightingControl_SWC")
        self.assertEqual(report["ports"], [])
        self.assertEqual(report["functional_flows"], [], "Must NOT invent fake functional flows when ports are empty!")
        self.assertEqual(report["source_references"], [], "Must NOT create source references when no port evidence exists!")

    def test_component_detail_report_doorlock_swc(self):
        """Verify component detail report for component with documented ports (DoorLock_SWC)."""
        reporter = ReportGenerator(OUTPUT_DIR)
        builder = RelationshipBuilder()
        tree_bcm = builder.build_tree(self.pages_bcm_v1, self.entities_bcm_v1)
        analyzer = CompletenessAnalyzer()
        findings = analyzer.analyze_completeness(self.pages_bcm_v1, self.entities_bcm_v1, tree_bcm)

        dl_node = next((n for n in tree_bcm if n["swc_name"] == "DoorLock_SWC"), {})
        report = reporter.export_component_detail_report("DoorLock_SWC", dl_node, findings)

        self.assertEqual(report["component_name"], "DoorLock_SWC")
        self.assertGreater(len(report["ports"]), 0)
        self.assertGreater(len(report["functional_flows"]), 0)
        self.assertIn("Document Page 1", report["source_references"])

    def test_completeness_analyzer(self):
        """Test rule-based completeness analysis and exact reason text."""
        builder = RelationshipBuilder()
        tree = builder.build_tree(self.pages_ecu_v1, self.entities_ecu_v1)
        analyzer = CompletenessAnalyzer()
        findings = analyzer.analyze_completeness(self.pages_ecu_v1, self.entities_ecu_v1, tree)
        self.assertIsInstance(findings, list)
        
        runnable_finding = next((f for f in findings if f.get("category") == "Incomplete Component Specification"), None)
        self.assertIsNotNone(runnable_finding)
        self.assertEqual(
            runnable_finding["reason_for_flagging"],
            "The HLD does not document how SWC execution is triggered or scheduled. This may limit verification of RTE scheduling and execution behavior."
        )

    def test_report_generator_structured_export(self):
        """Test structured JSON export."""
        reporter = ReportGenerator(OUTPUT_DIR)
        builder = RelationshipBuilder()
        tree = builder.build_tree(self.pages_ecu_v1, self.entities_ecu_v1)
        analyzer = CompletenessAnalyzer()
        findings = analyzer.analyze_completeness(self.pages_ecu_v1, self.entities_ecu_v1, tree)

        json_path = reporter.export_structured_json(
            {"doc_name": "V1.pdf"},
            self.entities_ecu_v1,
            tree,
            findings
        )
        self.assertTrue(json_path.exists())

if __name__ == "__main__":
    unittest.main()
