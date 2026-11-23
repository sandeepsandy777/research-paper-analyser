"""
AI Research Paper Assistant – Chat with PDF
================================================================================
A college-level, AI-powered web application that allows students to upload
academic research papers in PDF format and ask questions about their content.
Powered by Streamlit, Google Gemini API (official google-genai SDK), and pypdf.

Key Capabilities:
- Robust multi-page PDF text extraction with pypdf
- Error-resilient parsing (empty files, scanned PDFs, corrupted files)
- Strict grounded answering with Google Gemini API (no hallucination)
- If information is absent, responds: "This is not mentioned in the paper."
- Student-friendly explanations with structured formatting
- Complete chat history with Clear Chat and auto-reset on new upload
- Modern UI/UX with refreshed light-blue / white / purple gradients
- 100% Backend API key management via Streamlit secrets
- Ultra-fast responses with Google Gemini 3.1 Flash-Lite & 3.5 Flash engines
================================================================================
"""

import io
import os
import hashlib
import time
from typing import Dict, Any, List, Optional
import streamlit as st
from pypdf import PdfReader

# Attempt official google-genai SDK import
try:
    from google import genai
    from google.genai import types
    from google.genai.errors import APIError
    GENAI_SDK_AVAILABLE = True
except ImportError:
    GENAI_SDK_AVAILABLE = False
    genai = None
    types = None
    APIError = Exception


