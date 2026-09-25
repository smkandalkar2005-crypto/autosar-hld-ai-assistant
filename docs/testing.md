# AUTOSAR HLD Analysis Assistant — Testing & Verification Guide

## Overview

The test suite validates the core functionality of the **AUTOSAR HLD Document Analysis Assistant** using Python's built-in `unittest` framework.

Tests verify deterministic entity extraction, 5-tier dependency tree mapping, rule-based architectural completeness checks, revision comparison diffs, grounded citation Q&A synthesis, component detail report flows, and Architecture Knowledge Base schema generation with stable IDs.

---

## Test Execution Command

Run the complete test suite from the project root directory:

```bash
python -m unittest discover tests
```

---

## Current Test Summary

- **Total Test Count**: 10 tests
- **Test File**: `tests/test_hld_features.py`
- **Expected Execution Result**: `OK` (All 10 tests passing)

---

## Test Coverage Breakdown

| Test Method | Category | Verified Behavior |
|-------------|----------|-------------------|
| `test_relationship_builder` | 5-Tier Mapping | Verifies construction of 5-tier relationship tree (`SWC -> Port -> Interface -> Signal -> Target`). |
| `test_bcm_v1_vs_v2_revision_comparison` | Revision Comparison | Compares Body Control Module HLD V1 (`Version 1.0`) vs V2 (`Version 2.0`). Verifies detection of added SWC (`WindowControl_SWC`), added Interface (`If_WindowPosition`), added Signal (`Sig_WindowPos_pct`), added BSW module (`Dem`), removed Interface (`If_LegacyState`), removed Signal (`Sig_Legacy_status`), and common elements. |
| `test_version_aware_qa_synthesis` | Version Q&A | Verifies `generate_rag_response` outputs structured diffs for multi-category change queries, correctly formats removed items (`If_LegacyState`), and attaches section citations (`Section 2. Application Components`, `Section 3. Interface & Port Configuration`, `Section 4. Basic Software Stack & Diagnostics`). |
| `test_ui_citation_data_flow` | UI Citation Grounding | Confirms citation objects returned by RAG engine are non-empty and compatible with single-line markdown rendering in Streamlit expanders. |
| `test_component_detail_report_lighting_swc_no_fake_flows` | Detail Report | Verifies `LightingControl_SWC` (which has no documented ports) produces `ports: []`, `functional_flows: []`, and `source_references: []` without fabricating RPort/PPort flows. |
| `test_component_detail_report_doorlock_swc` | Detail Report | Verifies `DoorLock_SWC` (which has documented ports) preserves real mapping `RPort_DoorStatus -> If_DoorState -> Sig_DoorLock_status` and page references. |
| `test_completeness_analyzer` | Completeness Analysis | Verifies rule-based check detection for runnable entities and exact flagging reason: *"The HLD does not document how SWC execution is triggered or scheduled. This may limit verification of RTE scheduling and execution behavior."* |
| `test_report_generator_structured_export` | JSON Export | Verifies generation of `autosar_structured_architecture_spec.json`. |
| `test_architecture_knowledge_base` | Knowledge Base | Verifies `ArchitectureKnowledgeBase` schema construction, stable IDs (`SWC-xxx`, `PORT-xxx`, `IF-xxx`, `SIG-xxx`, `BSW-xxx`), original name preservation (`DoorLock_SWC`, `RPort_DoorStatus`, `If_DoorState`, `Sig_DoorLock_status`, `EcuM`), KPI counts, grounding (`"Not specified in source document"` for unknown targets), and JSON export (`architecture_knowledge_base.json`). |

---

## Sample Execution Output

```text
..........
----------------------------------------------------------------------
Ran 10 tests in 0.075s

OK
```
