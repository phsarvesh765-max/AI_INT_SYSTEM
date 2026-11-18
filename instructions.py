import streamlit as st

# =====================================================
# SYSTEM & HARDWARE VERIFICATION LAYOUT
# =====================================================
def show_instructions():
    # Inject Custom CSS for modern status grids, animations, and checklists
    st.markdown(
        """
        <style>
        /* Pulse Animations */
        @keyframes pulseDotGreen {
            0% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.4); }
            70% { box-shadow: 0 0 0 10px rgba(16, 185, 129, 0); }
            100% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
        }
        @keyframes pulseDotIndigo {
            0% { box-shadow: 0 0 0 0 rgba(99, 102, 241, 0.4); }
            70% { box-shadow: 0 0 0 10px rgba(99, 102, 241, 0); }
            100% { box-shadow: 0 0 0 0 rgba(99, 102, 241, 0); }
        }

        /* Status Badge Components */
        .status-badge-green {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: rgba(16, 185, 129, 0.08) !important;
            border: 1px solid rgba(16, 185, 129, 0.25) !important;
            padding: 12px 16px !important;
            border-radius: 14px !important;
            color: #10B981 !important;
            font-weight: 600 !important;
            text-transform: uppercase;
            font-size: 12px;
            letter-spacing: 0.5px;
            width: 100%;
            justify-content: center;
            box-shadow: 0 4px 15px rgba(16, 185, 129, 0.02);
        }
        .status-badge-green .dot {
            width: 8px;
            height: 8px;
            background: #10B981;
            border-radius: 50%;
            animation: pulseDotGreen 2s infinite;
        }

        .status-badge-indigo {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: rgba(99, 102, 241, 0.08) !important;
            border: 1px solid rgba(99, 102, 241, 0.25) !important;
            padding: 12px 16px !important;
            border-radius: 14px !important;
            color: #818CF8 !important;
            font-weight: 600 !important;
            text-transform: uppercase;
            font-size: 12px;
            letter-spacing: 0.5px;
            width: 100%;
            justify-content: center;
            box-shadow: 0 4px 15px rgba(99, 102, 241, 0.02);
        }
        .status-badge-indigo .dot {
            width: 8px;
            height: 8px;
            background: #818CF8;
            border-radius: 50%;
            animation: pulseDotIndigo 2s infinite;
        }

        /* Modern Guidelines Grid Card */
        .guideline-box {
            background: rgba(30, 41, 59, 0.2) !important;
            border: 1px solid rgba(255, 255, 255, 0.05) !important;
            border-radius: 16px !important;
            padding: 18px !important;
            margin-bottom: 12px !important;
            display: flex !important;
            align-items: center !important;
            gap: 15px !important;
            transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1) !important;
        }
        .guideline-box:hover {
            background: rgba(30, 41, 59, 0.38) !important;
            border-color: rgba(6, 182, 212, 0.25) !important;
            transform: translateX(4px) !important;
            box-shadow: 0 5px 15px rgba(6, 182, 212, 0.05) !important;
        }
        .guideline-icon {
            font-size: 22px;
            background: rgba(6, 182, 212, 0.08);
            border: 1px solid rgba(6, 182, 212, 0.2);
            min-width: 44px;
            height: 44px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 10px;
            color: #06B6D4;
        }
        .guideline-content {
            flex: 1;
        }
        .guideline-content h4 {
            margin: 0;
            color: #F8FAFC;
            font-size: 14px;
            font-weight: 600;
        }
        .guideline-content p {
            margin: 3px 0 0 0;
            color: #94A3B8;
            font-size: 12px;
            line-height: 1.4;
        }

        /* Interactive Action Panels */
        .proctoring-warning-card {
            background: rgba(245, 158, 11, 0.05) !important;
            border: 1px dashed rgba(245, 158, 11, 0.25) !important;
            border-radius: 16px !important;
            padding: 20px !important;
            margin-bottom: 15px !important;
        }

        .pledge-card {
            background: rgba(236, 72, 153, 0.03) !important;
            border: 1px dashed rgba(236, 72, 153, 0.2) !important;
            border-radius: 16px !important;
            padding: 20px !important;
            margin-top: 15px !important;
        }
        
        /* Checkbox label enhancements */
        .stCheckbox label {
            color: #CBD5E1 !important;
            font-size: 14px !important;
            font-weight: 500 !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div style='text-align: center; margin-bottom: 25px;'>
            <h2 style='color:#00ADB5; margin:0; font-size: 30px; font-weight:800;'>📋 Pre-Assessment Control Center</h2>
            <p style='color:#94A3B8; margin:5px 0 0 0;'>Please complete device verification and pledge authorization to commence the assessment.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # 1. LIVE HARDWARE & SECURITY STATUS MONITOR
    col_sys1, col_sys2, col_sys3, col_sys4 = st.columns(4)
    
    with col_sys1:
        st.markdown(
            """
            <div class="status-badge-green">
                <div class="dot"></div>
                🎙 Audio Mic Calibrated
            </div>
            """,
            unsafe_allow_html=True
        )
    with col_sys2:
        st.markdown(
            """
            <div class="status-badge-green">
                <div class="dot"></div>
                🌐 Network Stream Secure
            </div>
            """,
            unsafe_allow_html=True
        )
    with col_sys3:
        st.markdown(
            """
            <div class="status-badge-indigo">
                <div class="dot"></div>
                🖥 Proctor Guard Armed
            </div>
            """,
            unsafe_allow_html=True
        )
    with col_sys4:
        st.markdown(
            """
            <div class="status-badge-indigo">
                <div class="dot"></div>
                🧠 Grading Core Active
            </div>
            """,
            unsafe_allow_html=True
        )

    st.write("")
    st.write("")

    # 2. MAIN GRID LAYOUT
    left_col, right_col = st.columns([11, 9])

    # LEFT COLUMN: Assessment Proctoring Rules
    with left_col:
        st.markdown("<h3 style='color:#F8FAFC; font-size:18px; margin: 0 0 15px 0; font-weight:600;'>📌 Proctoring Guidelines</h3>", unsafe_allow_html=True)
        
        rules = [
            ("Quiet Environment", "Ensure you are in a quiet, distraction-free environment before starting the interview.", "🤫"),
            ("No Tab Switching", "Do not switch browser tabs or minimize your window. Doing so triggers security warnings.", "🚫"),
            ("Clear Articulation", "Speak clearly, audibly, and confidently when recording your voice answers.", "🎤"),
            ("Professional Decorum", "Maintain formal communication and answer all questions to the best of your ability.", "💼"),
            ("Stable Network", "Ensure your internet connection remains stable throughout the entire session.", "🌐"),
            ("Academic Integrity", "Do not use external help, mobile devices, or search engines during this test.", "📴"),
            ("Single Attempt", "Carefully review and submit your answer before proceeding. Backtracking is disabled.", "⚠️")
        ]

        for title, desc, icon in rules:
            st.markdown(
                f"""
                <div class="guideline-box">
                    <div class="guideline-icon">{icon}</div>
                    <div class="guideline-content">
                        <h4>{title}</h4>
                        <p>{desc}</p>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

    # RIGHT COLUMN: Proctor Alerts, Agreements, and Lock Logic
    with right_col:
        st.markdown("<h3 style='color:#F8FAFC; font-size:18px; margin: 0 0 15px 0; font-weight:600;'>🔒 Security Authorization</h3>", unsafe_allow_html=True)
        
        # Proctoring warnings card
        st.markdown(
            """
            <div class="proctoring-warning-card">
                <h4 style="color:#F59E0B; margin: 0 0 8px 0; font-size: 14px; text-transform: uppercase; font-weight:700;">⚠️ Proctor Compliance warning</h4>
                <ul style="color:#CBD5E1; font-size: 13px; margin: 0; padding-left: 18px; line-height: 1.6;">
                    <li>Attempting to switch tabs or minimize full-screen mode <b>3 times</b> will immediately terminate the interview and log an failure.</li>
                    <li>Your spoken answers are recorded, processed, and transcribed for automated grading.</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Honor Pledge Box
        st.markdown('<div class="pledge-card">', unsafe_allow_html=True)
        st.markdown(
            """
            <h4 style="color:#EC4899; margin: 0 0 8px 0; font-size: 14px; text-transform: uppercase; font-weight:700;">🤝 Smart Hire Candidate Pledge</h4>
            <p style="color:#CBD5E1; font-size: 12px; line-height: 1.5; margin: 0 0 15px 0;">
                By proceeding, you pledge on your honor that you will complete the coding domain assessment
                independently, without consulting secondary devices, AI generators, or search engines.
            </p>
            """,
            unsafe_allow_html=True
        )

        # Interactive Checkboxes
        agree_rules = st.checkbox("I have read, understood, and agree to follow all 7 proctoring guidelines.", key="chk_agree_rules")
        pledge_honor = st.checkbox("I solemnly pledge to complete this assessment with absolute integrity.", key="chk_pledge_honor")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.write("")
        st.write("")

        # Lock / Unlock Begin Assessment button based on checkbox inputs
        is_ready = agree_rules and pledge_honor
        
        if is_ready:
            st.markdown(
                """
                <div style="background: rgba(16, 185, 129, 0.08); border: 1px solid rgba(16, 185, 129, 0.2); padding: 12px; border-radius: 12px; text-align: center; margin-bottom: 15px;">
                    <span style="color:#10B981; font-weight: 600; font-size: 13px;">🛡️ All checks completed! Assessment is unlocked.</span>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                """
                <div style="background: rgba(239, 68, 68, 0.05); border: 1px solid rgba(239, 68, 68, 0.15); padding: 12px; border-radius: 12px; text-align: center; margin-bottom: 15px;">
                    <span style="color:#F87171; font-weight: 500; font-size: 13px;">🔒 Check both authorization statements to unlock the session.</span>
                </div>
                """,
                unsafe_allow_html=True
            )

        # Button trigger
        if st.button("🚀 Initialize Assessment Session", key="start_interview_btn", use_container_width=True, disabled=not is_ready):
            st.session_state.stage = "resume"
            # Clear previous states
            for k in ["q_index", "questions", "last_spoken", "asked_questions"]:
                if k in st.session_state:
                    del st.session_state[k]
            st.rerun()