# ==============================================================================
# 1. UI THEME STYLING CONSTANTS (Refreshed Color Palette)
# ==============================================================================
CUSTOM_CSS = """
<style>
    /* Global App Background: Clean Modern Light-Blue to Soft-Indigo Gradient */
    .stApp {
        background: linear-gradient(135deg, #F0F6FF 0%, #E6F0FA 35%, #EEF2FF 70%, #F5F3FF 100%) !important;
        background-attachment: fixed !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif !important;
    }

    /* Force High-Contrast Readable Text Across Entire App (Prevents Invisible Text in Dark Mode) */
    .stApp, .stApp p, .stApp span, .stApp label, .stApp li {
        color: #0F172A !important;
    }
    
    /* Headings */
    h1, h2, h3, h4, h5, h6 {
        color: #0F172A !important;
        font-weight: 700 !important;
    }

    /* Main Container Padding */
    .main .block-container {
        padding-top: 1.8rem;
        padding-bottom: 3.5rem;
        max-width: 1050px;
    }

    /* Header Banner styling */
    .hero-container {
        background: linear-gradient(135deg, #1E40AF 0%, #2563EB 35%, #4F46E5 70%, #7C3AED 100%) !important;
        padding: 2.2rem 2.6rem;
        border-radius: 20px;
        margin-bottom: 1.8rem;
        box-shadow: 0 12px 28px -6px rgba(37, 99, 235, 0.35);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    .hero-container, .hero-container h1, .hero-container p, .hero-container span {
        color: #FFFFFF !important;
    }
    .hero-badge {
        display: inline-block;
        background: rgba(255, 255, 255, 0.22);
        backdrop-filter: blur(10px);
        padding: 0.35rem 0.9rem;
        border-radius: 50px;
        font-size: 0.8rem;
        font-weight: 700;
        letter-spacing: 0.6px;
        text-transform: uppercase;
        margin-bottom: 0.75rem;
        border: 1px solid rgba(255, 255, 255, 0.3);
        color: #FFFFFF !important;
    }
    .hero-title {
        font-size: 2.2rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: -0.5px;
        color: #FFFFFF !important;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.15);
    }
    .hero-subtitle {
        font-size: 1.05rem;
        margin-top: 0.5rem;
        margin-bottom: 0;
        color: #E0E7FF !important;
        font-weight: 400;
        line-height: 1.4;
    }

    /* Chat Messages: Pure Crisp Visibility */
    [data-testid="stChatMessage"] {
        background-color: #FFFFFF !important;
        border: 1px solid #CBD5E1 !important;
        border-radius: 14px !important;
        padding: 1.1rem 1.3rem !important;
        margin-bottom: 0.9rem !important;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.05) !important;
    }
    [data-testid="stChatMessage"] * {
        color: #0F172A !important;
    }
    [data-testid="stChatMessage"] strong {
        color: #1E3A8A !important;
        font-weight: 700 !important;
    }
    [data-testid="stChatMessage"] code {
        background-color: #F1F5F9 !important;
        color: #1E40AF !important;
        padding: 0.2rem 0.45rem !important;
        border-radius: 5px !important;
        font-weight: 600 !important;
    }

    /* Chat Input Area */
    [data-testid="stChatInput"] {
        background-color: transparent !important;
    }
    [data-testid="stChatInput"] textarea {
        background-color: #FFFFFF !important;
        color: #0F172A !important;
        border: 1.5px solid #94A3B8 !important;
        border-radius: 12px !important;
        font-size: 1rem !important;
    }
    [data-testid="stChatInput"] textarea::placeholder {
        color: #64748B !important;
    }

    /* Document Metadata Card */
    .doc-card {
        background: #FFFFFF !important;
        border: 1px solid #BFDBFE !important;
        border-radius: 16px !important;
        padding: 1.25rem !important;
        margin-bottom: 1.5rem !important;
        box-shadow: 0 8px 20px rgba(37, 99, 235, 0.08) !important;
    }
    .doc-card, .doc-card * {
        color: #0F172A !important;
    }
    .doc-card-title {
        font-weight: 700 !important;
        color: #1E3A8A !important;
        font-size: 0.95rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin-bottom: 0.75rem;
    }
    .stat-pill {
        background: #EFF6FF !important;
        border: 1px solid #BFDBFE !important;
        border-radius: 8px;
        padding: 0.4rem 0.65rem;
        font-size: 0.82rem;
        color: #1D4ED8 !important;
        font-weight: 600;
        display: inline-block;
        margin-right: 0.4rem;
        margin-bottom: 0.4rem;
    }

    /* Welcome / Getting Started Card */
    .welcome-card {
        background: #FFFFFF !important;
        border: 1px solid #DBEAFE !important;
        border-radius: 18px !important;
        padding: 2.5rem !important;
        text-align: center;
        margin: 2rem 0;
        box-shadow: 0 10px 30px rgba(37, 99, 235, 0.07);
    }
    .welcome-icon {
        font-size: 3.8rem;
        margin-bottom: 1rem;
    }
    .welcome-title {
        font-size: 1.5rem;
        font-weight: 800;
        color: #1E293B !important;
        margin-bottom: 0.5rem;
    }
    .welcome-desc {
        color: #475569 !important;
        font-size: 0.98rem;
        max-width: 620px;
        margin: 0 auto 1.5rem auto;
        line-height: 1.6;
    }

    /* Feature Highlights in Cards */
    .feature-card {
        background: #FFFFFF !important;
        border: 1px solid #CBD5E1 !important;
        border-radius: 14px !important;
        padding: 1.25rem !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
        height: 100%;
        transition: transform 0.2s ease;
    }
    .feature-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 18px rgba(37, 99, 235, 0.12);
        border-color: #3B82F6 !important;
    }
    .feature-card h4 {
        color: #1E3A8A !important;
        margin: 0 0 0.5rem 0;
    }
    .feature-card p {
        color: #475569 !important;
        font-size: 0.88rem;
        margin: 0;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background: #FFFFFF !important;
        border-right: 1px solid #E2E8F0 !important;
    }
    section[data-testid="stSidebar"] * {
        color: #1E293B !important;
    }
    .sidebar-header {
        font-size: 1.2rem;
        font-weight: 800;
        color: #1E3A8A !important;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin-bottom: 0.5rem;
    }

    /* Status Badges */
    .badge-backend {
        background-color: #ECFDF5 !important;
        color: #065F46 !important;
        border: 1px solid #A7F3D0 !important;
        padding: 0.35rem 0.75rem;
        border-radius: 8px;
        font-size: 0.82rem;
        font-weight: 700;
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
    }
    .badge-warning {
        background-color: #FEF3C7 !important;
        color: #92400E !important;
        border: 1px solid #FDE68A !important;
        padding: 0.35rem 0.75rem;
        border-radius: 8px;
        font-size: 0.82rem;
        font-weight: 700;
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
    }

    /* Button styling */
    div.stButton > button {
        border-radius: 10px !important;
        font-weight: 600 !important;
        color: #1E293B !important;
        background-color: #FFFFFF !important;
        border: 1.5px solid #CBD5E1 !important;
        transition: all 0.2s ease-in-out;
    }
    div.stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.18);
        border-color: #2563EB !important;
        color: #1D4ED8 !important;
    }
</style>
"""

