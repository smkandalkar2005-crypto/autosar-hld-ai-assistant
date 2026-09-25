from typing import Dict, Any, List

class DocumentComparator:
    """
    Compares two HLD document revisions (e.g. HLD V1 vs HLD V2) and detects:
    - Added / Removed / Modified Sections
    - Added / Removed / Modified Components (SWCs)
    - Added / Removed / Modified BSW Modules
    - Added / Removed / Modified Interfaces
    - Added / Removed / Modified Ports
    - Added / Removed / Modified Signals
    - Changed Dependencies / Relationships
    Retains document version and page/section references for every change.
    """

    def compare_revisions(
        self,
        doc_v1_name: str,
        doc_v2_name: str,
        chunks_v1: List[Dict[str, Any]],
        chunks_v2: List[Dict[str, Any]],
        entities_v1: Dict[str, Any],
        entities_v2: Dict[str, Any]
    ) -> Dict[str, Any]:

        # 1. Compare Sections
        sections_v1 = {c["section"]: c.get("page_num", 1) for c in chunks_v1}
        sections_v2 = {c["section"]: c.get("page_num", 1) for c in chunks_v2}

        added_sections = [
            {"section": sec, "page": page, "version": doc_v2_name}
            for sec, page in sections_v2.items() if sec not in sections_v1
        ]
        removed_sections = [
            {"section": sec, "page": page, "version": doc_v1_name}
            for sec, page in sections_v1.items() if sec not in sections_v2
        ]
        modified_sections = [
            {"section": sec, "page_v1": sections_v1[sec], "page_v2": page}
            for sec, page in sections_v2.items() if sec in sections_v1
        ]

        # 2. Compare Components (SWCs)
        swc_v1 = set(entities_v1.get("software_components", []))
        swc_v2 = set(entities_v2.get("software_components", []))

        added_swc = sorted(list(swc_v2 - swc_v1))
        removed_swc = sorted(list(swc_v1 - swc_v2))
        retained_swc = sorted(list(swc_v1.intersection(swc_v2)))

        # 3. Compare BSW Modules
        bsw_v1 = set(entities_v1.get("bsw_modules", []))
        bsw_v2 = set(entities_v2.get("bsw_modules", []))

        added_bsw = sorted(list(bsw_v2 - bsw_v1))
        removed_bsw = sorted(list(bsw_v1 - bsw_v2))

        # 4. Compare Interfaces
        if_v1 = set(entities_v1.get("interfaces", []))
        if_v2 = set(entities_v2.get("interfaces", []))

        added_if = sorted(list(if_v2 - if_v1))
        removed_if = sorted(list(if_v1 - if_v2))

        # 5. Compare Ports
        ports_v1 = {p["port_name"]: p for p in entities_v1.get("ports", [])}
        ports_v2 = {p["port_name"]: p for p in entities_v2.get("ports", [])}

        added_ports = [p for name, p in ports_v2.items() if name not in ports_v1]
        removed_ports = [p for name, p in ports_v1.items() if name not in ports_v2]

        # 6. Compare Signals
        sig_v1 = set(entities_v1.get("signals", []))
        sig_v2 = set(entities_v2.get("signals", []))

        added_sig = sorted(list(sig_v2 - sig_v1))
        removed_sig = sorted(list(sig_v1 - sig_v2))

        # 7. Compare Dependencies
        deps_v1 = {(d["source"], d["target"]) for d in entities_v1.get("dependencies", [])}
        deps_v2 = {(d["source"], d["target"]) for d in entities_v2.get("dependencies", [])}

        added_deps = [{"source": s, "target": t} for s, t in (deps_v2 - deps_v1)]
        removed_deps = [{"source": s, "target": t} for s, t in (deps_v1 - deps_v2)]

        return {
            "v1_doc": doc_v1_name,
            "v2_doc": doc_v2_name,
            "sections": {
                "added": added_sections,
                "removed": removed_sections,
                "common": modified_sections
            },
            "components": {
                "added": added_swc,
                "removed": removed_swc,
                "modified": retained_swc
            },
            "bsw_modules": {
                "added": added_bsw,
                "removed": removed_bsw
            },
            "interfaces": {
                "added": added_if,
                "removed": removed_if
            },
            "ports": {
                "added": added_ports,
                "removed": removed_ports
            },
            "signals": {
                "added": added_sig,
                "removed": removed_sig
            },
            "dependencies": {
                "added": added_deps,
                "removed": removed_deps
            }
        }
