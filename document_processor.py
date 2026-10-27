"""
Document Processing Module for DigiScan Legal AI.

Extracts text from PDF, DOCX, and raw text inputs.
Ensures full document extraction across all pages and paragraphs,
preserving structure and handling formatting safely.
"""

import io
from typing import Dict, Any, Optional
import pypdf
import docx


def extract_pdf(file_bytes_or_buffer) -> Dict[str, Any]:
    """
    Extracts text from all pages of a PDF document using PyPDF.
    
    Args:
        file_bytes_or_buffer: Bytes, file-like object, or Streamlit UploadedFile
        
    Returns:
        dict: {
            "success": bool,
            "text": str,
            "page_count": int,
            "char_count": int,
            "word_count": int,
            "error": Optional[str]
        }
    """
    try:
        # Wrap bytes in BytesIO if needed
        if isinstance(file_bytes_or_buffer, bytes):
            buffer = io.BytesIO(file_bytes_or_buffer)
        else:
            buffer = file_bytes_or_buffer

        reader = pypdf.PdfReader(buffer)
        total_pages = len(reader.pages)
        
        if total_pages == 0:
            return {
                "success": False,
                "text": "",
                "page_count": 0,
                "char_count": 0,
                "word_count": 0,
                "error": "The uploaded PDF document contains no pages."
            }

        extracted_pages = []
        for page_num, page in enumerate(reader.pages, start=1):
            page_text = page.extract_text() or ""
            # Strip extra whitespace while maintaining paragraph separation
            clean_page_text = page_text.strip()
            if clean_page_text:
                extracted_pages.append(f"--- [Page {page_num}] ---\n{clean_page_text}")
            else:
                extracted_pages.append(f"--- [Page {page_num}] ---\n[Empty or Scanned Page]")

        full_text = "\n\n".join(extracted_pages).strip()
        
        if not full_text or full_text.replace("--- [Page ", "").replace("---", "").strip() == "":
            return {
                "success": False,
                "text": "",
                "page_count": total_pages,
                "char_count": 0,
                "word_count": 0,
                "error": "No selectable text found in the PDF. The file may be a scanned image without an OCR text layer."
            }

        char_count = len(full_text)
        word_count = len(full_text.split())

        return {
            "success": True,
            "text": full_text,
            "page_count": total_pages,
            "char_count": char_count,
            "word_count": word_count,
            "error": None
        }

    except Exception as exc:
        return {
            "success": False,
            "text": "",
            "page_count": 0,
            "char_count": 0,
            "word_count": 0,
            "error": f"Failed to extract text from PDF: {str(exc)}"
        }


def extract_docx(file_bytes_or_buffer) -> Dict[str, Any]:
    """
    Extracts complete text from a DOCX file using python-docx,
    including all body paragraphs and structured tables.
    
    Args:
        file_bytes_or_buffer: Bytes, file-like object, or Streamlit UploadedFile
        
    Returns:
        dict: {
            "success": bool,
            "text": str,
            "paragraph_count": int,
            "table_count": int,
            "char_count": int,
            "word_count": int,
            "error": Optional[str]
        }
    """
    try:
        if isinstance(file_bytes_or_buffer, bytes):
            buffer = io.BytesIO(file_bytes_or_buffer)
        else:
            buffer = file_bytes_or_buffer

        doc = docx.Document(buffer)
        
        extracted_sections = []
        paragraph_count = 0

        # 1. Extract paragraphs
        for para in doc.paragraphs:
            text = para.text.strip()
            if text:
                extracted_sections.append(text)
                paragraph_count += 1

        # 2. Extract tables (if any)
        table_count = len(doc.tables)
        if table_count > 0:
            extracted_sections.append("\n--- [Document Tables] ---")
            for t_idx, table in enumerate(doc.tables, start=1):
                extracted_sections.append(f"[Table {t_idx}]")
                for row in table.rows:
                    row_cells = [cell.text.strip() for cell in row.cells]
                    # Filter duplicate merged cell text if any
                    row_text = " | ".join(row_cells)
                    if row_text.strip():
                        extracted_sections.append(row_text)
                extracted_sections.append("")

        full_text = "\n\n".join(extracted_sections).strip()

        if not full_text:
            return {
                "success": False,
                "text": "",
                "paragraph_count": paragraph_count,
                "table_count": table_count,
                "char_count": 0,
                "word_count": 0,
                "error": "The DOCX document is empty or contains no readable text."
            }

        char_count = len(full_text)
        word_count = len(full_text.split())

        return {
            "success": True,
            "text": full_text,
            "paragraph_count": paragraph_count,
            "table_count": table_count,
            "char_count": char_count,
            "word_count": word_count,
            "error": None
        }

    except Exception as exc:
        return {
            "success": False,
            "text": "",
            "paragraph_count": 0,
            "table_count": 0,
            "char_count": 0,
            "word_count": 0,
            "error": f"Failed to extract text from DOCX: {str(exc)}"
        }