# ==============================================================================
# 2. SYSTEM INSTRUCTION PROMPT
# ==============================================================================
SYSTEM_PROMPT = """You are an expert AI Research Paper Assistant dedicated to helping college students understand academic research papers.

CRITICAL OPERATIONAL RULES:
1. Answer the student's question STRICTLY and EXCLUSIVELY using the provided research paper content.
2. Do NOT invent, assume, extrapolate, or bring in external knowledge not present in the paper.
3. If the answer is not mentioned, not addressed, or cannot be directly proven from the paper content, you MUST respond with the EXACT sentence:
"This is not mentioned in the paper."
Do NOT add apologies, do not provide external facts, and do not elaborate if the topic is absent.
4. When information IS present in the paper:
   - Explain technical concepts in simple, clear, student-friendly English.
   - Organize your response with clear markdown headings (###), bullet points, and bold terms for readability.
   - When applicable, mention the page number reference (e.g., [Page 3]) indicated in the paper text.
"""


# ==============================================================================
# 3. PDF TEXT EXTRACTION (ROBUST & RESILIENT)
# ==============================================================================
def extract_text_from_pdf(pdf_bytes: bytes, filename: str) -> Dict[str, Any]:
    """
    Extracts readable text from an uploaded PDF using pypdf.
    Handles:
      - Empty (0-byte) files
      - Corrupted / damaged PDF headers
      - Password-protected PDFs
      - Scanned / image-only PDFs with no extractable text
      - Multi-page documents with page delimiter tags
    Returns a dictionary with status, extracted text, and document metrics.
    """
    print(f"[PDF Extraction] Starting extraction for '{filename}' ({len(pdf_bytes):,} bytes)")

    result = {
        "success": False,
        "error": None,
        "text": "",
        "page_count": 0,
        "word_count": 0,
        "char_count": 0,
        "filename": filename,
        "is_scanned": False
    }

    # 1. Check for empty file
    if not pdf_bytes or len(pdf_bytes) == 0:
        result["error"] = "The uploaded file is empty (0 bytes). Please upload a valid PDF document."
        print(f"[PDF Extraction Error] File is empty (0 bytes)")
        return result

    # 2. Initialize PDF Reader safely
    try:
        stream = io.BytesIO(pdf_bytes)
        reader = PdfReader(stream)
    except Exception as exc:
        result["error"] = f"Unable to parse '{filename}'. The file appears corrupted or is not a valid PDF. Error details: {str(exc)}"
        print(f"[PDF Extraction Error] Corrupted: {exc}")
        return result

    # 3. Handle password protection / encryption
    if reader.is_encrypted:
        try:
            decrypted = reader.decrypt("")
            if not decrypted:
                result["error"] = f"The PDF '{filename}' is password protected. Please remove the password and re-upload."
                print(f"[PDF Extraction Error] Password protected")
                return result
        except Exception:
            result["error"] = f"The PDF '{filename}' is encrypted and cannot be read without a password."
            return result

    # 4. Check for pages
    total_pages = len(reader.pages)
    if total_pages == 0:
        result["error"] = f"The PDF '{filename}' has 0 pages."
        print(f"[PDF Extraction Error] 0 pages found")
        return result

    result["page_count"] = total_pages

    # 5. Extract text from each page
    extracted_sections = []
    total_chars = 0

    for idx, page in enumerate(reader.pages):
        page_num = idx + 1
        try:
            page_raw_text = page.extract_text() or ""
            cleaned = page_raw_text.strip()
            if cleaned:
                extracted_sections.append(f"--- [Page {page_num}] ---\n{cleaned}")
                total_chars += len(cleaned)
            else:
                extracted_sections.append(f"--- [Page {page_num}] ---\n(No extractable text on this page)")
        except Exception as page_err:
            extracted_sections.append(f"--- [Page {page_num}] ---\n(Error extracting text: {str(page_err)})")

    full_text = "\n\n".join(extracted_sections).strip()
    words = len(full_text.split())

    result["char_count"] = total_chars
    result["word_count"] = words

    # 6. Scanned PDF detection (very few characters across the document)
    if total_chars < 60 or words < 15:
        result["is_scanned"] = True
        result["error"] = (
            f"No readable text could be extracted from '{filename}'. "
            "This document appears to be a scanned image or contains non-selectable text. "
            "Please upload a digital PDF containing selectable text."
        )
        print(f"[PDF Extraction Warning] Document appears scanned ({total_chars} chars, {words} words)")
        return result

    result["success"] = True
    result["text"] = full_text
    print(f"[PDF Extraction Success] Extracted {total_pages} pages, {words:,} words, {total_chars:,} characters.")
    return result


