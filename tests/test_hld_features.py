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

        cls.parser_v1 = PDFParser(str(cls.pdf_v1_path), doc_version="V1.0")
        cls.pages_v1 = cls.parser_v1.extract_pages()
        cls.chunks_v1 = cls.parser_v1.chunk_document()

        cls.parser_v2 = PDFParser(str(cls.pdf_v2_path), doc_version="V2.0")
        cls.pages_v2 = cls.parser_v2.extract_pages()
        cls.chunks_v2 = cls.parser_v2.chunk_document()

        cls.extractor = ArchitectureExtractor()
        cls.entities_v1 = cls.extractor.extract_entities(cls.pages_v1)
        cls.entities_v2 = cls.extractor.extract_entities(cls.pages_v2)

    def test_relationship_builder(self):
        """Test 5-tier relationship tree construction."""
        builder = RelationshipBuilder()
        tree = builder.build_tree(self.pages_v1, self.entities_v1)
        self.assertIsInstance(tree, list)
        self.assertGreater(len(tree), 0)
        self.assertIn("swc_name", tree[0])
        self.assertIn("ports", tree[0])

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
