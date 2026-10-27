"""
Unit and Integration Test Suite for DigiScan Legal AI.
Verifies all document extractors, prompt builders, priority resolution,
and defensive error handling.
"""

import os
import io
import document_processor
import prompts
import ai

def run_all_tests():
    print("==================================================")
    print("  DigiScan Legal AI - Verification Test Suite")
    print("==================================================")

    # 1. Test PDF Extraction
    print("\n[TEST 1] PDF Multi-Page Extraction (PyPDF)...")
    pdf_path = os.path.join("sample_docs", "sample_commercial_nda_3pages.pdf")
    with open(pdf_path, "rb") as f:
        pdf_res = document_processor.extract_pdf(f)
    assert pdf_res["success"] is True, f"PDF extraction failed: {pdf_res}"
    assert pdf_res["page_count"] == 3, f"Expected 3 pages, got {pdf_res['page_count']}"
    assert pdf_res["word_count"] > 100, f"Expected >100 words, got {pdf_res['word_count']}"
    print(f"  --> PASSED: {pdf_res['page_count']} pages processed, {pdf_res['word_count']} words, {pdf_res['char_count']} characters.")

    # 2. Test DOCX Extraction
    print("\n[TEST 2] DOCX Paragraph and Table Extraction (python-docx)...")
    docx_path = os.path.join("sample_docs", "sample_nda.docx")
    with open(docx_path, "rb") as f:
        docx_res = document_processor.extract_docx(f)
    assert docx_res["success"] is True, f"DOCX extraction failed: {docx_res}"
    assert docx_res["paragraph_count"] >= 15, f"Expected >=15 paragraphs, got {docx_res['paragraph_count']}"
    print(f"  --> PASSED: {docx_res['paragraph_count']} paragraphs extracted, {docx_res['word_count']} words.")

    # 3. Test Pasted Text Processing
    print("\n[TEST 3] Pasted Text Processing & Sanitization...")
    lease_path = os.path.join("sample_docs", "sample_commercial_lease.txt")
    with open(lease_path, "r", encoding="utf-8") as f:
        lease_text = f.read()
    text_res = document_processor.process_pasted_text(lease_text)
    assert text_res["success"] is True
    assert text_res["word_count"] > 200
    print(f"  --> PASSED: {text_res['word_count']} words, {text_res['line_count']} lines.")

    # 4. Test Source Prioritization (Uploaded File > Pasted Text)
    print("\n[TEST 4] Automatic File-Type Detection & Upload Priority...")
    class StreamlitMockFile:
        def __init__(self, filename, filepath):
            self.name = filename
            with open(filepath, "rb") as f:
                self._data = f.read()
            self._io = io.BytesIO(self._data)
        def read(self, *args):
            return self._io.read(*args)
        def seek(self, *args):
            return self._io.seek(*args)

    mock_upload = StreamlitMockFile("sample_nda.docx", docx_path)
    prio_res = document_processor.process_document_source(mock_upload, "Some arbitrary pasted text")
    assert prio_res["source_type"] == "docx"
    assert prio_res["priority_note"] is not None
    assert "Prioritizing the uploaded file" in prio_res["priority_note"]
    print(f"  --> PASSED: Priority correctly resolved: {prio_res['priority_note']}")

    # 5. Test Prompt Engineering Module
    print("\n[TEST 5] Prompt Construction & Grounding Directives...")
    sys_prompt = prompts.build_system_prompt()
    assert "DigiScan" in sys_prompt
    assert "Not found in the provided document" in sys_prompt
    assert "UNTRUSTED DATA" in sys_prompt
    assert "[HIGH RISK]" in sys_prompt

    comp_prompt = prompts.build_comprehensive_analysis_prompt("Sample legal text")
    assert "Document Overview" in comp_prompt
    assert "Potential Risk Areas" in comp_prompt

    custom_p = prompts.build_custom_prompt("Sample legal text", "Summarize in 50 words or less.")
    assert "Summarize in 50 words or less." in custom_p
    assert "DOCUMENT DATA START" in custom_p

    chat_p = prompts.build_chat_prompt("Sample legal text", [{"role": "user", "content": "Question 1"}], "Follow-up question")
    assert "Follow-up question" in chat_p
    print("  --> PASSED: System prompt, comprehensive prompt, custom prompt, and chat prompt validated.")

    # 6. Test AI Error Handling (Defensive Execution)
    print("\n[TEST 6] AI Layer Missing Key & Defensive Error Handling...")
    ai_err_res = ai.analyze_document("Sample document text", custom_prompt="Test", api_key="")
    assert ai_err_res["success"] is False
    assert "API key is not configured" in ai_err_res["error"] or "API Key" in ai_err_res["error"]
    print(f"  --> PASSED: Clean error returned without tracebacks: '{ai_err_res['error']}'")

    print("\n==================================================")
    print("  ALL 6 TEST SUITE MODULES PASSED SUCCESSFULLY! [OK]")
    print("==================================================")

if __name__ == "__main__":
    run_all_tests()
