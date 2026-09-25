import re
from typing import List, Dict, Any

class RelationshipBuilder:
    """
    Builds structured multi-tier architectural relationship trees:
    SWC / Component -> Port Prototype -> Interface -> Signal -> Target Component / Dependency
    """

    def build_tree(self, pages: List[Dict[str, Any]], entities: Dict[str, Any]) -> List[Dict[str, Any]]:
        swcs = entities.get("software_components", [])
        ports = entities.get("ports", [])
        interfaces = entities.get("interfaces", [])
        signals = entities.get("signals", [])
        raw_deps = entities.get("dependencies", [])

        tree = []

        for swc in swcs:
            swc_node = {
                "swc_name": swc,
                "ports": [],
                "connected_components": [],
                "functional_flows": []
            }

            # Find ports associated with this SWC
            # Matching heuristic: port names containing component stem or mentioned on same page
            swc_stem = swc.replace("_SWC", "").replace("_Comp", "").replace("_App", "")

            for p in ports:
                port_name = p["port_name"]
                p_type = p["type"]
                page_num = p["page_num"]

                # Check if port maps to interface
                mapped_interface = "Unmapped Interface"
                for if_name in interfaces:
                    if if_name.lower().replace("if_", "") in port_name.lower() or swc_stem.lower() in if_name.lower():
                        mapped_interface = if_name
                        break
                    elif "Engine" in port_name and "Engine" in if_name:
                        mapped_interface = if_name
                        break

                # Check mapped signals
                mapped_signals = []
                for sig in signals:
                    sig_base = sig.replace("Sig_", "").replace("_sig", "")
                    if sig_base.lower() in port_name.lower() or port_name.lower().replace("port_", "") in sig.lower():
                        mapped_signals.append(sig)
                    elif "Engine" in port_name and "Engine" in sig:
                        mapped_signals.append(sig)

                # Target component connection
                target_comp = "RTE / BSW Gateway"
                for dep in raw_deps:
                    if dep.get("source") == swc:
                        target_comp = dep.get("target")

                swc_node["ports"].append({
                    "port_name": port_name,
                    "type": p_type,
                    "mapped_interface": mapped_interface,
                    "mapped_signals": mapped_signals or ["Default Payload Signal"],
                    "target_component": target_comp,
                    "page_num": page_num
                })

            # Explicit SWC-to-SWC connected components
            for dep in raw_deps:
                if dep.get("source") == swc and dep.get("target") not in swc_node["connected_components"]:
                    swc_node["connected_components"].append(dep.get("target"))

            tree.append(swc_node)

        return tree
