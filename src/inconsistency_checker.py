from typing import List, Dict, Any

class InconsistencyChecker:
    """Analyzes extracted AUTOSAR entities for missing dependencies, orphaned ports, and missing BSW modules."""

    def analyze(self, entities: Dict[str, Any], full_text: str) -> List[Dict[str, Any]]:
        inconsistencies = []

        swcs = entities.get("software_components", [])
        bsw = set(entities.get("bsw_modules", []))
        ports = entities.get("ports", [])

        # Check 1: Orphaned Ports (RPort without matching PPort)
        r_ports = [p["port_name"] for p in ports if "RPort" in p["type"]]
        p_ports = set(p["port_name"] for p in ports if "PPort" in p["type"])

        for rport in r_ports:
            # Expected matching PPort pattern (e.g., RPort_EngineSpeed -> PPort_EngineSpeed)
            base_name = rport.replace("RPort_", "").replace("R_", "")
            expected_pport_1 = f"PPort_{base_name}"
            expected_pport_2 = f"P_{base_name}"

            if expected_pport_1 not in p_ports and expected_pport_2 not in p_ports:
                inconsistencies.append({
                    "type": "Orphaned RPort",
                    "severity": "HIGH",
                    "item": rport,
                    "description": f"Requester port '{rport}' has no matching Provider port (PPort) defined in the architecture.",
                    "impact": "Unresolved component communication interface leading to build/RTE generation failure."
                })

        # Check 2: BSW Dependency Completeness
        if "CanIf" in bsw and "Can" not in bsw:
            inconsistencies.append({
                "type": "Missing BSW Driver",
                "severity": "CRITICAL",
                "item": "Can Driver (MCAL)",
                "description": "CAN Interface (CanIf) is included, but physical CAN Driver (Can MCAL) module is missing in HLD.",
                "impact": "CAN bus communication stack cannot initialize hardware registers."
            })

        if "Dem" in bsw and "Dcm" not in bsw:
            inconsistencies.append({
                "type": "Missing Diagnostic Stack Module",
                "severity": "MEDIUM",
                "item": "Dcm (Diagnostic Communication Manager)",
                "description": "Diagnostic Event Manager (Dem) is present, but Diagnostic Communication Manager (Dcm) is not defined.",
                "impact": "Diagnostic Trouble Codes (DTCs) stored by Dem cannot be transmitted over tester UDS services."
            })

        if "BswM" in bsw and "EcuM" not in bsw:
            inconsistencies.append({
                "type": "Missing Mode Management Dependency",
                "severity": "HIGH",
                "item": "EcuM (ECU State Manager)",
                "description": "BSW Mode Manager (BswM) is present, but ECU State Manager (EcuM) is omitted.",
                "impact": "ECU startup, shutdown, and sleep state transitions cannot be coordinated."
            })

        # Check 3: Undefined SWC Runnables
        if len(swcs) > 0 and "Runnable" not in full_text and "runnable" not in full_text:
            inconsistencies.append({
                "type": "Missing Runnable Entity Specification",
                "severity": "MEDIUM",
                "item": "Runnable Entities",
                "description": "Software Components are defined, but no Runnable Entities or OS Task mappings are specified.",
                "impact": "OS task scheduler cannot bind SWC execution triggers."
            })

        # Check 4: Unassigned Data Signals
        signals = entities.get("signals", [])
        if signals and not ports:
            inconsistencies.append({
                "type": "Unmapped Data Signals",
                "severity": "LOW",
                "item": f"{len(signals)} Signals",
                "description": "Data signals are mentioned in text without explicit Port Prototype mappings.",
                "impact": "Signal traceability from RTE to COM layer is incomplete."
            })

        return inconsistencies
