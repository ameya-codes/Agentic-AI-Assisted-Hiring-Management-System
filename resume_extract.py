"""Extract plain text from resume uploads (PDF, DOCX, TXT). POC-only."""

from __future__ import annotations

import io


def extract_resume_text(filename: str, data: bytes) -> str:
    if not data:
        raise ValueError("Empty file.")
    name = (filename or "").lower()
    if name.endswith(".txt"):
        return data.decode("utf-8", errors="replace")
    if name.endswith(".pdf"):
        from pypdf import PdfReader

        reader = PdfReader(io.BytesIO(data))
        parts: list[str] = []
        for page in reader.pages:
            t = page.extract_text()
            if t:
                parts.append(t)
        return "\n".join(parts).strip()
    if name.endswith(".docx"):
        from docx import Document

        doc = Document(io.BytesIO(data))
        return "\n".join(p.text for p in doc.paragraphs if p.text).strip()
    if name.endswith(".doc"):
        raise ValueError("Legacy .doc is not supported; please upload PDF or .docx.")
    raise ValueError("Unsupported format. Upload PDF, DOCX, or TXT.")
