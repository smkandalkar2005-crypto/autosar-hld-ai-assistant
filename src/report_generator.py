import json
from pathlib import Path
from typing import Dict, Any
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

class ReportGenerator:
    """Generates downloadable structured JSON and PDF executive reports."""

    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

    def export_json(self, data: Dict[str, Any], filename: str = "autosar_analysis_report.json") -> Path:
        out_path = self.output_dir / filename
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        return out_path

    def export_pdf(self, doc_name: str, entities: Dict[str, Any], inconsistencies: list, filename: str = "autosar_analysis_report.pdf") -> Path:
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
            ('BACKGROUND', (0, 0), (1, 0), colors.HexColor('#3B82F6')),
            ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(t)
        elements.append(Spacer(1, 16))

        # Inconsistency Findings Section
        elements.append(Paragraph("2. Detected Inconsistencies & Architecture Gaps", heading_style))

        if inconsistencies:
            inc_data = [["Severity", "Finding Type", "Description"]]
            for inc in inconsistencies:
                inc_data.append([
                    inc.get("severity", "MEDIUM"),
                    inc.get("type", "Gap"),
                    Paragraph(inc.get("description", ""), styles['Normal'])
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
