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
    .citation-box {
        background-color: #0F172A;
        border-left: 4px solid #38BDF8;
        padding: 10px 15px;
        margin-top: 10px;
        border-radius: 4px;
        font-size: 0.9rem;
    }
    .severity-CRITICAL { color: #EF4444; font-weight: bold; }
    .severity-HIGH { color: #F97316; font-weight: bold; }
    .severity-MEDIUM { color: #EAB308; font-weight: bold; }
    .severity-LOW { color: #3B82F6; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# Session State Initialization
if "current_doc" not in st.session_state:
    st.session_state.current_doc = None
if "parsed_chunks" not in st.session_state:
    st.session_state.parsed_chunks = []
if "extracted_entities" not in st.session_state:
    st.session_state.extracted_entities = {}
if "vector_store" not in st.session_state:
    st.session_state.vector_store = None
if "inconsistencies" not in st.session_state:
    st.session_state.inconsistencies = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Sidebar Configuration
with st.sidebar:
    st.title("🚗 AUTOSAR AI Assistant")
    st.caption("Case Study 1: HLD Document Analysis")
    st.markdown("---")

    st.subheader("⚙️ AI Model Setup")
    provider = st.selectbox("Select LLM Provider", ["Auto / Gemini API", "Offline Grounded Engine", "Ollama (Local)"], index=0)
    api_key = st.text_input("Gemini API Key (Optional)", type="password", help="Leave empty for offline grounded mode")
    
    st.markdown("---")
    st.subheader("📄 Document Selection")

    # Sample PDF selector
    sample_files = list(SAMPLE_DOCS_DIR.glob("*.pdf"))
    sample_names = [f.name for f in sample_files]
    selected_sample = st.selectbox("Load Sample AUTOSAR HLD PDF", ["-- Select Sample PDF --"] + sample_names)
    
    uploaded_file = st.file_uploader("Or Upload Custom AUTOSAR HLD PDF", type=["pdf"])

    process_btn = st.button("🚀 Analyze & Index Document", use_container_state=True, type="primary")

# Main Header
st.markdown("<div class='main-header'>AUTOSAR HLD Document Analysis Assistant</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-header'>Automated architectural knowledge extraction, RAG question answering, and design inconsistency validation for AUTOSAR High-Level Design documents.</div>", unsafe_allow_html=True)

# Document Processing Logic
target_pdf_path = None
if uploaded_file is not None:
    temp_path = SAMPLE_DOCS_DIR / uploaded_file.name
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    target_pdf_path = temp_path
elif selected_sample != "-- Select Sample PDF --":
    target_pdf_path = SAMPLE_DOCS_DIR / selected_sample

if process_btn and target_pdf_path:
    with st.spinner("Processing PDF, extracting AUTOSAR entities, and indexing vector database..."):
        # 1. Parse PDF & Chunking
        parser = PDFParser(str(target_pdf_path))
        pages = parser.extract_pages()
        chunks = parser.chunk_document()

        # 2. Extract Entities & Dependencies
        extractor = ArchitectureExtractor()
        entities = extractor.extract_entities(pages)

        # 3. Vector Database Indexing
        vs = VectorStore()
        vs.add_chunks(chunks)

        # 4. Inconsistency Analysis
        full_text = " ".join([p["text"] for p in pages])
        checker = InconsistencyChecker()
        inconsistencies = checker.analyze(entities, full_text)

        # Store in session
        st.session_state.current_doc = target_pdf_path.name
        st.session_state.parsed_chunks = chunks
        st.session_state.pages = pages
        st.session_state.extracted_entities = entities
        st.session_state.vector_store = vs
        st.session_state.inconsistencies = inconsistencies
        st.session_state.chat_history = []

        st.success(f"Successfully processed and indexed '{target_pdf_path.name}'!")

# Render Main Dashboard Tabs
if st.session_state.current_doc:
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Document Summary",
        "🏗️ Architecture Inventory",
        "⚠️ Inconsistency & Gap Checker",
        "💬 Citation Grounded Q&A",
        "📥 Report Export"
    ])

    entities = st.session_state.extracted_entities
    chunks = st.session_state.parsed_chunks

    # Tab 1: Overview
    with tab1:
        st.subheader("📄 Loaded Document Information")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Document Name", st.session_state.current_doc)
        col2.metric("Total Chunks", len(chunks))
        col3.metric("SWCs Found", len(entities.get("software_components", [])))
        col4.metric("BSW Modules", len(entities.get("bsw_modules", [])))

        st.markdown("### Document Section Preview")
        sections = list(set(c["section"] for c in chunks))
        st.write("**Detected Sections:**", ", ".join(sections))

    # Tab 2: Extracted Architecture Inventory
    with tab2:
        st.subheader("🏗️ Extracted AUTOSAR Architecture Inventory")

        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("#### Application Software Components (SWCs)")
            swc_df = pd.DataFrame({"SWC Name": entities.get("software_components", [])})
            st.dataframe(swc_df, use_container_width=True)

            st.markdown("#### Basic Software (BSW) Modules")
            bsw_df = pd.DataFrame({"BSW Module": entities.get("bsw_modules", [])})
            st.dataframe(bsw_df, use_container_width=True)

        with col_b:
            st.markdown("#### Component Interfaces")
            if_df = pd.DataFrame({"Interface Name": entities.get("interfaces", [])})
            st.dataframe(if_df, use_container_width=True)

            st.markdown("#### Data Signals")
            sig_df = pd.DataFrame({"Signal Name": entities.get("signals", [])})
            st.dataframe(sig_df, use_container_width=True)

        st.markdown("#### Port Prototypes")
        ports_df = pd.DataFrame(entities.get("ports", []))
        if not ports_df.empty:
            st.dataframe(ports_df, use_container_width=True)

    # Tab 3: Inconsistency & Gap Checker
    with tab3:
        st.subheader("⚠️ Architectural Inconsistencies & Gap Analysis")
        inconsistencies = st.session_state.inconsistencies

        if not inconsistencies:
            st.success("🎉 No architectural inconsistencies or missing dependencies detected!")
        else:
            for inc in inconsistencies:
                sev = inc.get("severity", "MEDIUM")
                st.markdown(f"""
                <div style="background-color:#1E293B; border-left: 5px solid {'#EF4444' if sev=='CRITICAL' else '#F97316' if sev=='HIGH' else '#EAB308'}; padding: 12px; margin-bottom: 10px; border-radius: 4px;">
                    <span class="severity-{sev}">[{sev}] {inc['type']}</span> - <b>{inc['item']}</b><br/>
                    <div style="margin-top: 5px; font-size: 0.95rem;">{inc['description']}</div>
                    <div style="margin-top: 5px; color: #94A3B8; font-size: 0.85rem;"><b>Potential Impact:</b> {inc['impact']}</div>
                </div>
                """, unsafe_allow_html=True)

    # Tab 4: Q&A Assistant with Citations
    with tab4:
        st.subheader("💬 Citation-Grounded Q&A Assistant")

        # Preset Question Chips
        st.write("**Quick Architectural Questions:**")
        q_cols = st.columns(4)
        preset_q = None
        if q_cols[0].button("What SWCs are defined?"):
            preset_q = "List all Software Components (SWCs) defined in the document with their responsibilities."
        if q_cols[1].button("What BSW modules exist?"):
            preset_q = "Which Basic Software (BSW) modules are present and what are their functions?"
        if q_cols[2].button("Check BSW dependencies"):
            preset_q = "Are there any missing BSW modules or drivers like Can, CanIf, Dem, or EcuM?"
        if q_cols[3].button("List ports & signals"):
            preset_q = "List all PPort, RPort prototypes and signals mentioned."

        # Chat interface
        user_query = st.chat_input("Ask a question about the AUTOSAR HLD architecture...")
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
                    with st.expander("📚 Source Citations & References"):
                        for cit in msg["citations"]:
                            st.markdown(f"- **Page {cit['page']}** (Section: *{cit['section']}*)\n  `{cit['snippet']}`")

    # Tab 5: Report Export
    with tab5:
        st.subheader("📥 Export Architecture Findings")
        st.write("Generate and download structured architecture reports for design reviews, safety audits, and GitHub repository submission.")

        col_ex1, col_ex2 = st.columns(2)
        reporter = ReportGenerator(OUTPUT_DIR)

        with col_ex1:
            st.markdown("#### 📄 Executive PDF Report")
            if st.button("Generate PDF Report", type="primary"):
                pdf_path = reporter.export_pdf(
                    st.session_state.current_doc,
                    st.session_state.extracted_entities,
                    st.session_state.inconsistencies
                )
                with open(pdf_path, "rb") as f:
                    st.download_button(
                        label="Download PDF Report",
                        data=f,
                        file_name=pdf_path.name,
                        mime="application/pdf"
                    )

        with col_ex2:
            st.markdown("#### ⚙️ Structured JSON Specification")
            if st.button("Generate JSON Specification"):
                json_data = {
                    "document": st.session_state.current_doc,
                    "entities": st.session_state.extracted_entities,
                    "inconsistencies": st.session_state.inconsistencies
                }
                json_path = reporter.export_json(json_data)
                with open(json_path, "rb") as f:
                    st.download_button(
                        label="Download JSON Spec",
                        data=f,
                        file_name=json_path.name,
                        mime="application/json"
                    )

else:
    st.info("👈 Please select a sample PDF or upload an AUTOSAR HLD document from the sidebar to begin analysis!")
