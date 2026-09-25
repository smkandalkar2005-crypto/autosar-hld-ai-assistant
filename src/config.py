import os
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
SAMPLE_DOCS_DIR = BASE_DIR / "sample_documents"
VECTOR_DB_DIR = BASE_DIR / "vector_db"
OUTPUT_DIR = BASE_DIR / "outputs"

# Ensure directories exist
SAMPLE_DOCS_DIR.mkdir(exist_ok=True)
VECTOR_DB_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# Embedding Settings
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"

# AUTOSAR Keywords Taxonomy
AUTOSAR_KEYWORDS = {
    "BSW_MODULES": [
        "EcuM", "BswM", "Com", "CanIf", "CanTp", "Can", "Dem", "Dcm", 
        "PduR", "Nvm", "MemIf", "Fee", "Ea", "WdgM", "Det", "Os"
    ],
    "INTERFACE_TYPES": [
        "SenderReceiverInterface", "ClientServerInterface", "ModeSwitchInterface", 
        "ParameterInterface", "NvDataInterface"
    ],
    "PORT_TYPES": [
        "PPortPrototype", "RPortPrototype", "PRPortPrototype", "PPort", "RPort"
    ],
    "ENTITY_CATEGORIES": [
        "SoftwareComponent", "Composition", "BSW_Module", "RunnableEntity",
        "Port", "DataElement", "Operation", "Signal"
    ]
}

# RAG Prompts
RAG_SYSTEM_PROMPT = """You are an expert AUTOSAR System and Software Architect assistant.
Your task is to analyze High-Level Design (HLD) documents for AUTOSAR software architectures.
You provide precise, evidence-based answers strictly grounded in the provided document context.

Guidelines:
1. Ground every statement in the provided context chunks.
2. Provide page numbers and section citations for every component, interface, port, or requirement mentioned.
3. If an architectural detail is missing or ambiguous in the document, explicitly highlight it as an architectural gap.
4. Maintain formal automotive engineering terminology (AUTOSAR Classic/Adaptive terminology).
"""
