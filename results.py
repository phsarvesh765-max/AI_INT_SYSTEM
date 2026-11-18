import streamlit as st
import sqlite3
import os

def show_results(username):
    # Retrieve candidates final results from DB
    with sqlite3.connect("interview.db", timeout=30.0, check_same_thread=False) as conn_db:
        conn_db.execute("PRAGMA journal_mode=WAL;")
        cursor = conn_db.cursor()
        
        # Resolve username to unique user_id
        user_row = cursor.execute("SELECT user_id FROM users WHERE username=?", (username,)).fetchone()
        if not user_row:
            # Fallback if username is already user_id
            if isinstance(username, str) and username.startswith("USR-"):
                user_id = username
            else:
                user_id = None
        else:
            user_id = user_row[0]
            
            final_res = None
        if user_id:
            final_res = cursor.execute(
                "SELECT comm_score, tech_score, apt_score, code_score, behavioral_score, recommendation, timestamp, applied_domain, alternative_domain, alternative_reason FROM final_results WHERE user_id=?",
                (user_id,)
            ).fetchone()

    if not final_res:
        st.markdown(
            """
            <div style="background: rgba(30, 41, 59, 0.45); border: 1px solid rgba(255, 255, 255, 0.08); padding: 40px; border-radius: 18px; text-align: center; margin-top: 30px;">
                <h3 style="color:#00ADB5; margin:0; font-size: 24px; font-weight:700;">📊 Assessment Performance Report</h3>
                <p style="color:#94A3B8; margin: 15px 0 0 0; font-size:16px;">You don't have any completed interview records in our database.</p>
                <p style="color:#64748B; font-size:14px; margin: 5px 0 0 0;">Please proceed to the <b>Live Interview</b> section to complete the evaluation.</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        return

    # Extract final results
    comm_score, tech_score, apt_score, code_score, beh_score, recommendation, timestamp, applied_domain, alternative_domain, alternative_reason = final_res

    st.markdown(
        f"""
        <div style='text-align: center; margin-bottom: 35px;'>
            <h1 class='glowing-title' style='margin:0; font-size:32px;'>📊 Candidate Assessment Report</h1>
            <p style='color:#94A3B8; margin:5px 0 0 0;'>Detailed multi-dimensional review for <b>{username}</b> | Completed on {timestamp}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Dynamic Career Alignment Callout Box
    if alternative_domain and alternative_reason:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, rgba(30, 41, 59, 0.7), rgba(15, 23, 42, 0.8)) !important;
                    border: 1px dashed rgba(245, 158, 11, 0.4) !important;
                    border-left: 5px solid #F59E0B !important;
                    padding: 20px !important;
                    border-radius: 12px !important;
                    margin-bottom: 25px !important;
                    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2) !important;">
            <div style="color: #F59E0B !important; font-size: 15px !important; font-weight: 700 !important; margin-bottom: 8px !important; display: flex !important; align-items: center !important; gap: 8px !important; letter-spacing: 0.5px !important;">
                💡 DYNAMIC AI CAREER ALIGNMENT INSIGHT
            </div>
            <p style="color: #E2E8F0 !important; font-size: 13.5px !important; line-height: 1.5 !important; margin: 0 !important;">
                You applied for <strong>{applied_domain or 'General Software Engineering'}</strong>, but our advanced skill evaluation indicates a stellar alignment with our <strong>{alternative_domain}</strong> career track!
                <br><br>
                <strong>AI Career Counsel:</strong> {alternative_reason}
            </p>
        </div>
        """, unsafe_allow_html=True)

    # Set up recommendation style
    if recommendation == "Selected":
        rec_label = "Strongly Selected ✅"
        rec_color = "#10B981"
        rec_bg = "rgba(16, 185, 129, 0.15)"
        feedback_text = "Outstanding performance! You have demonstrated exceptional command over both technical and coding challenges, excellent analytical aptitude, and strong verbal articulation."
    elif recommendation == "Average":
        rec_label = "Suitable / Training ⚠"
        rec_color = "#F59E0B"
        rec_bg = "rgba(245, 158, 11, 0.15)"
        feedback_text = "Solid foundational candidate. Showed reasonable competency across computer science concepts and communication, but would benefit from brushing up on algorithmic coding and complex system topics."
    else:
        rec_label = "Developing / Rejected ❌"
        rec_color = "#EF4444"
        rec_bg = "rgba(239, 68, 68, 0.15)"
        feedback_text = "Further preparation recommended. Domain-specific knowledge, programming patterns, and analytical fluency require stronger development. We suggest active practice on core algorithms and CS theories."

    # 1. Performance Overview Grid
    st.markdown("### 📈 Multi-Dimensional Score Metrics")
    
    # Render progress bar styling
    def get_progress_bar(score, color_hex):
        return f"""
        <div style="background-color: rgba(255,255,255,0.05); border-radius: 10px; height: 10px; width: 100%; margin-top: 8px; overflow: hidden; border: 1px solid rgba(255,255,255,0.05);">
            <div style="background: {color_hex}; width: {score}%; height: 100%; border-radius: 10px;"></div>
        </div>
        """

    m_col1, m_col2 = st.columns([3, 1])
    
    with m_col1:
        with st.container():
            st.markdown(
                f"""
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 15px; background: rgba(30, 41, 59, 0.25); border: 1px solid rgba(255,255,255,0.05); border-radius: 16px; padding: 20px;">
                    <div>
                        <span style="font-size: 12px; color: #94A3B8; font-weight: 600; text-transform: uppercase;">🗣️ Communication</span>
                        <h3 style="margin: 5px 0 0 0; color: #6366F1; font-weight: 800; font-size: 20px;">{comm_score:.1f}%</h3>
                        {get_progress_bar(comm_score, "#6366F1")}
                    </div>
                    <div>
                        <span style="font-size: 12px; color: #94A3B8; font-weight: 600; text-transform: uppercase;">💻 Technical CS</span>
                        <h3 style="margin: 5px 0 0 0; color: #00ADB5; font-weight: 800; font-size: 20px;">{tech_score:.1f}%</h3>
                        {get_progress_bar(tech_score, "#00ADB5")}
                    </div>
                    <div>
                        <span style="font-size: 12px; color: #94A3B8; font-weight: 600; text-transform: uppercase;">⚡ Aptitude</span>
                        <h3 style="margin: 5px 0 0 0; color: #EC4899; font-weight: 800; font-size: 20px;">{apt_score:.1f}%</h3>
                        {get_progress_bar(apt_score, "#EC4899")}
                    </div>
                    <div>
                        <span style="font-size: 12px; color: #94A3B8; font-weight: 600; text-transform: uppercase;">🚀 Coding Logic</span>
                        <h3 style="margin: 5px 0 0 0; color: #10B981; font-weight: 800; font-size: 20px;">{code_score:.1f}%</h3>
                        {get_progress_bar(code_score, "#10B981")}
                    </div>
                    <div>
                        <span style="font-size: 12px; color: #94A3B8; font-weight: 600; text-transform: uppercase;">🧠 Behavioral</span>
                        <h3 style="margin: 5px 0 0 0; color: #F59E0B; font-weight: 800; font-size: 20px;">{beh_score:.1f}%</h3>
                        {get_progress_bar(beh_score, "#F59E0B")}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
            
    with m_col2:
        st.markdown(
            f"""
            <div style="background: {rec_bg}; border: 1px solid {rec_color}44; border-radius: 16px; padding: 22px; text-align: center; height: 100%; display: flex; flex-direction: column; justify-content: center; align-items: center;">
                <span style="font-size: 11px; color: #94A3B8; text-transform: uppercase; font-weight: 700; letter-spacing: 0.5px;">Recruiter Verdict</span>
                <h4 style="margin: 8px 0 0 0; color: {rec_color}; font-size: 16px; font-weight: 800;">{rec_label}</h4>
                <span style="font-size: 10px; color: #64748B; margin-top: 4px;">Index: {((comm_score+tech_score+apt_score+code_score+beh_score)/5.0):.1f}%</span>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.write("")
    
    # Feedback Insight Alert Box
    st.markdown(
        f"""
        <div style="background: rgba(30, 41, 59, 0.35); border-left: 4px solid #00ADB5; padding: 18px; border-radius: 0 12px 12px 0; margin-bottom: 30px;">
            <h4 style="margin: 0 0 5px 0; color: #00ADB5; font-size: 15px; font-weight: 700;">🧠 AI Professional Assessment Summary</h4>
            <p style="margin: 0; color: #E2E8F0; font-size: 14px; line-height: 1.5; font-style: italic;">"{feedback_text}"</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Fetch data from the relational round tables
    with sqlite3.connect("interview.db", timeout=30.0, check_same_thread=False) as conn_db:
        conn_db.execute("PRAGMA journal_mode=WAL;")
        cursor = conn_db.cursor()
        
        # Resolve username to unique user_id
        user_row = cursor.execute("SELECT user_id FROM users WHERE username=?", (username,)).fetchone()
        if not user_row:
            if isinstance(username, str) and username.startswith("USR-"):
                user_id = username
            else:
                user_id = None
        else:
            user_id = user_row[0]
            
        r1_data = []
        r2_data = []
        r3_data = []
        r4_data = []
        feedback_data = None
        
        if user_id:
            r1_data = cursor.execute("""
                SELECT q.question_text, r.transcript, r.audio_path, r.score, r.confidence_score, q.question_type, r.is_follow_up, r.parent_question, r.knowledge_gap_noted
                FROM r1_hr_intro r
                INNER JOIN questions q ON r.question_id = q.question_id
                WHERE r.user_id=? 
                ORDER BY r.id ASC
            """, (user_id,)).fetchall()
            
            r2_data = cursor.execute("""
                SELECT q.question_type, q.question_text, r.selected_answer, q.correct_answer, r.audio_path, r.transcript, r.score, r.fluency, r.pronunciation, r.confidence, r.comm_quality, r.speaking_consistency, r.remarks 
                FROM r2_english_comm r
                INNER JOIN questions q ON r.question_id = q.question_id
                WHERE r.user_id=? 
                ORDER BY r.id ASC
            """, (user_id,)).fetchall()
            
            r3_data = cursor.execute("""
                SELECT q.question_id, q.question_text, r.selected_answer, q.correct_answer, r.score, q.subject_category 
                FROM r3_technical_mcq r
                INNER JOIN questions q ON r.question_id = q.question_id
                WHERE r.user_id=? 
                ORDER BY r.id ASC
            """, (user_id,)).fetchall()
            
            r4_data = cursor.execute("""
                SELECT q.question_id, q.question_type, q.question_text, r.selected_answer, q.correct_answer, r.code_submitted, r.language, r.execution_output, r.score, r.time_taken 
                FROM r4_aptitude_coding r
                INNER JOIN questions q ON r.question_id = q.question_id
                WHERE r.user_id=? 
                ORDER BY r.id ASC
            """, (user_id,)).fetchall()
            
            feedback_data = cursor.execute("""
                SELECT overall_rating, overall_comments, r1_rating, r2_rating, r3_rating, r4_rating, round_comments 
                FROM candidate_feedback 
                WHERE user_id=?
            """, (user_id,)).fetchone()

    # Create Round Tabs
    t1, t2, t3, t4, t5 = st.tabs([
        "🎤 Round 1: Intro Round", 
        "🗣️ Round 2: English & Comm", 
        "💻 Round 3: Technical MCQ", 
        "⚡ Round 4: Aptitude & Coding",
        "⭐ Candidate Feedback"
    ])

    # Helper function to generate score stars
    def make_stars(score, max_stars=6):
        score_int = min(max_stars, max(0, int(round(score))))
        stars = "".join([f"<span style='color: #F59E0B; font-size: 18px;'>★</span>" for _ in range(score_int)])
        stars += "".join([f"<span style='color: #475569; font-size: 18px;'>★</span>" for _ in range(max_stars - score_int)])
        return stars

    # --- TAB 1: ROUND 1 ---
    with t1:
        st.markdown("<h3 style='color:#6366F1;'>🎤 Round 1 — Introduction Round</h3>", unsafe_allow_html=True)
        st.write("Verbal introduction and skill-matching questions graded for communication fluency, technical accuracy, and confidence.")
        
        if not r1_data:
            st.info("No records found for Round 1.")
        else:
            for idx, r in enumerate(r1_data):
                q_text, trans, audio, score, conf, q_type, is_follow_up, parent_q, gap_noted = r
                
                if is_follow_up:
                    col_ind, col_main = st.columns([1, 15])
                    with col_main:
                        with st.container(border=True):
                            st.markdown(
                                f"""
                                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                                    <span style="font-size: 10px; padding: 2px 8px; background: rgba(99, 102, 241, 0.15); border-radius: 20px; color: #a5b4fc; font-weight: bold; border: 1px solid rgba(99,102,241,0.25); text-transform: uppercase;">
                                        🔄 AI Stress Test Probing Question
                                    </span>
                                    <span style="font-size:12px; font-weight:600; color:#E2E8F0;">Score: {score:.1f}/6</span>
                                </div>
                                <div style="font-size:11px; color:#64748B; margin-bottom: 8px;">
                                    Targeted Probe on: <span style="font-style:italic; color:#94A3B8;">"{parent_q}"</span>
                                </div>
                                <p style='color:#818cf8; font-size:15px; font-weight:600; margin: 4px 0 10px 0;'>{q_text}</p>
                                """,
                                unsafe_allow_html=True
                            )
                            st.markdown(make_stars(score), unsafe_allow_html=True)
                            st.markdown(f"💬 *Confidence Score:* **{conf:.1f}/10**")
                            
                            # Audio Playback
                            if audio and os.path.exists(audio):
                                st.audio(audio)
                            elif audio:
                                st.caption(f"ℹ️ Recording: {audio}")
                                
                            # Transcript
                            st.markdown(
                                f"""
                                <div style="background: rgba(99, 102, 241, 0.05); border-radius: 8px; padding: 10px; border: 1px dashed rgba(99,102,241,0.15); margin-bottom: 10px;">
                                    <span style="font-size:10px; color:#818cf8; text-transform:uppercase; font-weight:700;">Transcribed Probed Answer</span>
                                    <p style="margin: 5px 0 0 0; color:#E2E8F0; font-size:13.5px; line-height:1.4; font-style:italic;">"{trans}"</p>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )
                            
                            if gap_noted:
                                st.markdown(
                                    f"""
                                    <div style="
                                        background: rgba(245, 158, 11, 0.1);
                                        border: 1px solid rgba(245, 158, 11, 0.3);
                                        border-left: 4px solid #F59E0B;
                                        padding: 12px 16px;
                                        border-radius: 6px;
                                        margin-top: 10px;
                                        box-shadow: 0 4px 12px rgba(245, 158, 11, 0.05);
                                    ">
                                        <div style="font-size: 11px; text-transform: uppercase; color: #F59E0B; font-weight: 700; letter-spacing: 0.5px;">⚠️ AI Knowledge Gap Analysis</div>
                                        <div style="font-size: 13px; color: #FFE4E6; font-weight: 500; margin-top: 4px; line-height: 1.4;">{gap_noted}</div>
                                    </div>
                                    """,
                                    unsafe_allow_html=True
                                )
                else:
                    with st.container(border=True):
                        col_q1, col_q2 = st.columns([4, 1])
                        with col_q1:
                            st.markdown(f"**QUESTION {idx+1} ({q_type} Question)**")
                            st.markdown(f"<p style='color:#00ADB5; font-size:15px; font-weight:600;'>{q_text}</p>", unsafe_allow_html=True)
                        with col_q2:
                            st.markdown(f"**Score: {score:.1f}/6**")
                            st.markdown(make_stars(score), unsafe_allow_html=True)
                        
                        st.write("")
                        st.markdown(f"💬 *Confidence Score:* **{conf:.1f}/10**")
                        
                        # Audio Playback
                        if audio and os.path.exists(audio):
                            st.audio(audio)
                        elif audio:
                            st.caption(f"ℹ️ Recording: {audio}")
                            
                        # Transcript
                        st.markdown(
                            f"""
                            <div style="background: rgba(15, 23, 42, 0.4); border-radius: 8px; padding: 10px; border: 1px solid rgba(255,255,255,0.03);">
                                <span style="font-size:10px; color:#64748B; text-transform:uppercase; font-weight:700;">Transcribed Answer</span>
                                <p style="margin: 5px 0 0 0; color:#E2E8F0; font-size:13.5px; line-height:1.4; font-style:italic;">"{trans}"</p>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

    # --- TAB 2: ROUND 2 ---
    with t2:
        st.markdown("<h3 style='color:#00ADB5;'>🗣️ Round 2 — English & Communication</h3>", unsafe_allow_html=True)
        st.write("Assessment of grammar, vocabulary, logic correction, and scenario-based communication fluency.")
        
        if not r2_data:
            st.info("No records found for Round 2.")
        else:
            r2_mcq = [r for r in r2_data if r[0] == "MCQ"]
            r2_voice = [r for r in r2_data if r[0] == "Voice"]
            
            st.markdown("#### ✍️ Section A: English MCQs")
            for idx, r in enumerate(r2_mcq):
                _, q, sel, corr, _, _, score, _, _, _, _, _, _ = r
                is_correct = score > 0
                bg = "rgba(16, 185, 129, 0.05)" if is_correct else "rgba(239, 68, 68, 0.05)"
                border = "rgba(16, 185, 129, 0.2)" if is_correct else "rgba(239, 68, 68, 0.2)"
                mark = "✅" if is_correct else "❌"
                
                st.markdown(
                    f"""
                    <div style="background: {bg}; border: 1px solid {border}; border-radius: 12px; padding: 15px; margin-bottom: 12px;">
                        <span style="font-size:10px; padding:2px 8px; background:rgba(255,255,255,0.08); border-radius:10px; color:#94A3B8; font-weight:bold;">MCQ {idx+1}</span>
                        <p style="color:#FFFFFF; font-size:14px; font-weight:600; margin: 8px 0 5px 0;">{q}</p>
                        <div style="font-size:13px; color:#CBD5E1;">
                            <span>Your Selection: <b style="color:{'#10B981' if is_correct else '#EF4444'}">{sel}</b> {mark}</span> | 
                            <span>Correct Answer: <b>{corr}</b></span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
            st.write("")
            st.markdown("#### 🎧 Section B: Verbal Behavioral Scenarios")
            for idx, r in enumerate(r2_voice):
                _, q, _, _, audio, trans, score, fluency, pron, conf, comm, cons, remarks = r
                with st.container(border=True):
                    col_b1, col_b2 = st.columns([4, 1])
                    with col_b1:
                        st.markdown(f"**SCENARIO {idx+1}**")
                        st.markdown(f"<p style='color:#00ADB5; font-size:15px; font-weight:600;'>{q}</p>", unsafe_allow_html=True)
                    with col_b2:
                        st.markdown(f"**Score: {score:.1f}/6**")
                        st.markdown(make_stars(score), unsafe_allow_html=True)
                    
                    # Metrics Grid
                    st.markdown(
                        f"""
                        <div style="display: flex; gap: 15px; flex-wrap: wrap; font-size: 12px; color: #94A3B8; margin: 8px 0;">
                            <span>Fluency: <b style="color: #6366F1;">{fluency:.1f}/6</b></span>
                            <span>Pronunciation: <b style="color: #00ADB5;">{pron:.1f}/6</b></span>
                            <span>Confidence: <b style="color: #F59E0B;">{conf:.1f}/6</b></span>
                            <span>Quality: <b style="color: #10B981;">{comm:.1f}/6</b></span>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    
                    if remarks:
                        st.info(f"💡 AI Remarks: {remarks}")
                    
                    # Audio Playback
                    if audio and os.path.exists(audio):
                        st.audio(audio)
                    elif audio:
                        st.caption(f"Recording: {audio}")
                        
                    # Transcript
                    st.markdown(
                        f"""
                        <div style="background: rgba(15, 23, 42, 0.4); border-radius: 8px; padding: 10px; border: 1px solid rgba(255,255,255,0.03);">
                            <span style="font-size:10px; color:#64748B; text-transform:uppercase; font-weight:700;">Transcribed Answer</span>
                            <p style="margin: 5px 0 0 0; color:#E2E8F0; font-size:13.5px; line-height:1.4; font-style:italic;">"{trans}"</p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

    # --- TAB 3: ROUND 3 ---
    with t3:
        st.markdown("<h3 style='color:#EC4899;'>💻 Round 3 — Technical MCQ Round</h3>", unsafe_allow_html=True)
        st.write("10 randomized computer science MCQs testing knowledge in Database Management Systems (DBMS), Operating Systems (OS), and Computer Networks (CN).")
        
        if not r3_data:
            st.info("No records found for Round 3.")
        else:
            for idx, r in enumerate(r3_data):
                q_id, q, sel, corr, score, cat = r
                is_correct = score > 0
                bg = "rgba(16, 185, 129, 0.05)" if is_correct else "rgba(239, 68, 68, 0.05)"
                border = "rgba(16, 185, 129, 0.2)" if is_correct else "rgba(239, 68, 68, 0.2)"
                mark = "✅" if is_correct else "❌"
                
                st.markdown(
                    f"""
                    <div style="background: {bg}; border: 1px solid {border}; border-radius: 12px; padding: 15px; margin-bottom: 12px;">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <span style="font-size:10px; padding:2px 8px; background:rgba(255,255,255,0.08); border-radius:10px; color:#94A3B8; font-weight:bold;">QUESTION {idx+1}</span>
                            <span style="font-size:10px; color:#EC4899; font-weight:bold; text-transform:uppercase;">🏷️ {cat}</span>
                        </div>
                        <p style="color:#FFFFFF; font-size:14px; font-weight:600; margin: 8px 0 5px 0;">{q}</p>
                        <div style="font-size:13px; color:#CBD5E1;">
                            <span>Your Selection: <b style="color:{'#10B981' if is_correct else '#EF4444'}">{sel}</b> {mark}</span> | 
                            <span>Correct Answer: <b>{corr}</b></span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    # --- TAB 4: ROUND 4 ---
    with t4:
        st.markdown("<h3 style='color:#10B981;'>⚡ Round 4 — Aptitude & Coding</h3>", unsafe_allow_html=True)
        st.write("Problem-solving speed and dynamic algorithmic coding skills compiled inside premium environments.")
        
        if not r4_data:
            st.info("No records found for Round 4.")
        else:
            r4_apt = [r for r in r4_data if r[1] == "Aptitude"]
            r4_code = [r for r in r4_data if r[1] == "Coding"]
            
            st.markdown("#### 🧠 Section A: Numerical & Analytical Aptitude")
            for idx, r in enumerate(r4_apt):
                _, _, q, sel, corr, _, _, _, score, _ = r
                is_correct = score > 0
                bg = "rgba(16, 185, 129, 0.05)" if is_correct else "rgba(239, 68, 68, 0.05)"
                border = "rgba(16, 185, 129, 0.2)" if is_correct else "rgba(239, 68, 68, 0.2)"
                mark = "✅" if is_correct else "❌"
                
                st.markdown(
                    f"""
                    <div style="background: {bg}; border: 1px solid {border}; border-radius: 12px; padding: 15px; margin-bottom: 12px;">
                        <span style="font-size:10px; padding:2px 8px; background:rgba(255,255,255,0.08); border-radius:10px; color:#94A3B8; font-weight:bold;">APTITUDE {idx+1}</span>
                        <p style="color:#FFFFFF; font-size:14px; font-weight:600; margin: 8px 0 5px 0;">{q}</p>
                        <div style="font-size:13px; color:#CBD5E1;">
                            <span>Your Selection: <b style="color:{'#10B981' if is_correct else '#EF4444'}">{sel}</b> {mark}</span> | 
                            <span>Correct Answer: <b>{corr}</b></span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
            st.write("")
            st.markdown("#### 💻 Section B: Programming Challenges")
            for idx, r in enumerate(r4_code):
                _, _, q, _, _, code, lang, out, score, time_sec = r
                with st.container(border=True):
                    col_c1, col_c2 = st.columns([4, 1])
                    with col_c1:
                        st.markdown(f"**CODING TASK {idx+1} (Language: {lang.upper()})**")
                        st.markdown(f"<p style='color:#00ADB5; font-size:14.5px; font-weight:600;'>{q}</p>", unsafe_allow_html=True)
                    with col_c2:
                        st.markdown(f"**Score: {score:.1f}/6**")
                        st.markdown(make_stars(score), unsafe_allow_html=True)
                    
                    st.caption(f"⏱️ Time Taken: {time_sec} Seconds")
                    
                    # Code Box
                    st.markdown("**Submitted Solution:**")
                    st.code(code, language=lang.lower())
                    
                    # Execution Mock Console
                    st.markdown("**Compiler Execution Console:**")
                    st.code(out if out else "No output generated.", language="text")

    # --- TAB 5: FEEDBACK ---
    with t5:
        st.markdown("<h3 style='color:#F59E0B;'>⭐ Candidate Experience Feedback</h3>", unsafe_allow_html=True)
        st.write("Feedback provided by the applicant upon completing the assessment rounds.")
        
        if not feedback_data:
            st.info("No feedback submitted yet or feedback block was skipped.")
        else:
            ov, ov_cmt, fb_r1, fb_r2, fb_r3, fb_r4, rd_cmt = feedback_data
            
            with st.container(border=True):
                st.markdown("#### 🌟 Numerical Platform Experience Scores")
                
                f_col1, f_col2 = st.columns(2)
                with f_col1:
                    st.markdown(f"**Overall Platform Rating:** {make_stars(ov, 5)} ({ov}/5)")
                    st.markdown(f"**Round 1 (Intro Round) Rating:** {make_stars(fb_r1, 5)} ({fb_r1}/5)")
                    st.markdown(f"**Round 2 (English & Comm) Rating:** {make_stars(fb_r2, 5)} ({fb_r2}/5)")
                with f_col2:
                    st.markdown(f"**Round 3 (Technical MCQ) Rating:** {make_stars(fb_r3, 5)} ({fb_r3}/5)")
                    st.markdown(f"**Round 4 (Aptitude & Coding) Rating:** {make_stars(fb_r4, 5)} ({fb_r4}/5)")
                    
                st.write("")
                st.markdown("<hr style='margin:10px 0;'>", unsafe_allow_html=True)
                st.markdown("#### 💬 Written Feedback & Comments")
                
                st.markdown(f"**Platform Experience Comments:**")
                st.info(f"\"{ov_cmt}\"" if ov_cmt else "*No overall comments submitted.*")
                
                st.markdown(f"**Round Structure & Difficulty Comments:**")
                st.info(f"\"{rd_cmt}\"" if rd_cmt else "*No round-specific comments submitted.*")

    st.write("")
    st.info("🎯 You can access your full Recruiter assessment PDF via the administrator's Dashboard. Thank you for using SMART HIRE AI.")