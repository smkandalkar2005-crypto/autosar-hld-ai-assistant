import os
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def create_sample_pdf_1(out_path: Path):
    doc = SimpleDocTemplate(str(out_path), pagesize=letter)
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=20, textColor=colors.HexColor('#0F172A'), spaceAfter=12)
    h2_style = ParagraphStyle('H2Style', parent=styles['Heading2'], fontSize=14, textColor=colors.HexColor('#2563EB'), spaceBefore=10, spaceAfter=6)
    body_style = ParagraphStyle('BodyStyle', parent=styles['Normal'], fontSize=10, leading=14)

    elements = []
    
    # Page 1
    elements.append(Paragraph("AUTOSAR Engine Control Unit (ECU) High-Level Design", title_style))
    elements.append(Paragraph("Document Version: 2.1 | Classification: Technical Public", body_style))
    elements.append(Spacer(1, 14))

    elements.append(Paragraph("1. Executive Architecture Overview", h2_style))
    elements.append(Paragraph(
        "This document describes the AUTOSAR Classic architecture for the Engine Control Unit (ECU). "
        "The software system follows AUTOSAR 4.4 specifications, separating Application Software Components (SWCs) "
        "from the Basic Software (BSW) stack via the Runtime Environment (RTE).", body_style
    ))
    elements.append(Spacer(1, 10))

    elements.append(Paragraph("2. Software Component (SWC) Specification", h2_style))
    elements.append(Paragraph(
        "The application layer contains two primary components: <b>EngineSpeedControl_SWC</b> and <b>ThrottleControl_SWC</b>. "
        "EngineSpeedControl_SWC receives crankshaft sensor frequency data and calculates required torque output. "
        "ThrottleControl_SWC commands the throttle actuator position.", body_style
    ))
    elements.append(Spacer(1, 10))

    swc_table = [
        ["SWC Name", "Component Type", "Provided Ports", "Required Ports"],
        ["EngineSpeedControl_SWC", "Atomic Application SWC", "PPort_EngineSpeed", "RPort_ThrottlePos"],
        ["ThrottleControl_SWC", "Atomic Application SWC", "PPort_ThrottleActuator", "RPort_EngineSpeed"]
    ]
    t1 = Table(swc_table, colWidths=[140, 120, 110, 110])
    t1.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2563EB')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#94A3B8')),
        ('FONTSIZE', (0,0), (-1,-1), 9),
    ]))
    elements.append(t1)
    elements.append(Spacer(1, 14))

    elements.append(Paragraph("3. Basic Software (BSW) Stack Configuration", h2_style))
    elements.append(Paragraph(
        "The BSW layer includes <b>EcuM</b> (ECU State Manager), <b>BswM</b> (BSW Mode Manager), <b>CanIf</b> (CAN Interface), "
        "<b>Com</b> (Communication Stack), and <b>Dem</b> (Diagnostic Event Manager). "
        "CanIf handles frame routing between CanTp and MCAL CAN driver.", body_style
    ))
    elements.append(Spacer(1, 10))

    elements.append(Paragraph("4. Interface & Signal Specifications", h2_style))
    elements.append(Paragraph(
        "Inter-component communication relies on <i>SenderReceiverInterface</i>. "
        "Signal <b>Sig_EngineSpeed_rpm</b> transmits engine rotation velocity, while <b>Sig_ThrottlePos_pct</b> transmits percentage opening. "
        "Diagnostic errors are logged into Dem via <i>ClientServerInterface</i>.", body_style
    ))

    doc.build(elements)

def create_sample_pdf_2(out_path: Path):
    doc = SimpleDocTemplate(str(out_path), pagesize=letter)
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=20, textColor=colors.HexColor('#0F172A'), spaceAfter=12)
    h2_style = ParagraphStyle('H2Style', parent=styles['Heading2'], fontSize=14, textColor=colors.HexColor('#059669'), spaceBefore=10, spaceAfter=6)
    body_style = ParagraphStyle('BodyStyle', parent=styles['Normal'], fontSize=10, leading=14)

    elements = []
    
    elements.append(Paragraph("AUTOSAR Body Control Module (BCM) High-Level Design", title_style))
    elements.append(Paragraph("Document Version: 1.4 | Classification: Technical Public", body_style))
    elements.append(Spacer(1, 14))

    elements.append(Paragraph("1. System Purpose & Functional Scope", h2_style))
    elements.append(Paragraph(
        "The Body Control Module (BCM) manages vehicle interior lighting, door locks, and window position control. "
        "It integrates Application SWCs with the BSW CAN communication stack.", body_style
    ))
    elements.append(Spacer(1, 10))

    elements.append(Paragraph("2. Application Components", h2_style))
    elements.append(Paragraph(
        "Components defined include <b>LightingControl_SWC</b> and <b>DoorLock_SWC</b>. "
        "LightingControl_SWC receives headlight switch status over CAN and drives PWM headlight relays.", body_style
    ))
    elements.append(Spacer(1, 10))

    elements.append(Paragraph("3. Interface & Port Configuration", h2_style))
    elements.append(Paragraph(
        "DoorLock_SWC exposes <b>RPort_DoorStatus</b> to read latch microswitch state and <b>PPort_LockActuator</b> to trigger solenoids. "
        "Signal <b>Sig_DoorLock_status</b> is broadcast on CAN matrix.", body_style
    ))

    doc.build(elements)

if __name__ == "__main__":
    sample_dir = Path(__file__).parent / "sample_documents"
    sample_dir.mkdir(exist_ok=True)
    create_sample_pdf_1(sample_dir / "AUTOSAR_Engine_Control_Unit_HLD.pdf")
    create_sample_pdf_2(sample_dir / "AUTOSAR_Body_Control_Module_HLD.pdf")
    print(f"Sample PDF documents generated successfully in {sample_dir}")
