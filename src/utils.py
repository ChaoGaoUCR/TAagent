import json
import os
from typing import Any, Dict


def load_json(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def read_text_file(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def extract_text(path: str) -> str:
    ext = os.path.splitext(path)[1].lower()
    if ext in {".txt", ".md"}:
        return read_text_file(path)

    if ext == ".docx":
        try:
            from docx import Document  # type: ignore
        except Exception:
            return ""
        doc = Document(path)
        return "\n".join(p.text for p in doc.paragraphs)

    if ext == ".pdf":
        try:
            import pdfplumber  # type: ignore
        except Exception:
            return ""
        text_parts = []
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                text_parts.append(page.extract_text() or "")
        return "\n".join(text_parts)

    return ""