# ==============================================================================
# 4. API KEY CONFIGURATION (100% BACKEND RESOLUTION)
# ==============================================================================
def get_gemini_api_key() -> Optional[str]:
    """
    Safely retrieves the Gemini API key strictly from the backend.
    Loading priority:
      1. Streamlit secrets (.streamlit/secrets.toml)
      2. Environment variable (GEMINI_API_KEY / GOOGLE_API_KEY)
    Never exposes or displays the key on screen.
    """
    # 1. Try Streamlit Secrets
    try:
        if "GEMINI_API_KEY" in st.secrets and st.secrets["GEMINI_API_KEY"]:
            return str(st.secrets["GEMINI_API_KEY"]).strip()
        if "GOOGLE_API_KEY" in st.secrets and st.secrets["GOOGLE_API_KEY"]:
            return str(st.secrets["GOOGLE_API_KEY"]).strip()
    except Exception:
        pass

    # 2. Try Environment Variable
    env_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if env_key and env_key.strip():
        return env_key.strip()

    # 3. Fallback to manual session entry if needed
    return st.session_state.get("backend_fallback_key", None)


# ==============================================================================
# 5. GOOGLE GEMINI AI ENGINE (OFFICIAL google-genai SDK)
# ==============================================================================
def query_gemini_ai(
    api_key: str,
    paper_text: str,
    chat_history: List[Dict[str, str]],
    user_question: str
) -> str:
    """
    Communicates with the Google Gemini API using the official google-genai SDK.
    Enforces strict context adherence, empty context guard, and graceful error handling.
    """
    if not GENAI_SDK_AVAILABLE:
        return (
            "⚠️ The official `google-genai` SDK is not installed or could not be loaded. "
            "Please run: `pip install google-genai`"
        )

    # Empty Context Guard
    if not paper_text or not paper_text.strip():
        return (
            "⚠️ **Empty Context Error**: No readable text was found in the uploaded research paper. "
            "Please make sure the uploaded PDF has selectable text and is not an empty or scanned document."
        )

    # Compile recent conversation history for conversational context (last 6 turns)
    recent_history = chat_history[-6:] if len(chat_history) > 6 else chat_history
    history_str = ""
    for msg in recent_history:
        speaker = "Student" if msg["role"] == "user" else "Assistant"
        history_str += f"{speaker}: {msg['content']}\n\n"

    # Construct the grounded prompt
    prompt_payload = f"""=== EXTRACTED RESEARCH PAPER CONTENT ===
{paper_text}
=== END OF RESEARCH PAPER CONTENT ===

CONVERSATION HISTORY (Previous Questions & Answers):
{history_str if history_str else "No prior questions asked."}

STUDENT QUESTION:
{user_question}

INSTRUCTIONS REMINDER:
Answer strictly based on the research paper content above. If the answer is not found in the paper, respond EXACTLY:
"This is not mentioned in the paper."
"""

    # List of candidate models in preference order (fast modern 3.x models)
    candidate_models = [
        "gemini-3.1-flash-lite",
        "gemini-3.5-flash-lite",
        "gemini-3.5-flash",
        "gemini-3.8-flash",
    ]
    last_error = None

    try:
        client = genai.Client(api_key=api_key)

        for model_name in candidate_models:
            try:
                t0 = time.time()
                print(f"[Gemini Query] Attempting model: {model_name}...")
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt_payload,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_PROMPT,
                        temperature=0.2,  # Low temperature ensures high factual adherence
                    )
                )

                elapsed = round(time.time() - t0, 2)
                if response and response.text:
                    print(f"[Gemini Query Success] Model {model_name} responded in {elapsed}s.")
                    return response.text.strip()
                elif response and response.candidates:
                    print(f"[Gemini Query Success] Model {model_name} candidate fallback responded in {elapsed}s.")
                    return response.candidates[0].content.parts[0].text.strip()

            except Exception as model_err:
                last_error = model_err
                error_msg = str(model_err).lower()
                print(f"[Gemini Query Model Failed] {model_name}: {model_err}")

                # If authentication failed, do not retry other models
                if "api_key" in error_msg or "unauthenticated" in error_msg or "401" in error_msg or "403" in error_msg:
                    return (
                        "❌ **Invalid Gemini API Key**: The provided API key was rejected by Google AI. "
                        "Please verify your API key in `.streamlit/secrets.toml`."
                    )

                # If quota/rate limit error, report immediately
                if "429" in error_msg or "resource_exhausted" in error_msg or "quota" in error_msg:
                    return (
                        "⏳ **Gemini API Rate Limit / Quota Exceeded**: You have reached the rate limit for requests. "
                        "Please wait a few moments before submitting your next question."
                    )

                # Otherwise, continue to try fallback model
                continue

        # If all candidate models failed
        return f"⚠️ **Gemini API Error**: Could not generate an answer. Details: {str(last_error)}"

    except Exception as exc:
        err_str = str(exc).lower()
        print(f"[Gemini Query Fatal Error] {exc}")
        if "connection" in err_str or "timeout" in err_str or "dns" in err_str:
            return "📡 **Connection Error**: Unable to reach Google Gemini API servers. Please check your internet connection."
        return f"⚠️ **Unexpected Error**: {str(exc)}"


