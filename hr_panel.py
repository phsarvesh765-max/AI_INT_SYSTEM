import streamlit as st
import sqlite3
import pandas as pd
import os
import html
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors

# =====================================================
# CONSOLIDATED PDF REPORT GENERATOR (Relational Architecture)
# =====================================================
def generate_report(username):
    file_name = f"{username}_assessment_report.pdf"
    doc = SimpleDocTemplate(file_name, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Title'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#0F172A'),
        spaceAfter=15
    )
    h1_style = ParagraphStyle(
        'H1_Header',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=colors.HexColor('#00ADB5'),
        spaceBefore=15,
        spaceAfter=10,
        keepWithNext=True
    )
    h2_style = ParagraphStyle(
        'H2_Header',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        textColor=colors.HexColor('#6366F1'),
        spaceBefore=10,
        spaceAfter=6,
        keepWithNext=True
    )
    body_style = ParagraphStyle(
        'Body_Text',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor('#334155'),
        spaceAfter=6
    )
    code_style = ParagraphStyle(
        'Code_Text',
        parent=styles['Code'],
        fontName='Courier',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor('#0F172A'),
        spaceAfter=6
    )
    italic_style = ParagraphStyle(
        'Italic_Text',
        parent=body_style,
        fontStyle='Oblique',
        textColor=colors.HexColor('#64748B')
    )

    elements = []

    # Retrieve all relational tables data for the candidate
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
            
        final_res = None
        r1_data = []
        r2_data = []
        r3_data = []
        r4_data = []
        feedback_data = None
        
        if user_id:
            final_res = cursor.execute("SELECT skills, comm_score, tech_score, apt_score, code_score, behavioral_score, recommendation, timestamp, applied_domain, alternative_domain, alternative_reason FROM final_results WHERE user_id=?", (user_id,)).fetchone()
            r1_data = cursor.execute("""
                SELECT q.question_text, r.transcript, r.score, r.confidence_score, q.question_type, r.is_follow_up, r.parent_question, r.knowledge_gap_noted
                FROM r1_hr_intro r
                INNER JOIN questions q ON r.question_id = q.question_id
                WHERE r.user_id=? 
                ORDER BY r.id ASC
            """, (user_id,)).fetchall()
            
            r2_data = cursor.execute("""
                SELECT q.question_type, q.question_text, r.selected_answer, q.correct_answer, r.transcript, r.score, r.remarks 
                FROM r2_english_comm r
                INNER JOIN questions q ON r.question_id = q.question_id
                WHERE r.user_id=? 
                ORDER BY r.id ASC
            """, (user_id,)).fetchall()
            
            r3_data = cursor.execute("""
                SELECT q.question_text, r.selected_answer, q.correct_answer, r.score, q.subject_category 
                FROM r3_technical_mcq r
                INNER JOIN questions q ON r.question_id = q.question_id
                WHERE r.user_id=? 
                ORDER BY r.id ASC
            """, (user_id,)).fetchall()
            
            r4_data = cursor.execute("""
                SELECT q.question_type, q.question_text, r.selected_answer, q.correct_answer, r.code_submitted, r.language, r.execution_output, r.score 
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

    if not final_res:
        return None

    skills, comm, tech, apt, code, beh, recommendation, timestamp, applied_domain, alternative_domain, alternative_reason = final_res
    overall_avg = (comm + tech + apt + code + beh) / 5.0

    # Header Panel
    elements.append(Paragraph("SMART HIRE AI — CANDIDATE ASSESSMENT REPORT", title_style))
    elements.append(Paragraph(f"<b>Candidate:</b> {html.escape(username)} | <b>Evaluated On:</b> {timestamp}", body_style))
    elements.append(Paragraph(f"<b>Resume extracted skillset:</b> {html.escape(skills or 'General Software Engineering')}", body_style))
    elements.append(Spacer(1, 10))

    # Consolidated Metrics Grid Table
    metrics_data = [
        [
            Paragraph("<b>Assessment Metric</b>", body_style),
            Paragraph("<b>Score (%)</b>", body_style),
            Paragraph("<b>Status Benchmarking</b>", body_style)
        ],
        [Paragraph("Communication round", body_style), f"{comm:.1f}%", "Strong Fluency" if comm >= 75 else "Competent" if comm >= 50 else "Requires Brush-up"],
        [Paragraph("Technical CS (DBMS/OS/CN)", body_style), f"{tech:.1f}%", "High Command" if tech >= 75 else "Foundational" if tech >= 50 else "Developing"],
        [Paragraph("Aptitude (Quantitative/Logical)", body_style), f"{apt:.1f}%", "Sharp Reasoner" if apt >= 75 else "Adequate" if apt >= 50 else "Needs Work"],
        [Paragraph("Coding round (Logic & Compilation)", body_style), f"{code:.1f}%", "Solid Engineer" if code >= 75 else "Basic Coder" if code >= 50 else "Developing"],
        [Paragraph("Behavioral (NLP Confidence & Scenarios)", body_style), f"{beh:.1f}%", "High Alignment" if beh >= 75 else "Acceptable" if beh >= 50 else "Developing"],
        [Paragraph("<b>CONSOLIDATED AVERAGE INDEX</b>", body_style), f"<b>{overall_avg:.1f}%</b>", f"<b>VERDICT: {recommendation.upper()}</b>"]
    ]
    
    t = Table(metrics_data, colWidths=[200, 100, 200])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#F1F5F9')),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#ECFDF5') if recommendation == 'Selected' else colors.HexColor('#FFFBEB') if recommendation == 'Average' else colors.HexColor('#FEF2F2')),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 15))

    # AI Career Path Matcher Verdict Section
    if alternative_domain and alternative_reason:
        elements.append(Paragraph("AI CAREER PATH MATCHER VERDICT", h1_style))
        verdict_text = (
            f"<b>Applied Domain:</b> {html.escape(applied_domain or 'General Software Engineering')}<br/>"
            f"<b>Alternative Career Suggestion:</b> <b>{html.escape(alternative_domain)}</b><br/><br/>"
            f"<b>AI Recommendation Rationale:</b> {html.escape(alternative_reason)}"
        )
        verdict_p = Paragraph(verdict_text, body_style)
        verdict_table = Table([[verdict_p]], colWidths=[520])
        verdict_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#FFFBEB')), # Sleek warm cream background
            ('BORDER', (0,0), (-1,-1), 1, colors.HexColor('#F59E0B')), # Elegant amber border
            ('TOPPADDING', (0,0), (-1,-1), 10),
            ('BOTTOMPADDING', (0,0), (-1,-1), 10),
            ('LEFTPADDING', (0,0), (-1,-1), 15),
            ('RIGHTPADDING', (0,0), (-1,-1), 15),
        ]))
        elements.append(verdict_table)
        elements.append(Spacer(1, 15))

    # Round 1 Section
    elements.append(Paragraph("Round 1 — Introduction Round (Spoken)", h1_style))
    if not r1_data:
        elements.append(Paragraph("No evaluation records exist for Round 1.", italic_style))
    else:
        for idx, r in enumerate(r1_data):
            q_text, trans, score, conf, q_type, is_follow_up, parent_q, gap_noted = r
            q_esc = html.escape(q_text)
            trans_esc = html.escape(trans)
            
            if is_follow_up:
                parent_esc = html.escape(parent_q or "")
                elements.append(Paragraph(f"<b>Q{idx+1} [AI Stress Test Probe] (Targeting Claim on \"{parent_esc}\"):</b> {q_esc}", h2_style))
                elements.append(Paragraph(f"<i>Transcribed Probed Answer:</i> \"{trans_esc}\"", body_style))
                elements.append(Paragraph(f"Score: <b>{score:.1f}/6.0</b> | Speech Confidence: <b>{conf:.1f}/10.0</b>", body_style))
                
                if gap_noted:
                    gap_esc = html.escape(gap_noted)
                    # Styled table with soft-red background (#FEF2F2) and red border (#EF4444) to mark gaps clearly
                    gap_table_data = [
                        [Paragraph("<b>⚠️ AI STRESS TEST & KNOWLEDGE GAP ANALYSIS</b>", ParagraphStyle('RedTitle', parent=h2_style, textColor=colors.HexColor('#EF4444')))],
                        [Paragraph(f"<b>Noted Gap:</b> {gap_esc}", body_style)]
                    ]
                    gap_table = Table(gap_table_data, colWidths=[460])
                    gap_table.setStyle(TableStyle([
                        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#FEF2F2')),
                        ('BORDER', (0,0), (-1,-1), 1.5, colors.HexColor('#EF4444')),
                        ('TOPPADDING', (0,0), (-1,-1), 8),
                        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
                        ('LEFTPADDING', (0,0), (-1,-1), 12),
                        ('RIGHTPADDING', (0,0), (-1,-1), 12),
                    ]))
                    elements.append(Spacer(1, 4))
                    elements.append(gap_table)
                    elements.append(Spacer(1, 6))
                else:
                    elements.append(Spacer(1, 4))
            else:
                elements.append(Paragraph(f"<b>Q{idx+1} ({q_type}):</b> {q_esc}", h2_style))
                elements.append(Paragraph(f"<i>Transcribed Answer:</i> \"{trans_esc}\"", body_style))
                elements.append(Paragraph(f"Score: <b>{score:.1f}/6.0</b> | Speech Confidence: <b>{conf:.1f}/10.0</b>", body_style))
                elements.append(Spacer(1, 4))

    # Round 2 Section
    elements.append(Paragraph("Round 2 — English & Communication (MCQ + Verbal Scenarios)", h1_style))
    if not r2_data:
        elements.append(Paragraph("No evaluation records exist for Round 2.", italic_style))
    else:
        r2_mcq = [r for r in r2_data if r[0] == 'MCQ']
        r2_voice = [r for r in r2_data if r[0] == 'Voice']

        if r2_mcq:
            elements.append(Paragraph("<b>Section A: English Grammar & Vocabulary MCQs</b>", h2_style))
            for idx, r in enumerate(r2_mcq):
                _, q, sel, corr, _, score, _ = r
                q_esc = html.escape(q)
                sel_esc = html.escape(sel)
                corr_esc = html.escape(corr)
                status = "Correct" if score > 0 else "Incorrect"
                elements.append(Paragraph(f"Q{idx+1}: {q_esc}<br/>Selection: <b>{sel_esc}</b> | Correct: <b>{corr_esc}</b> ({status})", body_style))
                elements.append(Spacer(1, 3))

        if r2_voice:
            elements.append(Paragraph("<b>Section B: Verbal Behavioral Scenarios</b>", h2_style))
            for idx, r in enumerate(r2_voice):
                _, q, _, _, trans, score, remarks = r
                q_esc = html.escape(q)
                trans_esc = html.escape(trans)
                rem_esc = html.escape(remarks or "N/A")
                elements.append(Paragraph(f"Scenario {idx+1}: {q_esc}", body_style))
                elements.append(Paragraph(f"<i>Transcribed Response:</i> \"{trans_esc}\"", body_style))
                elements.append(Paragraph(f"Score: <b>{score:.1f}/6.0</b> | <i>AI Remarks:</i> {rem_esc}", body_style))
                elements.append(Spacer(1, 4))

    # Round 3 Section
    elements.append(Paragraph("Round 3 — Technical MCQ Round (DBMS, OS, Networks)", h1_style))
    if not r3_data:
        elements.append(Paragraph("No evaluation records exist for Round 3.", italic_style))
    else:
        for idx, r in enumerate(r3_data):
            q, sel, corr, score, cat = r
            q_esc = html.escape(q)
            sel_esc = html.escape(sel)
            corr_esc = html.escape(corr)
            status = "Correct" if score > 0 else "Incorrect"
            elements.append(Paragraph(f"<b>Q{idx+1} [{cat.upper()}]:</b> {q_esc}<br/>Selection: <b>{sel_esc}</b> | Correct: <b>{corr_esc}</b> ({status})", body_style))
            elements.append(Spacer(1, 3))

    # Round 4 Section
    elements.append(Paragraph("Round 4 — Aptitude & Coding Round", h1_style))
    if not r4_data:
        elements.append(Paragraph("No evaluation records exist for Round 4.", italic_style))
    else:
        r4_apt = [r for r in r4_data if r[0] == 'Aptitude']
        r4_code = [r for r in r4_data if r[0] == 'Coding']

        if r4_apt:
            elements.append(Paragraph("<b>Section A: Numerical & Analytical Aptitude MCQs</b>", h2_style))
            for idx, r in enumerate(r4_apt):
                _, q, sel, corr, _, _, _, score = r
                q_esc = html.escape(q)
                sel_esc = html.escape(sel)
                corr_esc = html.escape(corr)
                status = "Correct" if score > 0 else "Incorrect"
                elements.append(Paragraph(f"Q{idx+1}: {q_esc}<br/>Selection: <b>{sel_esc}</b> | Correct: <b>{corr_esc}</b> ({status})", body_style))
                elements.append(Spacer(1, 3))

        if r4_code:
            elements.append(Paragraph("<b>Section B: Programming Challenges</b>", h2_style))
            for idx, r in enumerate(r4_code):
                _, q, _, _, code_sub, lang, exec_out, score = r
                q_esc = html.escape(q)
                lang_esc = html.escape(lang or 'unknown')
                code_esc = html.escape(code_sub or '')
                out_esc = html.escape(exec_out or 'No output generated.')
                elements.append(Paragraph(f"<b>Task {idx+1}:</b> {q_esc} (Language: <b>{lang_esc.upper()}</b>)", body_style))
                elements.append(Paragraph("<b>Submitted Solution Code:</b>", body_style))
                elements.append(Paragraph(code_esc.replace('\n', '<br/>').replace(' ', '&nbsp;'), code_style))
                elements.append(Paragraph(f"<b>Compiler Execution Console Output:</b><br/><i>{out_esc}</i>", body_style))
                elements.append(Paragraph(f"Coding Score: <b>{score:.1f}/6.0</b>", body_style))
                elements.append(Spacer(1, 6))

    # Candidate Feedback Section
    if feedback_data:
        elements.append(Paragraph("Candidate Platform Feedback Review", h1_style))
        ov_r, ov_c, r1_r, r2_r, r3_r, r4_r, rd_c = feedback_data
        elements.append(Paragraph(f"Overall Experience: <b>{ov_r}/5 Stars</b> | Platform Feedback: \"{html.escape(ov_c or '')}\"", body_style))
        elements.append(Paragraph(f"Round Ratings: Intro: <b>{r1_r}/5</b> | Comm: <b>{r2_r}/5</b> | Tech MCQ: <b>{r3_r}/5</b> | Aptitude: <b>{r4_r}/5</b>", body_style))
        elements.append(Paragraph(f"Round Structure Remarks: \"{html.escape(rd_c or '')}\"", body_style))

    doc.build(elements)
    return file_name

# =====================================================
# ADMIN HR RECRUITMENT CONTROL PANEL
# =====================================================
def hr_panel():
    st.markdown(
        """
        <style>
        /* Custom style for delete button to make it stand out as a danger action */
        .delete-btn-container button {
            background: linear-gradient(135deg, #dc2626 0%, #991b1b 100%) !important;
            box-shadow: 0 4px 15px rgba(220, 38, 38, 0.2) !important;
            border: none !important;
            font-weight: 700 !important;
        }
        .delete-btn-container button:hover {
            background: linear-gradient(135deg, #ef4444 0%, #b91c1c 100%) !important;
            box-shadow: 0 8px 25px rgba(220, 38, 38, 0.4) !important;
        }
        </style>
        <div style='text-align: center; margin-bottom: 25px;'>
            <h1 class='glowing-title' style='margin:0; font-size:32px;'>💼 AI Recruitment Control Panel</h1>
            <p style='color:#94A3B8; margin:5px 0 0 0;'>Track candidate performance benchmarks, review ratings, explore feedback insights, and print assessments</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Fetch rows from the relational tables
    with sqlite3.connect("interview.db", timeout=30.0, check_same_thread=False) as conn_db:
        conn_db.execute("PRAGMA journal_mode=WAL;")
        cursor_db = conn_db.cursor()
        
        candidates = cursor_db.execute("""
            SELECT u.username, f.skills, f.comm_score, f.tech_score, f.apt_score, f.code_score, f.behavioral_score, f.recommendation, f.timestamp,
                   f.applied_domain, f.alternative_domain, f.alternative_reason, f.growth_roadmap, f.email_sent, u.email
            FROM users u
            INNER JOIN final_results f ON u.user_id = f.user_id
            WHERE u.role = 'Applicant'
        """).fetchall()

    if not candidates:
        st.markdown(
            """
            <div style="background: rgba(245, 158, 11, 0.1); border: 1px solid rgba(245, 158, 11, 0.3); padding: 25px; border-radius: 12px; text-align: center; margin-top: 20px;">
                <h3 style="color:#F59E0B; margin:0; font-size:20px; font-weight:700;">📋 No Completed Assessments Found</h3>
                <p style="color:#94A3B8; margin:10px 0 0 0; font-size:15px;">No candidates have completed and sealed their 4-round AI assessments yet.</p>
                <p style="color:#64748B; font-size:13.5px; margin:5px 0 0 0;">Candidates must submit the final post-interview feedback form to appear here.</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        return

    cdf = pd.DataFrame(
        candidates,
        columns=["User", "Skills", "CommScore", "TechScore", "AptScore", "CodeScore", "BehScore", "Recommendation", "Timestamp",
                 "AppliedDomain", "AlternativeDomain", "AlternativeReason", "GrowthRoadmap", "EmailSent", "Email"]
    )
    cdf["OverallAvg"] = (cdf["CommScore"] + cdf["TechScore"] + cdf["AptScore"] + cdf["CodeScore"] + cdf["BehScore"]) / 5.0

    # Top Metrics Cards
    total_reviewed = len(cdf)
    avg_composite_score = round(cdf["OverallAvg"].mean(), 1)
    selected_count = len(cdf[cdf["Recommendation"] == 'Selected'])
    avg_count = len(cdf[cdf["Recommendation"] == 'Average'])
    rejected_count = len(cdf[cdf["Recommendation"] == 'Rejected'])

    # Grid columns
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("👥 Candidates Reviewed", total_reviewed)
    with m2:
        st.metric("⭐ Average Composite", f"{avg_composite_score}%")
    with m3:
        st.metric("✅ Strongly Selected", selected_count)
    with m4:
        st.metric("❌ Not Recommended", rejected_count)

    st.write("")
    st.markdown("<hr style='margin: 10px 0;'>", unsafe_allow_html=True)

    # Tabs: Candidates list & Feedback Insights
    tab_list, tab_feedback = st.tabs(["👨‍💼 Candidate Profiles & Grades", "📊 Candidate Feedback Insights"])

    with tab_list:
        st.write("")
        st.subheader("🔍 Filters & Search")
        
        c1, c2, c3 = st.columns(3)
        with c1:
            search = st.text_input("Search Candidate Name", placeholder="Enter candidate name...", key="search_cname")
        with c2:
            # Collect unique skills dynamically
            all_skills = set()
            for s_str in cdf["Skills"].dropna():
                for s in s_str.split(", "):
                    if s.strip():
                        all_skills.add(s.strip().upper())
            skill_filter = st.selectbox("Filter By Skillset Match", ["ALL"] + sorted(list(all_skills)), key="skill_sel")
        with c3:
            sort_opt = st.selectbox("Sort Order", ["Highest Score", "Lowest Score"], key="sort_sel")

        # Career switch recommendations filter
        show_switches_only = st.checkbox("🎯 Show Career Switch Recommendations Only", key="switch_only_sel")

        # Filtering logic
        filtered_df = cdf.copy()
        if search:
            filtered_df = filtered_df[filtered_df["User"].str.contains(search, case=False)]
        if skill_filter != "ALL":
            filtered_df = filtered_df[filtered_df["Skills"].fillna("").str.upper().str.contains(skill_filter)]
        if show_switches_only:
            filtered_df = filtered_df[filtered_df["AlternativeDomain"].notna() & (filtered_df["AlternativeDomain"] != "")]
            
        if sort_opt == "Highest Score":
            filtered_df = filtered_df.sort_values(by="OverallAvg", ascending=False)
        else:
            filtered_df = filtered_df.sort_values(by="OverallAvg", ascending=True)

        # Performance Graph
        st.write("")
        with st.container(border=True):
            st.markdown("<h3 style='margin:0 0 15px 0; font-size:16px; color:#94A3B8;'>📈 Candidate Multidimensional Score Comparison (%)</h3>", unsafe_allow_html=True)
            if not filtered_df.empty:
                chart_data = filtered_df[["User", "CommScore", "TechScore", "AptScore", "CodeScore", "BehScore"]].set_index("User")
                st.bar_chart(chart_data)
            else:
                st.info("No candidates match criteria to plot.")

        st.write("")
        st.markdown("<hr style='margin:10px 0;'>", unsafe_allow_html=True)
        st.subheader("👨‍💻 Candidate Assessment Profile Records")

        def render_candidate_card(row, is_selected):
            with st.container(border=True):
                hcol1, hcol2 = st.columns([4, 1])
                with hcol1:
                    st.markdown(f"<h2 style='margin:0; color:#00ADB5;'>👤 {row['User']}</h2>", unsafe_allow_html=True)
                    
                    # Show applied career domain
                    applied_dom = row["AppliedDomain"] if row["AppliedDomain"] else "Software Engineering"
                    st.markdown(f"<p style='margin:5px 0 10px 0; color:#E2E8F0; font-size:14px;'><strong>Applied Career Domain:</strong> {applied_dom}</p>", unsafe_allow_html=True)
                    
                    # Skills pills
                    skills_val = row["Skills"]
                    s_pills = ""
                    if skills_val:
                        for s in skills_val.split(", "):
                            if s.strip():
                                s_pills += f"""
                                <span style="background: rgba(99, 102, 241, 0.1); border: 1px solid rgba(99, 102, 241, 0.3); padding: 2px 8px; border-radius: 20px; color: #6366F1; font-size: 11px; font-weight: bold; margin-right: 5px; display: inline-block; margin-top: 5px;">
                                    {s.strip().upper()}
                                </span>
                                """
                    else:
                        s_pills = "<span style='color:#64748B; font-size:12px;'>No skills parsed</span>"
                    st.markdown(s_pills, unsafe_allow_html=True)
                    
                with hcol2:
                    st.markdown(
                        f"""
                        <div style='text-align:right;'>
                            <h2 style='margin:0; color:#06B6D4;'>{row['OverallAvg']:.1f}%</h2>
                            <span style='font-size:11px; color:#64748B; font-weight:600;'>COMPOSITE INDEX</span>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                st.write("")

                # Recommendation Alert Badge
                rec = row["Recommendation"]
                if rec == "Selected":
                    st.success(f"🎯 AI Recruitment recommendation: Strongly Selected (Average Index >= 75%)")
                elif rec == "Average":
                    st.warning(f"⚠️ AI Recruitment recommendation: Suitable / Training Recommended (Average Index >= 50%)")
                else:
                    st.error(f"❌ AI Recruitment recommendation: Developing / Not Recommended (Average Index < 50%)")

                # Alternative Career Path recommendation banner
                alt_dom = row["AlternativeDomain"]
                alt_reas = row["AlternativeReason"]
                if alt_dom and alt_reas:
                    st.markdown(f"""
                    <div style="background: rgba(245, 158, 11, 0.08); border: 1px dashed rgba(245, 158, 11, 0.4); border-left: 5px solid #F59E0B; padding: 15px; border-radius: 8px; margin: 15px 0;">
                        <span style="color:#F59E0B; font-weight:bold; font-size:13px; letter-spacing:0.5px; display:block; margin-bottom:5px;">🎯 AI CAREER PATH MATCH RECOMMENDATION</span>
                        <p style="color:#E2E8F0; font-size:13px; line-height:1.5; margin:0;">
                            This candidate has applied for <strong>{applied_dom}</strong> but their profile highlights exceptional skills better suited for <strong>{alt_dom}</strong>.
                            <br><br>
                            <strong>AI Rationale:</strong> {alt_reas}
                        </p>
                    </div>
                    """, unsafe_allow_html=True)

                st.write("")

                # Expandable detailed reports
                with st.expander("📊 View Complete Multi-Round Assessment Log"):
                    from results import show_results
                    show_results(row["User"])

                st.write("")

                # PDF download section
                pdf_path = generate_report(row["User"])
                if pdf_path and os.path.exists(pdf_path):
                    with open(pdf_path, "rb") as pdf_file:
                        st.download_button(
                            label=f"📄 Download {row['User']} Consolidated Evaluation Report (PDF)",
                            data=pdf_file,
                            file_name=pdf_path,
                            mime="application/pdf",
                            key=f"dl_pdf_admin_{row['User']}"
                        )
                else:
                    st.error("Failed to generate PDF. Check DB connections.")

                st.write("")

                # 📧 HR Communication Center
                st.markdown("<h3 style='margin: 15px 0 10px 0; font-size: 16px; color: #E2E8F0; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 5px;'>✉️ HR Communication Center</h3>", unsafe_allow_html=True)
                email_sent = row["EmailSent"]
                candidate_email = row["Email"]
                
                if email_sent == 1:
                    st.success("✅ Professional Email Dispatched Successfully! (Recruiter approved & sent)")
                else:
                    st.info(f"⏳ Candidate Notification Email Pending (Roadmap Compiled & Ready to send to: {candidate_email or 'No registered email'})")
                    
                    button_label = "📧 Dispatch Selection Confirmation Email" if is_selected else "📧 Dispatch Personalized Growth Roadmap Email"
                    btn_key = f"dispatch_mail_{row['User']}"
                    
                    if st.button(button_label, key=btn_key):
                        if not candidate_email:
                            st.error("Error: This candidate does not have a registered email address.")
                        else:
                            with st.spinner("Processing SMTP secure dispatch..."):
                                import auth
                                if is_selected:
                                    success, message = auth.send_selection_email(
                                        to_email=candidate_email,
                                        username=row["User"],
                                        overall_avg=row["OverallAvg"],
                                        applied_domain=row["AppliedDomain"] if row["AppliedDomain"] else "Software Engineering"
                                    )
                                else:
                                    success, message = auth.send_deescalation_email(
                                        to_email=candidate_email,
                                        username=row["User"],
                                        roadmap_json_str=row["GrowthRoadmap"],
                                        applied_domain=row["AppliedDomain"] if row["AppliedDomain"] else "Software Engineering"
                                    )
                                
                                if success:
                                    # Update Database
                                    with sqlite3.connect("interview.db", timeout=30.0, check_same_thread=False) as conn_db:
                                        conn_db.execute("PRAGMA journal_mode=WAL;")
                                        cursor = conn_db.cursor()
                                        u_row = cursor.execute("SELECT user_id FROM users WHERE username=?", (row['User'],)).fetchone()
                                        if u_row:
                                            user_id = u_row[0]
                                            cursor.execute("UPDATE final_results SET email_sent = 1 WHERE user_id=?", (user_id,))
                                            conn_db.commit()
                                    st.success(f"🎉 Success: {message}")
                                    st.rerun()
                                else:
                                    st.error(f"❌ SMTP Dispatch Failed: {message}")

                st.write("")

                # Danger Zone expander for candidate deletion
                with st.expander("⚠️ Danger Zone: Delete Candidate Data", expanded=False):
                    st.markdown(
                        f"""
                        <div style="background: rgba(239, 68, 68, 0.05); border: 1px solid rgba(239, 68, 68, 0.2); padding: 15px; border-radius: 12px; margin-bottom: 15px;">
                            <h4 style="color: #EF4444; margin: 0 0 8px 0; font-size: 14px; font-weight: 700;">PERMANENT DATA REMOVAL</h4>
                            <p style="color: #CBD5E1; margin: 0; font-size: 13px; line-height: 1.4;">
                                You are about to permanently delete all data for candidate <strong>{row['User']}</strong>. 
                                This will erase all assessment rounds, transcribed answers, feedback records, generated reports, and applicant credentials.
                            </p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    
                    confirm_delete = st.checkbox(
                        f"I confirm that I want to delete candidate {row['User']} and all associated records.", 
                        key=f"confirm_del_{row['User']}"
                    )
                    
                    st.markdown('<div class="delete-btn-container">', unsafe_allow_html=True)
                    if st.button("🔴 Permanently Delete Applicant Data", key=f"del_btn_{row['User']}", disabled=not confirm_delete):
                        # perform database deletion
                        with sqlite3.connect("interview.db", timeout=30.0, check_same_thread=False) as conn_db:
                            conn_db.execute("PRAGMA journal_mode=WAL;")
                            cursor = conn_db.cursor()
                            
                            # Resolve user_id first
                            u_row = cursor.execute("SELECT user_id FROM users WHERE username=?", (row['User'],)).fetchone()
                            if u_row:
                                user_id = u_row[0]
                                # Delete from all relevant tables
                                cursor.execute("DELETE FROM final_results WHERE user_id=?", (user_id,))
                                cursor.execute("DELETE FROM candidate_feedback WHERE user_id=?", (user_id,))
                                cursor.execute("DELETE FROM r1_hr_intro WHERE user_id=?", (user_id,))
                                cursor.execute("DELETE FROM r2_english_comm WHERE user_id=?", (user_id,))
                                cursor.execute("DELETE FROM r3_technical_mcq WHERE user_id=?", (user_id,))
                                cursor.execute("DELETE FROM r4_aptitude_coding WHERE user_id=?", (user_id,))
                                cursor.execute("DELETE FROM users WHERE user_id=?", (user_id,))
                                conn_db.commit()
                        
                        # Also delete the assessment report PDF file if it exists
                        report_pdf = f"{row['User']}_assessment_report.pdf"
                        if os.path.exists(report_pdf):
                            try:
                                os.remove(report_pdf)
                            except Exception:
                                pass
                        
                        st.success(f"Candidate **{row['User']}** has been completely removed from the system.")
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

        subtab_selected, subtab_rejected = st.tabs(["✅ Selected & Suitable Candidates", "❌ Non-Selected / Rejected Candidates"])
        
        with subtab_selected:
            selected_df = filtered_df[filtered_df["Recommendation"].isin(["Selected", "Average"])]
            if selected_df.empty:
                st.info("No selected or suitable candidates matching current filter criteria.")
            else:
                for _, row in selected_df.iterrows():
                    render_candidate_card(row, is_selected=True)

        with subtab_rejected:
            rejected_df = filtered_df[filtered_df["Recommendation"] == "Rejected"]
            if rejected_df.empty:
                st.info("No non-selected or rejected candidates matching current filter criteria.")
            else:
                for _, row in rejected_df.iterrows():
                    render_candidate_card(row, is_selected=False)

    # --- TAB 2: CANDIDATE FEEDBACK INSIGHTS ---
    with tab_feedback:
        st.write("")
        st.markdown("<h3 style='color:#F59E0B;'>⭐ Candidate Platform Experience Insights</h3>", unsafe_allow_html=True)
        st.write("Numerical distributions and qualitative remarks submitted by candidates upon assessment completion.")

        # Query all feedback from database
        with sqlite3.connect("interview.db", timeout=30.0, check_same_thread=False) as conn_db:
            conn_db.execute("PRAGMA journal_mode=WAL;")
            cursor = conn_db.cursor()
            
            feedbacks = cursor.execute("""
                SELECT u.username, f.overall_rating, f.overall_comments, f.r1_rating, f.r2_rating, f.r3_rating, f.r4_rating, f.round_comments, f.timestamp
                FROM users u
                INNER JOIN candidate_feedback f ON u.user_id = f.user_id
            """).fetchall()

        if not feedbacks:
            st.info("No candidate feedback has been recorded in the database yet.")
        else:
            fdf = pd.DataFrame(
                feedbacks,
                columns=["User", "OverallRating", "OverallComments", "R1Rating", "R2Rating", "R3Rating", "R4Rating", "RoundComments", "Timestamp"]
            )

            # Rating Averages
            avg_ov = round(fdf["OverallRating"].mean(), 1)
            avg_r1 = round(fdf["R1Rating"].mean(), 1)
            avg_r2 = round(fdf["R2Rating"].mean(), 1)
            avg_r3 = round(fdf["R3Rating"].mean(), 1)
            avg_r4 = round(fdf["R4Rating"].mean(), 1)

            # Glassmorphic ratings summary card
            st.markdown(
                f"""
                <div style="background: rgba(30, 41, 59, 0.25); border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 16px; padding: 20px; display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 15px; text-align: center;">
                    <div>
                        <span style="font-size: 11px; color:#94A3B8; text-transform:uppercase; font-weight:700;">Overall Rating</span>
                        <h2 style="margin:5px 0 0 0; color:#F59E0B; font-weight:800; font-size:24px;">⭐ {avg_ov} <span style="font-size:14px; color:#64748B;">/ 5</span></h2>
                    </div>
                    <div>
                        <span style="font-size: 11px; color:#94A3B8; text-transform:uppercase; font-weight:700;">R1: Intro Round</span>
                        <h2 style="margin:5px 0 0 0; color:#6366F1; font-weight:800; font-size:24px;">⭐ {avg_r1} <span style="font-size:14px; color:#64748B;">/ 5</span></h2>
                    </div>
                    <div>
                        <span style="font-size: 11px; color:#94A3B8; text-transform:uppercase; font-weight:700;">R2: English Comm</span>
                        <h2 style="margin:5px 0 0 0; color:#00ADB5; font-weight:800; font-size:24px;">⭐ {avg_r2} <span style="font-size:14px; color:#64748B;">/ 5</span></h2>
                    </div>
                    <div>
                        <span style="font-size: 11px; color:#94A3B8; text-transform:uppercase; font-weight:700;">R3: Tech MCQ</span>
                        <h2 style="margin:5px 0 0 0; color:#EC4899; font-weight:800; font-size:24px;">⭐ {avg_r3} <span style="font-size:14px; color:#64748B;">/ 5</span></h2>
                    </div>
                    <div>
                        <span style="font-size: 11px; color:#94A3B8; text-transform:uppercase; font-weight:700;">R4: Apt & Code</span>
                        <h2 style="margin:5px 0 0 0; color:#10B981; font-weight:800; font-size:24px;">⭐ {avg_r4} <span style="font-size:14px; color:#64748B;">/ 5</span></h2>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            st.write("")
            st.markdown("#### 💬 Qualitative Reviews & Suggestions")

            for _, row in fdf.iterrows():
                with st.container(border=True):
                    col_f1, col_f2 = st.columns([3, 1])
                    with col_f1:
                        st.markdown(f"👤 Candidate Name: **{row['User']}**")
                        st.markdown(f"Platform Feedback: *\"{row['OverallComments']}\"*")
                        if row["RoundComments"]:
                            st.markdown(f"Round Feedback: *\"{row['RoundComments']}\"*")
                    with col_f2:
                        st.markdown(f"**Overall Star Rating:** {'★'*int(row['OverallRating'])}{'☆'*(5-int(row['OverallRating']))}")
                        st.caption(f"Submitted: {row['Timestamp']}")

    st.write("")
    st.success("AI Recruiter Control Panel sync completed. Candidate metrics and feedback profiles updated. ✅")