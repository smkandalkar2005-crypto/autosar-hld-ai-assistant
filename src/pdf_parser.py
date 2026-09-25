import re
from pathlib import Path
from typing import List, Dict, Any
import pypdf

class PDFParser:
    """Parses AUTOSAR HLD PDF documents into structured section chunks with page citations."""

    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        if not self.file_path.exists():
            raise FileNotFoundError(f"PDF file not found at: {file_path}")

    def extract_pages(self) -> List[Dict[str, Any]]:
        """Extract text and metadata page by page using pypdf."""
        pages_data = []
        reader = pypdf.PdfReader(str(self.file_path))
        
        for i, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            pages_data.append({
                "page_num": i + 1,
                "text": text.strip(),
                "file_name": self.file_path.name
            })
        return pages_data

    def chunk_document(self, chunk_size: int = 500, overlap: int = 100) -> List[Dict[str, Any]]:
        """
        Chunks PDF content into context-aware chunks preserving section headings & page numbers.
        """
        pages = self.extract_pages()
        chunks = []
        chunk_id = 0

        current_heading = "General Architecture Overview"
        heading_pattern = re.compile(r'^(?:\d+\.|\d+\.\d+|\b[A-Z0-9\s]{4,30}\b)(?:\s+[A-Z][a-zA-Z0-9\s_-]+)')

        for page in pages:
            lines = page["text"].split("\n")
            page_num = page["page_num"]
            buffer = []
            
            for line in lines:
                line_str = line.strip()
                if not line_str:
                    continue
                
                # Check for section headers
                if heading_pattern.match(line_str) and len(line_str) < 80:
                    current_heading = line_str

                buffer.append(line_str)
                
                # Create chunk when buffer reaches chunk size (by word count approx)
                current_text = " ".join(buffer)
                if len(current_text.split()) >= chunk_size:
                    chunks.append({
                        "chunk_id": f"{self.file_path.stem}_p{page_num}_c{chunk_id}",
                        "text": current_text,
                        "page_num": page_num,
                        "section": current_heading,
                        "file_name": self.file_path.name
                    })
                    chunk_id += 1
                    # Keep overlap words
                    words = current_text.split()
                    buffer = [ " ".join(words[-overlap:]) ] if len(words) > overlap else []

            if buffer:
                current_text = " ".join(buffer)
                if current_text.strip():
                    chunks.append({
                        "chunk_id": f"{self.file_path.stem}_p{page_num}_c{chunk_id}",
                        "text": current_text,
                        "page_num": page_num,
                        "section": current_heading,
                        "file_name": self.file_path.name
                    })
                    chunk_id += 1

        return chunks
