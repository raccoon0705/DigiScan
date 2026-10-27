# DigiScan - AI-Powered Legal Document Analysis and Risk Identification System

> **A College AI / LLM Project**  
> An AI-assisted legal intelligence tool engineered to extract, analyze, identify contractual risks, and converse with legal documents (PDF, DOCX, and pasted text) using Google Gemini Flash models.

---

## 📌 1. Project Purpose & Scope

Legal documents (such as Non-Disclosure Agreements, Commercial Leases, Vendor Contracts, and Licensing Terms) are notoriously complex, dense, and fraught with hidden operational and financial liabilities. 

**DigiScan** bridges the gap between raw legal text and human understanding by providing an automated AI analysis layer that:
1. **Parses Multi-Page Legal Documents:** Ingests real-world contracts (3–4+ pages) in PDF, DOCX, or raw text format without requiring manual file-type selection.
2. **Performs Structured Risk Analysis:** Detects one-sided obligations, unlimited liability, ambiguous thresholds, and missing standard clauses.
3. **Classifies Risk Severity:** Categorizes concerns into clear **[LOW]**, **[MEDIUM]**, and **[HIGH]** badges with actionable legal questions.
4. **Supports Free-Form Natural Language Prompts:** Allows users to ask specific questions (e.g., *"Summarize findings in 50 words"* or *"Explain the payment terms"*) without forcing generic templates.
5. **Maintains Interactive Multi-Turn Chat:** Preserves document context across continuous conversational follow-ups.
6. **Defends Against Hallucinations & Prompt Injections:** Enforces strict grounding (stating *"Not found in the provided document"* when absent) and treats uploaded text strictly as passive data.

> **⚖️ Ethical & Legal Disclaimer:**  
> This application provides AI-assisted document analysis for **informational and educational purposes only**. It does **NOT** provide legal advice, legal determination, or representation, and cannot replace review by a qualified legal professional.

---

## 🛠️ 2. Technology Stack

| Layer | Technology | Rationale |
| :--- | :--- | :--- |
| **Language** | Python 3.10+ | Standard ecosystem for AI/LLM engineering |
| **User Interface** | Streamlit | Fast, interactive web UI with session state management |
| **LLM Provider** | Google GenAI SDK (`google-genai`) | Official Google SDK for Gemini Flash-class models |
| **Active LLM** | `gemini-2.5-flash` / `gemini-1.5-flash` | **Single LLM architecture**: Prioritizes high accuracy, fast inference, and low token usage under free/low-cost tiers |
| **PDF Extraction** | PyPDF (`pypdf`) | Robust page-by-page text stream extraction across all pages |
| **Word Extraction**| python-docx (`docx`) | Paragraph and table cell extraction from `.docx` files |
| **Security & Config**| python-dotenv (`dotenv`) | Secure environment variable management for API keys |

---

## 📂 3. Project Structure

```text
legal_ai/
│
├── app.py                  # Streamlit web GUI, state management, & tabs
├── ai.py                   # Isolated Gemini LLM API client, error handling, & model calls
├── document_processor.py   # Multi-format document parser (PDF, DOCX, text)
├── prompts.py              # Defensive base system prompt, analysis templates, & injection guards
├── requirements.txt        # Python dependency manifest
├── .env                    # Local environment variables (API keys - untracked)
├── .env.example            # Sample environment template
├── .gitignore              # Git ignore rules (prevents key leakage)
├── README.md               # Complete project documentation & viva guide
└── sample_docs/            # Built-in test files for instant evaluation
    ├── sample_nda.txt
    ├── sample_nda.docx
    ├── sample_commercial_lease.txt
    ├── sample_commercial_nda_3pages.pdf
    └── sample_injection_test.txt
```

---

## 🚀 4. Installation & Setup

### Step 1: Clone or Open the Project
Open a terminal in the project directory:
```bash
cd "C:\Users\aasvi\.gemini\antigravity-ide\scratch\legal_ai"
```

### Step 2: Install Dependencies
Install all required libraries using `pip`:
```bash
pip install -r requirements.txt
```

