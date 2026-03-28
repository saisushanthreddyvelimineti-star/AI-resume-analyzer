import streamlit as st
from src.helper import extract_text_from_pdf, ask_openai
from src.job_api import fetch_linkedin_jobs, fetch_naukri_jobs



st.set_page_config(page_title="Job Recommender", layout="wide")
st.title("🤖AI Job Recommender")
st.markdown("Upload your resume and get Job recommendations based on your skills and experience from Linkedin and Naukri.")

uploaded_file = st.file_uploader("Upload your resume (pdf)", type=["pdf"])

if uploaded_file:
    with st.spinner("Extracting text from your resume..."):
        resume_text = extract_text_from_pdf(uploaded_file)
    
    with st.spinner("Summeraizing your resume..."):
        summary = ask_openai(f"Summarize this resume highlighting the skills, education, and experience: \n\n{resume_text}", max_tokens = 500)

    with st.spinner("Finding skill Gaps..."):
        gaps = ask_openai(f"Analyze this resume and highlight missing skills, certificate, and experience needed for better job opportunities: \n\n{resume_text}", max_tokens = 400)

    with st.spinner("Creating Future Roadmap..."):
        roadmap = ask_openai(f"Based on this resume, suggest a future roadmap to improve this person's career prospects(skills to learn, certification needed, industry exposure): \n\n{resume_text}", max_tokens = 400)
    
    import streamlit as st

st.set_page_config(page_title="AI Resume Analyzer", layout="wide")

# ------------------ GLOBAL STYLING ------------------
st.markdown("""
<style>

/* Background Gradient */
.stApp {
    background: linear-gradient(135deg, #0f172a, #1e3a8a, #312e81);
    color: white;
}

/* Glass Card */
.glass-card {
    background: rgba(255, 255, 255, 0.06);
    padding: 25px;
    border-radius: 16px;
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    box-shadow: 0 8px 32px rgba(0,0,0,0.4);
    margin-bottom: 20px;
}

/* Titles */
.section-title {
    font-size: 22px;
    font-weight: 600;
    margin-bottom: 12px;
    background: linear-gradient(90deg, #60A5FA, #A78BFA);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

/* Header */
.main-header {
    font-size: 36px;
    font-weight: 700;
    background: linear-gradient(90deg, #38BDF8, #A78BFA);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

/* Resume-style panel */
.resume-box {
    background: rgba(255,255,255,0.08);
    padding: 20px;
    border-left: 4px solid #60A5FA;
    border-radius: 10px;
    line-height: 1.7;
}

/* Metric Cards */
.metric-card {
    background: rgba(255,255,255,0.07);
    padding: 15px;
    border-radius: 12px;
    text-align: center;
}

/* Small text */
.subtle {
    color: #cbd5f5;
    font-size: 14px;
}

</style>
""", unsafe_allow_html=True)

# ------------------ HEADER ------------------
st.markdown("<div class='main-header'>🚀 AI Resume Analyzer</div>", unsafe_allow_html=True)
st.markdown("<div class='subtle'>Smart insights to improve your resume & land better jobs</div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ------------------ METRICS ------------------
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="metric-card">
        <h2>85%</h2>
        <div class="subtle">ATS Score</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="metric-card">
        <h2>72%</h2>
        <div class="subtle">Skill Match</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="metric-card">
        <h2>Medium</h2>
        <div class="subtle">Profile Strength</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ------------------ MAIN LAYOUT ------------------
col_left, col_right = st.columns([2, 1])

# -------- LEFT (Resume-style insights) --------
with col_left:

    st.markdown("""
    <div class="glass-card">
        <div class="section-title">🤖 Resume Summary</div>
        <div class="resume-box">{}</div>
    </div>
    """.format(summary), unsafe_allow_html=True)

    st.markdown("""
    <div class="glass-card">
        <div class="section-title">🛠️ Skill Gaps</div>
        <div class="resume-box">{}</div>
    </div>
    """.format(gaps), unsafe_allow_html=True)

    st.markdown("""
    <div class="glass-card">
        <div class="section-title">🚀 Career Roadmap</div>
        <div class="resume-box">{}</div>
    </div>
    """.format(roadmap), unsafe_allow_html=True)


# -------- RIGHT (Visual + Resume feel) --------
with col_right:

    st.markdown("""
    <div class="glass-card">
        <div class="section-title">📊 Skill Strength</div>
    </div>
    """, unsafe_allow_html=True)

    st.progress(80, text="Python")
    st.progress(70, text="Machine Learning")
    st.progress(50, text="System Design")
    st.progress(40, text="Cloud")

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("""
    <div class="glass-card">
        <div class="section-title">🎯 Quick Suggestions</div>
        <ul>
            <li>Improve project descriptions</li>
            <li>Add measurable impact</li>
            <li>Use ATS keywords</li>
            <li>Include GitHub links</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    if st.button("🔍 get Job Recommendation"):
        with st.spinner("Feteching job recommendation..."):
            keywords = ask_openai(f"Based on this resume summary, suggest the best job titles and keywords for searching job. Given a comma seperated list only, no explanation.: \n\nSummary : {summary}", max_tokens = 100)
        
            search_keywords_clean = keywords.replace("\n", "").strip()

        st.success(f"Extracted Job Keywords: {search_keywords_clean}")

        with st.spinner("Fetching jobs from LinkedIn and Naukri..."):
            linkedin_jobs = fetch_linkedin_jobs(search_keywords_clean, rows= 60)
            naukri_jobs = fetch_naukri_jobs(search_keywords_clean, rows=60)

        st.markdown("---")
        st.header("💼 Top LinkedIn Jobs")

        if linkedin_jobs:
            for job in linkedin_jobs:
                st.markdown(f"💥💥{job.get('title')}💥💥 at 💥{job.get('companyName')}💥")
                st.markdown(f"- 📍 {job.get('location')}")
                st.markdown(f"- 🔗[View Job]({job.get('link')})")
                st.markdown("---")
        else:
            st.warning("No LinkedIn jobs found.")

        st.markdown("---")
        st.header("💼 Top Naukri Jobs")

        if naukri_jobs:
            for job in naukri_jobs:
                st.markdown(f"💥💥{job.get('title')}💥💥 at 💥{job.get('companyName')}💥")
                st.markdown(f"- 📍 {job.get('location')}")
                st.markdown(f"- 🔗[View Job]({job.get('url')})")
                st.markdown("---")

        else:
            st.warning("No Naukri jobs found.")


        




    
    


        
