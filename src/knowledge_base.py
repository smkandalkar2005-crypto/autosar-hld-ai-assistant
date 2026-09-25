import json
from pathlib import Path
from typing import Dict, Any, List

class ArchitectureKnowledgeBase:
    """
    Standardized AUTOSAR Architecture Knowledge Base.
    Acts as the single source of truth for extracted architecture entities, 
    relationships, version metadata, and citations, designed for downstream 
    automotive engineering consumption (HARA, TARA, Secure Code, UDS Diagnostics).
    """

    def __init__(
        self,
        doc_metadata: Dict[str, Any],
        entities: Dict[str, Any],
        relationship_tree: List[Dict[str, Any]],
        completeness_findings: List[Dict[str, Any]],
        comparison_results: Dict[str, Any] = None
    ):
        self.doc_metadata = doc_metadata or {}
        self.entities = entities or {}
        self.relationship_tree = relationship_tree or []
        self.completeness_findings = completeness_findings or []
        self.comparison_results = comparison_results or {}
        
        self.data = self._build_knowledge_base()

    def _build_knowledge_base(self) -> Dict[str, Any]:
        doc_name = self.doc_metadata.get("file_name", "AUTOSAR_HLD.pdf")
        doc_ver = self.doc_metadata.get("doc_version", "Version 1.0")
        total_pages = self.doc_metadata.get("total_pages", 1)

        project_info = {
            "name": doc_name.replace(".pdf", "").replace("_", " "),
            "description": "AUTOSAR High-Level Design Architecture Specification",
            "platform": "AUTOSAR Classic Platform",
            "version": doc_ver
        }

        document_info = {
            "file_name": doc_name,
            "version": doc_ver,
            "total_pages": total_pages,
            "status": "Parsed & Analyzed"
        }

        # 1. Software Components with Stable IDs (SWC-001, SWC-002, ...)
        components = []
        swc_id_map = {}
        raw_swcs = self.entities.get("software_components", [])
        for idx, swc_name in enumerate(raw_swcs, 1):
            stable_id = f"SWC-{idx:03d}"
            swc_id_map[swc_name] = stable_id
            
            tree_node = next((n for n in self.relationship_tree if n.get("swc_name") == swc_name), {})
            port_list = [p.get("port_name") for p in tree_node.get("ports", [])]
            
            components.append({
                "id": stable_id,
                "name": swc_name,
                "type": "Atomic Application Software Component",
                "ports": port_list,
                "source_citation": {
                    "doc_name": doc_name,
                    "doc_version": doc_ver,
                    "page": 1,
                    "section": "2. Application Components"
                }
            })

        # 2. Ports with Stable IDs (PORT-001, PORT-002, ...)
        ports = []
        port_id_map = {}
        port_counter = 1
        processed_port_names = set()

        # Harvest resolved ports from relationship_tree
        for node in self.relationship_tree:
            swc_name = node.get("swc_name", "Not specified in source document")
            swc_id = swc_id_map.get(swc_name, "SWC-UNMAPPED")

            for p in node.get("ports", []):
                p_name = p.get("port_name")
                if not p_name:
                    continue

                processed_port_names.add(p_name)
                stable_id = f"PORT-{port_counter:03d}"
                port_id_map[p_name] = stable_id
                port_counter += 1

                p_type = p.get("type", "Port Prototype")
                mapped_if = p.get("mapped_interface", "Not specified in source document")
                mapped_sigs = [s for s in p.get("mapped_signals", []) if s != "Not specified in source document"]
                target_comp = p.get("target_component", "Not specified in source document")
                p_page = p.get("page_num", 1)

                ports.append({
                    "id": stable_id,
                    "name": p_name,
                    "component": swc_name,
                    "component_id": swc_id,
                    "type": p_type,
                    "interface": mapped_if,
                    "signals": mapped_sigs,
                    "target_component": target_comp,
                    "source_citation": {
                        "doc_name": doc_name,
                        "doc_version": doc_ver,
                        "page": p_page,
                        "section": "3. Interface & Port Configuration"
                    }
                })

        # Harvest any remaining unmapped ports from self.entities["ports"]
        raw_ports = self.entities.get("ports", [])
        for p_obj in raw_ports:
            p_name = p_obj.get("port_name") if isinstance(p_obj, dict) else str(p_obj)
            if p_name and p_name not in processed_port_names:
                processed_port_names.add(p_name)
                stable_id = f"PORT-{port_counter:03d}"
                port_id_map[p_name] = stable_id
                port_counter += 1

                p_type = p_obj.get("type", "Port Prototype") if isinstance(p_obj, dict) else "Port Prototype"
                p_comp = p_obj.get("component", "Not specified in source document") if isinstance(p_obj, dict) else "Not specified in source document"
                p_if = p_obj.get("interface", "Not specified in source document") if isinstance(p_obj, dict) else "Not specified in source document"
                p_sigs = p_obj.get("signals", []) if isinstance(p_obj, dict) else []
                p_page = p_obj.get("page_num", 1) if isinstance(p_obj, dict) else 1
                target_comp = p_obj.get("target_component", "Not specified in source document") if isinstance(p_obj, dict) else "Not specified in source document"

                ports.append({
                    "id": stable_id,
                    "name": p_name,
                    "component": p_comp,
                    "component_id": swc_id_map.get(p_comp, "SWC-UNMAPPED"),
                    "type": p_type,
                    "interface": p_if,
                    "signals": p_sigs,
                    "target_component": target_comp,
                    "source_citation": {
                        "doc_name": doc_name,
                        "doc_version": doc_ver,
                        "page": p_page,
                        "section": "3. Interface & Port Configuration"
                    }
                })

        # 3. Interfaces with Stable IDs (IF-001, IF-002, ...)
        interfaces = []
        raw_ifs = self.entities.get("interfaces", [])
        for idx, if_name in enumerate(raw_ifs, 1):
            stable_id = f"IF-{idx:03d}"
            
            mapped_sigs = []
            for p in ports:
                if p["interface"] == if_name:
                    for s in p["signals"]:
                        if s != "Not specified in source document" and s not in mapped_sigs:
                            mapped_sigs.append(s)

            if not mapped_sigs:
                for sig_name in self.entities.get("signals", []):
                    if "door" in if_name.lower() and "door" in sig_name.lower():
                        if sig_name not in mapped_sigs:
                            mapped_sigs.append(sig_name)
                    elif "legacy" in if_name.lower() and "legacy" in sig_name.lower():
                        if sig_name not in mapped_sigs:
                            mapped_sigs.append(sig_name)

            interfaces.append({
                "id": stable_id,
                "name": if_name,
                "signals": mapped_sigs,
                "source_citation": {
                    "doc_name": doc_name,
                    "doc_version": doc_ver,
                    "page": 1,
                    "section": "3. Interface & Port Configuration"
                }
            })

        # 4. Signals with Stable IDs (SIG-001, SIG-002, ...)
        signals = []
        raw_sigs = self.entities.get("signals", [])
        for idx, sig_name in enumerate(raw_sigs, 1):
            stable_id = f"SIG-{idx:03d}"
            
            parent_if = "Not specified in source document"
            for if_obj in interfaces:
                if sig_name in if_obj["signals"]:
                    parent_if = if_obj["name"]
                    break

            signals.append({
                "id": stable_id,
                "name": sig_name,
                "interface": parent_if,
                "source_citation": {
                    "doc_name": doc_name,
                    "doc_version": doc_ver,
                    "page": 1,
                    "section": "3. Interface & Port Configuration"
                }
            })

        # 5. Basic Software (BSW) Stack Modules with Stable IDs (BSW-001, BSW-002, ...)
        bsw_modules = []
        raw_bsw = self.entities.get("bsw_modules", [])
        for idx, bsw_name in enumerate(raw_bsw, 1):
            stable_id = f"BSW-{idx:03d}"
            bsw_modules.append({
                "id": stable_id,
                "name": bsw_name,
                "category": "Basic Software Stack Module",
                "source_citation": {
                    "doc_name": doc_name,
                    "doc_version": doc_ver,
                    "page": 1,
                    "section": "4. Basic Software Stack & Diagnostics"
                }
            })

        # 6. Dependencies & Functional Flows
        dependencies = []
        functional_flows = []
        for node in self.relationship_tree:
            swc = node.get("swc_name")
            for p in node.get("ports", []):
                p_name = p.get("port_name")
                iface = p.get("mapped_interface")
                sigs = p.get("mapped_signals", [])
                target = p.get("target_component")

                if iface and iface != "Not specified in source document":
                    dependencies.append({
                        "source_component": swc,
                        "port": p_name,
                        "interface": iface,
                        "signals": [s for s in sigs if s != "Not specified in source document"],
                        "target_destination": target,
                        "type": "Port Interface Binding"
                    })

                if target and target != "Not specified in source document":
                    sig_label = ", ".join([s for s in sigs if s != "Not specified in source document"])
                    flow_str = f"{swc} [{p_name}] -> {iface} ({sig_label or 'Signal'}) -> {target}"
                    if flow_str not in functional_flows:
                        functional_flows.append(flow_str)

        # 7. Citations Summary
        citations_summary = [
            {
                "section": "1. System Purpose & Functional Scope",
                "doc_name": doc_name,
                "doc_version": doc_ver,
                "page": 1,
                "topics": ["System Overview", "Functional Requirements"]
            },
            {
                "section": "2. Application Components",
                "doc_name": doc_name,
                "doc_version": doc_ver,
                "page": 1,
                "topics": ["SWC Declarations", "Application Layer"]
            },
            {
                "section": "3. Interface & Port Configuration",
                "doc_name": doc_name,
                "doc_version": doc_ver,
                "page": 1,
                "topics": ["Port Prototypes", "Sender-Receiver / Client-Server Interfaces", "Data Elements"]
            },
            {
                "section": "4. Basic Software Stack & Diagnostics",
                "doc_name": doc_name,
                "doc_version": doc_ver,
                "page": 1,
                "topics": ["BSW Service Drivers", "EcuM", "BswM", "CanIf", "Com"]
            }
        ]

        return {
            "project": project_info,
            "document": document_info,
            "kpi_counts": {
                "components": len(components),
                "bsw_modules": len(bsw_modules),
                "interfaces": len(interfaces),
                "signals": len(signals),
                "ports": len(ports),
                "findings": len(self.completeness_findings)
            },
            "components": components,
            "ports": ports,
            "interfaces": interfaces,
            "signals": signals,
            "bsw_modules": bsw_modules,
            "dependencies": dependencies,
            "functional_flows": functional_flows,
            "relationships": self.relationship_tree,
            "revision_history": self.comparison_results or {},
            "findings": self.completeness_findings,
            "citations": citations_summary
        }

    def export_json(self, output_path: Path) -> Path:
        """Exports the Architecture Knowledge Base to JSON file for downstream compatibility."""
        output_path = Path(output_path)
        output_path.parent.mkdir(exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2)
        return output_path
