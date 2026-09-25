import re
from typing import List, Dict, Any
from src.config import AUTOSAR_KEYWORDS

class ArchitectureExtractor:
    """Extracts AUTOSAR software components, interfaces, ports, signals, and BSW modules from document text."""

    def __init__(self):
        self.swc_pattern = re.compile(r'\b([A-Z][a-zA-Z0-9_]*(?:_SWC|_Comp|_Component|_App))\b')
        self.bsw_modules = AUTOSAR_KEYWORDS["BSW_MODULES"]
        self.interface_pattern = re.compile(r'\b(If_[A-Za-z0-9_]+|[A-Za-z0-9_]+_If|[A-Za-z0-9_]+Interface)\b')
        self.port_pattern = re.compile(r'\b([PR]Port_[A-Za-z0-9_]+|P_[A-Za-z0-9_]+|R_[A-Za-z0-9_]+)\b')
        self.signal_pattern = re.compile(r'\b(Sig_[A-Za-z0-9_]+|[A-Za-z0-9_]+_sig|[A-Za-z0-9_]+_rpm|[A-Za-z0-9_]+_degC|[A-Za-z0-9_]+_pct|[A-Za-z0-9_]+_status)\b', re.IGNORECASE)

    def extract_entities(self, pages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Scans pages and extracts structured architectural inventories."""
        components = set()
        detected_bsw = set()
        interfaces = set()
        ports = []
        signals = set()
        dependencies = []

        for page in pages:
            text = page["text"]
            page_num = page["page_num"]

            # Extract SWCs
            found_swcs = self.swc_pattern.findall(text)
            for swc in found_swcs:
                components.add(swc)

            # Extract BSW Modules
            for bsw in self.bsw_modules:
                if re.search(r'\b' + bsw + r'\b', text):
                    detected_bsw.add(bsw)

            # Extract Interfaces
            found_if = self.interface_pattern.findall(text)
            for if_name in found_if:
                interfaces.add(if_name)

            # Extract Ports
            found_ports = self.port_pattern.findall(text)
            for p in found_ports:
                p_type = "PPort (Provider)" if p.startswith("P") else "RPort (Requester)"
                ports.append({
                    "port_name": p,
                    "type": p_type,
                    "page_num": page_num
                })

            # Extract Signals
            found_sig = self.signal_pattern.findall(text)
            for sig in found_sig:
                signals.add(sig)

            # Extract Dependency Relationships (e.g. SWC_A -> SWC_B or SWC -> BSW)
            dep_matches = re.findall(r'([A-Za-z0-9_]+(?:_SWC|_Comp))\s+(?:calls|sends data to|depends on|receives from|triggers)\s+([A-Za-z0-9_]+)', text, re.IGNORECASE)
            for src, tgt in dep_matches:
                dependencies.append({
                    "source": src,
                    "target": tgt,
                    "page_num": page_num
                })

        # Deduplicate ports
        unique_ports = {p["port_name"]: p for p in ports}.values()

        return {
            "software_components": sorted(list(components)),
            "bsw_modules": sorted(list(detected_bsw)),
            "interfaces": sorted(list(interfaces)),
            "ports": list(unique_ports),
            "signals": sorted(list(signals)),
            "dependencies": dependencies
        }
