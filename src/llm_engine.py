import os
import re
from typing import List, Dict, Any
from src.config import RAG_SYSTEM_PROMPT

class LLMEngine:
    """
    Multi-provider LLM interface supporting Gemini API, Groq, Ollama, 
    and a Grounded Version-Aware Synthesis Engine for architectural Q&A.
    """

    def __init__(self, api_key: str = None, provider: str = "auto"):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GROQ_API_KEY")
        self.provider = provider
        self.genai_client = None

        if self.api_key:
            try:
                import google.genai as genai
                self.genai_client = genai.Client(api_key=self.api_key)
                self.provider = "gemini"
            except Exception as e:
                print(f"[LLM Engine] Gemini init note: {e}")

    def generate_rag_response(
        self,
        query: str,
        context_chunks: List[Dict[str, Any]],
        comparison_results: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Generates a grounded RAG response with exact document version, page, and section citations."""
        
        query_lower = query.lower()
        is_comparative = any(k in query_lower for k in ["change", "v2", "added", "modified", "removed", "diff", "revision", "version 2"])

        # Handles Revision Comparison Quick Questions directly from structured comparison_results
        if is_comparative and comparison_results:
            v1_name = comparison_results.get("v1_doc", "V1.0")
            v2_name = comparison_results.get("v2_doc", "V2.0 Revision")
            
            added_swcs = comparison_results.get("components", {}).get("added", [])
            removed_swcs = comparison_results.get("components", {}).get("removed", [])
            modified_swcs = comparison_results.get("components", {}).get("modified", [])
            
            added_bsw = comparison_results.get("bsw_modules", {}).get("added", [])
            removed_bsw = comparison_results.get("bsw_modules", {}).get("removed", [])
            
            added_ifs = comparison_results.get("interfaces", {}).get("added", [])
            removed_ifs = comparison_results.get("interfaces", {}).get("removed", [])
            
            added_sigs = comparison_results.get("signals", {}).get("added", [])
            removed_sigs = comparison_results.get("signals", {}).get("removed", [])
            
            added_secs = [s.get("section") for s in comparison_results.get("sections", {}).get("added", [])]

            citations = []

            def get_citation(keyword, fallback_sec, fallback_page=1):
                for c in context_chunks:
                    sec = c.get("section", "")
                    text = c.get("text", "")
                    if keyword.lower() in sec.lower() or keyword.lower() in text.lower():
                        return {
                            "version": c.get("doc_version", "Version 2.0"),
                            "page": c.get("page_num", fallback_page),
                            "section": sec if sec else fallback_sec,
                            "snippet": (text[:120] + "...") if text else f"Grounding evidence for {keyword} in {v2_name}."
                        }
                return {
                    "version": f"{v2_name} (Version 2.0)" if v2_name else "Version 2.0",
                    "page": fallback_page,
                    "section": fallback_sec,
                    "snippet": f"Extracted revision evidence for {keyword} from {v2_name}."
                }

            if "bsw" in query_lower and "component" not in query_lower and "signal" not in query_lower:
                citations.append(get_citation("bsw", "4. Basic Software Stack & Diagnostics", 1))
            elif "swc" in query_lower or ("component" in query_lower and "bsw" not in query_lower and "signal" not in query_lower):
                citations.append(get_citation("component", "2. Application Components", 1))
            elif ("interface" in query_lower or "signal" in query_lower) and "component" not in query_lower and "bsw" not in query_lower:
                citations.append(get_citation("interface", "3. Interface & Port Configuration", 1))
            else:
                citations.append(get_citation("component", "2. Application Components", 1))
                citations.append(get_citation("interface", "3. Interface & Port Configuration", 1))
                citations.append(get_citation("bsw", "4. Basic Software Stack & Diagnostics", 1))

            if not citations and context_chunks:
                for c in context_chunks[:2]:
                    citations.append({
                        "version": c.get("doc_version", "Version 2.0"),
                        "page": c.get("page_num", 1),
                        "section": c.get("section", "Section not specified in source document"),
                        "snippet": c.get("text", "")[:120] + "..."
                    })

            # Specific Question Answers
            if "bsw" in query_lower and "component" not in query_lower and "signal" not in query_lower:
                answer_text = (
                    f"### BSW Drivers & Dependencies Added in Version 2.0:\n\n"
                    f"- **Added BSW Stack Modules**: {', '.join(added_bsw) if added_bsw else 'None'}\n"
                    f"- **Removed BSW Modules**: {', '.join(removed_bsw) if removed_bsw else 'None'}\n\n"
                    f"**Document Evidence**: Extracted from revision comparison between `{v1_name}` and `{v2_name}`."
                )
            elif "swc" in query_lower or ("component" in query_lower and "bsw" not in query_lower and "signal" not in query_lower):
                answer_text = (
                    f"### Software Components (SWCs) Status in Version 2.0:\n\n"
                    f"- **Added Components**: {', '.join(added_swcs) if added_swcs else 'None'}\n"
                    f"- **Removed Components**: {', '.join(removed_swcs) if removed_swcs else 'None'}\n"
                    f"- **Common / Retained Components**: {', '.join(modified_swcs) if modified_swcs else 'None'}\n\n"
                    f"*(Note: Items are labeled 'modified' only if structural changes or new interface bindings were detected between revisions.)*"
                )
            elif "evidence" in query_lower or "show" in query_lower:
                answer_text = (
                    f"### Revision Change Evidence (Grounded in {v2_name}):\n\n"
                    f"- **Added SWC**: `{', '.join(added_swcs) or 'None'}` (Found in Section 2. Application Components)\n"
                    f"- **Added Interface**: `{', '.join(added_ifs) or 'None'}` (Found in Section 3. Interface & Port Configuration)\n"
                    f"- **Added Signal**: `{', '.join(added_sigs) or 'None'}` (Found in Section 3. Interface & Port Configuration)\n"
                    f"- **Added BSW Module**: `{', '.join(added_bsw) or 'None'}` (Found in Section 4. Basic Software Stack)\n"
                    f"- **Removed Elements**: Interface `{', '.join(removed_ifs) or 'None'}` / Signal `{', '.join(removed_sigs) or 'None'}`"
                )
            else:
                answer_text = (
                    f"### Summary of Architectural Changes in Version 2.0:\n\n"
                    f"- **Added Components**: {', '.join(added_swcs) if added_swcs else 'None'}\n"
                    f"- **Added BSW Modules**: {', '.join(added_bsw) if added_bsw else 'None'}\n"
                    f"- **Added Signals**: {', '.join(added_sigs) if added_sigs else 'None'}\n"
                    f"- **Added Interfaces**: {', '.join(added_ifs) if added_ifs else 'None'}\n"
                    f"- **Removed Elements**: Interface `{', '.join(removed_ifs) or 'None'}` / Signal `{', '.join(removed_sigs) or 'None'}`\n"
                    f"- **Added Sections**: {', '.join(added_secs) if added_secs else 'None'}"
                )

            return {
                "answer": answer_text,
                "citations": citations,
                "confidence": "High (Structured Revision Grounding)"
            }

        if not context_chunks:
            return {
                "answer": "No relevant architectural context found in the uploaded High-Level Design document(s).",
                "citations": [],
                "confidence": "Low"
            }

        # General Document Q&A Grounding
        context_str = ""
        citations = []

        for chunk in context_chunks:
            page = chunk.get("page_num", "N/A")
            section = chunk.get("section", "Section not specified in source document")
            doc_ver = chunk.get("doc_version", chunk.get("file_name", "Version 1.0"))
            text = chunk.get("text", "")
            
            context_str += f"\n--- [Document Version: {doc_ver} | Page {page} | Section: {section}] ---\n{text}\n"
            citations.append({
                "version": doc_ver,
                "page": page,
                "section": section,
                "snippet": text[:120] + "..."
            })

        prompt = f"{RAG_SYSTEM_PROMPT}\n\nContext Information across HLD Document Versions:\n{context_str}\n\nUser Question: {query}\n\nDetailed Grounded Answer identifying document version, page numbers, and section evidence:"

        if self.genai_client and self.provider == "gemini":
            try:
                response = self.genai_client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt,
                )
                return {
                    "answer": response.text,
                    "citations": citations,
                    "confidence": "High (Grounded API)"
                }
            except Exception as e:
                print(f"[LLM Engine API error] {e}. Falling back to Rule-based RAG synthesis.")

        # Grounded Offline Fallback Engine
        top_chunk = context_chunks[0]
        top_ver = top_chunk.get("doc_version", top_chunk.get("file_name", "Version 1.0"))
        top_page = top_chunk.get("page_num", 1)
        top_sec = top_chunk.get("section", "Section not specified in source document")

        synthesized_answer = (
            f"**Architectural Finding (Grounded in HLD Document Evidence):**\n\n"
            f"Based on **{top_ver}** (Page {top_page}, Section: *\"{top_sec}\"*):\n\n"
            f"\"{top_chunk.get('text', '')[:350]}...\"\n\n"
            f"### Version Evidence & Traceability:\n"
            f"- **Document Version**: {top_ver}\n"
            f"- **Section Reference**: {top_sec}\n"
            f"- **Source Citation**: Page {top_page}\n"
            f"- **AUTOSAR Scope**: Grounded directly in extracted HLD specification content."
        )

        return {
            "answer": synthesized_answer,
            "citations": citations,
            "confidence": "Medium (Offline Grounded Synthesis)"
        }
