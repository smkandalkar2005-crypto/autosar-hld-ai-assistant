# Architecture Knowledge Base Schema & Downstream Integration Specification

## Overview

The **Architecture Knowledge Base** is the standardized JSON data model constructed by the **AUTOSAR HLD Analysis Assistant**. It aggregates extracted AUTOSAR entities, stable identifiers, 5-tier relationship trees, document version citations, and completeness findings into a single source of truth.

It is specifically designed to enable downstream compatibility for future Automotive Engineering Case Studies without reparsing original HLD PDF documents.

---

## Downstream AI Pipeline Integration

```
┌──────────────────────┐
│   AUTOSAR HLD PDF    │
└──────────┬───────────┘
           │ (Ingestion & Parsing)
           ▼
┌──────────────────────────────────────────────┐
│ Case Study 1: AUTOSAR HLD Analysis Assistant │
└──────────┬───────────────────────────────────┘
           │ (Standard Schema & Stable IDs)
           ▼
┌──────────────────────────────────────────────┐
│     Architecture Knowledge Base (JSON)       │
└──────────┬───────────────────────────────────┘
           │ (Downstream Consumption for Case Studies 2–5)
           ├───────────────────────────┬───────────────────────────┬───────────────────────────┐
           ▼                           ▼                           ▼                           ▼
┌─────────────────────┐     ┌─────────────────────┐     ┌─────────────────────┐     ┌─────────────────────┐
│ Case Study 2: HARA  │     │ Case Study 3: TARA  │     │ Case Study 4: Code  │     │ Case Study 5: UDS   │
│ (Functional Safety) │     │ (Cybersecurity)     │     │ (Secure Review)     │     │ (Diagnostics)       │
└─────────────────────┘     └─────────────────────┘     └─────────────────────┘     └─────────────────────┘
```

> **Disclaimer**: Case Studies 2–5 represent future downstream consumer modules designed to consume this standardized Knowledge Base schema. They are NOT implemented in Case Study 1.

---

## Schema Structure

```json
{
  "project": {
    "name": "AUTOSAR Body Control Module HLD",
    "description": "AUTOSAR High-Level Design Architecture Specification",
    "platform": "AUTOSAR Classic Platform",
    "version": "Version 1.0"
  },
  "document": {
    "file_name": "AUTOSAR_Body_Control_Module_HLD.pdf",
    "version": "Version 1.0",
    "total_pages": 1,
    "status": "Parsed & Analyzed"
  },
  "kpi_counts": {
    "components": 2,
    "bsw_modules": 4,
    "interfaces": 2,
    "signals": 2,
    "ports": 2,
    "findings": 3
  },
  "components": [
    {
      "id": "SWC-001",
      "name": "LightingControl_SWC",
      "type": "Atomic Application Software Component",
      "ports": [],
      "source_citation": {
        "doc_name": "AUTOSAR_Body_Control_Module_HLD.pdf",
        "doc_version": "Version 1.0",
        "page": 1,
        "section": "2. Application Components"
      }
    },
    {
      "id": "SWC-002",
      "name": "DoorLock_SWC",
      "type": "Atomic Application Software Component",
      "ports": ["RPort_DoorStatus", "PPort_LockActuator"],
      "source_citation": {
        "doc_name": "AUTOSAR_Body_Control_Module_HLD.pdf",
        "doc_version": "Version 1.0",
        "page": 1,
        "section": "2. Application Components"
      }
    }
  ],
  "ports": [
    {
      "id": "PORT-001",
      "name": "RPort_DoorStatus",
      "component": "DoorLock_SWC",
      "component_id": "SWC-002",
      "type": "Requester / Receiver",
      "interface": "If_DoorState",
      "signals": ["Sig_DoorLock_status"],
      "target_component": "Not specified in source document",
      "source_citation": {
        "doc_name": "AUTOSAR_Body_Control_Module_HLD.pdf",
        "doc_version": "Version 1.0",
        "page": 1,
        "section": "3. Interface & Port Configuration"
      }
    },
    {
      "id": "PORT-002",
      "name": "PPort_LockActuator",
      "component": "DoorLock_SWC",
      "component_id": "SWC-002",
      "type": "Provider / Transmitter",
      "interface": "Not specified in source document",
      "signals": [],
      "target_component": "Not specified in source document",
      "source_citation": {
        "doc_name": "AUTOSAR_Body_Control_Module_HLD.pdf",
        "doc_version": "Version 1.0",
        "page": 1,
        "section": "3. Interface & Port Configuration"
      }
    }
  ],
  "interfaces": [
    {
      "id": "IF-001",
      "name": "If_DoorState",
      "signals": ["Sig_DoorLock_status"],
      "source_citation": {
        "doc_name": "AUTOSAR_Body_Control_Module_HLD.pdf",
        "doc_version": "Version 1.0",
        "page": 1,
        "section": "3. Interface & Port Configuration"
      }
    }
  ],
  "signals": [
    {
      "id": "SIG-001",
      "name": "Sig_DoorLock_status",
      "interface": "If_DoorState",
      "source_citation": {
        "doc_name": "AUTOSAR_Body_Control_Module_HLD.pdf",
        "doc_version": "Version 1.0",
        "page": 1,
        "section": "3. Interface & Port Configuration"
      }
    }
  ],
  "bsw_modules": [
    {
      "id": "BSW-001",
      "name": "EcuM",
      "category": "Basic Software Stack Module",
      "source_citation": {
        "doc_name": "AUTOSAR_Body_Control_Module_HLD.pdf",
        "doc_version": "Version 1.0",
        "page": 1,
        "section": "4. Basic Software Stack & Diagnostics"
      }
    }
  ],
  "dependencies": [
    {
      "source_component": "DoorLock_SWC",
      "port": "RPort_DoorStatus",
      "interface": "If_DoorState",
      "signals": ["Sig_DoorLock_status"],
      "target_destination": "Not specified in source document",
      "type": "Port Interface Binding"
    }
  ],
  "functional_flows": [],
  "relationships": [...],
  "revision_history": {},
  "findings": [...],
  "citations": [...]
}
```

