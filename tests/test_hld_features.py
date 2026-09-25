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
from src.report_generator import ReportGenerator
from src.config import SAMPLE_DOCS_DIR, OUTPUT_DIR

class TestHLDAssistantFeatures(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.pdf_v1_path = SAMPLE_DOCS_DIR / "AUTOSAR_Engine_Control_Unit_HLD.pdf"
        cls.pdf_v2_path = SAMPLE_DOCS_DIR / "AUTOSAR_Engine_Control_Unit_HLD_V2.pdf"
        cls.pdf_bcm_path = SAMPLE_DOCS_DIR / "AUTOSAR_Body_Control_Module_HLD.pdf"

        cls.parser_v1 = PDFParser(str(cls.pdf_v1_path), doc_version="V1.0")
        cls.pages_v1 = cls.parser_v1.extract_pages()
        cls.chunks_v1 = cls.parser_v1.chunk_document()

        cls.parser_v2 = PDFParser(str(cls.pdf_v2_path), doc_version="V2.0")
        cls.pages_v2 = cls.parser_v2.extract_pages()
        cls.chunks_v2 = cls.parser_v2.chunk_document()

        cls.parser_bcm = PDFParser(str(cls.pdf_bcm_path), doc_version="V1.4")
        cls.pages_bcm = cls.parser_bcm.extract_pages()
        cls.chunks_bcm = cls.parser_bcm.chunk_document()

        cls.extractor = ArchitectureExtractor()
        cls.entities_v1 = cls.extractor.extract_entities(cls.pages_v1)
        cls.entities_v2 = cls.extractor.extract_entities(cls.pages_v2)
        cls.entities_bcm = cls.extractor.extract_entities(cls.pages_bcm)

    def test_relationship_builder(self):
        """Test 5-tier relationship tree construction."""
        builder = RelationshipBuilder()
        tree = builder.build_tree(self.pages_v1, self.entities_v1)
        self.assertIsInstance(tree, list)
        self.assertGreater(len(tree), 0)
        self.assertIn("swc_name", tree[0])
        self.assertIn("ports", tree[0])

    def test_port_non_duplication_and_mapping(self):
        """Verify ports belong ONLY to their owner SWC and generic fallbacks are avoided."""
        builder = RelationshipBuilder()
        tree = builder.build_tree(self.pages_v1, self.entities_v1)

        all_seen_ports = []
        for swc_node in tree:
            swc_name = swc_node["swc_name"]
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

        esc_node = next((node for node in tree if node["swc_name"] == "EngineSpeedControl_SWC"), None)
        self.assertIsNotNone(esc_node)
        port_names = [p["port_name"] for p in esc_node["ports"]]
        self.assertIn("PPort_EngineSpeed", port_names)
        self.assertNotIn("PPort_ThrottleActuator", port_names)

    def test_bcm_mapping_and_no_generic_fallbacks(self):
        """Verify BCM relationships, no invented interfaces/signals, and total absence of RTE / BSW Gateway."""
        builder = RelationshipBuilder()
        tree_bcm = builder.build_tree(self.pages_bcm, self.entities_bcm)

        # Verify 'RTE / BSW Gateway' is NEVER present anywhere in tree
        for swc_node in tree_bcm:
            self.assertNotIn("RTE / BSW Gateway", swc_node["connected_components"])
            for p in swc_node["ports"]:
                self.assertNotEqual(p["target_component"], "RTE / BSW Gateway")
                self.assertNotEqual(p["mapped_interface"], "Unmapped Interface")
                self.assertNotIn("Default Payload Signal", p["mapped_signals"])

        # Check DoorLock_SWC specific ports
        dl_node = next((node for node in tree_bcm if node["swc_name"] == "DoorLock_SWC"), None)
        self.assertIsNotNone(dl_node)

        # 1. RPort_DoorStatus -> If_DoorState -> Sig_DoorLock_status
        rport_ds = next((p for p in dl_node["ports"] if p["port_name"] == "RPort_DoorStatus"), None)
        self.assertIsNotNone(rport_ds)
        self.assertEqual(rport_ds["mapped_interface"], "If_DoorState")
        self.assertIn("Sig_DoorLock_status", rport_ds["mapped_signals"])

        # 2. PPort_LockActuator -> "Not specified in source document" for interface & signal
        pport_la = next((p for p in dl_node["ports"] if p["port_name"] == "PPort_LockActuator"), None)
        self.assertIsNotNone(pport_la)
        self.assertEqual(pport_la["mapped_interface"], "Not specified in source document")
        self.assertEqual(pport_la["mapped_signals"], ["Not specified in source document"])
        self.assertEqual(pport_la["target_component"], "Not specified in source document")

    def test_completeness_analyzer(self):
        """Test rule-based completeness analysis."""
        builder = RelationshipBuilder()
        tree = builder.build_tree(self.pages_v1, self.entities_v1)
        analyzer = CompletenessAnalyzer()
        findings = analyzer.analyze_completeness(self.pages_v1, self.entities_v1, tree)
        self.assertIsInstance(findings, list)
        for f in findings:
            self.assertIn("category", f)
            self.assertIn("evidence", f)
            self.assertIn("detected_gap", f)
            self.assertIn("reason_for_flagging", f)
            self.assertIn("citation", f)

    def test_document_comparator(self):
        """Test HLD V1 vs V2 revision comparison."""
        comparator = DocumentComparator()
        diff = comparator.compare_revisions(
            "V1.pdf", "V2.pdf",
            self.chunks_v1, self.chunks_v2,
            self.entities_v1, self.entities_v2
        )
        self.assertIn("components", diff)
        self.assertIn("added", diff["components"])
        self.assertIn("TurboBoostControl_SWC", diff["components"]["added"])

    def test_version_aware_vector_store(self):
        """Test version-aware vector store filtering."""
        vs = VectorStore()
        vs.add_chunks(self.chunks_v1)
        vs.add_chunks(self.chunks_v2)
        results = vs.search("EngineSpeedControl_SWC", top_k=2, version_filter="V2.0")
        self.assertIsInstance(results, list)
        if results:
            self.assertEqual(results[0].get("doc_version"), "V2.0")

    def test_report_generator_structured_export(self):
        """Test component detail report & structured JSON export."""
        reporter = ReportGenerator(OUTPUT_DIR)
        builder = RelationshipBuilder()
        tree = builder.build_tree(self.pages_v1, self.entities_v1)
        analyzer = CompletenessAnalyzer()
        findings = analyzer.analyze_completeness(self.pages_v1, self.entities_v1, tree)

        detail = reporter.export_component_detail_report("EngineSpeedControl_SWC", tree[0], findings)
        self.assertEqual(detail["component_name"], "EngineSpeedControl_SWC")

        json_path = reporter.export_structured_json(
            {"doc_name": "V1.pdf"},
            self.entities_v1,
            tree,
            findings
        )
        self.assertTrue(json_path.exists())

if __name__ == "__main__":
    unittest.main()
