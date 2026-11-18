import streamlit as st
from auth import show_auth_page
from instructions import show_instructions
from resume import resume_module
from interview import interview_module
from hr_panel import hr_panel
from results import show_results

# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="SMART HIRE AI",
    page_icon="🎯",
    layout="wide"
)

# ---------- GLOBAL STYLE SYSTEM ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');

html, body, [data-testid="stAppViewContainer"] {
    font-family: 'Outfit', -apple-system, BlinkMacSystemFont, sans-serif;
    background: radial-gradient(circle at 50% 50%, #0f172a 0%, #090d16 100%) !important;
    color: #F8FAFC !important;
    overflow-x: hidden;
}

.stApp {
    background: transparent !important;
}

/* --- Trendy SaaS background mesh blobs --- */
body::before {
    content: "";
    position: fixed;
    top: -10%;
    left: -10%;
    width: 50%;
    height: 50%;
    background: radial-gradient(circle, rgba(99, 102, 241, 0.15) 0%, transparent 70%);
    z-index: -2;
    filter: blur(80px);
    animation: floatBlob1 25s infinite alternate ease-in-out;
    pointer-events: none;
}
body::after {
    content: "";
    position: fixed;
    bottom: -10%;
    right: -10%;
    width: 50%;
    height: 50%;
    background: radial-gradient(circle, rgba(6, 182, 212, 0.12) 0%, transparent 70%);
    z-index: -2;
    filter: blur(80px);
    animation: floatBlob2 30s infinite alternate ease-in-out;
    pointer-events: none;
}
@keyframes floatBlob1 {
    0% { transform: translate(0, 0) scale(1); }
    100% { transform: translate(10%, 8%) scale(1.15); }
}
@keyframes floatBlob2 {
    0% { transform: translate(0, 0) scale(1.15); }
    100% { transform: translate(-10%, -8%) scale(0.9); }
}

/* --- Smooth Element Slide-in / Page Load Animation --- */
@keyframes slideUpFade {
    from {
        opacity: 0;
        transform: translateY(15px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}
[data-testid="stAppViewContainer"] .main .block-container {
    animation: slideUpFade 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

/* --- High-End Glassmorphism Card Containers with diagonal shine & neon hover --- */
div[data-testid="stVerticalBlock"] > div[style*="border: 1px solid"] {
    background: rgba(30, 41, 59, 0.38) !important;
    backdrop-filter: blur(20px) !important;
    border: 1px solid rgba(255, 255, 255, 0.06) !important;
    border-radius: 20px !important;
    padding: 30px !important;
    box-shadow: 0 10px 35px 0 rgba(0, 0, 0, 0.25) !important;
    position: relative !important;
    overflow: hidden !important;
    transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1) !important;
}

div[data-testid="stVerticalBlock"] > div[style*="border: 1px solid"]:hover {
    transform: translateY(-4px) scale(1.005) !important;
    border-color: rgba(6, 182, 212, 0.35) !important;
    box-shadow: 0 15px 40px 0 rgba(6, 182, 212, 0.12), 0 0 15px rgba(6, 182, 212, 0.05) !important;
}

/* Sweeping visual reflection shine */
div[data-testid="stVerticalBlock"] > div[style*="border: 1px solid"]::before {
    content: '' !important;
    position: absolute !important;
    top: 0 !important;
    left: -150% !important;
    width: 60% !important;
    height: 100% !important;
    background: linear-gradient(to right, rgba(255, 255, 255, 0) 0%, rgba(255, 255, 255, 0.03) 50%, rgba(255, 255, 255, 0) 100%) !important;
    transform: skewX(-25deg) !important;
    transition: 0.85s !important;
    pointer-events: none !important;
}
div[data-testid="stVerticalBlock"] > div[style*="border: 1px solid"]:hover::before {
    left: 150% !important;
}

/* --- Trendy Styled Metric card overrides --- */
div[data-testid="metric-container"] {
    background: rgba(15, 23, 42, 0.35) !important;
    border: 1px solid rgba(255, 255, 255, 0.05) !important;
    border-radius: 14px !important;
    padding: 15px 20px !important;
    box-shadow: inset 0 1px 1px rgba(255, 255, 255, 0.05) !important;
    transition: all 0.3s ease !important;
}
div[data-testid="metric-container"]:hover {
    border-color: rgba(99, 102, 241, 0.3) !important;
    box-shadow: 0 5px 15px rgba(99, 102, 241, 0.08) !important;
}

/* --- Action Buttons (Teal-Indigo gradients with neon pulsing glow) --- */
.stButton>button, .stDownloadButton>button {
    background: linear-gradient(135deg, #4f46e5 0%, #06b6d4 100%) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 14px !important;
    padding: 12px 24px !important;
    font-weight: 700 !important;
    box-shadow: 0 4px 15px rgba(6, 182, 212, 0.15) !important;
    transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1) !important;
    width: 100% !important;
    text-transform: uppercase;
    letter-spacing: 1px;
}
.stButton>button:hover, .stDownloadButton>button:hover {
    transform: translateY(-3px) !important;
    box-shadow: 0 8px 25px rgba(6, 182, 212, 0.4), 0 0 15px rgba(99, 102, 241, 0.2) !important;
    background: linear-gradient(135deg, #5b53e8 0%, #08c2df 100%) !important;
}
.stButton>button:active, .stDownloadButton>button:active {
    transform: translateY(1px) !important;
}

/* --- Glowing Inputs & Dropdowns --- */
.stTextInput input, .stSelectbox [data-baseweb="select"] {
    background-color: rgba(15, 23, 42, 0.6) !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-radius: 12px !important;
    color: #F8FAFC !important;
    padding: 10px 14px !important;
    transition: all 0.3s ease !important;
}
.stTextInput input:focus, .stSelectbox [data-baseweb="select"]:focus {
    border-color: #06b6d4 !important;
    box-shadow: 0 0 15px rgba(6, 182, 212, 0.25) !important;
}

/* --- Gradient Progress Bars --- */
div[data-testid="stProgress"] > div > div {
    background: linear-gradient(90deg, #4f46e5 0%, #00adb5 100%) !important;
    border-radius: 10px !important;
}

/* --- Slim Neon Custom Scrollbars --- */
::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}
::-webkit-scrollbar-track {
    background: rgba(15, 23, 42, 0.5);
}
::-webkit-scrollbar-thumb {
    background: rgba(6, 182, 212, 0.3);
    border-radius: 4px;
}
::-webkit-scrollbar-thumb:hover {
    background: rgba(6, 182, 212, 0.5);
}

/* --- Dividers --- */
hr {
    border: 0;
    height: 1px;
    background: linear-gradient(to right, rgba(255, 255, 255, 0), rgba(255, 255, 255, 0.1), rgba(255, 255, 255, 0)) !important;
    margin: 24px 0 !important;
}

/* --- Dynamic Shifting Title Gradient --- */
@keyframes textShine {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}
.glowing-title {
    background: linear-gradient(120deg, #00ADB5, #6366f1, #06b6d4, #00ADB5) !important;
    background-size: 200% auto !important;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    animation: textShine 5s linear infinite !important;
    font-weight: 800;
}
</style>
""", unsafe_allow_html=True)

# ---------- SESSION ----------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "stage" not in st.session_state:
    st.session_state.stage = "login"

# ---------- HEADER ----------
col1, col2 = st.columns([1, 6])

with col1:
    try:
        st.image("logo.png", width=80)
    except:
        st.markdown("<h1 style='text-align: center; margin: 0; font-size: 50px;'>🤖</h1>", unsafe_allow_html=True)

with col2:
    st.markdown("<h1 class='glowing-title' style='margin:0; font-size: 40px;'>SMART HIRE AI</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#94A3B8; margin:0; font-size: 16px; font-weight: 500;'>AI-Powered Adaptive Recruitment Platform</p>", unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

# ---------- MAIN ----------
if not st.session_state.logged_in:
    show_auth_page()

else:
    # ---------- SINGLE-ATTEMPT ENFORCEMENT ----------
    if st.session_state.role == "Applicant":
        import sqlite3
        with sqlite3.connect("interview.db", timeout=30.0, check_same_thread=False) as conn_temp:
            conn_temp.execute("PRAGMA journal_mode=WAL;")
            cursor_temp = conn_temp.cursor()
            cursor_temp.execute("SELECT 1 FROM final_results WHERE user_id=?", (st.session_state.user_id,))
            if cursor_temp.fetchone():
                st.session_state.stage = "completed"
                st.session_state.already_taken = True

    # ---------- SIDEBAR ----------
    st.sidebar.markdown(
        f"""
        <div style="background: rgba(30, 41, 59, 0.5); padding: 15px; border-radius: 12px; border: 1px solid rgba(255, 255, 255, 0.1); margin-bottom: 20px;">
            <h4 style="margin: 0; color: #94A3B8; font-size: 12px; text-transform: uppercase;">Active Session</h4>
            <h2 style="margin: 5px 0 0 0; color: #00ADB5; font-size: 18px; font-weight: 600;">👤 {st.session_state.username}</h2>
            <span style="font-size: 11px; padding: 2px 8px; background: rgba(0, 173, 181, 0.2); border-radius: 20px; color: #00ADB5; font-weight: bold; border: 1px solid rgba(0,173,181,0.3); margin-top: 5px; display: inline-block;">{st.session_state.role}</span>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    st.sidebar.markdown("### Navigation")
    
    # ---------- APPLICANT NAVIGATION VIEW ----------
    if st.session_state.role != "HR Admin":
        stages_ui = {
            "instructions": "📋 Instructions",
            "resume": "📄 Resume Upload",
            "interview": "🎤 Live Interview"
        }
        keys = list(stages_ui.keys())
        curr_idx = keys.index(st.session_state.stage) if st.session_state.stage in keys else (999 if st.session_state.stage == "completed" else -1)

        for stg, label in stages_ui.items():
            is_active = st.session_state.stage == stg
            bg_color = "rgba(6, 182, 212, 0.15)" if is_active else "transparent"
            border_color = "rgba(6, 182, 212, 0.4)" if is_active else "transparent"
            color = "#00ADB5" if is_active else "#94A3B8"
            show_check = curr_idx > keys.index(stg)

            st.sidebar.markdown(
                f"""
                <div style="background: {bg_color}; border: 1px solid {border_color}; padding: 10px 15px; border-radius: 8px; margin-bottom: 8px; color: {color}; font-weight: 600;">
                    {label} {"✓" if show_check else ""}
                </div>
                """,
                unsafe_allow_html=True
            )
    else:
        st.sidebar.markdown(
            """
            <div style="background: rgba(99, 102, 241, 0.15); border: 1px solid rgba(99, 102, 241, 0.4); padding: 10px 15px; border-radius: 8px; color: #6366F1; font-weight: 600;">
                💼 View Candidate Dash
            </div>
            """,
            unsafe_allow_html=True
        )

    st.sidebar.markdown("<br><hr>", unsafe_allow_html=True)
    
    # ---------- LOGOUT ----------
    if st.sidebar.button("🚪 Logout", key="logout_btn"):
        st.session_state.clear()
        st.rerun()

    # ---------- FLOW ROUTER ----------
    if st.session_state.role == "HR Admin":
        # Database Role Validation to prevent session state tampering
        import sqlite3
        is_verified_admin = False
        try:
            with sqlite3.connect("interview.db", timeout=30.0, check_same_thread=False) as conn_verify:
                conn_verify.execute("PRAGMA journal_mode=WAL;")
                c_verify = conn_verify.cursor()
                db_role = c_verify.execute(
                    "SELECT role FROM users WHERE user_id=?", 
                    (st.session_state.get("user_id", ""),)
                ).fetchone()
                if db_role and db_role[0] == "HR Admin":
                    is_verified_admin = True
        except Exception:
            pass

        if is_verified_admin:
            hr_panel()
        else:
            st.session_state.clear()
            st.error("Access Denied: Security role verification failed. Session terminated.")
            st.toast("Security violation: Session terminated.", icon="🚨")
            st.rerun()
    else:
        if st.session_state.stage == "instructions":
            show_instructions()
        elif st.session_state.stage == "resume":
            resume_module()
        elif st.session_state.stage == "interview":
            interview_module()
        elif st.session_state.stage == "completed":
            if st.session_state.get("already_taken", False):
                st.markdown(
                    """
                    <div style="background: rgba(239, 68, 68, 0.15); border: 1px solid rgba(239, 68, 68, 0.4); padding: 18px; border-radius: 16px; text-align: center; margin-bottom: 25px;">
                        <h3 style="color:#EF4444; margin:0; font-weight: 800; font-size: 18px;">⚠️ MULTIPLE INTERVIEWS BLOCKED</h3>
                        <p style="color:#CBD5E1; margin: 8px 0 0 0; font-size: 14px;">You have already submitted an assessment response for this position. Re-taking the interview is strictly prohibited.</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            
            st.markdown(
                """
                <div style="background: rgba(16, 185, 129, 0.05); border: 1px solid rgba(16, 185, 129, 0.25); padding: 45px 35px; border-radius: 24px; text-align: center; margin-top: 30px; box-shadow: 0 15px 35px rgba(16, 185, 129, 0.04); position: relative; overflow: hidden;">
                    <div style="font-size: 60px; margin-bottom: 20px;">🎉</div>
                    <h1 style="color:#10B981; margin:0; font-size: 34px; font-weight: 800; letter-spacing: -0.5px;">Assessment Completed!</h1>
                    <p style="color:#F8FAFC; margin: 15px 0 0 0; font-size:18px; font-weight: 500;">Your interview has been recorded and submitted successfully.</p>
                    <p style="color:#94A3B8; margin: 10px 0 0 0; font-size:14px; max-width: 550px; margin-left: auto; margin-right: auto; line-height: 1.5;">
                        The HR recruitment panel will review your automated evaluation report and get in touch with you shortly. You may now close this window or log out.
                    </p>
                    <hr style="margin: 25px 0 !important; opacity: 0.1;">
                    <div style="display: inline-flex; align-items: center; gap: 8px; padding: 10px 20px; background: rgba(15, 23, 42, 0.45); border-radius: 12px; border: 1px solid rgba(255,255,255,0.05); color: #94A3B8; font-size: 12px; font-weight: 600; letter-spacing: 0.5px; text-transform: uppercase;">
                        🔒 Session Securely Sealed • Response Stream Closed
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            # Query database for final results
            import sqlite3
            import json
            
            recom, growth_roadmap_str, comm_score, tech_score, apt_score, code_score, beh_score, skills_str, applied_domain = None, None, 0, 0, 0, 0, 0, "", ""
            try:
                with sqlite3.connect("interview.db", timeout=30.0, check_same_thread=False) as conn_db:
                    conn_db.execute("PRAGMA journal_mode=WAL;")
                    cursor = conn_db.cursor()
                    res = cursor.execute("""
                        SELECT recommendation, growth_roadmap, comm_score, tech_score, apt_score, code_score, behavioral_score, skills, applied_domain
                        FROM final_results 
                        WHERE user_id = ?
                    """, (st.session_state.user_id,)).fetchone()
                    if res:
                        recom, growth_roadmap_str, comm_score, tech_score, apt_score, code_score, beh_score, skills_str, applied_domain = res
            except Exception as e:
                pass

            if recom == "Rejected" and growth_roadmap_str:
                roadmap = {}
                try:
                    roadmap = json.loads(growth_roadmap_str)
                except Exception:
                    pass
                
                if roadmap:
                    st.markdown("<hr>", unsafe_allow_html=True)
                    st.markdown("<h2 class='glowing-title' style='font-size: 28px; text-align: center; margin: 20px 0 5px 0;'>🌱 AI Candidate Growth & Personal Development Portal</h2>", unsafe_allow_html=True)
                    st.markdown("<p style='color: #94A3B8; text-align: center; margin-bottom: 30px; font-size: 15px;'>Your assessment is securely saved. Explore your diagnostic insights, custom checklist, study guide, and live coding sandbox below.</p>", unsafe_allow_html=True)
                    
                    tab_gaps, tab_plan, tab_resources, tab_exercises, tab_letter = st.tabs([
                        "📊 Skills Diagnostic & Gaps", 
                        "📅 4-Week Custom Plan", 
                        "📚 Study Guide & Resources", 
                        "💡 Practice Sandbox & Challenges", 
                        "✉️ Mentor Encouragement"
                    ])
                    
                    with tab_gaps:
                        st.write("")
                        st.markdown("<h3 style='color: #00ADB5;'>📊 Performance Diagnostic Dashboard</h3>", unsafe_allow_html=True)
                        
                        # High-End Glassmorphic Metrics Columns
                        cols_scores = st.columns(5)
                        metrics_list = [
                            ("Communication", comm_score, "#6366F1"),
                            ("Technical CS", tech_score, "#00ADB5"),
                            ("Aptitude", apt_score, "#EC4899"),
                            ("Coding Logic", code_score, "#10B981"),
                            ("NLP Confidence", beh_score, "#F59E0B")
                        ]
                        
                        for col, (name, val, color) in zip(cols_scores, metrics_list):
                            with col:
                                st.markdown(
                                    f"""
                                    <div style="background: rgba(30, 41, 59, 0.4); border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 16px; padding: 15px; text-align: center; border-top: 4px solid {color};">
                                        <span style="font-size: 11px; color:#94A3B8; text-transform:uppercase; font-weight:700;">{name}</span>
                                        <h2 style="margin:8px 0 0 0; color:{color}; font-weight:800; font-size:24px;">{val:.1f}%</h2>
                                    </div>
                                    """,
                                    unsafe_allow_html=True
                                )
                        
                        st.write("")
                        st.write("")
                        
                        # Gaps Analysis Section
                        with st.container(border=True):
                            st.markdown("#### 🧠 AI Knowledge & Concept Gaps Analysis")
                            st.write(roadmap.get("gaps_analysis", "The assessment logs show developing proficiency in core areas. Structured training is recommended to boost accuracy under pressure."))
                            
                            # Skills parsed
                            if skills_str:
                                st.write("")
                                st.markdown("##### Extracted Skill Profile:")
                                s_pills = ""
                                for s in skills_str.split(", "):
                                    if s.strip():
                                        s_pills += f'<span style="background: rgba(99, 102, 241, 0.1); border: 1px solid rgba(99, 102, 241, 0.3); padding: 2px 8px; border-radius: 20px; color: #6366F1; font-size: 11px; font-weight: bold; margin-right: 5px; display: inline-block; margin-top: 5px;">{s.strip().upper()}</span>'
                                st.markdown(s_pills, unsafe_allow_html=True)
                                
                    with tab_plan:
                        st.write("")
                        st.markdown("<h3 style='color: #6366F1;'>📅 4-Week Step-by-Step Action Plan</h3>", unsafe_allow_html=True)
                        st.markdown("<p style='color: #94A3B8; font-size: 14px;'>Check off each target milestone as you complete it during your 4-week growth journey.</p>", unsafe_allow_html=True)
                        
                        weekly_plan = roadmap.get("weekly_plan", [])
                        if not weekly_plan:
                            st.info("Your custom weekly checklist is being finalized.")
                        else:
                            for idx, week_item in enumerate(weekly_plan):
                                with st.container(border=True):
                                    st.markdown(f"#### 📌 {week_item.get('week', f'Week {idx+1}')}")
                                    st.markdown(f"<p style='color:#94A3B8; font-size: 13.5px; font-style: italic; margin-top: -5px;'>Focus: {week_item.get('focus', '')}</p>", unsafe_allow_html=True)
                                    
                                    # Topics Pills
                                    t_pills = ""
                                    for t in week_item.get("topics", []):
                                        t_pills += f'<span style="display:inline-block; background:rgba(6,182,212,0.1); border:1px solid rgba(6,182,212,0.25); color:#a5f3fc; padding:2px 8px; border-radius:10px; font-size:11px; margin-right:5px; margin-top:5px; font-weight:600;">{t}</span>'
                                    if t_pills:
                                        st.markdown(f"<div style='margin-bottom: 12px;'>{t_pills}</div>", unsafe_allow_html=True)
                                    
                                    # Interactive Checklist
                                    for action_idx, action in enumerate(week_item.get("action_items", [])):
                                        st.checkbox(action, key=f"user_check_{idx}_{action_idx}")
                                        
                    with tab_resources:
                        st.write("")
                        st.markdown("<h3 style='color: #06B6D4;'>📚 Recommended Learning Resources</h3>", unsafe_allow_html=True)
                        st.markdown("<p style='color: #94A3B8; font-size: 14px;'>Top hand-picked academic and practical resources to accelerate your development.</p>", unsafe_allow_html=True)
                        
                        resources = roadmap.get("recommended_resources", [])
                        if not resources:
                            st.info("No resources parsed.")
                        else:
                            # Render resources grid
                            r_cols = st.columns(len(resources) if len(resources) > 0 else 1)
                            for col, r in zip(r_cols, resources):
                                with col:
                                    with st.container(border=True):
                                        st.markdown(f"<span style='font-size:10px; padding:2px 8px; background:rgba(6,182,212,0.15); color:#06b6d4; border-radius:4px; font-weight:bold; text-transform:uppercase;'>{r.get('type', 'Resource')}</span>", unsafe_allow_html=True)
                                        st.markdown(f"##### {r.get('name', 'Learning Guide')}")
                                        st.caption(r.get("url_or_desc", ""))
                                        
                    with tab_exercises:
                        st.write("")
                        st.markdown("<h3 style='color: #EC4899;'>💡 Practice Exercises & Coding Sandbox</h3>", unsafe_allow_html=True)
                        
                        exercises = roadmap.get("custom_exercises", [])
                        if not exercises:
                            st.info("Practice exercises are currently loading.")
                        else:
                            st.markdown("#### 🎯 Custom Target Challenges")
                            for ex_idx, ex in enumerate(exercises):
                                with st.container(border=True):
                                    diff = ex.get("difficulty", "Medium")
                                    diff_color = "#10B981" if "easy" in diff.lower() else ("#F59E0B" if "medium" in diff.lower() else "#EF4444")
                                    st.markdown(
                                        f"""
                                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                                            <h5 style="margin:0; font-weight:bold;">🛠️ {ex.get('title', 'Coding Challenge')}</h5>
                                            <span style="font-size: 10px; padding: 2px 8px; background: {diff_color}22; color: {diff_color}; border-radius: 4px; font-weight: bold; border: 1px solid {diff_color}44;">{diff}</span>
                                        </div>
                                        """,
                                        unsafe_allow_html=True
                                    )
                                    st.write(ex.get("description", ""))
                            
                            st.write("")
                            st.markdown("---")
                            st.markdown("#### 💻 Live Interactive Python Sandbox")
                            st.caption("Write and run your solutions below. Compiles and executes code locally using secure stdout captures.")
                            
                            sandbox_code = st.text_area(
                                "Python Code Editor", 
                                value="def solve():\n    # Write your solution here\n    print('Hello, Sandbox!')\n\nsolve()", 
                                height=150, 
                                key="sandbox_code_field"
                            )
                            
                            if st.button("🚀 Run Code Solution", key="btn_run_sandbox"):
                                if not sandbox_code.strip():
                                    st.warning("Please enter some Python code before compilation.")
                                else:
                                    with st.spinner("Compiling and executing in isolated sandbox..."):
                                        from sandbox import run_python_sandbox
                                        success, output = run_python_sandbox(sandbox_code, timeout=5.0)
                                        if success:
                                            st.success("✅ Code Execution Successful!")
                                            if output:
                                                st.code(f"Console Output:\n{output}", language="python")
                                            else:
                                                st.info("Code executed successfully with no output to stdout.")
                                        else:
                                            st.error(f"{output}")
                                            
                    with tab_letter:
                        st.write("")
                        st.markdown("<h3 style='color: #F59E0B;'>✉️ Encouragement & Recruiter Note</h3>", unsafe_allow_html=True)
                        
                        with st.container(border=True):
                            st.markdown(f"##### Dear {st.session_state.username},")
                            st.write(roadmap.get("encouragement", "Every successful developer and leader started with foundational practice. Take this roadmap as a strategic blueprint to level-up your coding, language, and quantitative skills, and make your next assessment a triumph."))
                            st.write("")
                            st.markdown(
                                """
                                <p style="font-size:13.5px; color:#94A3B8; margin-top:20px; line-height:1.5;">
                                    Best of luck on your career journey,<br>
                                    <strong>AI Talent Acquisition & Mentor</strong><br>
                                    Smart Hire Platform
                                </p>
                                """,
                                unsafe_allow_html=True
                            )