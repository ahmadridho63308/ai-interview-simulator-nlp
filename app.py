"""
app.py
------
Streamlit UI untuk AI Interview Simulator.

Menggunakan design system "Reflect Notes" — dark observatory theme
dengan violet-tinted near-black canvas, inset rim-light glows,
dan lavender accent. Lihat DESIGN.md untuk referensi lengkap.
"""

import streamlit as st
import time
from typing import Any

from config import (
    JOB_ROLES,
    MAX_QUESTIONS,
    validate_config,
)
from graph import (
    initialize_state,
    run_generate_question,
    run_evaluate_and_check,
    InterviewState,
)

# ============================================================
# PAGE CONFIGURATION
# ============================================================
st.set_page_config(
    page_title="AI Interview Simulator",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# DESIGN SYSTEM CSS — Reflect Notes
# Tokens: void-canvas #030014, midnight-surface #060317,
# deep-indigo #10093a, lilac-white #f4f0ff, ash #a8a6b7,
# fog #918ea0, lavender-accent #9382ff, iris #5046e4
# ============================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500&display=swap');

    * {
        font-family: 'Inter', ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
        font-variant-ligatures: none !important;
    }

    .stApp {
        background: #030014;
        min-height: 100vh;
    }

    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 900px;
    }

    /* ---- SIDEBAR ---- */
    [data-testid="stSidebar"] {
        background: #060317 !important;
        border-right: 1px solid rgba(81, 70, 228, 0.15) !important;
        box-shadow: inset 0 0 24px rgba(255, 255, 255, 0.04);
    }
    [data-testid="stSidebar"] .stMarkdown {
        color: #a8a6b7;
    }

    /* ---- BUTTONS ---- */
    .stButton > button {
        background: #5046e4 !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 5px !important;
        font-weight: 500 !important;
        font-size: 0.9375rem !important;
        padding: 0.5rem 1rem !important;
        transition: background 0.2s ease, box-shadow 0.2s ease !important;
    }
    .stButton > button:hover {
        background: #9382ff !important;
        color: #ffffff !important;
        box-shadow: inset 0 0 24px rgba(255, 255, 255, 0.06) !important;
    }
    .stButton > button:disabled {
        opacity: 0.35;
        cursor: not-allowed;
    }
    .stButton > button[kind="secondary"] {
        background: #10093a !important;
        color: #f4f0ff !important;
    }
    .stButton > button[kind="secondary"]:hover {
        background: #5046e4 !important;
        color: #ffffff !important;
    }
    button[data-testid="baseButton-secondary"] {
        background: #10093a !important;
        color: #f4f0ff !important;
        border: 1px solid rgba(147, 130, 255, 0.2) !important;
        border-radius: 5px !important;
        font-weight: 500 !important;
        font-size: 0.9375rem !important;
        padding: 0.5rem 1rem !important;
    }
    button[data-testid="baseButton-secondary"]:hover {
        background: #5046e4 !important;
        color: #ffffff !important;
    }

    /* ---- TEXT INPUT / TEXTAREA ---- */
    .stTextArea textarea,
    .stTextInput input {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(81, 70, 228, 0.2) !important;
        border-radius: 5px !important;
        color: #f4f0ff !important;
        font-size: 0.9375rem !important;
        font-weight: 400 !important;
        box-shadow: inset 0 0 24px rgba(255, 255, 255, 0.02) !important;
    }
    .stTextArea textarea:focus,
    .stTextInput input:focus {
        border-color: #9382ff !important;
        box-shadow: inset 0 0 24px rgba(255, 255, 255, 0.04), 0 0 0 2px rgba(147, 130, 255, 0.15) !important;
    }
    .stTextArea textarea::placeholder {
        color: #54525f !important;
    }

    /* ---- SELECTBOX ---- */
    .stSelectbox > div > div {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(81, 70, 228, 0.2) !important;
        border-radius: 5px !important;
        color: #f4f0ff !important;
        box-shadow: inset 0 0 24px rgba(255, 255, 255, 0.02) !important;
    }
    .stSelectbox > div > div:hover {
        border-color: #9382ff !important;
    }

    /* ---- ALERTS ---- */
    .stAlert {
        border-radius: 5px !important;
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(147, 130, 255, 0.2) !important;
        color: #f4f0ff !important;
    }

    /* ---- SPINNER ---- */
    .stSpinner > div {
        border-color: #9382ff transparent transparent transparent !important;
    }

    /* ---- EXPANDER ---- */
    .streamlit-expanderHeader {
        color: #a8a6b7 !important;
        font-weight: 400 !important;
        font-size: 0.875rem !important;
        background: rgba(255, 255, 255, 0.02) !important;
        border-radius: 5px !important;
        border: 1px solid rgba(255, 255, 255, 0.04) !important;
    }
    .streamlit-expanderContent {
        border: none !important;
    }

    /* ---- DIVIDER ---- */
    hr {
        border-color: rgba(255, 255, 255, 0.06) !important;
        margin: 1.5rem 0 !important;
    }

    /* ---- HERO HEADER ---- */
    .hero-header {
        text-align: center;
        padding: 2.5rem 2rem 1.5rem;
        background: #060317;
        border-radius: 16px;
        margin-bottom: 2rem;
        box-shadow: inset 0 0 24px rgba(255, 255, 255, 0.04);
    }
    .hero-header h1 {
        font-family: 'Inter', ui-sans-serif, system-ui, sans-serif !important;
        font-weight: 500 !important;
        font-size: 2.5rem !important;
        color: #f4f0ff !important;
        margin-bottom: 0.5rem !important;
        letter-spacing: -0.3px !important;
    }
    .hero-header .hero-gradient {
        background: linear-gradient(90.01deg, #e59cff 0.01%, #ba9cff 50.01%, #9cb2ff 100%);
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        background-clip: text !important;
    }
    .hero-header p {
        color: #a8a6b7 !important;
        font-size: 1rem !important;
        font-weight: 400 !important;
        margin: 0 0 1.5rem 0 !important;
    }

    /* ---- AI BADGE PILL ---- */
    .badge-pill {
        display: inline-block;
        background: #060317;
        border: 1px solid #5046e4;
        border-radius: 32px;
        padding: 0.3rem 1rem;
        font-size: 0.8125rem;
        font-weight: 500;
        color: #f4f0ff;
        box-shadow: rgba(164, 143, 255, 0.12) 0px -7px 11px 0px inset;
        margin-bottom: 1rem;
    }

    /* ---- INFO CARD (setup page) ---- */
    .info-card {
        background: #060317;
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: inset 0 0 24px rgba(255, 255, 255, 0.04);
    }
    .info-card h4 {
        color: #f4f0ff;
        font-weight: 500;
        font-size: 1.125rem;
        margin: 0 0 0.8rem 0;
        letter-spacing: -0.2px;
    }
    .info-card p, .info-card div {
        color: #a8a6b7;
        font-size: 0.9rem;
        font-weight: 400;
        line-height: 1.6;
    }
    .info-card strong {
        color: #f4f0ff;
        font-weight: 500;
    }

    /* ---- SETUP CARD ---- */
    /* ---- SETUP CARD — targets col2 of the first 2-column horizontal block ---- */
    div[data-testid="stHorizontalBlock"]:first-of-type > div[data-testid="column"]:nth-child(2):nth-last-child(2) {
        padding: 1.5rem !important;
        background: #060317 !important;
        border-radius: 16px !important;
        box-shadow: inset 0 0 24px rgba(255, 255, 255, 0.04) !important;
    }
    .setup-info {
        background: rgba(255, 255, 255, 0.02);
        border-radius: 5px;
        padding: 0.8rem 1rem;
        margin: 0.8rem 0;
        font-size: 0.85rem;
        color: #918ea0;
        line-height: 1.5;
    }
    .setup-info strong {
        color: #f4f0ff;
        font-weight: 500;
    }

    /* ---- QUESTION CARD ---- */
    .question-card {
        background: #060317;
        border-radius: 16px;
        padding: 1.5rem 1.75rem;
        margin-bottom: 1.5rem;
        box-shadow: inset 0 0 24px rgba(255, 255, 255, 0.04);
        position: relative;
        overflow: hidden;
    }
    .question-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0;
        width: 3px; height: 100%;
        background: linear-gradient(180deg, rgba(183,164,251,0) 0%, #b7a4fb 50%, #8562ff 100%, rgba(133,98,255,0) 100%);
        border-radius: 2px 0 0 2px;
    }
    .question-label {
        font-size: 0.75rem;
        font-weight: 500;
        color: #9382ff;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        margin-bottom: 0.6rem;
    }
    .question-text {
        font-size: 1.125rem;
        font-weight: 400;
        color: #f4f0ff;
        line-height: 1.6;
    }

    /* ---- PROGRESS ---- */
    .progress-container {
        background: #060317;
        border-radius: 16px;
        padding: 1rem 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: inset 0 0 24px rgba(255, 255, 255, 0.04);
    }
    .progress-label {
        display: flex;
        justify-content: space-between;
        margin-bottom: 0.5rem;
        color: #918ea0;
        font-size: 0.8125rem;
        font-weight: 400;
    }
    .progress-label strong {
        color: #9382ff;
        font-weight: 500;
    }
    .progress-bar-bg {
        background: rgba(255, 255, 255, 0.06);
        border-radius: 999px;
        height: 6px;
        overflow: hidden;
    }
    .progress-bar-fill {
        height: 100%;
        border-radius: 999px;
        background: #9382ff;
        transition: width 0.4s ease;
    }

    /* ---- METRIC CARDS ---- */
    .metric-card {
        background: #060317;
        border-radius: 16px;
        padding: 1.25rem 1rem;
        text-align: center;
        box-shadow: inset 0 0 24px rgba(255, 255, 255, 0.04);
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 500;
        color: #f4f0ff;
        letter-spacing: -0.3px;
    }
    .metric-label {
        font-size: 0.75rem;
        color: #918ea0;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        margin-top: 0.3rem;
        font-weight: 400;
    }

    /* ---- SCORE BADGE ---- */
    .score-badge {
        display: inline-block;
        border-radius: 32px;
        padding: 0.35rem 1.2rem;
        font-size: 0.875rem;
        font-weight: 500;
        color: #f4f0ff;
        background: #060317;
        border: 1px solid rgba(147, 130, 255, 0.3);
        box-shadow: rgba(164, 143, 255, 0.12) 0px -7px 11px 0px inset;
    }
    .score-badge-high {
        border-color: rgba(147, 130, 255, 0.5);
        color: #f4f0ff;
    }
    .score-badge-medium {
        border-color: rgba(147, 130, 255, 0.25);
        color: #a8a6b7;
    }
    .score-badge-low {
        border-color: rgba(84, 82, 95, 0.5);
        color: #918ea0;
    }

    /* ---- SKILL BAR ---- */
    .skill-item {
        margin-bottom: 0.75rem;
    }
    .skill-header {
        display: flex;
        justify-content: space-between;
        margin-bottom: 0.3rem;
        color: #a8a6b7;
        font-size: 0.875rem;
        font-weight: 400;
    }
    .skill-header span:last-child {
        color: #f4f0ff;
        font-weight: 500;
    }
    .skill-bar-bg {
        background: rgba(255, 255, 255, 0.06);
        border-radius: 999px;
        height: 6px;
        overflow: hidden;
    }
    .skill-bar-fill {
        height: 100%;
        border-radius: 999px;
        background: #9382ff;
        transition: width 0.5s ease;
    }

    /* ---- LIST ITEMS (strengths / improvements) ---- */
    .list-item {
        border-radius: 5px;
        padding: 0.6rem 0.9rem;
        margin-bottom: 0.4rem;
        font-size: 0.9rem;
        display: flex;
        align-items: flex-start;
        gap: 0.6rem;
        line-height: 1.5;
    }
    .list-item-strength {
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.04);
        color: #a8a6b7;
    }
    .list-item-improvement {
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.04);
        color: #a8a6b7;
    }
    .list-item-icon {
        color: #9382ff;
        font-weight: 500;
        flex-shrink: 0;
    }

    /* ---- RECOMMENDATION BOX ---- */
    .recommendation-box {
        background: #060317;
        border-radius: 16px;
        padding: 1.5rem 1.75rem;
        color: #a8a6b7;
        line-height: 1.8;
        font-size: 0.9375rem;
        font-weight: 400;
        box-shadow: inset 0 0 24px rgba(255, 255, 255, 0.04);
    }

    /* ---- SECTION HEADER ---- */
    .section-header {
        font-size: 0.9375rem;
        font-weight: 500;
        color: #f4f0ff;
        margin: 1.5rem 0 0.75rem;
        letter-spacing: -0.15px;
    }

    /* ---- EVAL CARD (history) ---- */
    .eval-card {
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.04);
        border-radius: 5px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.6rem;
    }
    .eval-card .eval-label {
        color: #9382ff;
        font-size: 0.75rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        margin-bottom: 0.4rem;
    }
    .eval-card .eval-question {
        color: #f4f0ff;
        font-size: 0.875rem;
        margin-bottom: 0.4rem;
    }
    .eval-card .eval-answer {
        color: #918ea0;
        font-size: 0.8125rem;
        margin-bottom: 0.4rem;
    }
    .eval-card .eval-score {
        color: #9382ff;
        font-size: 0.8125rem;
        font-weight: 500;
    }

    /* ---- HEADER BAR (interview page) ---- */
    .interview-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        background: #060317;
        border-radius: 16px;
        padding: 0.9rem 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: inset 0 0 24px rgba(255, 255, 255, 0.04);
    }
    .interview-header .brand {
        color: #f4f0ff;
        font-weight: 500;
        font-size: 1.05rem;
    }
    .interview-header .separator {
        color: #54525f;
        margin: 0 0.8rem;
    }
    .interview-header .role {
        color: #918ea0;
        font-size: 0.875rem;
    }
    .interview-header .counter {
        color: #918ea0;
        font-size: 0.8125rem;
    }
    .interview-header .counter strong {
        color: #9382ff;
        font-weight: 500;
    }

    /* ---- RESULTS HERO ---- */
    .results-hero {
        text-align: center;
        padding: 2.5rem 2rem;
        background: #060317;
        border-radius: 16px;
        margin-bottom: 2rem;
        box-shadow: inset 0 0 24px rgba(255, 255, 255, 0.04);
    }
    .results-hero h2 {
        color: #f4f0ff;
        margin: 0 0 0.5rem;
        font-size: 1.5rem;
        font-weight: 500;
        letter-spacing: -0.3px;
    }
    .results-hero p {
        color: #918ea0;
        margin-bottom: 1rem;
        font-size: 0.9375rem;
        font-weight: 400;
    }
    .results-hero p strong {
        color: #9382ff;
        font-weight: 500;
    }

    /* ---- OVERALL SUMMARY ---- */
    .overall-summary {
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.04);
        border-radius: 5px;
        padding: 1.2rem 1.5rem;
        margin-bottom: 1.5rem;
        color: #918ea0;
        font-size: 0.9375rem;
        line-height: 1.7;
        font-weight: 400;
    }

    /* ---- DETAIL VIEW ---- */
    .detail-label {
        color: #9382ff;
        font-size: 0.8125rem;
        margin-bottom: 0.4rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.8px;
    }
    .detail-text {
        color: #f4f0ff;
        margin-bottom: 0.8rem;
        line-height: 1.6;
        font-size: 0.9375rem;
        font-weight: 400;
    }
    .detail-answer {
        color: #918ea0;
        margin-bottom: 0.8rem;
        line-height: 1.6;
        font-size: 0.9375rem;
        font-weight: 400;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================
# SESSION STATE INITIALIZATION
# ============================================================
def init_session_state():
    defaults = {
        "interview_state": None,
        "phase": "setup",
        "selected_role": JOB_ROLES[0],
        "current_answer": "",
        "is_loading": False,
        "error_message": "",
        "question_history": [],
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


# ============================================================
# HELPERS
# ============================================================
def render_header():
    st.markdown("""
    <div class="hero-header">
        <div class="badge-pill">AI-Powered Interview</div>
        <h1>Simulasi Wawancara <span class="hero-gradient">Berbasis AI</span></h1>
        <p>Sistem simulasi wawancara kerja interaktif dengan evaluasi cerdas</p>
    </div>
    """, unsafe_allow_html=True)


def render_progress(current: int, total: int = MAX_QUESTIONS):
    pct = int((current / total) * 100)
    st.markdown(f"""
    <div class="progress-container">
        <div class="progress-label">
            <span>Progress Wawancara</span>
            <span><strong>{current}</strong> / {total} Pertanyaan</span>
        </div>
        <div class="progress-bar-bg">
            <div class="progress-bar-fill" style="width: {pct}%"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_question_card(question_num: int, question_text: str, q_type: str = ""):
    type_label = q_type.upper() if q_type else "INTERVIEW"
    st.markdown(f"""
    <div class="question-card">
        <div class="question-label">PERTANYAAN {question_num} — {type_label}</div>
        <div class="question-text">{question_text}</div>
    </div>
    """, unsafe_allow_html=True)


def get_score_badge(score: float) -> str:
    if score >= 80:
        css_class = "score-badge score-badge-high"
    elif score >= 70:
        css_class = "score-badge score-badge-medium"
    else:
        css_class = "score-badge score-badge-low"
    return f'<span class="{css_class}">{score:.0f}/100</span>'


# ============================================================
# PHASE 1: SETUP PAGE
# ============================================================
def render_setup_page():
    render_header()

    is_valid, errors = validate_config()

    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.markdown("""
        <div class="info-card">
            <h4>Cara Menggunakan</h4>
            <p><strong>1.</strong> Pilih posisi pekerjaan yang ingin dilamar</p>
            <p><strong>2.</strong> Klik mulai untuk memulai sesi interview</p>
            <p><strong>3.</strong> Jawab pertanyaan AI dengan teks jawaban Anda</p>
            <p><strong>4.</strong> Terima evaluasi setelah 5 pertanyaan selesai</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="info-card">
            <h4>Teknologi</h4>
            <div><strong>LangChain</strong> — Chains & Structured Output</div>
            <div><strong>LangGraph</strong> — Stateful Workflow</div>
            <div><strong>LangSmith</strong> — Tracing & Monitoring</div>
            <div><strong>Google Gemini</strong> — LLM Engine</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown('<h4 style="color:#f4f0ff; font-weight:500; font-size:1.125rem; margin:0 0 1rem 0; letter-spacing:-0.2px;">Mulai Interview</h4>', unsafe_allow_html=True)

        selected = st.selectbox(
            "Pilih Posisi Pekerjaan",
            options=JOB_ROLES,
            index=JOB_ROLES.index(st.session_state.selected_role),
            key="role_select",
        )
        st.session_state.selected_role = selected

        st.markdown(f"""
        <div class="setup-info">
            Anda akan diwawancarai sebagai calon <strong>{selected}</strong>.
            Sesi terdiri dari <strong>5 pertanyaan</strong> yang semakin mendalam.
        </div>
        """, unsafe_allow_html=True)

        if not is_valid:
            for err in errors:
                if "GOOGLE_API_KEY" in err:
                    st.error(err)
                else:
                    st.warning(err)

        google_key_missing = not any(
            True for e in errors if "GOOGLE_API_KEY" not in e
        ) and any(True for e in errors if "GOOGLE_API_KEY" in e)

        if st.button("Mulai Sesi Interview", disabled=google_key_missing, use_container_width=True):
            start_interview()


# ============================================================
# PHASE 2: INTERVIEW PAGE
# ============================================================
def render_interview_page():
    state: InterviewState = st.session_state.interview_state

    st.markdown(f"""
    <div class="interview-header">
        <div>
            <span class="brand">AI Interview Simulator</span>
            <span class="separator">•</span>
            <span class="role">{state['job_role']}</span>
        </div>
        <div class="counter">
            Pertanyaan <strong>{state['question_count']}</strong> / {MAX_QUESTIONS}
        </div>
    </div>
    """, unsafe_allow_html=True)

    render_progress(state["question_count"], MAX_QUESTIONS)

    if st.session_state.question_history:
        with st.expander("Riwayat Pertanyaan", expanded=False):
            for i, hist in enumerate(st.session_state.question_history, 1):
                eval_data = hist.get("evaluation", {})
                score = eval_data.get("score", "-")
                st.markdown(f"""
                <div class="eval-card">
                    <div class="eval-label">Pertanyaan {i}</div>
                    <div class="eval-question">{hist.get('question','')}</div>
                    <div class="eval-answer">{hist.get('answer','')[:150]}{'...' if len(hist.get('answer','')) > 150 else ''}</div>
                    <div class="eval-score">Skor: {score}/100</div>
                </div>
                """, unsafe_allow_html=True)

    if state["current_question"]:
        render_question_card(
            state["question_count"],
            state["current_question"],
            state.get("current_question_type", "")
        )

        st.markdown('<div style="color:#918ea0; font-size:0.8125rem; margin-bottom:0.5rem;">Ketik jawaban Anda di bawah ini:</div>', unsafe_allow_html=True)

        answer = st.text_area(
            label="Jawaban Anda",
            placeholder="Tuliskan jawaban Anda secara lengkap dan jelas...",
            height=180,
            key=f"answer_{state['question_count']}",
            label_visibility="collapsed",
        )

        col_submit, col_tip = st.columns([1, 2])
        with col_submit:
            submit_clicked = st.button(
                "Kirim Jawaban",
                disabled=st.session_state.is_loading,
                use_container_width=True,
            )

        with col_tip:
            st.markdown("""
            <div style="color:#54525f; font-size:0.8rem; padding-top:0.7rem;">
             Jawablah dengan lengkap. AI akan mengevaluasi kualitas, relevansi, dan kedalaman jawaban Anda.
            </div>
            """, unsafe_allow_html=True)

        if submit_clicked:
            if not answer or len(answer.strip()) < 10:
                st.warning("Jawaban terlalu singkat. Harap jawab dengan lebih lengkap (minimal 10 karakter).")
            else:
                process_answer(answer.strip())
                st.rerun()

    if st.session_state.is_loading:
        with st.spinner("AI sedang memproses..."):
            time.sleep(0.5)


# ============================================================
# PHASE 3: RESULTS PAGE
# ============================================================
def render_results_page():
    state: InterviewState = st.session_state.interview_state
    report: dict[str, Any] = state.get("final_report", {})

    if not report:
        st.error("Laporan tidak tersedia. Silakan mulai sesi baru.")
        return

    avg_score = report.get("average_score", 0)
    badge_html = get_score_badge(avg_score)

    st.markdown(f"""
    <div class="results-hero">
        <h2>Interview Selesai</h2>
        <p>Posisi: <strong>{state['job_role']}</strong></p>
        {badge_html}
    </div>
    """, unsafe_allow_html=True)

    soft_skills = report.get("soft_skill_scores", {})
    comm_score = soft_skills.get("communication", 0)
    ps_score = soft_skills.get("problem_solving", 0)
    conf_score = soft_skills.get("confidence", 0)
    prof_score = soft_skills.get("professionalism", 0)

    c1, c2, c3, c4, c5 = st.columns(5)
    metric_data = [
        (c1, f"{avg_score:.0f}", "Skor Rata-rata"),
        (c2, f"{comm_score}", "Komunikasi"),
        (c3, f"{ps_score}", "Problem Solving"),
        (c4, f"{conf_score}", "Kepercayaan Diri"),
        (c5, f"{prof_score}", "Profesionalisme"),
    ]
    for col, val, label in metric_data:
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{val}</div>
                <div class="metric-label">{label}</div>
            </div>
            """, unsafe_allow_html=True)

    overall = report.get("overall_summary", "")
    if overall:
        st.markdown(f"""
        <div class="overall-summary">{overall}</div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="section-header">Soft Skill Assessment</div>', unsafe_allow_html=True)

    skills_data = [
        ("Komunikasi", comm_score),
        ("Problem Solving", ps_score),
        ("Kepercayaan Diri", conf_score),
        ("Profesionalisme", prof_score),
    ]
    for skill_name, skill_score in skills_data:
        st.markdown(f"""
        <div class="skill-item">
            <div class="skill-header">
                <span>{skill_name}</span>
                <span>{skill_score}/100</span>
            </div>
            <div class="skill-bar-bg">
                <div class="skill-bar-fill" style="width:{skill_score}%"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    col_left, col_right = st.columns(2, gap="large")

    with col_left:
        st.markdown('<div class="section-header">Kelebihan Kandidat</div>', unsafe_allow_html=True)
        strengths = report.get("candidate_strengths", [])
        for strength in strengths:
            st.markdown(f"""
            <div class="list-item list-item-strength">
                <span class="list-item-icon">&#10003;</span>
                <span>{strength}</span>
            </div>
            """, unsafe_allow_html=True)

    with col_right:
        st.markdown('<div class="section-header">Area Perbaikan</div>', unsafe_allow_html=True)
        improvements = report.get("improvement_areas", [])
        for improvement in improvements:
            st.markdown(f"""
            <div class="list-item list-item-improvement">
                <span class="list-item-icon">&rarr;</span>
                <span>{improvement}</span>
            </div>
            """, unsafe_allow_html=True)

    st.markdown('<div class="section-header">Rekomendasi HR Profesional</div>', unsafe_allow_html=True)
    hr_rec = report.get("hr_recommendation", "")
    st.markdown(f"""
    <div class="recommendation-box">{hr_rec}</div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-header">Detail Evaluasi Per Pertanyaan</div>', unsafe_allow_html=True)

    for i, qa in enumerate(state.get("answers", []), 1):
        eval_data = qa.get("evaluation", {})
        score = eval_data.get("score", 0)
        with st.expander(f"Pertanyaan {i} — Skor: {score}/100", expanded=False):
            st.markdown(f"""
            <div class="detail-label">Pertanyaan</div>
            <div class="detail-text">{qa.get('question','')}</div>
            <div class="detail-label">Jawaban Anda</div>
            <div class="detail-answer">{qa.get('answer','')}</div>
            """, unsafe_allow_html=True)

            sc1, sc2 = st.columns([1, 3])
            with sc1:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{score}</div>
                    <div class="metric-label">Skor</div>
                </div>
                """, unsafe_allow_html=True)
            with sc2:
                brief = eval_data.get("brief_feedback", "")
                if brief:
                    st.markdown(f'<div style="color:#918ea0; font-size:0.9rem; padding-top:0.5rem;">{brief}</div>', unsafe_allow_html=True)

            col_s, col_w = st.columns(2)
            with col_s:
                st.markdown('**Kelebihan:**')
                for s in eval_data.get("strengths", []):
                    st.markdown(f"* {s}")
            with col_w:
                st.markdown('**Kekurangan:**')
                for w in eval_data.get("weaknesses", []):
                    st.markdown(f"* {w}")

            sugg = eval_data.get("suggestions", [])
            if sugg:
                st.markdown('**Saran Perbaikan:**')
                for sug in sugg:
                    st.markdown(f"* {sug}")

    if st.button("Mulai Interview Baru", use_container_width=False):
        reset_session()
        st.rerun()


# ============================================================
# ACTION FUNCTIONS
# ============================================================
def start_interview():
    job_role = st.session_state.selected_role
    state = initialize_state(job_role)

    with st.spinner("Menyiapkan sesi interview..."):
        try:
            state = run_generate_question(state)
            st.session_state.interview_state = state
            st.session_state.phase = "interviewing"
            st.session_state.question_history = []
            st.session_state.error_message = ""
        except Exception as e:
            st.session_state.error_message = f"Error: {str(e)}"
            st.error(f"Gagal memulai interview: {str(e)}")


def process_answer(answer: str):
    state: InterviewState = st.session_state.interview_state
    current_question = state["current_question"]
    current_q_type = state.get("current_question_type", "")

    with st.spinner("AI sedang mengevaluasi jawaban Anda..."):
        try:
            st.session_state.question_history.append({
                "question": current_question,
                "answer": answer,
                "question_type": current_q_type,
            })

            updated_state = run_evaluate_and_check(state, current_question, answer)
            st.session_state.interview_state = updated_state

            if updated_state["answers"]:
                last_eval = updated_state["answers"][-1].get("evaluation", {})
                st.session_state.question_history[-1]["evaluation"] = last_eval

            if updated_state.get("is_complete", False):
                st.session_state.phase = "complete"
            else:
                next_state = run_generate_question(updated_state)
                st.session_state.interview_state = next_state

        except Exception as e:
            st.error(f"Error saat memproses jawaban: {str(e)}")
            st.session_state.error_message = str(e)


def reset_session():
    keys_to_reset = [
        "interview_state", "phase", "current_answer",
        "is_loading", "error_message", "question_history"
    ]
    for key in keys_to_reset:
        if key in st.session_state:
            del st.session_state[key]


# ============================================================
# SIDEBAR
# ============================================================
def render_sidebar():
    with st.sidebar:
        st.markdown("""
        <div style="text-align:center; padding: 0.5rem 0;">
            <div style="font-weight:500; font-size:1.05rem; color:#f4f0ff; letter-spacing:-0.15px;">AI Interview Simulator</div>
            <div style="color:#54525f; font-size:0.75rem; margin-top:0.2rem;">v1.0.0</div>
        </div>
        """, unsafe_allow_html=True)

        st.divider()

        phase = st.session_state.get("phase", "setup")

        if phase == "setup":
            st.markdown('<div style="color:#918ea0; font-size:0.8rem;"><span style="color:#9382ff;">&#9679;</span> Status: Belum dimulai</div>', unsafe_allow_html=True)
            st.markdown("""
            <div style="color:#54525f; font-size:0.8rem; line-height:1.7; margin-top:0.5rem;">
                Pilih posisi pekerjaan dan klik Mulai Interview untuk memulai sesi wawancara.
            </div>
            """, unsafe_allow_html=True)

        elif phase == "interviewing":
            state = st.session_state.interview_state
            q_count = state["question_count"] if state else 0
            st.markdown(f'<div style="color:#918ea0; font-size:0.8rem;"><span style="color:#9382ff;">&#9679;</span> Status: Sesi Aktif</div>', unsafe_allow_html=True)
            st.markdown(f'<div style="color:#a8a6b7; font-size:0.8rem; margin-top:0.4rem;">Posisi: <span style="color:#f4f0ff;">{state["job_role"] if state else "-"}</span></div>', unsafe_allow_html=True)
            st.markdown(f'<div style="color:#a8a6b7; font-size:0.8rem;">Pertanyaan: <span style="color:#f4f0ff;">{q_count} / {MAX_QUESTIONS}</span></div>', unsafe_allow_html=True)

            st.divider()
            if st.button("Hentikan Sesi", use_container_width=True):
                reset_session()
                st.rerun()

        elif phase == "complete":
            state = st.session_state.interview_state
            report = state.get("final_report", {}) if state else {}
            avg_score = report.get("average_score", 0)

            st.markdown(f'<div style="color:#918ea0; font-size:0.8rem;"><span style="color:#9382ff;">&#9679;</span> Status: Selesai</div>', unsafe_allow_html=True)
            st.markdown(f'<div style="color:#a8a6b7; font-size:0.8rem; margin-top:0.4rem;">Posisi: <span style="color:#f4f0ff;">{state["job_role"] if state else "-"}</span></div>', unsafe_allow_html=True)
            st.markdown(f'<div style="color:#a8a6b7; font-size:0.8rem;">Skor: <span style="color:#f4f0ff;">{avg_score:.1f}/100</span></div>', unsafe_allow_html=True)
            st.markdown(f'<div style="color:#a8a6b7; font-size:0.8rem;">Kategori: <span style="color:#f4f0ff;">{report.get("candidate_category", "-")}</span></div>', unsafe_allow_html=True)

            st.divider()
            if st.button("Interview Baru", use_container_width=True):
                reset_session()
                st.rerun()

        st.divider()

        from config import LANGCHAIN_API_KEY, LANGCHAIN_PROJECT
        langsmith_active = bool(LANGCHAIN_API_KEY)

        st.markdown(f"""
        <div style="background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.04);
             border-radius: 5px; padding: 0.8rem; font-size:0.78rem;">
            <div style="font-weight:500; color:#{'a8a6b7' if langsmith_active else '54525f'}; margin-bottom:0.3rem;">
                {'&#9679;' if langsmith_active else '&#9679;'} LangSmith Tracing
            </div>
            <div style="color:#54525f;">
                {'Aktif — ' + LANGCHAIN_PROJECT if langsmith_active else 'Tidak aktif (API key belum di-set)'}
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div style="color:#54525f; font-size:0.72rem; text-align:center; margin-top:1.5rem;">
            Powered by LangChain · LangGraph<br>LangSmith · Google Gemini
        </div>
        """, unsafe_allow_html=True)


# ============================================================
# MAIN APP
# ============================================================
def main():
    init_session_state()
    render_sidebar()

    phase = st.session_state.get("phase", "setup")

    if phase == "setup":
        render_setup_page()
    elif phase == "interviewing":
        render_interview_page()
    elif phase == "complete":
        render_results_page()
    else:
        render_setup_page()


if __name__ == "__main__":
    main()