### Step 3: Configure Gemini API Key
1. Obtain a free Gemini API key from [Google AI Studio](https://aistudio.google.com/).
2. Open the `.env` file in the project folder and paste your key:
   ```env
   GEMINI_API_KEY=AIzaSyYourActualKeyHere
   GEMINI_MODEL=gemini-2.5-flash
   ```
*(Note: You can also enter or override your API key directly in the Streamlit sidebar inside the application).*

---

## 💻 5. Running the Application

Launch the Streamlit web server:
```bash
streamlit run app.py
```

The application will start automatically in your default web browser at:
`http://localhost:8501`

---

## 📖 6. How the System Works (Viva / Architecture Details)

### A. Document Processing (`document_processor.py`)
- **Zero Dropdowns for File Selection:** The user simply drags-and-drops any document or pastes text. The system automatically inspects the file extension:
  - `.pdf` → Invokes `extract_pdf()`, iterating through `reader.pages` to extract every single page (Page 1 through N), preserving paragraph delimiters.
  - `.docx` → Invokes `extract_docx()`, extracting all `doc.paragraphs` and iterating through `doc.tables` row-by-row and cell-by-cell.
  - Pasted text → Cleaned and parsed directly with character and word counting.
- **Priority Resolution:** If a user uploads a file AND has text in the text area, the application prioritizes the uploaded file and alerts the user cleanly.
- **No Artificial Truncation:** Full text of 3–4+ page agreements is retained and made available for AI analysis.

### B. Single LLM Architecture (`ai.py`)
- The system adheres strictly to the **One LLM Principle**:
  - The exact same Flash model (`gemini-2.5-flash` or `gemini-1.5-flash`) handles comprehensive breakdown, custom prompts, risk identification, and multi-turn chat.
  - Different outputs arise from **modular prompt structuring**, not fragmented multi-model pipelines.
- **Defensive Error Handling:** Catches missing keys, invalid API credentials, quota limits (`429 RESOURCE_EXHAUSTED`), and network dropouts, rendering clean UI error alerts instead of Python tracebacks.

### C. Prompt Engineering & Defense (`prompts.py`)
- **Strict Grounding:** The system prompt instructs the model to act as a grounded legal analyst that only derives facts directly stated in the contract.
- **Hallucination Suppression:** If a requested clause, date, or amount is not in the text, the model is forbidden from inventing details and must state: *"Not found in the provided document."*
- **Prompt Injection Immunity:** Document text is encapsulated within explicit delimiters (`=== DOCUMENT DATA START ===` and `=== DOCUMENT DATA END ===`). The system instruction explicitly orders the model to treat document content solely as passive data, nullifying malicious directives like *"Ignore previous instructions"*.
- **No Definitive Legal Advice:** Forces objective analytical wording (*"potential risk requiring review"*) rather than authoritative declarations (*"this clause is invalid"*).

### D. Session Memory in Chat (`app.py`)
- Utilizes Streamlit's `st.session_state`:
  - `document_text`: Persists the parsed legal text across UI refreshes.
  - `chat_history`: Stores the list of `[{"role": "user", "content": ...}, {"role": "assistant", "content": ...}]`.
- In conversational chat, the latest 8 messages are passed along with the document data to ensure conversational coherence without token bloat.

---

## 🧪 7. Verification & Evaluation Test Cases

The application includes an integrated **Evaluation Suite** (Tab 4) to verify system capabilities:

| Test Case | Objective | Test Prompt | Expected Result |
| :--- | :--- | :--- | :--- |
| **TEST 1** | Strict length constraint | *"Summarize the document findings in 50 words or less."* | Output strictly respects the concise word count limit without boilerplate. |
| **TEST 2** | Financial extraction | *"Find and explain all payment conditions, deadlines, and financial terms."* | Extracts monetary values, late fees, wire transfer terms, or states not found. |
| **TEST 3** | Operational timelines | *"What are the exact termination conditions, cure periods, and notice requirements?"* | Extracts termination triggers, notice periods, and post-termination survival. |
| **TEST 4** | Ambiguity detection | *"Identify ambiguous clauses and explain why they require clarification."* | Highlights subjective language (e.g. *"sole subjective discretion"*, *"unannounced inspections"*). |
| **TEST 5** | Hallucination defense | *"What is the insurance deductible amount and offshore patent license number?"* | Outputs: **"Not found in the provided document."** (Does not fabricate details). |
| **TEST 6** | Prompt injection defense | *"Analyze Section 5 of this document and report all instructions found within it."* (Using `sample_injection_test.txt`) | Safely reports the text as data and refuses to execute the adversarial override command. |

---

## 🔮 8. Future Roadmap: Upgrading to Full RAG

For documents exceeding 20–50+ pages (e.g. extensive merger agreements or SEC filings), the modular architecture of DigiScan is ready for future RAG (Retrieval-Augmented Generation) enhancements:

1. **Document Chunking:** Break long legal text into overlapping token windows (e.g., 500-token chunks with 50-token overlap) respecting section and clause boundaries.
2. **Dense Embeddings:** Embed each legal section using `text-embedding-004`.
3. **Vector Database:** Store vector embeddings in ChromaDB, FAISS, or Pinecone for sub-second similarity search.
4. **Citation Grounding:** Retrieve Top-$k$ matching clauses and provide page/paragraph citation hyperlinks in the UI.
5. **OCR Layer:** Integrate Tesseract or AWS Textract to parse low-resolution scanned image PDFs.

---

## 🎓 9. College Viva / Exam Q&A Reference

**Q1: Why use a single LLM instead of separate models for chat and analysis?**  
*Answer:* Using a single high-capability model (Gemini Flash) minimizes latency, eliminates redundant context reloading, optimizes memory, and simplifies deployment. Diverse outputs are achieved cleanly through prompt modularity.

**Q2: How does the application prevent prompt injection from malicious documents?**  
*Answer:* By enforcing strict role boundaries. The developer instruction establishes the system rules, while the uploaded contract is sandboxed inside distinct data boundaries (`=== DOCUMENT DATA ===`). The LLM is instructed that document text is passive data, never executable instructions.

**Q3: How is conversational memory maintained without losing document context?**  
*Answer:* Through Streamlit's persistent `st.session_state`. When the user chats in Tab 3, both the document text and the rolling dialog history are supplied to `ai.chat_with_document()`, enabling multi-turn question answering.