# ==============================================================================
# 6. MAIN APPLICATION ENTRYPOINT
# ==============================================================================
def main():
    """Main function executing the Streamlit application workflow."""
    # Configure page settings
    st.set_page_config(
        page_title="AI Research Paper Assistant",
        page_icon="📄",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Inject visual styling
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

    # Initialize Session State
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "current_file_hash" not in st.session_state:
        st.session_state.current_file_hash = None
    if "doc_data" not in st.session_state:
        st.session_state.doc_data = None
    if "active_prompt" not in st.session_state:
        st.session_state.active_prompt = None

    # --- SIDEBAR RENDERING ---
    with st.sidebar:
        st.markdown("""
        <div class="sidebar-header">
            <span style="font-size: 1.6rem;">📄</span>
            <span>AI Paper Assistant</span>
        </div>
        """, unsafe_allow_html=True)

        st.caption("College B.Tech AI Assignment • Chat with PDF")
        st.divider()

        # Backend API Key Status
        api_key = get_gemini_api_key()
        st.markdown("#### 🔒 Backend Configuration")

        if api_key:
            st.markdown(
                '<div class="badge-backend">🛡️ Backend Key: Active & Secured</div>',
                unsafe_allow_html=True
            )
            st.caption("Configured via backend secrets (`.streamlit/secrets.toml`).")
        else:
            st.markdown(
                '<div class="badge-warning">⚠️ Backend Key Missing</div>',
                unsafe_allow_html=True
            )
            with st.expander("Configure API Key", expanded=True):
                st.info("Add your Gemini API key to `.streamlit/secrets.toml` or enter below:")
                k_input = st.text_input("Gemini API Key:", type="password", key="manual_k")
                if k_input:
                    st.session_state.backend_fallback_key = k_input.strip()
                    st.rerun()

        st.divider()

        # PDF Upload Section
        st.markdown("#### 📂 Upload Research Paper")
        uploaded_file = st.file_uploader(
            "Choose a PDF file",
            type=["pdf"],
            help="Upload an academic research paper in PDF format (multi-page supported)."
        )

        # Process uploaded file (Ensures extraction runs on new upload or if doc_data is missing)
        if uploaded_file is not None:
            file_bytes = uploaded_file.getvalue()
            file_hash = hashlib.sha256(file_bytes).hexdigest()

            # Detect new PDF upload or state recovery
            if st.session_state.doc_data is None or st.session_state.current_file_hash != file_hash:
                st.session_state.current_file_hash = file_hash
                st.session_state.messages = []
                extraction_result = extract_text_from_pdf(file_bytes, uploaded_file.name)
                st.session_state.doc_data = extraction_result

                if extraction_result["success"]:
                    st.toast(f"📄 '{uploaded_file.name}' processed successfully!", icon="✅")
                else:
                    st.toast("Failed to extract text from PDF.", icon="⚠️")

        # Document Metrics Card
        if st.session_state.doc_data and st.session_state.doc_data.get("success"):
            doc = st.session_state.doc_data
            st.markdown(f"""
            <div class="doc-card">
                <div class="doc-card-title">
                    <span>📑</span>
                    <span>Active Document</span>
                </div>
                <div style="font-weight: 700; font-size: 0.9rem; color: #1E293B; word-break: break-all; margin-bottom: 0.6rem;">
                    {doc["filename"]}
                </div>
                <div>
                    <span class="stat-pill">📄 {doc["page_count"]} Pages</span>
                    <span class="stat-pill">📝 {doc["word_count"]:,} Words</span>
                    <span class="stat-pill">🔤 {doc["char_count"]:,} Chars</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Clear Chat Button
        if st.session_state.messages:
            if st.button("🗑️ Clear Chat History", use_container_width=True, type="secondary"):
                st.session_state.messages = []
                st.rerun()

        st.divider()

        # User Guide
        with st.expander("ℹ️ How to Use This App", expanded=False):
            st.markdown("""
            1. **Backend Key**: Gemini API key is managed securely in the backend.
            2. **Upload PDF**: Upload any multi-page research paper using the sidebar.
            3. **Ask Questions**: Type your questions in the chat box at the bottom.
            4. **Grounded Answers**: The AI answers strictly using the paper. If a topic is absent, it responds: *"This is not mentioned in the paper."*
            """)

        st.markdown(
            "<div style='text-align: center; color: #64748B; font-size: 0.78rem; margin-top: 1.5rem;'>"
            "Designed for B.Tech AI Projects • Built with Streamlit & Gemini"
            "</div>",
            unsafe_allow_html=True
        )

    # --- MAIN VIEWPORT RENDERING ---

    # Hero Banner
    st.markdown("""
    <div class="hero-container">
        <div class="hero-badge">AI Research Paper Assistant</div>
        <h1 class="hero-title">Chat with Your Research Paper</h1>
        <p class="hero-subtitle">Upload complex research papers in PDF format and get clear, instant, grounded explanations powered by Google Gemini AI.</p>
    </div>
    """, unsafe_allow_html=True)

    # View 1: Welcome Screen (No PDF uploaded yet)
    if uploaded_file is None or not st.session_state.doc_data:
        st.markdown("""
        <div class="welcome-card">
            <div class="welcome-icon">📚</div>
            <div class="welcome-title">Welcome to AI Research Paper Assistant!</div>
            <div class="welcome-desc">
                Upload any academic paper (PDF) using the sidebar on the left to begin.
                The assistant extracts all text across every page and answers questions strictly based on the paper content.
            </div>
        </div>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("""
            <div class="feature-card">
                <h4 style="margin: 0 0 0.5rem 0; color: #1E3A8A;">🔍 1. Multi-Page PDF</h4>
                <p style="color: #64748B; font-size: 0.88rem; margin: 0;">Reads all pages with pypdf and provides detailed metrics for your documents.</p>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown("""
            <div class="feature-card">
                <h4 style="margin: 0 0 0.5rem 0; color: #1E3A8A;">🎯 2. Strict Accuracy</h4>
                <p style="color: #64748B; font-size: 0.88rem; margin: 0;">Zero hallucinations. If a concept is not in the paper, the AI explicitly states it.</p>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown("""
            <div class="feature-card">
                <h4 style="margin: 0 0 0.5rem 0; color: #1E3A8A;">💡 3. Student-Friendly</h4>
                <p style="color: #64748B; font-size: 0.88rem; margin: 0;">Complex concepts translated into structured markdown, bullet points, and clear headers.</p>
            </div>
            """, unsafe_allow_html=True)
        return

    # View 2: Extraction Error Alert
    doc_info = st.session_state.doc_data
    if not doc_info.get("success", False):
        st.error(f"❌ {doc_info.get('error', 'Failed to read PDF.')}")
        if doc_info.get("is_scanned"):
            st.warning(
                "💡 **Tip for scanned PDFs**: Use an Optical Character Recognition (OCR) tool "
                "or download the official digital PDF directly from arXiv, IEEE Xplore, or Google Scholar."
            )
        return

    # View 3: Document Loaded & Chat Interface
    st.success(
        f"✅ **Loaded Document:** `{doc_info['filename']}` — **{doc_info['page_count']} Pages** | "
        f"**{doc_info['word_count']:,} Words extracted**."
    )

    # Quick Suggestion Chips for Students
    st.markdown("###### 💡 Quick Questions to Try:")
    chip_cols = st.columns(4)
    quick_questions = [
        "Summarize the main problem and objective of this paper.",
        "What methodology or architecture is proposed?",
        "What datasets and experimental results were achieved?",
        "What are the stated limitations and future work?"
    ]

    for idx, q_text in enumerate(quick_questions):
        with chip_cols[idx]:
            if st.button(f"📌 {q_text[:28]}...", key=f"quick_btn_{idx}", use_container_width=True, help=q_text):
                st.session_state.active_prompt = q_text

    # Render Chat History
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat Input Box
    prompt_input = st.chat_input("Ask a question about this research paper...")

    # Check for active prompt from button clicks
    if st.session_state.active_prompt:
        prompt_input = st.session_state.active_prompt
        st.session_state.active_prompt = None

    if prompt_input:
        if not api_key:
            st.error(
                "⚠️ **Gemini API Key Missing**: Please ensure your Gemini API key is configured in `.streamlit/secrets.toml`."
            )
        else:
            # Empty Context Guard before calling API
            extracted_text = doc_info.get("text", "").strip()
            if not extracted_text:
                st.error("⚠️ **No readable text found**: The uploaded PDF does not contain extractable digital text. Please upload a PDF with selectable text.")
            else:
                # 1. Display and save user question
                st.session_state.messages.append({"role": "user", "content": prompt_input})
                with st.chat_message("user"):
                    st.markdown(prompt_input)

                # 2. Query Gemini and stream/display response with loading spinner
                with st.chat_message("assistant"):
                    with st.spinner("Analyzing research paper with Google Gemini..."):
                        try:
                            ai_response = query_gemini_ai(
                                api_key=api_key,
                                paper_text=extracted_text,
                                chat_history=st.session_state.messages[:-1],
                                user_question=prompt_input
                            )
                            st.markdown(ai_response)
                            # 3. Store assistant response
                            st.session_state.messages.append({"role": "assistant", "content": ai_response})
                        except Exception as chat_err:
                            err_msg = f"❌ An error occurred during chat response: {str(chat_err)}"
                            print(f"[Chat Handler Exception] {chat_err}")
                            st.error(err_msg)


if __name__ == "__main__":
    main()
