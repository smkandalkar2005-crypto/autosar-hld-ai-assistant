import json
from pathlib import Path
from typing import Dict, Any, List
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

class ReportGenerator:
    """Generates downloadable structured JSON specifications, executive PDF reports, component detail reports, and comparison findings."""

    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

    def export_structured_json(
        self,
        doc_metadata: Dict[str, Any],
        entities: Dict[str, Any],
        relationship_tree: List[Dict[str, Any]],
        completeness_findings: List[Dict[str, Any]],
        comparison_results: Dict[str, Any] = None,
        filename: str = "autosar_structured_architecture_spec.json"
    ) -> Path:
        """Requirement 5: Structured Architecture JSON export with full schema."""
        out_path = self.output_dir / filename
        data = {
            "document_metadata": doc_metadata,
            "architecture_inventory": {
                "software_components": entities.get("software_components", []),
                "bsw_modules": entities.get("bsw_modules", []),
                "interfaces": entities.get("interfaces", []),
                "ports": entities.get("ports", []),
                "signals": entities.get("signals", [])
            },
            "five_tier_relationships": relationship_tree,
            "completeness_findings": completeness_findings,
            "revision_comparison": comparison_results or {}
        }
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        return out_path

    def export_component_detail_report(self, component_name: str, swc_node: Dict[str, Any], completeness_findings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Requirement 4: Detailed Component Report for selected SWC."""
        comp_findings = [f for f in completeness_findings if component_name in f.get("item", "") or component_name in f.get("evidence", "")]
        
        connected = swc_node.get("connected_components", [])
        target_name = connected[0] if connected else "Not specified in source document"

        return {
            "component_name": component_name,
            "type": "Atomic Application Software Component",
            "ports": swc_node.get("ports", []),
            "connected_components": connected,
            "functional_flows": [
                f"Receives sensor data via RPort -> Computes internal algorithm -> Outputs control signal over PPort to {target_name}"
            ],
            "findings_and_gaps": comp_findings,
            "source_references": [f"Document Page {p.get('page_num', 1)}" for p in swc_node.get("ports", [])]
        }

    def export_pdf(self, doc_name: str, entities: Dict[str, Any], inconsistencies: list, filename: str = "autosar_analysis_report.pdf") -> Path:
        """Preserves existing executive PDF export capability."""
        out_path = self.output_dir / filename
        doc = SimpleDocTemplate(str(out_path), pagesize=letter)
        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            'TitleStyle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#0F172A'),
            spaceAfter=12
        )
        heading_style = ParagraphStyle(
            'HeadingStyle',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#1E293B'),
            spaceBefore=12,
            spaceAfter=6
        )

        elements = []
        elements.append(Paragraph("AUTOSAR HLD Architecture Analysis Report", title_style))
        elements.append(Paragraph(f"<b>Document Analyzed:</b> {doc_name}", styles['Normal']))
        elements.append(Spacer(1, 12))

        # Extracted Inventory Section
        elements.append(Paragraph("1. Extracted Architecture Inventory", heading_style))
        
        swcs = ", ".join(entities.get("software_components", [])) or "None detected"
        bsw = ", ".join(entities.get("bsw_modules", [])) or "None detected"
        interfaces = ", ".join(entities.get("interfaces", [])) or "None detected"

        table_data = [
            ["Category", "Extracted Items"],
            ["Software Components", Paragraph(swcs, styles['Normal'])],
            ["BSW Modules", Paragraph(bsw, styles['Normal'])],
            ["Interfaces", Paragraph(interfaces, styles['Normal'])],
            ["Port Prototypes", str(len(entities.get("ports", [])))],
            ["Signals", str(len(entities.get("signals", [])))]
        ]

        t = Table(table_data, colWidths=[150, 350])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (1, 0), colors.HexColor('#2563EB')),
            ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(t)
        elements.append(Spacer(1, 16))

        # Inconsistency Findings Section
        elements.append(Paragraph("2. Architectural Completeness & Inconsistency Findings", heading_style))

        if inconsistencies:
            inc_data = [["Severity", "Finding Type", "Description"]]
            for inc in inconsistencies:
                inc_data.append([
                    inc.get("severity", "MEDIUM"),
                    inc.get("type", inc.get("category", "Gap")),
                    Paragraph(inc.get("description", inc.get("detected_gap", "")), styles['Normal'])
                ])
            inc_table = Table(inc_data, colWidths=[80, 140, 280])
            inc_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E293B')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ]))
            elements.append(inc_table)
        else:
            elements.append(Paragraph("No critical architectural inconsistencies detected.", styles['Normal']))

        doc.build(elements)
        return out_path