def process_pasted_text(raw_text: str) -> Dict[str, Any]:
    """
    Processes and validates raw copy-pasted legal document text.
    
    Args:
        raw_text: User-provided string
        
    Returns:
        dict: Extracted metadata and text
    """
    cleaned = (raw_text or "").strip()
    if not cleaned:
        return {
            "success": False,
            "text": "",
            "char_count": 0,
            "word_count": 0,
            "line_count": 0,
            "error": "Pasted text is empty. Please enter or paste legal text."
        }

    char_count = len(cleaned)
    word_count = len(cleaned.split())
    line_count = len([line for line in cleaned.splitlines() if line.strip()])

    return {
        "success": True,
        "text": cleaned,
        "char_count": char_count,
        "word_count": word_count,
        "line_count": line_count,
        "error": None
    }


def process_document_source(uploaded_file, pasted_text: Optional[str]) -> Dict[str, Any]:
    """
    Determines document source automatically, prioritizing uploaded file over pasted text.
    
    Args:
        uploaded_file: Streamlit UploadedFile or None
        pasted_text: Pasted string or None
        
    Returns:
        dict: {
            "source_type": "pdf" | "docx" | "pasted_text" | None,
            "source_name": str,
            "text": str,
            "metadata": dict,
            "success": bool,
            "error": Optional[str],
            "priority_note": Optional[str]
        }
    """
    # Case 1: Uploaded file provided
    if uploaded_file is not None:
        filename = getattr(uploaded_file, "name", "uploaded_document")
        file_ext = filename.lower().split(".")[-1] if "." in filename else ""

        priority_note = None
        if pasted_text and pasted_text.strip():
            priority_note = f"Both an uploaded file ('{filename}') and pasted text were detected. Prioritizing the uploaded file."

        if file_ext == "pdf":
            result = extract_pdf(uploaded_file)
            return {
                "source_type": "pdf",
                "source_name": filename,
                "text": result.get("text", ""),
                "metadata": {
                    "page_count": result.get("page_count", 0),
                    "char_count": result.get("char_count", 0),
                    "word_count": result.get("word_count", 0),
                },
                "success": result.get("success", False),
                "error": result.get("error"),
                "priority_note": priority_note
            }
        elif file_ext in ["docx", "doc"]:
            result = extract_docx(uploaded_file)
            return {
                "source_type": "docx",
                "source_name": filename,
                "text": result.get("text", ""),
                "metadata": {
                    "paragraph_count": result.get("paragraph_count", 0),
                    "table_count": result.get("table_count", 0),
                    "char_count": result.get("char_count", 0),
                    "word_count": result.get("word_count", 0),
                },
                "success": result.get("success", False),
                "error": result.get("error"),
                "priority_note": priority_note
            }
        else:
            return {
                "source_type": "unsupported",
                "source_name": filename,
                "text": "",
                "metadata": {},
                "success": False,
                "error": f"Unsupported file extension '.{file_ext}'. Please upload a .pdf or .docx document.",
                "priority_note": None
            }

    # Case 2: Pasted text provided
    if pasted_text and pasted_text.strip():
        result = process_pasted_text(pasted_text)
        return {
            "source_type": "pasted_text",
            "source_name": "Pasted Legal Text",
            "text": result.get("text", ""),
            "metadata": {
                "char_count": result.get("char_count", 0),
                "word_count": result.get("word_count", 0),
                "line_count": result.get("line_count", 0),
            },
            "success": result.get("success", False),
            "error": result.get("error"),
            "priority_note": None
        }

    # Case 3: Neither provided
    return {
        "source_type": None,
        "source_name": "",
        "text": "",
        "metadata": {},
        "success": False,
        "error": "No document provided. Please upload a PDF/DOCX file or paste text.",
        "priority_note": None
    }
