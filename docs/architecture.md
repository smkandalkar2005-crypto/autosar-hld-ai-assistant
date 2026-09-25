# AUTOSAR HLD Analysis Assistant — System Architecture

## Overview

The **AUTOSAR HLD Document Analysis Assistant** is an Automotive AI workstation designed for High-Level Design (HLD) document ingestion, entity extraction, 5-tier dependency mapping, rule-based architectural completeness checks, HLD revision comparison, and version-aware citation-grounded Q&A.

It acts as the upstream ingestion and analysis engine for the **Tata TechPulse Automotive Engineering AI Case Study 1**, constructing a standardized **Architecture Knowledge Base** that serves as the single source of truth for downstream automotive engineering case studies (HARA, TARA, Secure Code Review, UDS Diagnostics).

---

## High-Level Data Flow Architecture

```
┌────────────────────────────────────────────────────────────────────────┐
│                          AUTOSAR HLD PDF Document                      │
│      (e.g., AUTOSAR_Body_Control_Module_HLD.pdf / Version 1.0 & 2.0)   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                        1. PDF Ingestion & Parsing                      │
│   • Page-by-Page Text Extraction (pypdf)                               │
│   • Dynamic Version Detection Regex (Document Version: X.X)            │
│   • Section Header Chunking (Section-aligned buffers)                  │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                       2. Entity Extraction Engine                      │
│   • Software Components (SWCs)                                         │
│   • Port Prototypes (RPort / PPort)                                    │
│   • Component Interfaces (If_...)                                      │
│   • Data Element Signals (Sig_...)                                     │
│   • Basic Software Stack Modules (EcuM, BswM, CanIf, Com, Dem)         │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                     3. Architectural Analysis Engines                  │
│                                                                        │
│   ┌────────────────────────┐         ┌─────────────────────────────┐   │
│   │ 5-Tier Relationship    │         │ Architectural Completeness  │   │
│   │ Mapping Engine         │         │ Analysis Engine             │   │
│   │ (SWC→Port→If→Sig→Target)│        │ (Rule-based Gap Check)      │   │
│   └───────────┬────────────┘         └──────────────┬──────────────┘   │
│               │                                     │                  │
│               ├─────────────────────────────────────┤                  │
│               ▼                                     ▼                  │
│   ┌────────────────────────┐         ┌─────────────────────────────┐   │
│   │ HLD Revision           │         │ Grounded Version-Aware      │   │
│   │ Comparison Engine      │         │ Q&A Engine                  │   │
│   │ (V1 vs V2 Revision Diff│         │ (RAG Vector Store & LLM)    │   │
│   └────────────────────────┘         └─────────────────────────────┘   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                    4. Standardized Knowledge Base                      │
│   • Stable Entity Identifiers (SWC-xxx, PORT-xxx, IF-xxx, SIG-xxx)     │
│   • Document Version & Page/Section Citations                          │
│   • KPI Metrics & Relationship Bindings                                │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                     5. Downstream Export & Interface                   │
│   • architecture_knowledge_base.json                                   │
│   • Component & Interface Detail Reports                               │
│   • Executive PDF Analysis Report                                      │
└────────────────────────────────────────────────────────────────────────┘
```

---

## Core System Modules

### 1. Ingestion & PDF Parser (`src/pdf_parser.py`)
- Uses `pypdf` to parse AUTOSAR HLD documents into structured page objects.
- Dynamically extracts document version tags using regular expression patterns (`(Document Version|Version):\s*([0-9\.]+)`) from PDF text, avoiding hardcoded version strings.
- Flushes buffer chunks on section headers so every text chunk is tagged with its exact section title and page number.

### 2. Entity Extractor (`src/extractor.py`)
- Extracts AUTOSAR architecture elements using deterministic pattern matching:
  - **Software Components (SWCs)**: `[A-Z][a-zA-Z0-9_]*_SWC`
  - **Port Prototypes**: `(RPort|PPort)_[a-zA-Z0-9_]+`
  - **Interfaces**: `If_[a-zA-Z0-9_]+`
  - **Signals**: `Sig_[a-zA-Z0-9_]+`
  - **BSW Stack Modules**: `EcuM`, `BswM`, `CanIf`, `Com`, `Dem`, `Det`, `NvM`, `PduR`, `CanTp`, `CanDcm`, `Fee`, `Fls`

### 3. 5-Tier Relationship Mapping (`src/relationship_builder.py`)
- Maps end-to-end dependency hierarchies across 5 tiers:
  `SWC -> Port Prototype -> Bound Interface -> Payload Signal -> Target Destination Component / BSW`
- Preserves explicit provider/requester relationships when documented in the HLD.
- Uses `"Not specified in source document"` when a target destination or interface binding is genuinely omitted in the HLD, avoiding fabricated relationships.

### 4. Architectural Completeness Analyzer (`src/completeness_analyzer.py`)
- Performs deterministic rule-based checks for:
  - Unmapped Port Prototypes
  - Missing Interface / Signal Definitions
  - Disconnected SWC Targets
  - Runnable Entity & OS Task Scheduling omissions
- Flagged findings include Category, Severity (`HIGH`, `MEDIUM`, `LOW`), Evidence Found, Detected Gap, Reason for Flagging, and Source Reference Citation.

### 5. HLD Revision Comparison Engine (`src/comparator.py`)
- Compares structural architecture revisions (e.g. Version 1.0 vs Version 2.0).
- Detects added, removed, modified, and retained SWCs, BSW modules, interfaces, signals, and document sections.

### 6. Standardized Architecture Knowledge Base (`src/knowledge_base.py`)
- Aggregates document metadata, entity catalogs, 5-tier relationships, completeness findings, and revision comparison into a single standardized JSON schema.
- Assigns stable entity identifiers (`SWC-xxx`, `PORT-xxx`, `IF-xxx`, `SIG-xxx`, `BSW-xxx`) while preserving original entity names.
- Computes KPI metrics (`components`, `bsw_modules`, `interfaces`, `signals`, `ports`, `findings`).

### 7. Grounded Version-Aware Q&A Engine (`src/llm_engine.py` & `src/vector_store.py`)
- Embeds document text chunks using `sentence-transformers` and local TF-IDF vector search (`src/vector_store.py`).
- Synthesizes exact comparative answers using `comparison_results` for quick version queries.
- Returns citations containing document version, page number, section name, and evidence text without fallback placeholders.

### 8. Report Generator (`src/report_generator.py`)
- Exports `autosar_structured_architecture_spec.json`, `architecture_knowledge_base.json`, component detail cards, and executive PDF reports using ReportLab.

### 9. Interactive Streamlit Workstation UI (`app.py`)
- Multi-tab workstation interface featuring:
  - Executive KPI metrics header.
  - Interactive Graphviz relationship diagram (`st.graphviz_chart`).
  - Architecture Knowledge Base tab with downstream AI pipeline documentation.
  - Interactive chat interface with citation expanders.
