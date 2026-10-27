"""
DigiScan — AI-Powered Legal Document Analysis and Risk Identification System
Desktop Legal-Tech Workspace.
"""

import os
from datetime import datetime
import streamlit as st
from dotenv import load_dotenv

import document_processor
import prompts
import ai
import database

# Load environment variables
load_dotenv()

# -----------------------------------------------------------------------------
# PAGE CONFIGURATION
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="DigiScan | Legal Document Analysis",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# -----------------------------------------------------------------------------
# SESSION STATE INITIALIZATION
# -----------------------------------------------------------------------------
if "theme" not in st.session_state:
    st.session_state.theme = "light"

if "document_text" not in st.session_state:
    st.session_state.document_text = ""

if "document_name" not in st.session_state:
    st.session_state.document_name = ""

if "analyzed_at" not in st.session_state:
    st.session_state.analyzed_at = ""

if "analysis_data" not in st.session_state:
    st.session_state.analysis_data = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "active_doc_id" not in st.session_state:
    st.session_state.active_doc_id = None

if "pending_question" not in st.session_state:
    st.session_state.pending_question = None

if "history_open" not in st.session_state:
    st.session_state.history_open = False


# -----------------------------------------------------------------------------
# THEME CONFIGURATION & CSS STYLES
# -----------------------------------------------------------------------------
is_dark = st.session_state.theme == "dark"

if is_dark:
    bg_app = "#161513"
    bg_card = "#211F1C"
    bg_card_subtle = "#1C1A18"
    border_color = "#33302B"
    text_primary = "#F5F3EF"
    text_secondary = "#A6A095"
    text_muted = "#736E65"
    accent_gold = "#D4A359"
    accent_gold_subtle = "#2B2419"
    chat_panel_bg = "#211F1C"
    chat_user_bg = "#262420"
    chat_user_text = "#F5F3EF"
    chat_ai_bg = "#1B1917"
    chat_ai_text = "#F5F3EF"
    excerpt_bg = "#1A1917"
    excerpt_border = "#474136"
    badge_high_bg = "#381B1A"
    badge_high_border = "#5A2624"
    badge_high_text = "#FCA5A5"
    badge_med_bg = "#362912"
    badge_med_border = "#574019"
    badge_med_text = "#FDE68A"
    badge_low_bg = "#162B1D"
    badge_low_border = "#20462B"
    badge_low_text = "#86EFAC"
    btn_sugg_bg = "#211F1C"
    btn_sugg_border = "#33302B"
else:
    bg_app = "#FAF8F5"
    bg_card = "#FFFFFF"
    bg_card_subtle = "#F5F2EB"
    border_color = "#EBE6DD"
    text_primary = "#211F1C"
    text_secondary = "#787267"
    text_muted = "#9E978C"
    accent_gold = "#B88746"
    accent_gold_subtle = "#FBF6EE"
    chat_panel_bg = "#FFFFFF"
    chat_user_bg = "#FFFFFF"      # Crisp white background (no blue)
    chat_user_text = "#211F1C"    # Dark clearly visible text
    chat_ai_bg = "#FAF8F5"
    chat_ai_text = "#211F1C"
    excerpt_bg = "#FAF8F5"
    excerpt_border = "#DDD7CC"
    badge_high_bg = "#FDF0ED"
    badge_high_border = "#F5C6CB"
    badge_high_text = "#C0392B"
    badge_med_bg = "#FEF9E7"
    badge_med_border = "#FCE8A6"
    badge_med_text = "#B78103"
    badge_low_bg = "#F0F9F3"
    badge_low_border = "#C8E6C9"
    badge_low_text = "#2E7D32"
    btn_sugg_bg = "#FFFFFF"       # Crisp white background (no blue)
    btn_sugg_border = "#E6DFD2"

