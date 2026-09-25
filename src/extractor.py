import re
from typing import List, Dict, Any
from src.config import AUTOSAR_KEYWORDS

class ArchitectureExtractor:
    """
    Extracts AUTOSAR software components, BSW modules, interfaces, 
    owner-bound ports, signals, and dependencies from document pages.
    """

    def __init__(self):
        self.swc_pattern = re.compile(r'\b([A-Z][a-zA-Z0-9_]*(?:_SWC|_Comp|_Component|_App))\b')
        self.bsw_modules = AUTOSAR_KEYWORDS["BSW_MODULES"]
        self.interface_pattern = re.compile(r'\b(If_[A-Za-z0-9_]+|[A-Za-z0-9_]+_If|[A-Za-z0-9_]+Interface)\b')
        self.port_pattern = re.compile(r'\b([PR]Port_[A-Za-z0-9_]+|P_[A-Za-z0-9_]+|R_[A-Za-z0-9_]+)\b')
        self.signal_pattern = re.compile(r'\b(Sig_[A-Za-z0-9_]+|[A-Za-z0-9_]+_sig|[A-Za-z0-9_]+_rpm|[A-Za-z0-9_]+_degC|[A-Za-z0-9_]+_pct|[A-Za-z0-9_]+_status)\b', re.IGNORECASE)

    def extract_entities(self, pages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Scans pages and extracts structured architectural inventories with SWC-port ownership."""
        components = set()
        detected_bsw = set()
        interfaces = set()
        ports_dict = {}  # (owner_swc, port_name) -> port_data
        signals = set()
        dependencies = []

        # First pass: Collect all SWCs, BSW, Interfaces, Signals
        for page in pages:
            text = page["text"]
            for swc in self.swc_pattern.findall(text):
                components.add(swc)
            for bsw in self.bsw_modules:
                if re.search(r'\b' + bsw + r'\b', text):
                    detected_bsw.add(bsw)
            for if_name in self.interface_pattern.findall(text):
                interfaces.add(if_name)
            for sig in self.signal_pattern.findall(text):
                signals.add(sig)

        all_swcs = sorted(list(components))
        all_ifs = sorted(list(interfaces))
        all_sigs = sorted(list(signals))

        # Second pass: Extract Port-to-SWC Ownership and Bindings line-by-line
        for page in pages:
            lines = page["text"].split("\n")
            page_num = page["page_num"]
            current_swc = None

            for line in lines:
                line_str = line.strip()
                if not line_str:
                    continue

                # Check if line introduces an SWC
                line_swcs = self.swc_pattern.findall(line_str)
                if line_swcs:
                    current_swc = line_swcs[0]

                # Check for ports in this line
                line_ports = self.port_pattern.findall(line_str)
                if line_ports:
                    # Determine owner SWC for ports on this line
                    target_swc = line_swcs[0] if line_swcs else current_swc
                    
                    # If no SWC on line or in section, try matching port stem to known SWCs
                    if not target_swc and all_swcs:
                        for p in line_ports:
                            p_stem = p.replace("PPort_", "").replace("RPort_", "").replace("P_", "").replace("R_", "")
                            for s in all_swcs:
                                if p_stem.lower() in s.lower() or s.lower().replace("_swc", "") in p_stem.lower():
                                    target_swc = s
                                    break

                    if not target_swc and all_swcs:
                        target_swc = all_swcs[0]

                    for p_name in line_ports:
                        p_type = "PPort (Provider)" if p_name.startswith("P") else "RPort (Requester)"
                        key = (target_swc, p_name)
                        
                        if key not in ports_dict:
                            ports_dict[key] = {
                                "owner_swc": target_swc,
                                "port_name": p_name,
                                "type": p_type,
                                "page_num": page_num
                            }

                # Extract explicit dependencies (SWC_A -> SWC_B)
                dep_matches = re.findall(
                    r'([A-Za-z0-9_]+(?:_SWC|_Comp))\s+(?:calls|sends data to|depends on|receives from|triggers|connects to)\s+([A-Za-z0-9_]+)',
                    line_str, re.IGNORECASE
                )
                for src, tgt in dep_matches:
                    dependencies.append({
                        "source": src,
                        "target": tgt,
                        "page_num": page_num
                    })

        # Deduplicate ports array
        unique_ports = list(ports_dict.values())

        return {
            "software_components": all_swcs,
            "bsw_modules": sorted(list(detected_bsw)),
            "interfaces": all_ifs,
            "ports": unique_ports,
            "signals": all_sigs,
            "dependencies": dependencies
        }
