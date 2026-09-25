import os
import sys
from pathlib import Path
import streamlit as st
import pandas as pd

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.config import SAMPLE_DOCS_DIR, OUTPUT_DIR
from src.pdf_parser import PDFParser
from src.extractor import ArchitectureExtractor
from src.vector_store import VectorStore
from src.llm_engine import LLMEngine
from src.inconsistency_checker import InconsistencyChecker
from src.completeness_analyzer import CompletenessAnalyzer
from src.relationship_builder import RelationshipBuilder
from src.comparator import DocumentComparator
from src.report_generator import ReportGenerator

# Page Configuration
st.set_page_config(
    page_title="AUTOSAR HLD Document Analysis Assistant",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling (Dark Mode Automotive Theme)
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #38BDF8;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #94A3B8;
        margin-bottom: 1.5rem;
    }
    .stMetric {
        background-color: #1E293B;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #334155;
    }
    .finding-card {
        background-color: #1E293B;
        border-left: 5px solid #38BDF8;
        padding: 14px;
        margin-bottom: 12px;
        border-radius: 6px;
    }
    .severity-CRITICAL { border-left-color: #EF4444 !important; }
    .severity-HIGH { border-left-color: #F97316 !important; }
    .severity-MEDIUM { border-left-color: #EAB308 !important; }
    .severity-LOW { border-left-color: #3B82F6 !important; }
    .comp-box {
        background-color: #0F172A;
        border: 1px solid #334155;
        padding: 12px;
        border-radius: 6px;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Session State Initialization
if "current_doc" not in st.session_state:
    st.session_state.current_doc = None
if "doc_v2" not in st.session_state:
    st.session_state.doc_v2 = None
if "parsed_chunks" not in st.session_state:
    st.session_state.parsed_chunks = []
if "extracted_entities" not in st.session_state:
    st.session_state.extracted_entities = {}
if "entities_v2" not in st.session_state:
    st.session_state.entities_v2 = {}
if "vector_store" not in st.session_state:
    st.session_state.vector_store = VectorStore()
if "inconsistencies" not in st.session_state:
    st.session_state.inconsistencies = []
if "completeness_findings" not in st.session_state:
    st.session_state.completeness_findings = []
if "relationship_tree" not in st.session_state:
    st.session_state.relationship_tree = []
if "comparison_results" not in st.session_state:
    st.session_state.comparison_results = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Sidebar Configuration
with st.sidebar:
    st.title("🚗 AUTOSAR AI Assistant")
    st.caption("Tata TechPulse Case Study 1 Platform")
    st.markdown("---")

    st.subheader("⚙️ AI Model Setup")
    provider = st.selectbox("Select LLM Provider", ["Auto / Gemini API", "Offline Grounded Engine", "Ollama (Local)"], index=0)
    api_key = st.text_input("Gemini API Key (Optional)", type="password", help="Leave empty for offline grounded mode")
    
    st.markdown("---")
    st.subheader("📄 Document Selection & Revision Setup")

    sample_files = list(SAMPLE_DOCS_DIR.glob("*.pdf"))
    sample_names = [f.name for f in sample_files]
    
    selected_sample = st.selectbox("Primary HLD (V1)", ["-- Select HLD V1 --"] + sample_names, index=1 if len(sample_names) > 0 else 0)
    selected_sample_v2 = st.selectbox("Comparison HLD (V2) [Optional]", ["-- Select HLD V2 --"] + sample_names, index=2 if len(sample_names) > 1 else 0)

    uploaded_file = st.file_uploader("Upload Custom HLD PDF", type=["pdf"])

    process_btn = st.button("🚀 Analyze & Index Architecture", use_container_width=True, type="primary")

# Main Header
st.markdown("<div class='main-header'>AUTOSAR HLD Document Analysis Assistant</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-header'>Automated architectural extraction, 5-tier dependency mapping, rule-based completeness checks, HLD revision comparison, and grounded Q&A.</div>", unsafe_allow_html=True)

# Document Processing Logic
target_pdf_path = None
target_v2_path = None

if uploaded_file is not None:
    temp_path = SAMPLE_DOCS_DIR / uploaded_file.name
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    target_pdf_path = temp_path
elif selected_sample != "-- Select HLD V1 --":
    target_pdf_path = SAMPLE_DOCS_DIR / selected_sample

if selected_sample_v2 != "-- Select HLD V2 --":
    target_v2_path = SAMPLE_DOCS_DIR / selected_sample_v2

if process_btn and target_pdf_path:
    with st.spinner("Analyzing HLD architecture, building 5-tier relationship tree, running completeness checks..."):
        # 1. Parse & Chunk Primary HLD V1
        parser = PDFParser(str(target_pdf_path), doc_version="V1.0")
        pages = parser.extract_pages()
        chunks = parser.chunk_document()

        # 2. Extract Entities
        extractor = ArchitectureExtractor()
        entities = extractor.extract_entities(pages)

        # 3. Build 5-Tier Relationship Tree (SWC -> Port -> Interface -> Signal -> Target)
        builder = RelationshipBuilder()
        rel_tree = builder.build_tree(pages, entities)

        # 4. Completeness Analysis
        comp_analyzer = CompletenessAnalyzer()
        comp_findings = comp_analyzer.analyze_completeness(pages, entities, rel_tree)

        # 5. Inconsistency Analysis
        full_text = " ".join([p["text"] for p in pages])
        checker = InconsistencyChecker()
        inconsistencies = checker.analyze(entities, full_text)

        # 6. Index Vector Store
        vs = VectorStore()
        vs.clear()
        vs.add_chunks(chunks)

        # 7. Revision Comparison if V2 selected
        comp_results = None
        entities_v2 = {}
        if target_v2_path:
            parser_v2 = PDFParser(str(target_v2_path), doc_version="V2.0")
            pages_v2 = parser_v2.extract_pages()
            chunks_v2 = parser_v2.chunk_document()
            entities_v2 = extractor.extract_entities(pages_v2)
            vs.add_chunks(chunks_v2)

            comparator = DocumentComparator()
            comp_results = comparator.compare_revisions(
                target_pdf_path.name,
                target_v2_path.name,
                chunks,
                chunks_v2,
                entities,
                entities_v2
            )

        # Store in session state
        st.session_state.current_doc = target_pdf_path.name
        st.session_state.doc_v2 = target_v2_path.name if target_v2_path else None
        st.session_state.parsed_chunks = chunks
        st.session_state.pages = pages
        st.session_state.extracted_entities = entities
        st.session_state.entities_v2 = entities_v2
        st.session_state.relationship_tree = rel_tree
        st.session_state.completeness_findings = comp_findings
        st.session_state.inconsistencies = inconsistencies
        st.session_state.vector_store = vs
        st.session_state.comparison_results = comp_results
        st.session_state.chat_history = []

        st.success(f"Analysis complete for '{target_pdf_path.name}'!")

# Render Dashboard Tabs
if st.session_state.current_doc:
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "📊 Overview & Summary",
        "🏗️ Architecture Inventory",
        "🔗 5-Tier Relationship Map",
        "🔍 Completeness Analysis",
        "🔄 HLD Revision Comparison",
        "💬 Version-Aware Q&A",
        "📥 Reports & Detail Export"
    ])

    entities = st.session_state.extracted_entities
    chunks = st.session_state.parsed_chunks
    rel_tree = st.session_state.relationship_tree
    comp_findings = st.session_state.completeness_findings

    # Tab 1: Overview
    with tab1:
        st.subheader("📄 Loaded HLD Document Metadata")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Primary HLD Document", st.session_state.current_doc)
        col2.metric("Comparison HLD V2", st.session_state.doc_v2 or "None Loaded")
        col3.metric("SWCs Identified", len(entities.get("software_components", [])))
        col4.metric("BSW Stack Modules", len(entities.get("bsw_modules", [])))

        st.markdown("### Document Section Breakdown")
        sections = list(set(c["section"] for c in chunks))
        for sec in sections:
            st.markdown(f"- **{sec}**")

    # Tab 2: Architecture Inventory
    with tab2:
        st.subheader("🏗️ Extracted Architecture Inventory")

        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("#### Application Software Components (SWCs)")
            st.dataframe(pd.DataFrame({"SWC Name": entities.get("software_components", [])}), use_container_width=True)

            st.markdown("#### Basic Software (BSW) Stack Modules")
            st.dataframe(pd.DataFrame({"BSW Module": entities.get("bsw_modules", [])}), use_container_width=True)

        with col_b:
            st.markdown("#### Component Interfaces")
            st.dataframe(pd.DataFrame({"Interface Name": entities.get("interfaces", [])}), use_container_width=True)

            st.markdown("#### Data Element Signals")
            st.dataframe(pd.DataFrame({"Signal Name": entities.get("signals", [])}), use_container_width=True)

        st.markdown("#### Port Prototype Catalog")
        ports_df = pd.DataFrame(entities.get("ports", []))
        if not ports_df.empty:
            st.dataframe(ports_df, use_container_width=True)

    # Tab 3: 5-Tier Relationship Map (SWC -> Port -> Interface -> Signal -> Target)
    with tab3:
        st.subheader("🔗 5-Tier Architectural Dependency & Relationship Map")
        st.write("Displays structured end-to-end trace: `SWC -> Port -> Interface -> Signal -> Target Component`")

        for swc_node in rel_tree:
            with st.expander(f"📦 Component: {swc_node['swc_name']}", expanded=True):
                st.markdown(f"**Connected Target Components:** {', '.join(swc_node['connected_components']) or 'Not specified in source document'}")
                st.markdown("**Port Prototype Hierarchy:**")
                for p in swc_node["ports"]:
                    st.markdown(f"""
                    <div class="comp-box">
                        <b>Port:</b> {p['port_name']} ({p['type']})<br/>
                        ↳ <b>Bound Interface:</b> {p['mapped_interface']}<br/>
                        ↳ <b>Payload Signals:</b> {', '.join(p['mapped_signals'])}<br/>
                        ↳ <b>Target Destination:</b> {p['target_component']}<br/>
                        <span style="color:#94A3B8; font-size:0.85rem;">Source Citation: Page {p['page_num']}</span>
                    </div>
                    """, unsafe_allow_html=True)

    # Tab 4: Completeness Analysis
    with tab4:
        st.subheader("🔍 Architectural Completeness Analysis")
        st.write("Deterministic rule-based checks identifying missing dependencies, interfaces, signals, and functional flows with exact document citations.")

        if not comp_findings:
            st.success("🎉 Architecture is complete. No missing dependencies or unmapped interfaces detected!")
        else:
            for finding in comp_findings:
                sev = finding.get("severity", "MEDIUM")
                st.markdown(f"""
                <div class="finding-card severity-{sev}">
                    <span class="severity-{sev}">[{sev}] {finding['category']}</span> — <b>{finding['item']}</b><br/>
                    <div style="margin-top:6px;"><b>Evidence Found:</b> {finding['evidence']}</div>
                    <div style="margin-top:4px; color:#EF4444;"><b>Detected Gap:</b> {finding['detected_gap']}</div>
                    <div style="margin-top:4px;"><b>Reason for Flagging:</b> {finding['reason_for_flagging']}</div>
                    <div style="margin-top:6px; color:#94A3B8; font-size:0.85rem;"><b>Source Reference:</b> {finding['citation']}</div>
                </div>
                """, unsafe_allow_html=True)

    # Tab 5: HLD Revision Comparison (V1 vs V2)
    with tab5:
        st.subheader("🔄 HLD Revision & Version Comparison")
        comp_res = st.session_state.comparison_results

        if not comp_res:
            st.info("💡 To compare document revisions, please select a secondary HLD (e.g. HLD V2) in the sidebar and click 'Analyze & Index Architecture'.")
        else:
            st.write(f"Comparing **{comp_res['v1_doc']} (V1)** vs **{comp_res['v2_doc']} (V2)**")

            col_c1, col_c2, col_c3 = st.columns(3)
            col_c1.metric("Added SWCs", len(comp_res["components"]["added"]))
            col_c2.metric("Added BSW Modules", len(comp_res["bsw_modules"]["added"]))
            col_c3.metric("Added Signals", len(comp_res["signals"]["added"]))

            col_diff1, col_diff2 = st.columns(2)
            with col_diff1:
                st.markdown("#### ➕ Added Components & Modules")
                st.write("**Added SWCs:**", ", ".join(comp_res["components"]["added"]) or "None")
                st.write("**Added BSW Stack Modules:**", ", ".join(comp_res["bsw_modules"]["added"]) or "None")
                st.write("**Added Interfaces:**", ", ".join(comp_res["interfaces"]["added"]) or "None")
                st.write("**Added Data Signals:**", ", ".join(comp_res["signals"]["added"]) or "None")

            with col_diff2:
                st.markdown("#### ➖ Removed / Modified Elements")
                st.write("**Removed SWCs:**", ", ".join(comp_res["components"]["removed"]) or "None")
                st.write("**Removed Interfaces:**", ", ".join(comp_res["interfaces"]["removed"]) or "None")
                st.write("**Modified Sections:**", str(len(comp_res["sections"]["common"])) + " Sections")

            st.markdown("#### Added Sections in V2 Revision")
            sec_df = pd.DataFrame(comp_res["sections"]["added"])
            if not sec_df.empty:
                st.dataframe(sec_df, use_container_width=True)

    # Tab 6: Version-Aware Q&A
    with tab6:
        st.subheader("💬 Version-Aware Citation-Grounded Q&A")

        st.write("**Quick Version Comparison & Architecture Questions:**")
        q_cols = st.columns(4)
        preset_q = None
        if q_cols[0].button("What changed in V2?"):
            preset_q = "What changed between HLD V1 and V2? List added components, BSW modules, and signals."
        if q_cols[1].button("Which SWCs modified?"):
            preset_q = "Which components were modified or added in Version 2.0?"
        if q_cols[2].button("What dependencies added?"):
            preset_q = "What BSW drivers or dependencies were added in Version 2.0?"
        if q_cols[3].button("Show evidence for changes"):
            preset_q = "Show the exact document version, page numbers, and section evidence for changes in V2."

        user_query = st.chat_input("Ask a question about the HLD architecture or version comparison...")
        query_to_run = preset_q or user_query

        if query_to_run:
            st.session_state.chat_history.append({"role": "user", "content": query_to_run})

            vs = st.session_state.vector_store
            context_chunks = vs.search(query_to_run, top_k=4)

            llm = LLMEngine(api_key=api_key, provider="gemini" if api_key else "offline")
            response = llm.generate_rag_response(query_to_run, context_chunks)

            st.session_state.chat_history.append({
                "role": "assistant",
                "content": response["answer"],
                "citations": response["citations"],
                "confidence": response["confidence"]
            })

        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])
                if msg.get("citations"):
                    st.caption(f"**Confidence Level:** {msg.get('confidence')}")
                    with st.expander("📚 Version & Page Citations"):
                        for cit in msg["citations"]:
                            st.markdown(f"- **Version: {cit['version']}** | **Page {cit['page']}** (Section: *{cit['section']}*)\n  `{cit['snippet']}`")

    # Tab 7: Reports & Component Detail Export
    with tab7:
        st.subheader("📥 Executive Export & Component Detail Reports")

        reporter = ReportGenerator(OUTPUT_DIR)

        # Component Detail Report Section (Requirement 4)
        st.markdown("### 🧩 Component & Interface Detail Report Generator")
        all_swcs = entities.get("software_components", [])
        if all_swcs:
            selected_swc = st.selectbox("Select Component (SWC)", all_swcs)
            swc_node = next((node for node in rel_tree if node["swc_name"] == selected_swc), {})
            
            if st.button("Generate SWC Detail Card"):
                detail_card = reporter.export_component_detail_report(selected_swc, swc_node, comp_findings)
                st.json(detail_card)

        st.markdown("---")
        col_ex1, col_ex2 = st.columns(2)

        with col_ex1:
            st.markdown("#### ⚙️ Structured Architecture JSON Specification")
            if st.button("Generate Structured JSON Spec", type="primary"):
                doc_meta = {
                    "doc_name": st.session_state.current_doc,
                    "version": "1.0",
                    "comparison_doc": st.session_state.doc_v2
                }
                json_path = reporter.export_structured_json(
                    doc_meta,
                    entities,
                    rel_tree,
                    comp_findings,
                    st.session_state.comparison_results
                )
                with open(json_path, "rb") as f:
                    st.download_button(
                        label="Download Structured JSON Spec",
                        data=f,
                        file_name=json_path.name,
                        mime="application/json"
                    )

        with col_ex2:
            st.markdown("#### 📄 Executive PDF Report")
            if st.button("Generate PDF Report"):
                pdf_path = reporter.export_pdf(
                    st.session_state.current_doc,
                    entities,
                    comp_findings
                )
                with open(pdf_path, "rb") as f:
                    st.download_button(
                        label="Download Executive PDF",
                        data=f,
                        file_name=pdf_path.name,
                        mime="application/pdf"
                    )

else:
    st.info("👈 Please select or upload HLD PDF documents in the sidebar and click 'Analyze & Index Architecture' to launch!")
