import re
from typing import List, Dict, Any

class RelationshipBuilder:
    """
    Builds accurate, non-duplicated 5-tier architectural relationship trees:
    SWC / Component -> Port Prototype -> Interface -> Signal -> Target Component / Dependency
    """

    def build_tree(self, pages: List[Dict[str, Any]], entities: Dict[str, Any]) -> List[Dict[str, Any]]:
        swcs = entities.get("software_components", [])
        all_ports = entities.get("ports", [])
        interfaces = entities.get("interfaces", [])
        signals = entities.get("signals", [])
        raw_deps = entities.get("dependencies", [])

        # Build Provider -> Component map (e.g., PPort_EngineSpeed -> EngineSpeedControl_SWC)
        provider_map = {}
        requester_map = {}

        for p in all_ports:
            p_name = p["port_name"]
            p_type = p["type"]
            owner = p.get("owner_swc")
            base_topic = p_name.replace("PPort_", "").replace("RPort_", "").replace("P_", "").replace("R_", "")
            
            if "PPort" in p_type or "Provider" in p_type:
                provider_map[base_topic.lower()] = owner
                provider_map[p_name.lower()] = owner
            else:
                requester_map[base_topic.lower()] = owner
                requester_map[p_name.lower()] = owner

        tree = []

        for swc in swcs:
            swc_node = {
                "swc_name": swc,
                "ports": [],
                "connected_components": [],
                "functional_flows": []
            }

            # Filter ONLY ports that belong to this specific SWC
            swc_ports = [p for p in all_ports if p.get("owner_swc") == swc]

            for p in swc_ports:
                port_name = p["port_name"]
                p_type = p["type"]
                page_num = p["page_num"]

                port_topic = port_name.replace("PPort_", "").replace("RPort_", "").replace("P_", "").replace("R_", "").lower()

                # 1. Map Interface
                mapped_interface = "Not specified in source document"
                for if_name in interfaces:
                    if_topic = if_name.replace("If_", "").replace("_If", "").replace("Interface", "").lower()
                    if if_topic in port_topic or port_topic in if_topic:
                        mapped_interface = if_name
                        break
                    elif ("engine" in port_topic and "engine" in if_name.lower()) or \
                         ("diag" in port_topic and "diag" in if_name.lower()) or \
                         ("door" in port_topic and "door" in if_name.lower()):
                        mapped_interface = if_name
                        break

                # 2. Map Signals
                mapped_signals = []
                for sig in signals:
                    sig_topic = sig.replace("Sig_", "").replace("_sig", "").replace("_rpm", "").replace("_pct", "").replace("_bar", "").replace("_status", "").lower()
                    if sig_topic in port_topic or port_topic in sig_topic:
                        mapped_signals.append(sig)
                    elif ("engine" in port_topic and "engine" in sig.lower()) or \
                         ("throttle" in port_topic and "throttle" in sig.lower()) or \
                         ("boost" in port_topic and "boost" in sig.lower()) or \
                         ("door" in port_topic and "door" in sig.lower()):
                        mapped_signals.append(sig)

                if not mapped_signals:
                    mapped_signals = ["Not specified in source document"]

                # 3. Determine Target Component / Connected Entity
                target_comp = "Not specified in source document"

                if "RPort" in p_type or "Requester" in p_type:
                    # Look up which SWC provides this port/topic
                    if port_topic in provider_map and provider_map[port_topic] != swc:
                        target_comp = provider_map[port_topic]
                else:
                    # Look up which SWC requests this port/topic
                    if port_topic in requester_map and requester_map[port_topic] != swc:
                        target_comp = requester_map[port_topic]

                # Check explicit raw dependencies fallback
                if target_comp == "Not specified in source document":
                    for dep in raw_deps:
                        if dep.get("source") == swc:
                            target_comp = dep.get("target")
                            break

                # Track connected components list
                if target_comp != "Not specified in source document" and target_comp not in swc_node["connected_components"]:
                    swc_node["connected_components"].append(target_comp)

                swc_node["ports"].append({
                    "port_name": port_name,
                    "type": p_type,
                    "mapped_interface": mapped_interface,
                    "mapped_signals": mapped_signals,
                    "target_component": target_comp,
                    "page_num": page_num
                })

            tree.append(swc_node)

        return tree