---

## Field Descriptions

| Field | Type | Description |
|-------|------|-------------|
| `project` | Object | Metadata including project name, description, platform (`AUTOSAR Classic Platform`), and version. |
| `document` | Object | Target PDF metadata including file name, extracted document version, total pages, and status. |
| `kpi_counts` | Object | Dynamic metrics count for components, BSW modules, interfaces, signals, ports, and findings. |
| `components` | Array | Application SWC catalog with stable IDs (`SWC-xxx`), names, types, ports list, and citations. |
| `ports` | Array | Port prototype catalog with stable IDs (`PORT-xxx`), bound component, port type, mapped interface, signals list, target component, and page citations. |
| `interfaces` | Array | Interface catalog with stable IDs (`IF-xxx`), names, mapped payload signals, and section citations. |
| `signals` | Array | Signal catalog with stable IDs (`SIG-xxx`), names, parent interface, and section citations. |
| `bsw_modules` | Array | Basic Software stack catalog with stable IDs (`BSW-xxx`), names, category, and section citations. |
| `dependencies` | Array | Port-interface dependency bindings connecting components, ports, interfaces, and signals. |
| `functional_flows` | Array | End-to-end functional flow descriptions derived from connected ports. |
| `relationships` | Array | Full 5-tier relationship hierarchy (`SWC -> Port -> Interface -> Signal -> Target`). |
| `revision_history` | Object | Structured diff output from revision comparison (if V2 revision document is provided). |
| `findings` | Array | Completeness gap analysis findings with severity tags and source reference citations. |
| `citations` | Array | Grounded document section citations mapping topics to page numbers and section headers. |

---

## Stable Entity Identifiers

Entities are assigned stable, sequential identifiers to simplify downstream relational referencing:
- **Software Components**: `SWC-001`, `SWC-002`, `SWC-003`, ...
- **Port Prototypes**: `PORT-001`, `PORT-002`, `PORT-003`, ...
- **Interfaces**: `IF-001`, `IF-002`, `IF-003`, ...
- **Data Signals**: `SIG-001`, `SIG-002`, `SIG-003`, ...
- **BSW Modules**: `BSW-001`, `BSW-002`, `BSW-003`, ...

All original entity names (e.g. `DoorLock_SWC`, `RPort_DoorStatus`, `If_DoorState`, `Sig_DoorLock_status`, `EcuM`) are preserved alongside stable IDs.

---

## Grounding & Fallback Handling

If a relationship or attribute is omitted in the source HLD PDF, the field explicitly preserves:
`"Not specified in source document"`

No artificial relationships or connections are invented.
