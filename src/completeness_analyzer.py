from typing import List, Dict, Any

class CompletenessAnalyzer:
    """
    Performs deterministic, rule-based architectural completeness checks on extracted HLD entities.
    Every finding explicitly distinguishes:
    1. Evidence found in document
    2. Detected gap
    3. Reason for flagging
    4. Source page/section citation
    """

    def analyze_completeness(self, pages: List[Dict[str, Any]], entities: Dict[str, Any], relationship_tree: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        findings = []

        swcs = entities.get("software_components", [])
        bsw = set(entities.get("bsw_modules", []))
        ports = entities.get("ports", [])
        interfaces = entities.get("interfaces", [])
        signals = entities.get("signals", [])
        deps = entities.get("dependencies", [])

        # Check 1: Incomplete Port/Interface Relationships
        for swc_node in relationship_tree:
            swc_name = swc_node["swc_name"]
            for port in swc_node["ports"]:
                if port["mapped_interface"] == "Not specified in source document":
                    page_ref = port.get("page_num", 1)
                    findings.append({
                        "category": "Incomplete Port/Interface Relationship",
                        "severity": "HIGH",
                        "item": f"{swc_name} :: {port['port_name']}",
                        "evidence": f"Port prototype '{port['port_name']}' found in component '{swc_name}' on Page {page_ref}.",
                        "detected_gap": "No matching SenderReceiver or ClientServer interface definition is explicitly bound to this port.",
                        "reason_for_flagging": "AUTOSAR ports must bind to a concrete Interface specification before RTE generation.",
                        "citation": f"Page {page_ref}, Section: Software Component Specification"
                    })

        # Check 2: Missing Signals on Connected Interfaces
        if interfaces and not signals:
            findings.append({
                "category": "Missing Data Signals",
                "severity": "HIGH",
                "item": "Interface Payload Signals",
                "evidence": f"Interfaces found: {', '.join(interfaces[:3])}.",
                "detected_gap": "No individual data element signals (e.g. Sig_*) are defined for these interfaces.",
                "reason_for_flagging": "Interfaces require explicit data elements and signal data types for COM mapping.",
                "citation": "Document-wide Interface Section"
            })

        # Check 3: Missing MCAL / Hardware Drivers
        if "CanIf" in bsw and "Can" not in bsw:
            page_num = 1
            for p in pages:
                if "CanIf" in p["text"]:
                    page_num = p["page_num"]
                    break
            findings.append({
                "category": "Missing BSW MCAL Driver",
                "severity": "CRITICAL",
                "item": "Can (MCAL CAN Driver)",
                "evidence": f"CanIf module specified on Page {page_num}.",
                "detected_gap": "Physical CAN Driver (Can MCAL) module is omitted in the HLD document.",
                "reason_for_flagging": "CanIf requires physical CAN driver API hooks to transmit hardware frames.",
                "citation": f"Page {page_num}, Section: Basic Software Configuration"
            })

        # Check 4: Missing Diagnostic Stack Linkage
        if "Dem" in bsw and "Dcm" not in bsw:
            page_num = 1
            for p in pages:
                if "Dem" in p["text"]:
                    page_num = p["page_num"]
                    break
            findings.append({
                "category": "Incomplete Diagnostic Stack",
                "severity": "MEDIUM",
                "item": "Dcm (Diagnostic Communication Manager)",
                "evidence": f"Diagnostic Event Manager (Dem) defined on Page {page_num}.",
                "detected_gap": "Diagnostic Communication Manager (Dcm) is missing in BSW stack.",
                "reason_for_flagging": "Stored DTCs in Dem cannot be polled via external UDS tester services without Dcm.",
                "citation": f"Page {page_num}, Section: BSW Diagnostics Layer"
            })

        # Check 5: Incomplete Component Information (Missing Runnable / OS Task)
        full_text = " ".join([p["text"] for p in pages])
        if swcs and "runnable" not in full_text.lower():
            findings.append({
                "category": "Incomplete Component Specification",
                "severity": "MEDIUM",
                "item": "Runnable Entities & OS Task Triggers",
                "evidence": f"{len(swcs)} Software Components defined ({', '.join(swcs[:2])}).",
                "detected_gap": "No Runnable Entities, period timing, or OS task execution bindings are documented.",
                "reason_for_flagging": "The HLD does not document how SWC execution is triggered or scheduled. This may limit verification of RTE scheduling and execution behavior.",
                "citation": "Document-wide Component Section"
            })

        # Check 6: Unresolved Component Dependencies
        if len(swcs) > 1 and not deps:
            findings.append({
                "category": "Incomplete Functional Flow",
                "severity": "LOW",
                "item": "Inter-Component Control Flow",
                "evidence": f"Multiple SWCs defined: {', '.join(swcs)}.",
                "detected_gap": "No explicit functional flow or inter-component call dependencies specified.",
                "reason_for_flagging": "System architecture lacks end-to-end data flow traceability.",
                "citation": "Document-wide Architecture Overview"
            })

        return findings
