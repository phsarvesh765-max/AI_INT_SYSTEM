import streamlit as st
import pdfplumber
import pandas as pd
from skills import extract_skills
import google.generativeai as genai
from PIL import Image

try:
    import os
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

try:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        try:
            api_key = st.secrets.get("GEMINI_API_KEY")
        except Exception:
            pass
    if api_key:
        genai.configure(api_key=api_key)
        gemini_model = genai.GenerativeModel(model_name="models/gemini-2.5-flash")
    else:
        gemini_model = None
except Exception:
    gemini_model = None

def resume_module():
    st.markdown(
        """
        <div style='text-align: center; margin-bottom: 25px;'>
            <h2 style='color:#00ADB5; margin:0;'>📄 Candidate Onboarding</h2>
            <p style='color:#94A3B8; margin:5px 0 0 0;'>Select your career domain and submit your professional PDF profile</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Glassmorphic Form Card
    with st.container(border=True):
        st.markdown("<h3 style='color:#F8FAFC; font-size:18px; margin: 0 0 15px 0;'>1. Position Domain</h3>", unsafe_allow_html=True)
        
        domains = [
            "Artificial Intelligence", "Machine Learning", "Data Science",
            "Web Development", "Cyber Security", "Cloud Computing",
            "Software Engineering", "Mobile App Development", "Blockchain",
            "DevOps", "Game Development", "UI/UX Design",
            "Database Management", "Networking", "Embedded Systems",
            "Big Data", "Robotics", "IoT",
            "AR/VR", "Digital Marketing", "Business Analytics",
            "Full Stack Development", "Backend Development",
            "Frontend Development", "Testing & QA", "System Design"
        ]

        # Initialize default index of selectbox if not set
        if "domain_selectbox" not in st.session_state:
            st.session_state.domain_selectbox = "Software Engineering"

        # Calculate matching index in domains list
        try:
            default_idx = domains.index(st.session_state.domain_selectbox)
        except ValueError:
            default_idx = 6  # Fallback to Software Engineering

        domain = st.selectbox("🎯 Select Target Job Domain", domains, index=default_idx, key="domain_selectbox_widget")
        st.session_state.domain_selectbox = domain
        st.session_state.domain = domain

    st.write("")

    with st.container(border=True):
        st.markdown("<h3 style='color:#F8FAFC; font-size:18px; margin: 0 0 15px 0;'>2. Upload Document</h3>", unsafe_allow_html=True)
        file = st.file_uploader(
            "Upload Resume (PDF, DOCX, TXT, or Image)", 
            type=["pdf", "docx", "txt", "png", "jpg", "jpeg"], 
            label_visibility="collapsed"
        )

        if file:
            text = ""
            file_extension = file.name.split(".")[-1].lower()
            with st.spinner("Analyzing document structure and extracting technical details..."):
                if file_extension == "pdf":
                    with pdfplumber.open(file) as pdf:
                        for p in pdf.pages:
                            text += p.extract_text() or ""
                elif file_extension == "docx":
                    import docx
                    doc = docx.Document(file)
                    text = "\n".join([para.text for para in doc.paragraphs])
                elif file_extension == "txt":
                    text = file.read().decode("utf-8", errors="ignore")
                elif file_extension in ["png", "jpg", "jpeg"]:
                    if gemini_model:
                        try:
                            img = Image.open(file)
                            prompt = """
                            You are an expert ATS resume reader and parsing system.
                            Extract all text written on this resume image.
                            Return only the extracted text exactly as it is, without any markdown formatting, wrappers, commentary, or headers.
                            """
                            response = gemini_model.generate_content([prompt, img])
                            text = response.text or ""
                        except Exception as e:
                            st.error(f"Failed to extract text from the image: {e}")
                            st.stop()
                    else:
                        st.error("📷 Image OCR extraction requires Gemini AI connection. Please upload a PDF, DOCX, or TXT file instead.")
                        st.stop()

            # Extract Skills
            clean_text = text.lower()
            skills = extract_skills(clean_text)

            st.write("")
            st.markdown("<h3 style='color:#F8FAFC; font-size:18px; margin: 0 0 15px 0;'>🔍 Skill Detection Results</h3>", unsafe_allow_html=True)

            if skills:
                # Store for interview
                st.session_state.skills = skills

                # Beautiful Tags Grid with custom stylesheet
                st.markdown("""
                <style>
                .skill-tag-pill {
                    background: rgba(6, 182, 212, 0.08) !important;
                    border: 1px solid rgba(6, 182, 212, 0.2) !important;
                    padding: 8px 16px !important;
                    border-radius: 30px !important;
                    color: #06B6D4 !important;
                    margin: 6px !important;
                    font-weight: 600 !important;
                    font-size: 13px !important;
                    letter-spacing: 0.5px !important;
                    text-transform: uppercase !important;
                    display: inline-block !important;
                    box-shadow: 0 2px 8px rgba(6, 182, 212, 0.03) !important;
                    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
                    cursor: default !important;
                }
                .skill-tag-pill:hover {
                    transform: scale(1.12) translateY(-3px) !important;
                    background: rgba(99, 102, 241, 0.2) !important;
                    border-color: #6366f1 !important;
                    color: #ffffff !important;
                    box-shadow: 0 8px 20px rgba(99, 102, 241, 0.3), 0 0 10px rgba(6, 182, 212, 0.2) !important;
                }
                .career-suggestion-card {
                    background: linear-gradient(135deg, rgba(30, 41, 59, 0.75), rgba(15, 23, 42, 0.85)) !important;
                    border: 1px dashed rgba(245, 158, 11, 0.5) !important;
                    border-left: 5px solid #F59E0B !important;
                    border-radius: 12px !important;
                    padding: 20px !important;
                    margin: 20px 0 !important;
                    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3) !important;
                    backdrop-filter: blur(10px) !important;
                    -webkit-backdrop-filter: blur(10px) !important;
                    animation: pulseGlow 3s infinite ease-in-out !important;
                }
                @keyframes pulseGlow {
                    0% { box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3), 0 0 0px rgba(245, 158, 11, 0); }
                    50% { box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3), 0 0 15px rgba(245, 158, 11, 0.25); border-color: rgba(245, 158, 11, 0.8) !important; }
                    100% { box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3), 0 0 0px rgba(245, 158, 11, 0); }
                }
                .career-suggestion-title {
                    color: #F59E0B !important;
                    font-size: 16px !important;
                    font-weight: 700 !important;
                    margin-bottom: 8px !important;
                    display: flex !important;
                    align-items: center !important;
                    gap: 8px !important;
                    letter-spacing: 0.5px !important;
                }
                .career-suggestion-text {
                    color: #E2E8F0 !important;
                    font-size: 14px !important;
                    line-height: 1.6 !important;
                    margin: 0 !important;
                }
                </style>
                """, unsafe_allow_html=True)

                tags_html = "<div style='display: flex; flex-wrap: wrap; margin-bottom: 20px;'>"
                for s in skills:
                    tags_html += f"<span class='skill-tag-pill'>✨ {s}</span>"
                tags_html += "</div>"

                st.markdown(tags_html, unsafe_allow_html=True)
                st.success("NLP Parser successfully matched technical skills above from your profile! ✅")

                # AI Career Path Matcher Logic
                if (
                    "alternative_domain_cached" not in st.session_state 
                    or st.session_state.get("last_checked_skills") != skills 
                    or st.session_state.get("last_checked_domain") != domain
                ):
                    from skills import match_career_path
                    alt_domain, alt_reason = match_career_path(skills, domain)
                    st.session_state.alternative_domain_cached = alt_domain
                    st.session_state.alternative_reason_cached = alt_reason
                    st.session_state.last_checked_skills = skills
                    st.session_state.last_checked_domain = domain
                else:
                    alt_domain = st.session_state.alternative_domain_cached
                    alt_reason = st.session_state.alternative_reason_cached

                if alt_domain:
                    st.session_state.alternative_domain = alt_domain
                    st.session_state.alternative_reason = alt_reason
                    
                    st.markdown(f"""
                    <div class="career-suggestion-card">
                        <div class="career-suggestion-title">
                            🎯 AI CAREER PATH MATCH RECOMMENDATION
                        </div>
                        <p class="career-suggestion-text">
                            We detected that your technical skills strongly align with our <strong>{alt_domain}</strong> career track rather than your selected role.
                            <br><br>
                            <strong>AI Analysis:</strong> {alt_reason}
                        </p>
                    </div>
                    """, unsafe_allow_html=True)

                    if st.button(f"✨ SWITCH POSITION TO RECOMMENDED TRACK ({alt_domain})", use_container_width=True):
                        st.session_state.domain_selectbox = alt_domain
                        st.session_state.domain = alt_domain
                        st.session_state.alternative_domain = None
                        st.session_state.alternative_reason = None
                        st.session_state.alternative_domain_cached = None
                        st.session_state.alternative_reason_cached = None
                        st.toast(f"Switched job domain to {alt_domain}! 🚀")
                        st.rerun()
                else:
                    st.session_state.alternative_domain = None
                    st.session_state.alternative_reason = None

                st.write("")

                # Start trigger with state reset
                if st.button("🚀 ENTER LIVE INTERVIEW", use_container_width=True, key="start_interview_nav"):
                    st.session_state.stage = "interview"
                    
                    # Force reset any stale states
                    for k in ["q_index", "questions", "last_spoken", "asked_questions"]:
                        if k in st.session_state:
                            del st.session_state[k]
                    st.rerun()

            else:
                st.error("No skills from our technical dictionary were detected in your resume. Please upload a valid IT/Software Engineering resume, or check your file content.")