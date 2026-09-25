import os
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def create_sample_pdf_1(out_path: Path):
    doc = SimpleDocTemplate(str(out_path), pagesize=letter)
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=18, textColor=colors.HexColor('#0F172A'), spaceAfter=10)
    h2_style = ParagraphStyle('H2Style', parent=styles['Heading2'], fontSize=13, textColor=colors.HexColor('#2563EB'), spaceBefore=8, spaceAfter=4)
    body_style = ParagraphStyle('BodyStyle', parent=styles['Normal'], fontSize=9.5, leading=13)

    elements = []
    
    elements.append(Paragraph("AUTOSAR Engine Control Unit (ECU) High-Level Design (Version 1.0)", title_style))
    elements.append(Paragraph("<b>[SAMPLE / TEST DATA FOR DEMONSTRATION ONLY]</b> | Document Version: 1.0", body_style))
    elements.append(Spacer(1, 10))

    elements.append(Paragraph("1. Executive Architecture Overview", h2_style))
    elements.append(Paragraph(
        "This document describes the AUTOSAR Classic architecture for the Engine Control Unit (ECU) V1.0. "
        "The software system follows AUTOSAR 4.4 specifications, separating Application Software Components (SWCs) "
        "from the Basic Software (BSW) stack via the Runtime Environment (RTE).", body_style
    ))
    elements.append(Spacer(1, 8))

    elements.append(Paragraph("2. Software Component (SWC) Specification", h2_style))
    elements.append(Paragraph(
        "The application layer contains two primary components: <b>EngineSpeedControl_SWC</b> and <b>ThrottleControl_SWC</b>. "
        "EngineSpeedControl_SWC receives crankshaft sensor frequency data and calculates required torque output. "
        "ThrottleControl_SWC commands the throttle actuator position.", body_style
    ))
    elements.append(Spacer(1, 8))

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
        ('FONTSIZE', (0,0), (-1,-1), 8.5),
    ]))
    elements.append(t1)
    elements.append(Spacer(1, 10))

    elements.append(Paragraph("3. Basic Software (BSW) Stack Configuration", h2_style))
    elements.append(Paragraph(
        "The BSW layer includes <b>EcuM</b> (ECU State Manager), <b>BswM</b> (BSW Mode Manager), <b>CanIf</b> (CAN Interface), "
        "<b>Com</b> (Communication Stack), and <b>Dem</b> (Diagnostic Event Manager). "
        "CanIf handles frame routing between CanTp and MCAL CAN driver.", body_style
    ))
    elements.append(Spacer(1, 8))

    elements.append(Paragraph("4. Interface & Signal Specifications", h2_style))
    elements.append(Paragraph(
        "Inter-component communication relies on <i>SenderReceiverInterface</i> named <b>If_EngineData</b>. "
        "Signal <b>Sig_EngineSpeed_rpm</b> transmits engine rotation velocity, while <b>Sig_ThrottlePos_pct</b> transmits percentage opening. "
        "Diagnostic errors are logged into Dem via <i>ClientServerInterface</i> named <b>If_DiagService</b>.", body_style
    ))

    doc.build(elements)

