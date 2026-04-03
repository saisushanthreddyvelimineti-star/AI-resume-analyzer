import html

import streamlit as st

from src.helper import (
    ask_interview_coach,
    ask_openai,
    extract_text_from_pdf,
    has_openai_config,
    synthesize_speech,
    transcribe_audio,
)
from src.job_api import fetch_linkedin_jobs, fetch_naukri_jobs, has_apify_config


st.set_page_config(page_title="Jarvis Career Studio", layout="wide")


def esc(value: str) -> str:
    return html.escape(value or "")


def init_state() -> None:
    defaults = {
        "resume_id": None,
        "resume_text": "",
        "summary": "Upload a resume to generate a sharp AI summary of your profile.",
        "gaps": "Your missing skills, certifications, and experience gaps will appear here.",
        "roadmap": "A targeted growth roadmap will appear here after analysis.",
        "analysis_ready": False,
        "job_keywords": "",
        "linkedin_jobs": [],
        "naukri_jobs": [],
        "jarvis_history": [],
        "jarvis_reply_audio": None,
        "jarvis_prompt": "",
        "jarvis_is_talking": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def render_svg_banner() -> None:
    st.markdown(
        """
        <div class="orbital-card">
            <svg viewBox="0 0 520 260" class="hero-art" xmlns="http://www.w3.org/2000/svg">
                <defs>
                    <linearGradient id="lineGlow" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" stop-color="#7cf7d4"/>
                        <stop offset="100%" stop-color="#74a5ff"/>
                    </linearGradient>
                </defs>
                <rect x="16" y="16" width="488" height="228" rx="28" fill="rgba(11,24,43,0.75)" stroke="rgba(133,161,203,0.18)"/>
                <circle cx="123" cy="132" r="54" fill="rgba(124,247,212,0.10)" stroke="url(#lineGlow)" stroke-width="3"/>
                <circle cx="123" cy="132" r="14" fill="#7cf7d4"/>
                <path d="M177 132 C220 90, 270 88, 318 114 S400 150, 452 90" fill="none" stroke="url(#lineGlow)" stroke-width="4" stroke-linecap="round"/>
                <path d="M176 148 C224 182, 278 186, 333 158 S413 119, 459 165" fill="none" stroke="rgba(244,201,107,0.82)" stroke-width="3" stroke-linecap="round"/>
                <rect x="308" y="68" width="120" height="56" rx="18" fill="rgba(255,255,255,0.05)" stroke="rgba(133,161,203,0.14)"/>
                <text x="326" y="92" fill="#97a8c2" font-size="13" font-family="IBM Plex Sans">Interview Mode</text>
                <text x="326" y="112" fill="#e8eef9" font-size="22" font-family="Space Grotesk">Jarvis Live</text>
                <rect x="254" y="152" width="156" height="56" rx="18" fill="rgba(255,255,255,0.05)" stroke="rgba(133,161,203,0.14)"/>
                <text x="272" y="176" fill="#97a8c2" font-size="13" font-family="IBM Plex Sans">Career Pulse</text>
                <text x="272" y="196" fill="#e8eef9" font-size="22" font-family="Space Grotesk">Resume -> Roles</text>
            </svg>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_metric(label: str, value: str, accent: str) -> None:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{esc(label)}</div>
            <div class="metric-value {esc(accent)}">{esc(value)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_insight_card(title: str, body: str, tone: str) -> None:
    st.markdown(
        f"""
        <section class="insight-card {esc(tone)}">
            <div class="card-header">{esc(title)}</div>
            <div class="card-copy">{esc(body)}</div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_job_card(job: dict, url_key: str, source_name: str) -> None:
    title = esc(job.get("title") or "Untitled role")
    company = esc(job.get("companyName") or "Unknown company")
    location = esc(job.get("location") or "Location not provided")
    url = esc(job.get(url_key) or "#")
    st.markdown(
        f"""
        <article class="job-card">
            <div class="job-source">{esc(source_name)}</div>
            <h3>{title}</h3>
            <div class="job-meta">{company}</div>
            <div class="job-meta">{location}</div>
            <a class="job-link" href="{url}" target="_blank">Open listing</a>
        </article>
        """,
        unsafe_allow_html=True,
    )


def render_chat(role: str, content: str) -> None:
    shell = "chat-user" if role == "user" else "chat-assistant"
    label = "You" if role == "user" else "Jarvis"
    st.markdown(
        f"""
        <div class="chat-bubble {shell}">
            <div class="chat-label">{esc(label)}</div>
            <div>{esc(content)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def get_resume_id(uploaded_file) -> str:
    return f"{uploaded_file.name}:{uploaded_file.size}"


def reset_resume_dependent_state() -> None:
    st.session_state.summary = "Upload a resume to generate a sharp AI summary of your profile."
    st.session_state.gaps = "Your missing skills, certifications, and experience gaps will appear here."
    st.session_state.roadmap = "A targeted growth roadmap will appear here after analysis."
    st.session_state.resume_text = ""
    st.session_state.analysis_ready = False
    st.session_state.job_keywords = ""
    st.session_state.linkedin_jobs = []
    st.session_state.naukri_jobs = []
    st.session_state.jarvis_history = []
    st.session_state.jarvis_reply_audio = None


def analyze_resume(uploaded_file) -> None:
    resume_id = get_resume_id(uploaded_file)
    if st.session_state.resume_id == resume_id and st.session_state.analysis_ready:
        return

    reset_resume_dependent_state()
    st.session_state.resume_id = resume_id

    with st.spinner("Extracting text from your resume..."):
        resume_text = extract_text_from_pdf(uploaded_file)
    st.session_state.resume_text = resume_text

    with st.spinner("Building your resume intelligence deck..."):
        st.session_state.summary = ask_openai(
            f"Summarize this resume highlighting the skills, education, and experience:\n\n{resume_text}",
            max_tokens=500,
        )
        st.session_state.gaps = ask_openai(
            "Analyze this resume and highlight missing skills, certificates, and experience needed "
            f"for better job opportunities:\n\n{resume_text}",
            max_tokens=400,
        )
        st.session_state.roadmap = ask_openai(
            "Based on this resume, suggest a future roadmap to improve this person's career prospects "
            f"(skills to learn, certifications needed, industry exposure):\n\n{resume_text}",
            max_tokens=400,
        )
    st.session_state.analysis_ready = True


def generate_jobs() -> None:
    keywords = ask_openai(
        "Based on this resume summary, suggest the best job titles and search keywords. Return a "
        f"comma-separated list only, with no explanation.\n\nSummary: {st.session_state.summary}",
        max_tokens=100,
    )
    st.session_state.job_keywords = keywords.replace("\n", " ").strip()
    st.session_state.linkedin_jobs = fetch_linkedin_jobs(st.session_state.job_keywords, rows=9)
    st.session_state.naukri_jobs = fetch_naukri_jobs(st.session_state.job_keywords, rows=9)


def run_jarvis(prompt: str) -> None:
    cleaned = prompt.strip()
    if not cleaned:
        return
    reply = ask_interview_coach(
        st.session_state.summary,
        st.session_state.jarvis_history,
        cleaned,
    )
    st.session_state.jarvis_history.extend(
        [
            {"role": "user", "content": cleaned},
            {"role": "assistant", "content": reply},
        ]
    )
    st.session_state.jarvis_is_talking = True
    try:
        st.session_state.jarvis_reply_audio = synthesize_speech(reply)
    except Exception:
        st.session_state.jarvis_reply_audio = None


init_state()
openai_ready = has_openai_config()
apify_ready = has_apify_config()

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;700&family=IBM+Plex+Sans:wght@400;500;600&display=swap');

    :root {
        --bg: #07101d;
        --bg-2: #0d1c32;
        --panel: rgba(10, 22, 40, 0.78);
        --panel-2: rgba(14, 28, 48, 0.92);
        --line: rgba(158, 178, 207, 0.16);
        --text: #e9f0fa;
        --muted: #9bb0cc;
        --mint: #7cf7d4;
        --blue: #74a5ff;
        --gold: #f4c96b;
        --rose: #ff8d92;
    }

    .stApp {
        background:
            radial-gradient(circle at 10% 10%, rgba(124, 247, 212, 0.10), transparent 22%),
            radial-gradient(circle at 88% 8%, rgba(116, 165, 255, 0.14), transparent 24%),
            linear-gradient(180deg, var(--bg) 0%, #081424 45%, var(--bg-2) 100%);
        color: var(--text);
        font-family: "IBM Plex Sans", sans-serif;
    }

    .block-container {
        max-width: 1320px;
        padding-top: 1.7rem;
        padding-bottom: 3rem;
    }

    h1, h2, h3, .title-xl, .card-header, .metric-value, .tab-title {
        font-family: "Space Grotesk", sans-serif;
    }

    .hero-grid {
        background: linear-gradient(145deg, rgba(10, 21, 37, 0.95), rgba(13, 28, 50, 0.80));
        border: 1px solid var(--line);
        border-radius: 30px;
        padding: 1.6rem;
        box-shadow: 0 26px 90px rgba(0, 0, 0, 0.34);
        margin-bottom: 1rem;
    }

    .eyebrow {
        color: var(--mint);
        text-transform: uppercase;
        letter-spacing: 0.16em;
        font-size: 0.76rem;
        margin-bottom: 0.65rem;
    }

    .title-xl {
        font-size: clamp(2.6rem, 5vw, 5rem);
        line-height: 0.94;
        margin: 0;
        max-width: 11ch;
    }

    .hero-copy {
        color: var(--muted);
        font-size: 1rem;
        max-width: 60ch;
        line-height: 1.8;
        margin-top: 1rem;
    }

    .hero-pills {
        display: flex;
        gap: 0.7rem;
        flex-wrap: wrap;
        margin-top: 1.1rem;
    }

    .hero-pill {
        border: 1px solid var(--line);
        background: rgba(255, 255, 255, 0.04);
        border-radius: 999px;
        padding: 0.55rem 0.85rem;
        color: var(--text);
        font-size: 0.92rem;
    }

    .orbital-card {
        background: rgba(255, 255, 255, 0.035);
        border: 1px solid var(--line);
        border-radius: 24px;
        padding: 0.8rem;
        height: 100%;
    }

    .hero-art {
        width: 100%;
        height: auto;
        display: block;
    }

    .upload-shell, .status-shell, .coach-rail, .jobs-toolbar {
        background: var(--panel);
        border: 1px solid var(--line);
        border-radius: 24px;
        padding: 1rem 1.1rem;
        box-shadow: 0 16px 40px rgba(0, 0, 0, 0.2);
    }

    .status-shell {
        margin-top: 1rem;
    }

    .metric-card {
        background: var(--panel-2);
        border: 1px solid var(--line);
        border-radius: 20px;
        padding: 1rem;
        height: 100%;
    }

    .metric-label {
        color: var(--muted);
        text-transform: uppercase;
        letter-spacing: 0.12em;
        font-size: 0.75rem;
    }

    .metric-value {
        margin-top: 0.35rem;
        font-size: 1.7rem;
    }

    .mint { color: var(--mint); }
    .blue { color: var(--blue); }
    .gold { color: var(--gold); }

    .insight-card, .job-card, .chat-shell, .prompt-card {
        border: 1px solid var(--line);
        border-radius: 24px;
        padding: 1.15rem;
        background: var(--panel);
        box-shadow: 0 18px 44px rgba(0, 0, 0, 0.22);
    }

    .insight-card {
        min-height: 260px;
    }

    .insight-summary { background: linear-gradient(180deg, rgba(10, 27, 49, 0.95), rgba(11, 23, 41, 0.86)); }
    .insight-gap { background: linear-gradient(180deg, rgba(44, 22, 31, 0.95), rgba(26, 17, 25, 0.84)); }
    .insight-roadmap { background: linear-gradient(180deg, rgba(39, 32, 16, 0.95), rgba(24, 21, 14, 0.86)); }

    .card-header {
        font-size: 1.15rem;
        margin-bottom: 0.75rem;
    }

    .card-copy {
        color: #d9e3f2;
        line-height: 1.8;
        white-space: pre-wrap;
    }

    .section-head {
        display: flex;
        justify-content: space-between;
        align-items: end;
        gap: 1rem;
        margin-bottom: 0.8rem;
    }

    .section-title {
        font-family: "Space Grotesk", sans-serif;
        font-size: 1.25rem;
    }

    .section-copy {
        color: var(--muted);
        font-size: 0.94rem;
    }

    .job-card h3 {
        margin: 0.15rem 0 0.45rem 0;
        font-size: 1.12rem;
    }

    .job-source {
        color: var(--mint);
        text-transform: uppercase;
        letter-spacing: 0.12em;
        font-size: 0.72rem;
    }

    .job-meta {
        color: var(--muted);
        margin-bottom: 0.25rem;
    }

    .job-link {
        display: inline-block;
        margin-top: 0.8rem;
        text-decoration: none;
        color: #08111b;
        background: linear-gradient(90deg, var(--mint), var(--blue));
        border-radius: 999px;
        padding: 0.55rem 0.95rem;
        font-weight: 700;
    }

    .chat-shell {
        min-height: 430px;
    }

    .chat-bubble {
        border-radius: 18px;
        padding: 0.9rem 1rem;
        margin-bottom: 0.75rem;
        line-height: 1.75;
        white-space: pre-wrap;
    }

    .chat-user {
        background: rgba(116, 165, 255, 0.11);
        border: 1px solid rgba(116, 165, 255, 0.18);
    }

    .chat-assistant {
        background: rgba(124, 247, 212, 0.08);
        border: 1px solid rgba(124, 247, 212, 0.16);
    }

    .chat-label {
        color: var(--muted);
        text-transform: uppercase;
        letter-spacing: 0.12em;
        font-size: 0.72rem;
        margin-bottom: 0.42rem;
    }

    .prompt-card {
        margin-bottom: 1rem;
        background: var(--panel-2);
    }

    .jarvis-stage {
        position: relative;
        overflow: hidden;
        background:
            linear-gradient(rgba(123, 199, 255, 0.06) 1px, transparent 1px),
            linear-gradient(90deg, rgba(123, 199, 255, 0.06) 1px, transparent 1px),
            linear-gradient(180deg, rgba(6, 17, 31, 0.96), rgba(5, 12, 24, 0.98));
        background-size: 22px 22px, 22px 22px, auto;
        border: 1px solid rgba(124, 247, 212, 0.14);
        border-radius: 30px;
        padding: 1rem;
        box-shadow: inset 0 0 90px rgba(116, 165, 255, 0.10), 0 24px 64px rgba(0, 0, 0, 0.35);
    }

    .jarvis-stage::before {
        content: "";
        position: absolute;
        inset: 0;
        background:
            radial-gradient(circle at center, rgba(124, 247, 212, 0.10), transparent 30%),
            radial-gradient(circle at 50% 50%, rgba(116, 165, 255, 0.18), transparent 42%);
        pointer-events: none;
    }

    .jarvis-panel {
        position: relative;
        z-index: 1;
        background: rgba(6, 18, 33, 0.82);
        border: 1px solid rgba(116, 165, 255, 0.18);
        border-radius: 22px;
        padding: 1rem;
        box-shadow: inset 0 0 24px rgba(116, 165, 255, 0.06);
    }

    .hud-label {
        color: var(--mint);
        text-transform: uppercase;
        letter-spacing: 0.16em;
        font-size: 0.72rem;
        margin-bottom: 0.5rem;
    }

    .hud-copy {
        color: var(--muted);
        line-height: 1.7;
        font-size: 0.94rem;
    }

    .reactor-shell {
        position: relative;
        z-index: 1;
        display: flex;
        align-items: center;
        justify-content: center;
        min-height: 420px;
    }

    .reactor-svg {
        width: min(100%, 480px);
        height: auto;
        filter: drop-shadow(0 0 24px rgba(116, 165, 255, 0.32));
    }

    .reactor-shell.talking .reactor-core {
        animation: reactorPulse 1.15s ease-in-out infinite;
    }

    .reactor-shell.talking .reactor-ring {
        animation: reactorSpin 9s linear infinite;
        transform-origin: 260px 260px;
    }

    .reactor-shell.talking .reactor-ring-fast {
        animation: reactorSpinReverse 4s linear infinite;
        transform-origin: 260px 260px;
    }

    .reactor-shell.talking .reactor-glow {
        animation: reactorGlow 1.2s ease-in-out infinite;
    }

    .reactor-caption {
        position: absolute;
        bottom: 10px;
        left: 50%;
        transform: translateX(-50%);
        text-align: center;
        color: var(--muted);
        font-size: 0.9rem;
        letter-spacing: 0.12em;
        text-transform: uppercase;
    }

    @keyframes reactorPulse {
        0%, 100% { transform: scale(1); opacity: 0.92; }
        50% { transform: scale(1.08); opacity: 1; }
    }

    @keyframes reactorSpin {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }

    @keyframes reactorSpinReverse {
        from { transform: rotate(360deg); }
        to { transform: rotate(0deg); }
    }

    @keyframes reactorGlow {
        0%, 100% { opacity: 0.45; }
        50% { opacity: 0.95; }
    }

    .mini-hud {
        display: grid;
        gap: 0.75rem;
    }

    .mini-hud-card {
        background: rgba(7, 20, 38, 0.86);
        border: 1px solid rgba(116, 165, 255, 0.16);
        border-radius: 18px;
        padding: 0.85rem;
    }

    .mini-hud-value {
        color: var(--text);
        font-family: "Space Grotesk", sans-serif;
        font-size: 1.1rem;
        margin-top: 0.2rem;
    }

    .console-box {
        background: rgba(4, 14, 26, 0.92);
        border: 1px solid rgba(124, 247, 212, 0.12);
        border-radius: 22px;
        padding: 1rem;
    }

    .prompt-tag {
        color: var(--gold);
        text-transform: uppercase;
        letter-spacing: 0.12em;
        font-size: 0.72rem;
        margin-bottom: 0.45rem;
    }

    .side-image {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid var(--line);
        border-radius: 24px;
        padding: 0.8rem;
    }

    .side-image svg {
        width: 100%;
        height: auto;
        display: block;
    }

    div.stButton > button {
        border: 0;
        border-radius: 999px;
        padding: 0.82rem 1.15rem;
        background: linear-gradient(90deg, var(--mint), var(--blue));
        color: #08111b;
        font-weight: 800;
        font-family: "Space Grotesk", sans-serif;
    }

    div.stButton > button:disabled {
        background: rgba(148, 163, 184, 0.2);
        color: rgba(233, 240, 250, 0.55);
    }

    div[data-testid="stFileUploader"] {
        background: transparent;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 0.6rem;
        margin-bottom: 1rem;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 999px;
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid var(--line);
        color: var(--text);
        padding: 0.65rem 0.95rem;
        height: auto;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(90deg, rgba(124, 247, 212, 0.18), rgba(116, 165, 255, 0.18));
    }

    @media (max-width: 900px) {
        .title-xl {
            max-width: none;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

hero_left, hero_right = st.columns([1.28, 0.92], vertical_alignment="center")

with hero_left:
    st.markdown(
        """
        <div class="hero-grid">
            <div class="eyebrow">Jarvis Career Studio</div>
            <h1 class="title-xl">Less clutter. Better prep. Stronger interviews.</h1>
            <div class="hero-copy">
                Analyze your resume once, keep the insights pinned, search roles in a dedicated area,
                and practice with Jarvis in a cleaner interview cockpit.
            </div>
            <div class="hero-pills">
                <div class="hero-pill">Resume intelligence</div>
                <div class="hero-pill">Job radar</div>
                <div class="hero-pill">Voice interview coach</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with hero_right:
    render_svg_banner()

top_left, top_mid, top_right = st.columns(3)
with top_left:
    render_metric("OpenAI", "Ready" if openai_ready else "Missing", "mint" if openai_ready else "gold")
with top_mid:
    render_metric("Apify", "Ready" if apify_ready else "Needs token", "blue" if apify_ready else "gold")
with top_right:
    render_metric("Resume State", "Analyzed" if st.session_state.analysis_ready else "Waiting", "mint" if st.session_state.analysis_ready else "gold")

upload_left, upload_right = st.columns([1.2, 0.8], vertical_alignment="top")
with upload_left:
    st.markdown('<div class="upload-shell">', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Upload your resume (PDF)", type=["pdf"])
    st.caption("Use a PDF with selectable text for the best extraction quality.")
    if uploaded_file is not None:
        current_id = get_resume_id(uploaded_file)
        if st.session_state.resume_id != current_id:
            reset_resume_dependent_state()
            st.session_state.resume_id = current_id
        if openai_ready:
            if st.button("Analyze Resume", use_container_width=True):
                try:
                    analyze_resume(uploaded_file)
                    st.rerun()
                except Exception as exc:
                    st.error(f"Resume analysis failed: {exc}")
        else:
            st.button("Analyze Resume", use_container_width=True, disabled=True)
    else:
        if st.session_state.resume_id is not None:
            st.session_state.resume_id = None
            reset_resume_dependent_state()
    st.markdown("</div>", unsafe_allow_html=True)

with upload_right:
    st.markdown(
        """
        <div class="status-shell">
            <div class="section-title">System Status</div>
            <div class="section-copy">The app now keeps resume analysis stable across reruns instead of recomputing everything on each interaction.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if not openai_ready:
        st.warning("OpenAI features are disabled until `OPENAI_API_KEY` is a valid `sk-...` key.")
    if not apify_ready:
        st.info("Job scraping is disabled until `APIFY_API_TOKEN` is a raw token, not a URL.")

analysis_tab, jobs_tab, coach_tab = st.tabs(["Resume Lab", "Job Radar", "Jarvis Coach"])

with analysis_tab:
    head_left, head_right = st.columns([1.1, 0.9], vertical_alignment="bottom")
    with head_left:
        st.markdown(
            """
            <div class="section-head">
                <div>
                    <div class="section-title">Analysis Deck</div>
                    <div class="section-copy">Your summary, gaps, and roadmap are separated into dedicated cards for faster reading.</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with head_right:
        st.markdown(
            """
            <div class="side-image">
                <svg viewBox="0 0 420 180" xmlns="http://www.w3.org/2000/svg">
                    <rect x="18" y="18" width="384" height="144" rx="24" fill="rgba(255,255,255,0.03)" stroke="rgba(158,178,207,0.18)"/>
                    <rect x="46" y="42" width="110" height="96" rx="18" fill="rgba(116,165,255,0.10)" stroke="rgba(116,165,255,0.2)"/>
                    <rect x="182" y="42" width="82" height="18" rx="9" fill="rgba(124,247,212,0.85)"/>
                    <rect x="182" y="76" width="168" height="14" rx="7" fill="rgba(233,240,250,0.22)"/>
                    <rect x="182" y="102" width="144" height="14" rx="7" fill="rgba(233,240,250,0.16)"/>
                    <rect x="182" y="128" width="108" height="14" rx="7" fill="rgba(244,201,107,0.42)"/>
                </svg>
            </div>
            """,
            unsafe_allow_html=True,
        )

    card_a, card_b, card_c = st.columns(3, vertical_alignment="top")
    with card_a:
        render_insight_card("Resume Summary", st.session_state.summary, "insight-summary")
    with card_b:
        render_insight_card("Skill Gaps", st.session_state.gaps, "insight-gap")
    with card_c:
        render_insight_card("Career Roadmap", st.session_state.roadmap, "insight-roadmap")

with jobs_tab:
    st.markdown(
        """
        <div class="section-head">
            <div>
                <div class="section-title">Job Radar</div>
                <div class="section-copy">Role search is now isolated from the resume and coaching workflow so it no longer clutters the main view.</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    tool_col, hint_col = st.columns([0.9, 1.1], vertical_alignment="top")
    with tool_col:
        st.markdown('<div class="jobs-toolbar">', unsafe_allow_html=True)
        st.text_input("Generated search keywords", value=st.session_state.job_keywords, disabled=True)
        if st.button(
            "Find Matching Jobs",
            use_container_width=True,
            disabled=not (st.session_state.analysis_ready and openai_ready and apify_ready),
        ):
            try:
                with st.spinner("Mapping resume summary to job keywords and fetching roles..."):
                    generate_jobs()
                st.rerun()
            except Exception as exc:
                st.error(f"Job recommendation failed: {exc}")
        st.markdown("</div>", unsafe_allow_html=True)
    with hint_col:
        st.markdown(
            """
            <div class="prompt-card">
                <div class="prompt-tag">How this works</div>
                Your resume summary is translated into search keywords, then LinkedIn and Naukri roles are fetched into separate columns.
            </div>
            """,
            unsafe_allow_html=True,
        )

    jobs_left, jobs_right = st.columns(2, vertical_alignment="top")
    with jobs_left:
        st.markdown('<div class="section-title">LinkedIn Matches</div>', unsafe_allow_html=True)
        if st.session_state.linkedin_jobs:
            for job in st.session_state.linkedin_jobs:
                render_job_card(job, "link", "LinkedIn")
        else:
            st.info("No LinkedIn results loaded yet.")
    with jobs_right:
        st.markdown('<div class="section-title">Naukri Matches</div>', unsafe_allow_html=True)
        if st.session_state.naukri_jobs:
            for job in st.session_state.naukri_jobs:
                render_job_card(job, "url", "Naukri")
        else:
            st.info("No Naukri results loaded yet.")

with coach_tab:
    reactor_talking = bool(st.session_state.jarvis_is_talking and st.session_state.jarvis_reply_audio)
    st.markdown(
        """
        <div class="section-head">
            <div>
                <div class="section-title">Jarvis Command Deck</div>
                <div class="section-copy">A HUD-style interview cockpit inspired by your reference: central reactor, side telemetry, and a cleaner command console.</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    top_hud_left, top_hud_mid, top_hud_right = st.columns([0.9, 1.3, 0.9], vertical_alignment="top")

    with top_hud_left:
        st.markdown(
            f"""
            <div class="jarvis-panel mini-hud">
                <div class="mini-hud-card">
                    <div class="hud-label">System</div>
                    <div class="mini-hud-value">{'ONLINE' if openai_ready else 'LIMITED'}</div>
                </div>
                <div class="mini-hud-card">
                    <div class="hud-label">Resume Feed</div>
                    <div class="mini-hud-value">{'LOCKED' if st.session_state.analysis_ready else 'STANDBY'}</div>
                </div>
                <div class="mini-hud-card">
                    <div class="hud-label">Voice Channel</div>
                    <div class="mini-hud-value">{'SPEAKING' if reactor_talking else ('READY' if openai_ready else 'OFFLINE')}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with top_hud_mid:
        st.markdown(
            f"""
            <div class="jarvis-stage">
                <div class="reactor-shell {'talking' if reactor_talking else ''}">
                    <svg viewBox="0 0 520 520" class="reactor-svg" xmlns="http://www.w3.org/2000/svg">
                        <defs>
                            <radialGradient id="coreGlow" cx="50%" cy="50%" r="50%">
                                <stop offset="0%" stop-color="#dffcff"/>
                                <stop offset="35%" stop-color="#6ff5ff"/>
                                <stop offset="75%" stop-color="#1b8eff"/>
                                <stop offset="100%" stop-color="#09101d"/>
                            </radialGradient>
                            <linearGradient id="ringGlow" x1="0%" y1="0%" x2="100%" y2="100%">
                                <stop offset="0%" stop-color="#7cf7d4"/>
                                <stop offset="100%" stop-color="#74a5ff"/>
                            </linearGradient>
                        </defs>
                        <circle class="reactor-ring" cx="260" cy="260" r="214" fill="none" stroke="rgba(255,255,255,0.14)" stroke-width="2"/>
                        <circle class="reactor-ring-fast" cx="260" cy="260" r="184" fill="none" stroke="rgba(116,165,255,0.22)" stroke-width="5"/>
                        <circle class="reactor-ring" cx="260" cy="260" r="152" fill="none" stroke="url(#ringGlow)" stroke-width="10" opacity="0.85"/>
                        <circle cx="260" cy="260" r="126" fill="rgba(5,16,29,0.70)" stroke="rgba(255,255,255,0.18)" stroke-width="2"/>
                        <circle class="reactor-glow" cx="260" cy="260" r="98" fill="rgba(124,247,212,0.06)"/>
                        <polygon class="reactor-core" points="260,132 362,316 158,316" fill="url(#coreGlow)" stroke="rgba(255,255,255,0.34)" stroke-width="6"/>
                        <circle class="reactor-core" cx="260" cy="260" r="52" fill="rgba(217,252,255,0.22)" stroke="rgba(255,255,255,0.6)" stroke-width="3"/>
                        <circle class="reactor-core" cx="260" cy="260" r="18" fill="#effdff"/>
                        <path class="reactor-ring-fast" d="M118 260 A142 142 0 0 1 402 260" fill="none" stroke="rgba(255,255,255,0.4)" stroke-width="4" stroke-dasharray="6 12"/>
                        <path class="reactor-ring" d="M146 348 A168 168 0 0 0 374 348" fill="none" stroke="rgba(124,247,212,0.55)" stroke-width="4" stroke-dasharray="5 10"/>
                        <circle cx="260" cy="260" r="232" fill="none" stroke="rgba(124,247,212,0.16)" stroke-width="1"/>
                    </svg>
                    <div class="reactor-caption">{'Jarvis speaking' if reactor_talking else 'Jarvis neural core'}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with top_hud_right:
        st.markdown(
            f"""
            <div class="jarvis-panel mini-hud">
                <div class="mini-hud-card">
                    <div class="hud-label">Interview Mode</div>
                    <div class="mini-hud-value">Adaptive</div>
                </div>
                <div class="mini-hud-card">
                    <div class="hud-label">Chat Memory</div>
                    <div class="mini-hud-value">{len(st.session_state.jarvis_history)} exchanges</div>
                </div>
                <div class="mini-hud-card">
                    <div class="hud-label">Role Focus</div>
                    <div class="mini-hud-value">{'Resume-based' if st.session_state.analysis_ready else 'Generic'}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    coach_left, coach_right = st.columns([1.25, 0.75], vertical_alignment="top")

    with coach_left:
        st.markdown('<div class="console-box">', unsafe_allow_html=True)
        st.markdown('<div class="hud-label">Conversation Console</div>', unsafe_allow_html=True)
        st.markdown('<div class="chat-shell">', unsafe_allow_html=True)
        if st.session_state.jarvis_history:
            for item in st.session_state.jarvis_history:
                render_chat(item["role"], item["content"])
        else:
            render_chat("assistant", "Jarvis online. Ask for mock interviews, answer critiques, STAR rewrites, salary prep, or role-specific questioning.")

        if st.session_state.jarvis_reply_audio:
            st.audio(st.session_state.jarvis_reply_audio, format="audio/mp3")
            st.session_state.jarvis_is_talking = False
        st.markdown("</div>", unsafe_allow_html=True)

        st.text_area(
            "Command input",
            key="jarvis_prompt",
            height=130,
            placeholder="Example: Simulate a data engineer interview and challenge me on trade-offs in my projects.",
        )
        voice_clip = st.audio_input("Voice uplink")
        send_col, voice_col = st.columns(2)
        with send_col:
            send_text = st.button("Execute Text Command", use_container_width=True, disabled=not openai_ready)
        with voice_col:
            send_voice = st.button("Execute Voice Command", use_container_width=True, disabled=not openai_ready)
        st.markdown("</div>", unsafe_allow_html=True)

        if send_text:
            try:
                run_jarvis(st.session_state.jarvis_prompt)
                st.session_state.jarvis_prompt = ""
                st.rerun()
            except Exception as exc:
                st.error(f"Jarvis failed: {exc}")

        if send_voice:
            if voice_clip is None:
                st.warning("Record a voice clip first.")
            else:
                try:
                    transcript = transcribe_audio(voice_clip)
                    run_jarvis(transcript)
                    st.session_state.jarvis_prompt = ""
                    st.rerun()
                except Exception as exc:
                    st.error(f"Voice coaching failed: {exc}")

    with coach_right:
        st.markdown(
            """
            <div class="prompt-card">
                <div class="prompt-tag">Mission Modes</div>
                Run fast drills, generate stronger introductions, or push Jarvis into a one-question-at-a-time interview loop.
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Launch HR Simulation", use_container_width=True, disabled=not openai_ready):
            try:
                run_jarvis("Start a mock HR interview based on my resume. Ask one question at a time and wait for my answer.")
                st.rerun()
            except Exception as exc:
                st.error(f"Jarvis failed: {exc}")
        if st.button("Launch Technical Drill", use_container_width=True, disabled=not openai_ready):
            try:
                run_jarvis("Start a technical interview based on my resume projects and skills. Ask one question at a time.")
                st.rerun()
            except Exception as exc:
                st.error(f"Jarvis failed: {exc}")
        if st.button("Forge My Intro", use_container_width=True, disabled=not openai_ready):
            try:
                run_jarvis("Write and coach me through a strong 60-second interview introduction based on my resume.")
                st.rerun()
            except Exception as exc:
                st.error(f"Jarvis failed: {exc}")
        if st.button("Clear Console", use_container_width=True):
            st.session_state.jarvis_history = []
            st.session_state.jarvis_reply_audio = None
            st.session_state.jarvis_prompt = ""
            st.session_state.jarvis_is_talking = False
            st.rerun()
