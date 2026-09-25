# AUTOSAR HLD Document Analysis Assistant — Tata TechPulse Case Study 1

> **Automotive AI Workstation for AUTOSAR High-Level Design (HLD) Extraction, 5-Tier Dependency Mapping, Architectural Completeness Analysis, Revision Comparison, and Standardized Knowledge Base Export.**

---

## 📋 Table of Contents

- [Project Title & Overview](#project-title--overview)
- [Problem Statement](#problem-statement)
- [Tata TechPulse Case Study 1 Scope](#tata-techpulse-case-study-1-scope)
- [Key Features](#key-features)
- [System Architecture](#system-architecture)
- [Processing Workflow](#processing-workflow)
- [Architecture Knowledge Base](#architecture-knowledge-base)
- [Downstream Compatibility (Case Studies 2–5)](#downstream-compatibility-case-studies-25)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Installation & Setup](#installation--setup)
- [How to Run](#how-to-run)
- [How to Test](#how-to-test)
- [Sample HLD Documents](#sample-hld-documents)
- [Limitations](#limitations)
- [Future Scope](#future-scope)

---

## 🚗 Project Title & Overview

**Project Title**: AUTOSAR HLD Document Analysis Assistant  
**Platform**: Tata TechPulse Automotive Engineering AI Workstation  

The **AUTOSAR HLD Document Analysis Assistant** automates the parsing, analysis, and verification of High-Level Design (HLD) specifications for AUTOSAR Classic ECU software architectures. It extracts application software components (SWCs), port prototypes, component interfaces, data element signals, and Basic Software (BSW) stack modules from PDF specifications into a standardized, version-aware **Architecture Knowledge Base**.

---

## 🎯 Problem Statement

Automotive ECU software development relies heavily on High-Level Design (HLD) PDF documents that define complex AUTOSAR component relationships, communication interfaces, and BSW service dependencies. Manual review of HLD documents is time-consuming, prone to human oversight, and often leads to:
- Missing port interface bindings and signal assignments.
- Unidentified execution triggering gaps for Runnable entities.
- Inconsistencies between HLD document versions during revision cycles.
- Lack of a machine-readable architecture representation for downstream safety, security, code review, and diagnostic workflows.

---

## 🏁 Tata TechPulse Case Study 1 Scope

This project fulfills the full scope of **Case Study 1: AUTOSAR HLD Document Analysis Assistant**:
- **PDF/HLD Ingestion**: Parses raw PDF architecture specifications with page citations and section header chunking.
- **Dynamic Version Detection**: Extracts actual document version declarations (e.g. `Version 1.0` and `Version 2.0`) from PDF text.
- **Architecture Entity Extraction**: Identifies SWCs, RPorts, PPorts, Interfaces, Signals, and BSW Stack Modules (`EcuM`, `BswM`, `CanIf`, `Com`, `Dem`).
- **5-Tier Dependency Mapping**: Maps end-to-end trace (`SWC -> Port -> Interface -> Signal -> Target Component / BSW`).
- **Architectural Completeness Analysis**: Detects unmapped ports, missing interface definitions, and runnable scheduling gaps.
- **HLD Revision Comparison**: Compares structural changes between document revisions (V1 vs V2).
- **Version-Aware Q&A**: Answers architectural change queries using structured comparison data and exact section citations.
- **Standardized Knowledge Base**: Generates a reusable schema (`architecture_knowledge_base.json`) with stable entity IDs (`SWC-xxx`, `PORT-xxx`, `IF-xxx`, `SIG-xxx`, `BSW-xxx`) for downstream case study compatibility.

---

## ⚡ Key Features

1. **Automated PDF Ingestion & Parsing**: Extract page text, metadata, section headers, and version tags.
2. **Architecture Entity Catalog**: Automatically extracts Application SWCs, Port Prototypes, Interfaces, Signals, and BSW modules.
3. **5-Tier Dependency Mapping & Graph Visualization**: Visualizes relationships using Graphviz vector diagrams (`st.graphviz_chart`).
4. **Architectural Completeness Analysis**: Rule-based detection of incomplete specifications and missing bindings.
5. **HLD Revision & Version Comparison**: Compares structural diffs between document revisions (Added/Removed/Modified items).
6. **Version-Aware Citation-Grounded Q&A**: RAG-powered natural language Q&A with exact version, page number, and section citations.
7. **Component & Interface Detail Reports**: Generates detailed component specification cards grounded in actual port citations.
8. **Structured Architecture JSON Specification**: Downloadable JSON specification of all analyzed entities and relationships.
9. **Executive PDF Analysis Report**: Formatted PDF report generation using ReportLab.
10. **Architecture Knowledge Base**: Centralized JSON data model with stable IDs (`SWC-xxx`, `PORT-xxx`, `IF-xxx`, `SIG-xxx`, `BSW-xxx`).
11. **Downstream Compatibility**: Designed to serve as the upstream input for future downstream case studies.

---

## 🏗️ System Architecture

```
HLD PDF Document
   │
   ▼
[ PDF Ingestion & Parsing ]  ──►  [ Entity Extractor ]
   │                                     │
   ▼                                     ▼
[ Vector Store / RAG ]       ──►  [ 5-Tier Relationship Builder ]
   │                                     │
   ▼                                     ▼
[ Grounded Q&A Engine ]      ──►  [ Completeness & Revision Analyzer ]
   │                                     │
   └───────────────────┬─────────────────┘
                       │
                       ▼
         [ Architecture Knowledge Base ]
                       │
         ┌─────────────┴─────────────┐
         ▼                           ▼
[ JSON / PDF / Detail Reports ]   [ Streamlit UI Workstation ]
```

---

## 🔄 Processing Workflow

1. **Document Selection / Upload**: User selects or uploads primary HLD PDF (and optional secondary V2 revision PDF).
2. **Parsing & Version Detection**: PDF text is parsed by `PDFParser` and scanned for document version strings.
3. **Entity & Relationship Extraction**: `ArchitectureExtractor` identifies entities; `RelationshipBuilder` constructs the 5-tier dependency tree.
4. **Completeness Verification**: `CompletenessAnalyzer` executes deterministic rules to identify architectural gaps.
5. **Revision Comparison**: `DocumentComparator` calculates structural diffs if a V2 revision is provided.
6. **Knowledge Base Construction**: `ArchitectureKnowledgeBase` assigns stable IDs and outputs the standardized JSON schema.
7. **Interactive Workstation Display**: Streamlit renders KPI cards, Graphviz diagrams, knowledge base tables, revision diffs, and citation-grounded Q&A.

---

## 🧠 Architecture Knowledge Base

The Knowledge Base is exported to `architecture_knowledge_base.json` with the following standardized structure:

```json
{
  "project": { "name": "AUTOSAR Body Control Module HLD", "platform": "AUTOSAR Classic Platform", "version": "Version 1.0" },
  "document": { "file_name": "AUTOSAR_Body_Control_Module_HLD.pdf", "version": "Version 1.0", "total_pages": 1 },
  "kpi_counts": { "components": 2, "bsw_modules": 4, "interfaces": 2, "signals": 2, "ports": 2, "findings": 3 },
  "components": [ { "id": "SWC-001", "name": "LightingControl_SWC", "ports": [] }, { "id": "SWC-002", "name": "DoorLock_SWC", "ports": ["RPort_DoorStatus", "PPort_LockActuator"] } ],
  "ports": [ { "id": "PORT-001", "name": "RPort_DoorStatus", "component": "DoorLock_SWC", "interface": "If_DoorState", "signals": ["Sig_DoorLock_status"] } ],
  "interfaces": [ { "id": "IF-001", "name": "If_DoorState", "signals": ["Sig_DoorLock_status"] } ],
  "signals": [ { "id": "SIG-001", "name": "Sig_DoorLock_status", "interface": "If_DoorState" } ],
  "bsw_modules": [ { "id": "BSW-001", "name": "EcuM", "category": "Basic Software Stack Module" } ],
  "dependencies": [...],
  "functional_flows": [...],
  "relationships": [...],
  "revision_history": {...},
  "findings": [...],
  "citations": [...]
}
```

---

## 🔗 Downstream Compatibility (Case Studies 2–5)

The standardized **Architecture Knowledge Base** is architected to serve as the upstream input for future Case Studies:

```
                                  ┌──────────────────────────────────────────────┐
                                  │   Architecture Knowledge Base (JSON Schema)  │
                                  └──────────┬───────────────────────────────────┘
                                             │ (Downstream Consumption)
                 ┌───────────────────────────┼───────────────────────────┬───────────────────────────┐
                 ▼                           ▼                           ▼                           ▼
      ┌─────────────────────┐     ┌─────────────────────┐     ┌─────────────────────┐     ┌─────────────────────┐
      │ Case Study 2: HARA  │     │ Case Study 3: TARA  │     │ Case Study 4: Code  │     │ Case Study 5: UDS   │
      │ (Functional Safety) │     │ (Cybersecurity)     │     │ (Secure Review)     │     │ (Diagnostics)       │
      └─────────────────────┘     └─────────────────────┘     └─────────────────────┘     └─────────────────────┘
```

> **Note**: Case Studies 2–5 represent future downstream modules designed to consume this standardized Knowledge Base schema. They are NOT implemented in Case Study 1.

---

## 🛠️ Technology Stack

- **UI Workstation**: Streamlit (`streamlit`)
- **PDF Parsing**: `pypdf`, `pdfplumber`
- **Visualization**: Graphviz (`st.graphviz_chart`)
- **Data Processing**: Pandas, NumPy
- **Vector Search & Embedding**: `sentence-transformers`, `chromadb`
- **Generative AI / RAG**: `google-genai` (Gemini API) with Grounded Offline Fallback Engine
- **PDF Export**: ReportLab (`reportlab`)

---

## 📁 Project Structure

```text
Tata techpulse/
├── app.py                      # Main Streamlit workstation UI application
├── generate_samples.py         # Sample PDF generator (ECU V1/V2, BCM V1/V2)
├── run_app.bat                 # Windows batch script launcher
├── requirements.txt            # Python dependencies specification
├── LICENSE                     # MIT License
├── README.md                   # Project overview & documentation
├── docs/                       # Detailed Architecture & Testing documentation
│   ├── architecture.md         # System architecture & data flow
│   ├── knowledge_base_schema.md# Knowledge Base JSON schema & downstream pipeline
│   └── testing.md              # Unit testing guide & test matrix
├── sample_documents/           # Sample HLD PDF documents
│   ├── AUTOSAR_Body_Control_Module_HLD.pdf     (Version 1.0)
│   ├── AUTOSAR_Body_Control_Module_HLD_V2.pdf  (Version 2.0 Revision)
│   ├── AUTOSAR_Engine_Control_Unit_HLD.pdf     (Version 1.0)
│   └── AUTOSAR_Engine_Control_Unit_HLD_V2.pdf  (Version 2.0 Revision)
├── outputs/                    # Exported JSON, PDF, and KB artifacts
├── src/                        # Core Python processing modules
│   ├── __init__.py
│   ├── config.py               # Paths & prompt configuration
│   ├── pdf_parser.py           # PDF parsing, version regex, section chunking
│   ├── extractor.py            # AUTOSAR entity extraction regex engine
│   ├── relationship_builder.py # 5-Tier dependency tree builder
│   ├── completeness_analyzer.py# Rule-based gap & schedule analyzer
│   ├── inconsistency_checker.py# Architecture inconsistency checker
│   ├── comparator.py           # HLD V1 vs V2 revision comparison engine
│   ├── knowledge_base.py       # Architecture Knowledge Base & stable IDs
│   ├── llm_engine.py           # Citation-grounded version-aware Q&A synthesis
│   ├── vector_store.py         # Local TF-IDF & vector retrieval
│   └── report_generator.py     # PDF & JSON report exporter
└── tests/                      # Unit test suite
    └── test_hld_features.py    # 10 comprehensive unit tests
```

---

## 💻 Installation & Setup

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/smkandalkar2005-crypto/autosar-hld-ai-assistant.git
   cd autosar-hld-ai-assistant
   ```

2. **Set Up Python Virtual Environment**:
   ```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # Linux/macOS:
   source .venv/bin/activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Generate Sample Documents** (Optional):
   ```bash
   python generate_samples.py
   ```

---

## 🚀 How to Run

Launch the Streamlit workstation:

```bash
streamlit run app.py
```

Alternatively, on Windows double-click `run_app.bat` or run:
```cmd
run_app.bat
```

Once launched, open `http://localhost:8501` in your web browser:
1. Select **Primary HLD (V1)**: `AUTOSAR_Body_Control_Module_HLD.pdf`.
2. Select **Comparison HLD (V2)**: `AUTOSAR_Body_Control_Module_HLD_V2.pdf`.
3. Click **🚀 Analyze & Index Architecture**.

---

## 🧪 How to Test

Execute the unit test suite:

```bash
python -m unittest discover tests
```

Expected output:
```text
..........
----------------------------------------------------------------------
Ran 10 tests in 0.075s

OK
```

---

## 📄 Sample HLD Documents

The repository includes pre-generated AUTOSAR sample HLD PDF specifications in `sample_documents/`:
- **`AUTOSAR_Body_Control_Module_HLD.pdf`**: Version 1.0 Body Control Module specification defining `LightingControl_SWC`, `DoorLock_SWC`, `RPort_DoorStatus`, `PPort_LockActuator`, `If_DoorState`, `Sig_DoorLock_status`, and BSW modules (`EcuM`, `BswM`, `CanIf`, `Com`).
- **`AUTOSAR_Body_Control_Module_HLD_V2.pdf`**: Version 2.0 Revision specification introducing `WindowControl_SWC`, `If_WindowPosition`, `Sig_WindowPos_pct`, `Dem`, and removing `If_LegacyState`. Explicitly labeled as `[SAMPLE / TEST DATA FOR REVISION COMPARISON DEMONSTRATION ONLY]`.

---

## ⚠️ Limitations

- **Text-based PDFs**: The extractor currently parses text-based HLD PDF specifications. Scanned image-only PDFs require pre-OCR processing.
- **AUTOSAR Classic Focus**: Optimized for AUTOSAR Classic specifications (SWC, Port, Interface, Signal, BSW stack).

---

## 🔮 Future Scope

- **Adaptive AUTOSAR Support**: Extending entity regex for Adaptive AUTOSAR Service Interfaces and SOME/IP bindings.
- **ARXML Import/Export**: Direct bi-directional import and export of official AUTOSAR `.arxml` files.
- **Downstream Integrations**: Consuming the exported `architecture_knowledge_base.json` in Case Studies 2–5 (HARA, TARA, Secure Code Review, and UDS Diagnostics).

---

## 📜 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