def create_sample_pdf_v2(out_path: Path):
    """Generates a Revision V2 document to test HLD revision comparison capabilities."""
    doc = SimpleDocTemplate(str(out_path), pagesize=letter)
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=18, textColor=colors.HexColor('#0F172A'), spaceAfter=10)
    h2_style = ParagraphStyle('H2Style', parent=styles['Heading2'], fontSize=13, textColor=colors.HexColor('#059669'), spaceBefore=8, spaceAfter=4)
    body_style = ParagraphStyle('BodyStyle', parent=styles['Normal'], fontSize=9.5, leading=13)

    elements = []
    
    elements.append(Paragraph("AUTOSAR Engine Control Unit (ECU) High-Level Design (Version 2.0 Revision)", title_style))
    elements.append(Paragraph("<b>[SAMPLE / TEST DATA FOR REVISION COMPARISON DEMONSTRATION ONLY]</b> | Document Version: 2.0", body_style))
    elements.append(Spacer(1, 10))

    elements.append(Paragraph("1. Executive Architecture Overview", h2_style))
    elements.append(Paragraph(
        "This document describes the updated AUTOSAR Classic architecture for the Engine Control Unit (ECU) V2.0. "
        "Version 2.0 introduces turbocharger boost management and advanced thermal supervision components.", body_style
    ))
    elements.append(Spacer(1, 8))

    elements.append(Paragraph("2. Software Component (SWC) Specification", h2_style))
    elements.append(Paragraph(
        "The application layer contains components: <b>EngineSpeedControl_SWC</b>, <b>ThrottleControl_SWC</b>, "
        "and new component <b>TurboBoostControl_SWC</b>. EngineSpeedControl_SWC has been updated with new temperature sensor inputs.", body_style
    ))
    elements.append(Spacer(1, 8))

    swc_table = [
        ["SWC Name", "Component Type", "Provided Ports", "Required Ports"],
        ["EngineSpeedControl_SWC", "Atomic Application SWC", "PPort_EngineSpeed", "RPort_ThrottlePos"],
        ["ThrottleControl_SWC", "Atomic Application SWC", "PPort_ThrottleActuator", "RPort_EngineSpeed"],
        ["TurboBoostControl_SWC", "Atomic Application SWC", "PPort_BoostPressure", "RPort_EngineSpeed"]
    ]
    t1 = Table(swc_table, colWidths=[140, 120, 110, 110])
    t1.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#059669')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#94A3B8')),
        ('FONTSIZE', (0,0), (-1,-1), 8.5),
    ]))
    elements.append(t1)
    elements.append(Spacer(1, 10))

    elements.append(Paragraph("3. Basic Software (BSW) Stack Configuration", h2_style))
    elements.append(Paragraph(
        "The BSW layer includes <b>EcuM</b>, <b>BswM</b>, <b>CanIf</b>, <b>Can</b>, <b>Com</b>, <b>Dem</b>, and <b>Dcm</b>. "
        "Physical CAN Driver (Can MCAL) and Diagnostic Communication Manager (Dcm) have been added in V2.0 to fulfill BSW completeness.", body_style
    ))
    elements.append(Spacer(1, 8))

    elements.append(Paragraph("4. Interface & Signal Specifications", h2_style))
    elements.append(Paragraph(
        "Inter-component communication relies on <i>SenderReceiverInterface</i> named <b>If_EngineData</b> and <b>If_BoostData</b>. "
        "Signal <b>Sig_EngineSpeed_rpm</b> transmits rotation velocity, <b>Sig_ThrottlePos_pct</b> transmits throttle percentage, "
        "and new signal <b>Sig_BoostPressure_bar</b> transmits manifold pressure.", body_style
    ))
    elements.append(Spacer(1, 8))

    elements.append(Paragraph("5. Thermal Management Subsystem", h2_style))
    elements.append(Paragraph(
        "Section 5 is added in V2.0 to define thermal protection strategies and radiator fan relay actuation.", body_style
    ))

    doc.build(elements)

def create_sample_pdf_bcm(out_path: Path):
    doc = SimpleDocTemplate(str(out_path), pagesize=letter)
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=18, textColor=colors.HexColor('#0F172A'), spaceAfter=10)
    h2_style = ParagraphStyle('H2Style', parent=styles['Heading2'], fontSize=13, textColor=colors.HexColor('#D97706'), spaceBefore=8, spaceAfter=4)
    body_style = ParagraphStyle('BodyStyle', parent=styles['Normal'], fontSize=9.5, leading=13)

    elements = []
    
    elements.append(Paragraph("AUTOSAR Body Control Module (BCM) High-Level Design", title_style))
    elements.append(Paragraph("<b>[SAMPLE / TEST DATA FOR DEMONSTRATION ONLY]</b> | Document Version: 1.4", body_style))
    elements.append(Spacer(1, 10))

    elements.append(Paragraph("1. System Purpose & Functional Scope", h2_style))
    elements.append(Paragraph(
        "The Body Control Module (BCM) manages vehicle interior lighting, door locks, and window position control. "
        "It integrates Application SWCs with the BSW CAN communication stack.", body_style
    ))
    elements.append(Spacer(1, 8))

    elements.append(Paragraph("2. Application Components", h2_style))
    elements.append(Paragraph(
        "Components defined include <b>LightingControl_SWC</b> and <b>DoorLock_SWC</b>. "
        "LightingControl_SWC receives headlight switch status over CAN and drives PWM headlight relays.", body_style
    ))
    elements.append(Spacer(1, 8))

    elements.append(Paragraph("3. Interface & Port Configuration", h2_style))
    elements.append(Paragraph(
        "DoorLock_SWC exposes <b>RPort_DoorStatus</b> to read latch microswitch state and <b>PPort_LockActuator</b> to trigger solenoids. "
        "Interface <b>If_DoorState</b> conveys lock state via signal <b>Sig_DoorLock_status</b>.", body_style
    ))

    doc.build(elements)

if __name__ == "__main__":
    sample_dir = Path(__file__).parent / "sample_documents"
    sample_dir.mkdir(exist_ok=True)
    create_sample_pdf_1(sample_dir / "AUTOSAR_Engine_Control_Unit_HLD.pdf")
    create_sample_pdf_v2(sample_dir / "AUTOSAR_Engine_Control_Unit_HLD_V2.pdf")
    create_sample_pdf_bcm(sample_dir / "AUTOSAR_Body_Control_Module_HLD.pdf")
    print(f"Sample PDF documents (V1, V2, BCM) generated successfully in {sample_dir}")