st.markdown(
    f"""
    <style>
    /* Global App Container */
    .stApp {{
        background-color: {bg_app} !important;
        color: {text_primary} !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }}

    /* Completely remove Streamlit deploy button, 3 dots menu, toolbar, and header bar */
    header[data-testid="stHeader"],
    div[data-testid="stToolbar"],
    .stDeployButton,
    #MainMenu,
    div[data-testid="stDecoration"],
    div[data-testid="stStatusWidget"],
    footer {{
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
        min-height: 0 !important;
        padding: 0 !important;
        margin: 0 !important;
    }}

    /* Remove any top margin / padding added by Streamlit container */
    [data-testid="stAppViewContainer"],
    [data-testid="stAppViewContainer"] > .main,
    [data-testid="stMain"],
    section.main {{
        padding-top: 0 !important;
        margin-top: 0 !important;
    }}

    /* Start right at the very top of the page without artificial blank space */
    .block-container {{
        padding-top: 0.2rem !important;
        padding-bottom: 0.5rem !important;
        padding-left: 1.5rem !important;
        padding-right: 1.5rem !important;
        max-width: 1560px !important;
    }}

    /* Balanced vertical block spacing */
    div[data-testid="stVerticalBlock"] {{
        gap: 0.5rem !important;
    }}

    /* Global Headings */
    h1, h2, h3, h4, h5, p, span, div {{
        color: {text_primary};
    }}

    /* Top Brand Header */
    .ds-topbar {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding-top: 0.1rem;
        padding-bottom: 0.45rem;
        border-bottom: 1px solid {border_color};
        margin-bottom: 0.35rem;
    }}

    .ds-brand-left {{
        display: flex;
        align-items: center;
        gap: 0.95rem;
    }}

    .ds-avatar-logo {{
        width: 48px;
        height: 48px;
        border-radius: 50%;
        background-color: {accent_gold};
        color: #FFFFFF !important;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 800;
        font-size: 1.25rem;
        letter-spacing: -0.02em;
        flex-shrink: 0;
        box-shadow: 0 3px 10px rgba(184, 135, 70, 0.28);
    }}

    .ds-title-text {{
        font-size: 1.65rem;
        font-weight: 800;
        color: {text_primary} !important;
        line-height: 1.15;
        letter-spacing: -0.02em;
    }}

    .ds-sub-tag {{
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.16em;
        text-transform: uppercase;
        color: {text_muted} !important;
        margin-top: 3px;
    }}

    /* Smooth animated theme toggle button */
    .ds-theme-toggle {{
        display: flex;
        justify-content: flex-end;
    }}

    .ds-theme-toggle div.stButton > button {{
        border-radius: 24px !important;
        padding: 0.45rem 1.15rem !important;
        font-size: 0.88rem !important;
        font-weight: 700 !important;
        letter-spacing: 0.02em !important;
        border: 1px solid {border_color} !important;
        background-color: {bg_card} !important;
        color: {text_primary} !important;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04) !important;
        transition: all 0.28s cubic-bezier(0.34, 1.56, 0.64, 1) !important;
        cursor: pointer !important;
    }}

    .ds-theme-toggle div.stButton > button:hover {{
        transform: translateY(-2px) scale(1.04) !important;
        border-color: {accent_gold} !important;
        box-shadow: 0 6px 18px rgba(184, 135, 70, 0.25) !important;
        color: {accent_gold} !important;
    }}

    .ds-theme-toggle div.stButton > button:active {{
        transform: translateY(0px) scale(0.97) !important;
        transition: all 0.1s ease !important;
    }}

    /* Left Sidebar: Document Intake */
    .intake-card {{
        background-color: {bg_card};
        border: 1px solid {border_color};
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 0.75rem;
    }}

    .intake-header-row {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.4rem;
        font-size: 0.88rem;
        font-weight: 700;
        color: {text_primary};
    }}

    .chars-counter {{
        font-size: 0.75rem;
        color: {text_muted};
        font-weight: 400;
    }}

    /* Clause Cards */
    .clause-card {{
        background-color: {bg_card};
        border: 1px solid {border_color};
        border-radius: 8px;
        padding: 0.85rem 1rem;
        margin-bottom: 0.65rem;
        box-shadow: 0 1px 2px rgba(0,0,0,0.02);
    }}

    .clause-top-row {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.5rem;
    }}

    .clause-title {{
        font-weight: 700;
        font-size: 0.98rem;
        color: {text_primary};
        display: flex;
        align-items: center;
        gap: 0.45rem;
    }}

    .clause-explanation {{
        font-size: 0.88rem;
        color: {text_primary};
        line-height: 1.5;
        margin-bottom: 0.65rem;
    }}

    .clause-quote-box {{
        background-color: {excerpt_bg};
        border-left: 3px solid {excerpt_border};
        border-radius: 0 4px 4px 0;
        padding: 0.6rem 0.85rem;
        margin-bottom: 0.6rem;
        font-size: 0.83rem;
        color: {text_secondary};
        font-style: italic;
        line-height: 1.45;
    }}

    /* Risk Badges */
    .badge-pill {{
        font-size: 0.68rem;
        font-weight: 700;
        letter-spacing: 0.05em;
        padding: 0.18rem 0.5rem;
        border-radius: 4px;
        text-transform: uppercase;
        display: inline-block;
    }}
    .badge-high {{ background-color: {badge_high_bg}; border: 1px solid {badge_high_border}; color: {badge_high_text}; }}
    .badge-med {{ background-color: {badge_med_bg}; border: 1px solid {badge_med_border}; color: {badge_med_text}; }}
    .badge-low {{ background-color: {badge_low_bg}; border: 1px solid {badge_low_border}; color: {badge_low_text}; }}

    /* Right Chatbot Header Bar */
    .chat-header-bar {{
        display: flex;
        align-items: center;
        gap: 0.65rem;
        padding: 0.45rem 0.85rem;
        background-color: {bg_card};
        border: 1px solid {border_color};
        border-radius: 6px;
        margin-bottom: 0.35rem;
        box-shadow: 0 1px 2px rgba(0,0,0,0.02);
    }}

    .chat-panel-container {{
        background-color: {chat_panel_bg};
        border: 1px solid {border_color};
        border-radius: 8px;
        padding: 0.75rem;
        box-shadow: 0 1px 2px rgba(0,0,0,0.02);
    }}

    .chat-header-row {{
        display: flex;
        align-items: center;
        gap: 0.6rem;
        padding-bottom: 0.45rem;
        border-bottom: 1px solid {border_color};
        margin-bottom: 0.45rem;
    }}

    .chat-avatar {{
        width: 30px;
        height: 30px;
        border-radius: 50%;
        background-color: {accent_gold};
        color: #FFFFFF !important;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.78rem;
        font-weight: 800;
        flex-shrink: 0;
    }}

    .chat-title {{
        font-weight: 700;
        font-size: 0.92rem;
        line-height: 1.15;
        color: {text_primary};
    }}

    .chat-sub {{
        font-size: 0.72rem;
        color: {text_muted};
    }}

    /* Chat Messages: Crisp White Background with clearly visible dark text (NO blue backgrounds) */
    .msg-user {{
        background-color: {chat_user_bg} !important;
        color: {chat_user_text} !important;
        border: 1px solid {border_color} !important;
        border-radius: 7px;
        padding: 0.55rem 0.85rem;
        font-size: 0.86rem;
        margin-bottom: 0.55rem;
        margin-left: 1.2rem;
        text-align: right;
        line-height: 1.4;
        display: block;
        box-shadow: 0 1px 2px rgba(0,0,0,0.02);
    }}

    .msg-ai {{
        background-color: {chat_ai_bg} !important;
        color: {chat_ai_text} !important;
        border: 1px solid {border_color} !important;
        border-radius: 7px;
        padding: 0.65rem 0.85rem;
        font-size: 0.86rem;
        margin-bottom: 0.55rem;
        margin-right: 1.2rem;
        line-height: 1.45;
        display: block;
    }}

    /* Empty State Hero */
    .empty-hero-wrap {{
        text-align: center;
        padding: 3rem 1.5rem;
        max-width: 540px;
        margin: 0 auto;
    }}

    .empty-hero-avatar {{
        width: 56px;
        height: 56px;
        border-radius: 50%;
        background-color: {accent_gold};
        color: #FFFFFF !important;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-size: 1.45rem;
        font-weight: 800;
        margin-bottom: 1.15rem;
    }}

    .empty-hero-title {{
        font-size: 1.25rem;
        font-weight: 700;
        color: {text_primary};
        margin-bottom: 0.45rem;
    }}

    .empty-hero-desc {{
        font-size: 0.88rem;
        color: {text_secondary};
        line-height: 1.6;
    }}

    /* Suggested Question Buttons */
    .sugg-box-title {{
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: {text_muted};
        margin-bottom: 0.35rem;
    }}

    /* Disclaimer Footer */
    .ds-footer {{
        font-size: 0.72rem;
        color: {text_muted};
        padding: 0.25rem 0 0.05rem 0;
        border-top: 1px solid {border_color};
        margin-top: 0.25rem;
        line-height: 1.35;
    }}

    /* Sleek custom scrollbars for all scrollable containers */
    ::-webkit-scrollbar {{
        width: 6px;
        height: 6px;
    }}
    ::-webkit-scrollbar-track {{
        background: transparent;
    }}
    ::-webkit-scrollbar-thumb {{
        background: {border_color};
        border-radius: 4px;
    }}
    ::-webkit-scrollbar-thumb:hover {{
        background: {accent_gold};
    }}

    /* Form styling: borderless clean inline chat bar */
    div[data-testid="stForm"] {{
        border: none !important;
        padding: 0 !important;
        background: transparent !important;
    }}

    /* STRICT OVERRIDE FOR ALL BUTTONS: White backgrounds, clearly visible dark text (NO blue) */
    div.stButton > button {{
        background-color: {bg_card} !important;
        color: {text_primary} !important;
        border: 1px solid {border_color} !important;
        font-weight: 600 !important;
        border-radius: 6px !important;
        box-shadow: 0 1px 2px rgba(0,0,0,0.02) !important;
    }}
    div.stButton > button:hover {{
        background-color: {bg_card_subtle} !important;
        color: {text_primary} !important;
        border-color: {accent_gold} !important;
    }}
    div.stButton > button[kind="primary"],
    button[data-testid="stBaseButton-primary"] {{
        background-color: {accent_gold} !important;
        color: #FFFFFF !important;
        border: 1px solid {accent_gold} !important;
        font-weight: 700 !important;
    }}
    div.stButton > button[kind="primary"]:hover,
    button[data-testid="stBaseButton-primary"]:hover {{
        opacity: 0.92 !important;
    }}

    /* Dedicated styling for Chat Send Button: Always shows 'Send', never cut off as 'se...' */
    div[data-testid="stFormSubmitButton"] {{
        display: flex !important;
        width: 100% !important;
        margin: 0 !important;
    }}
    div[data-testid="stFormSubmitButton"] > button,
    div[data-testid="stFormSubmitButton"] > button[kind="primary"] {{
        background-color: {accent_gold} !important;
        color: #FFFFFF !important;
        border: 1px solid {accent_gold} !important;
        font-weight: 700 !important;
        width: 100% !important;
        min-width: 68px !important;
        padding: 0.45rem 0.6rem !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        white-space: nowrap !important;
        overflow: visible !important;
        text-overflow: clip !important;
        border-radius: 6px !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05) !important;
        transition: opacity 0.15s ease !important;
    }}
    div[data-testid="stFormSubmitButton"] > button:hover {{
        opacity: 0.92 !important;
        background-color: {accent_gold} !important;
        color: #FFFFFF !important;
        border-color: {accent_gold} !important;
    }}
    div[data-testid="stFormSubmitButton"] > button *,
    div[data-testid="stFormSubmitButton"] > button p,
    div[data-testid="stFormSubmitButton"] > button span,
    div[data-testid="stFormSubmitButton"] > button div {{
        white-space: nowrap !important;
        overflow: visible !important;
        text-overflow: clip !important;
        color: #FFFFFF !important;
        font-size: 0.88rem !important;
        font-weight: 700 !important;
        letter-spacing: 0.01em !important;
        margin: 0 !important;
        padding: 0 !important;
    }}

    /* Input & Textarea Overrides: White background with clearly visible dark text */
    div[data-testid="stTextArea"] textarea, div[data-testid="stTextInput"] input {{
        background-color: {bg_card} !important;
        color: {text_primary} !important;
        border: 1px solid {border_color} !important;
        font-size: 0.88rem !important;
        border-radius: 6px !important;
    }}

    /* File Uploader Overrides: White background with clearly visible dark text (NO blue) */
    div[data-testid="stFileUploader"] section {{
        background-color: {bg_card} !important;
        border: 1px dashed {border_color} !important;
        border-radius: 6px !important;
        padding: 0.65rem 0.85rem !important;
    }}
    div[data-testid="stFileUploader"] section > div {{
        padding: 0 !important;
        gap: 0.25rem !important;
    }}
    div[data-testid="stFileUploader"] section button {{
        background-color: {bg_card_subtle} !important;
        color: {text_primary} !important;
        border: 1px solid {border_color} !important;
    }}
    div[data-testid="stFileUploader"] * {{
        color: {text_primary} !important;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)


# -----------------------------------------------------------------------------
# TOP APPLICATION BAR (AT THE VERY TOP & FULLY VISIBLE)
# -----------------------------------------------------------------------------
top_c1, top_c2 = st.columns([10, 1.8], vertical_alignment="center")

with top_c1:
    st.markdown(
        """
        <div class="ds-topbar" style="border-bottom:none; margin-bottom:0; padding-bottom:0; padding-top:0;">
            <div class="ds-brand-left">
                <div class="ds-avatar-logo">DS</div>
                <div>
                    <div class="ds-title-text">DigiScan</div>
                    <div class="ds-sub-tag">READ BEFORE YOU SIGN</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with top_c2:
    st.markdown('<div class="ds-theme-toggle">', unsafe_allow_html=True)
    theme_label = "🌙 Dark" if st.session_state.theme == "light" else "☀ Light"
    if st.button(theme_label, key="theme_toggle_btn", use_container_width=True, help="Toggle Light / Dark mode"):
        st.session_state.theme = "dark" if st.session_state.theme == "light" else "light"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown(f"<div style='border-bottom: 1px solid {border_color}; margin-bottom: 0.35rem; margin-top: 0.1rem;'></div>", unsafe_allow_html=True)


# (Chat question handling is executed interactively within the right-hand chat panel with live feedback)


# -----------------------------------------------------------------------------
# MAIN 3-COLUMN WORKSPACE:
# LEFT (26%): Document Intake & History
# CENTER (45%): Risky Clauses Analysis
# RIGHT (29%): Ask the Document Chatbot
# -----------------------------------------------------------------------------
has_doc = bool(st.session_state.document_text and st.session_state.analysis_data)

if has_doc:
    col_left, col_center, col_right = st.columns([26, 45, 29], gap="medium")
else:
    col_left, col_main = st.columns([28, 72], gap="large")


# =============================================================================
# LEFT PANEL: DOCUMENT INTAKE & HISTORY
# =============================================================================
with col_left:
    char_len = len(st.session_state.document_text) if st.session_state.document_text else 0

    st.markdown(
        f"""
        <div class="intake-header-row">
            <div>📄 Document intake</div>
            <div class="chars-counter">{char_len:,} / 25,000 chars</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 1. HISTORY DRAWER
    all_history = database.get_all_history()
    history_count = len(all_history)

    with st.expander(f"🗂 History ({history_count})", expanded=st.session_state.history_open):
        if not all_history:
            st.caption("No previously analyzed documents.")
        else:
            h_box = st.container(height=160) if history_count > 3 else st.container()
            with h_box:
                for item in all_history:
                    h_name = item["document_name"]
                    h_id = item["id"]
                    
                    h_c1, h_c2 = st.columns([4, 1])
                    with h_c1:
                        if st.button(f"📄 {h_name[:20]}", key=f"load_h_{h_id}", use_container_width=True):
                            rec = database.get_history_by_id(h_id)
                            if rec:
                                st.session_state.active_doc_id = rec["id"]
                                st.session_state.document_name = rec["document_name"]
                                st.session_state.document_text = rec["document_text"]
                                st.session_state.analyzed_at = rec["analyzed_at"]
                                st.session_state.analysis_data = rec["analysis_data"]
                                st.session_state.chat_history = rec["chat_history"]
                                st.session_state.history_open = False
                                st.rerun()
                    with h_c2:
                        if st.button("✕", key=f"del_h_{h_id}", help="Delete item"):
                            database.delete_history_item(h_id)
                            st.rerun()

    # 2. UPLOAD FILE BOX (PDF, DOCX, TXT)
    st.caption("Upload contract (.pdf, .docx, .txt)")
    uploaded_file = st.file_uploader(
        "Upload file",
        type=["pdf", "docx", "doc", "txt"],
        label_visibility="collapsed",
        key="intake_file_uploader",
    )

    # 3. PASTE RAW TEXT BOX
    pasted_text = st.text_area(
        "Or paste raw text",
        height=110,
        placeholder="Or paste the raw text of your contract here...",
        label_visibility="collapsed",
        key="intake_pasted_text",
    )

    # 4. ANALYZE BUTTON & ACTIVE STATUS
    if has_doc:
        st.markdown(
            f"""
            <div style="font-size:0.8rem; color:{accent_gold}; font-weight:700; margin-bottom:0.5rem;">
                ✓ Loaded: {st.session_state.document_name}
            </div>
            """,
            unsafe_allow_html=True,
        )
        c_an_btn, c_clr_btn = st.columns([2, 1])
        with c_an_btn:
            trigger_new_analysis = st.button("🔍 Re-analyze", use_container_width=True)
        with c_clr_btn:
            if st.button("Clear", use_container_width=True):
                st.session_state.document_text = ""
                st.session_state.document_name = ""
                st.session_state.analysis_data = None
                st.session_state.chat_history = []
                st.session_state.active_doc_id = None
                st.rerun()
    else:
        trigger_new_analysis = st.button("🔍 Analyze document", type="primary", use_container_width=True)

    if trigger_new_analysis:
        if uploaded_file is None and (not pasted_text or not pasted_text.strip()):
            st.warning("Please upload a document or paste contract text on the left.")
        else:
            with st.status("Analyzing document...", expanded=True) as status_box:
                st.write("Extracting clauses and text...")
                processed = document_processor.process_document_source(uploaded_file, pasted_text)

                if not processed.get("success"):
                    status_box.update(label="Document parsing failed", state="error")
                    st.error(processed.get("error", "Failed to parse document."))
                else:
                    st.write("Reviewing legal risks and obligations...")
                    doc_text = processed["text"]
                    doc_name = processed["source_name"]

                    struct_res = ai.analyze_document_structured(doc_text)
                    if not struct_res.get("success"):
                        status_box.update(label="Analysis failed", state="error")
                        st.error(struct_res.get("error", "Error connecting to AI engine."))
                    else:
                        status_box.update(label="Analysis complete", state="complete")
                        analysis_data = struct_res["data"]
                        now_str = datetime.now().strftime("%B %d, %Y • %I:%M %p")

                        doc_id = database.save_history(
                            document_name=doc_name,
                            document_text=doc_text,
                            analysis_data=analysis_data,
                            chat_history=[],
                        )

                        st.session_state.active_doc_id = doc_id
                        st.session_state.document_name = doc_name
                        st.session_state.document_text = doc_text
                        st.session_state.analyzed_at = now_str
                        st.session_state.analysis_data = analysis_data
                        st.session_state.chat_history = []
                        st.rerun()


# =============================================================================
# CENTER AREA: ANALYSIS & RISKY CLAUSES (OR HERO WHEN EMPTY)
# =============================================================================
if not has_doc:
    with col_main:
        st.markdown(
            f"""
            <div class="empty-hero-wrap">
                <div class="empty-hero-avatar">DS</div>
                <div class="empty-hero-title">Upload or paste a document on the left to analyze.</div>
                <div class="empty-hero-desc">
                    DigiScan reads the sections and returns a plain-English summary, alongside every clause worth a second look.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

else:
    with col_center:
        analysis = st.session_state.analysis_data or {}
        clauses = analysis.get("clauses", [])
        summary_pts = analysis.get("summary_points", [])

        # 1. Plain-English Summary Banner
        if summary_pts:
            top_pt = summary_pts[0].get("text", "") if isinstance(summary_pts[0], dict) else str(summary_pts[0])
            st.markdown(
                f"""
                <div style="background-color:{bg_card}; border:1px solid {border_color}; border-radius:6px; padding:0.45rem 0.85rem; margin-bottom:0.35rem; font-size:0.85rem; color:{text_primary}; display:flex; align-items:center; gap:0.6rem;">
                    <span style="display:inline-block; width:8px; height:8px; border-radius:50%; background-color:{accent_gold}; flex-shrink:0;"></span>
                    <div>{top_pt}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # 2. Section Header: RISKY CLAUSES
        flagged_count = len(clauses)
        st.markdown(
            f"""
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.35rem;">
                <div style="font-size:0.76rem; font-weight:700; letter-spacing:0.08em; text-transform:uppercase; color:{text_muted};">
                    Risky Clauses
                </div>
                <div style="font-size:0.75rem; font-weight:700; color:{accent_gold};">
                    {flagged_count} flagged
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # 3. Clause Cards Stream: Independent scrollable container (Middle scrolls independently)
        clauses_box = st.container(height=415, border=False)
        with clauses_box:
            if not clauses:
                st.markdown(
                    f"""
                    <div class="clause-card" style="color:{text_secondary}; font-size:0.88rem;">
                        No risky clauses identified in this document.
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                for c_idx, cl in enumerate(clauses):
                    title = cl.get("title", "Contractual Term")
                    risk_lvl = (cl.get("risk_level", "MEDIUM RISK")).upper()
                    explanation = cl.get("explanation", "")
                    excerpt = cl.get("excerpt", "")
                    suggested_q = cl.get("suggested_question", f"Can you explain the {title} clause in detail?")

                    # Badge classification
                    if "HIGH" in risk_lvl:
                        badge_cls = "badge-high"
                        icon_sym = "⚠"
                    elif "MED" in risk_lvl:
                        badge_cls = "badge-med"
                        icon_sym = "△"
                    else:
                        badge_cls = "badge-low"
                        icon_sym = "✓"

                    st.markdown(
                        f"""
                        <div class="clause-card">
                            <div class="clause-top-row">
                                <div class="clause-title">
                                    <span>{icon_sym}</span>
                                    <span>{title}</span>
                                </div>
                                <span class="badge-pill {badge_cls}">{risk_lvl}</span>
                            </div>
                            <div class="clause-explanation">
                                {explanation}
                            </div>
                            <div class="clause-quote-box">
                                "{excerpt}"
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                    # Card Actions: [ View in document ] & [ Ask about this ]
                    act_c1, act_c2 = st.columns([1, 1])
                    with act_c1:
                        with st.expander("▸ View in document", expanded=False):
                            st.caption(st.session_state.document_text[:1200] + "...")
                    with act_c2:
                        if st.button("💬 Ask about this", key=f"ask_btn_{c_idx}", use_container_width=True):
                            st.session_state.pending_question = suggested_q
                            st.rerun()


    # =========================================================================
    # RIGHT PANEL: ASK THE DOCUMENT CHATBOT
    # =========================================================================
    with col_right:
        st.markdown(
            f"""
            <div class="chat-header-bar">
                <div class="chat-avatar">DS</div>
                <div style="flex-grow: 1;">
                    <div class="chat-title">Ask the document</div>
                    <div class="chat-sub">Grounded strictly in the text you provided</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Chat Body
        has_chat = bool(st.session_state.chat_history or st.session_state.pending_question)

        if not has_chat:
            chat_box = st.container(height=360)
            with chat_box:
                st.markdown(
                    f"""
                    <div style="text-align:center; padding: 0.65rem 0.5rem 0.35rem 0.5rem;">
                        <div style="font-weight:700; font-size:0.92rem; color:{text_primary}; margin-bottom:0.25rem;">
                            Ask anything about this document
                        </div>
                        <div style="font-size:0.78rem; color:{text_secondary}; line-height:1.4;">
                            All answers are grounded strictly in the document text—no guessing.
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                # SUGGESTED QUESTIONS
                st.markdown("<div class='sugg-box-title' style='margin-bottom:0.35rem;'>✦ Suggested Questions</div>", unsafe_allow_html=True)

                suggested_list = (st.session_state.analysis_data or {}).get("suggested_questions", [
                    "What is the cancellation policy?",
                    "What happens to my data after termination?",
                    "What is the maximum liability cap?",
                    "Where and how are legal disputes resolved?"
                ])

                for sq_idx, sq_txt in enumerate(suggested_list[:4]):
                    if st.button(sq_txt, key=f"sq_pill_{sq_idx}", use_container_width=True):
                        st.session_state.pending_question = sq_txt
                        st.rerun()

        else:
            # Scrollable message history
            chat_box = st.container(height=360)
            with chat_box:
                for msg in st.session_state.chat_history:
                    if msg["role"] == "user":
                        st.markdown(
                            f"""
                            <div class="msg-user">
                                {msg['content']}
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                    else:
                        st.markdown(
                            f"""
                            <div class="msg-ai">
                                {msg['content']}
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                # Process pending question inline with live feedback
                if st.session_state.pending_question:
                    current_q = st.session_state.pending_question
                    st.markdown(
                        f"""
                        <div class="msg-user">
                            {current_q}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    with st.spinner("DigiScan is analyzing document..."):
                        chat_res = ai.chat_with_document(
                            document_text=st.session_state.document_text,
                            chat_history=st.session_state.chat_history,
                            user_message=current_q,
                        )

                    st.session_state.chat_history.append({"role": "user", "content": current_q})
                    if chat_res.get("success"):
                        st.session_state.chat_history.append({"role": "assistant", "content": chat_res["content"]})
                        if st.session_state.active_doc_id:
                            database.update_history_chat(st.session_state.active_doc_id, st.session_state.chat_history)
                    else:
                        err_msg = chat_res.get("error", "Unable to generate response.")
                        st.session_state.chat_history.append({"role": "assistant", "content": f"⚠️ {err_msg}"})

                    st.session_state.pending_question = None
                    st.rerun()

        # Chat Input Bar: Clean inline form with Send button
        with st.form("chat_input_bar_form", clear_on_submit=True):
            in_col, btn_col = st.columns([72, 28], vertical_alignment="center")
            with in_col:
                user_msg = st.text_input(
                    "Ask a question...",
                    placeholder="Ask a question...",
                    label_visibility="collapsed",
                    key="chat_msg_input",
                )
            with btn_col:
                send_pressed = st.form_submit_button("Send", type="primary", use_container_width=True)

        if send_pressed and user_msg and user_msg.strip():
            st.session_state.pending_question = user_msg.strip()
            st.rerun()

        st.markdown(
            f"""
            <div style="font-size:0.7rem; color:{text_muted}; text-align:center; margin-top:0.2rem;">
                Press Enter to send &bull; Answers strictly grounded in document
            </div>
            """,
            unsafe_allow_html=True,
        )


# -----------------------------------------------------------------------------
# APPLICATION FOOTER DISCLAIMER
# -----------------------------------------------------------------------------
st.markdown(
    """
    <div class="ds-footer">
        ⓘ <b>Disclaimer:</b> This tool is for educational purposes and does not provide legal advice. AI summaries can miss clauses, misinterpret context, or misjudge risk. Always consult a qualified attorney before signing or relying on any legal agreement.
    </div>
    """,
    unsafe_allow_html=True,
)
