import streamlit as st
import sqlite3
import re
import os
import smtplib
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# =====================================================
# SMTP EMAIL DISPATCHER
# =====================================================
def get_smtp_config():
    # 1. Try DB first (allows instant setup in browser)
    try:
        with sqlite3.connect("interview.db", timeout=30.0, check_same_thread=False) as conn:
            conn.execute("PRAGMA journal_mode=WAL;")
            c = conn.cursor()
            res = c.execute("SELECT smtp_server, smtp_port, smtp_user, smtp_pass FROM smtp_settings ORDER BY id DESC LIMIT 1").fetchone()
            if res and all([res[0], res[2], res[3]]):
                return {
                    "server": res[0],
                    "port": int(res[1]) if res[1] else 587,
                    "user": res[2],
                    "pass": res[3],
                    "source": "Database Settings"
                }
    except Exception:
        pass

    # 2. Try Streamlit secrets
    try:
        smtp_server = st.secrets.get("SMTP_SERVER")
        smtp_port = st.secrets.get("SMTP_PORT")
        smtp_user = st.secrets.get("SMTP_USER")
        smtp_pass = st.secrets.get("SMTP_PASS")
        if smtp_server and smtp_user and smtp_pass:
            return {
                "server": smtp_server,
                "port": int(smtp_port) if smtp_port else 587,
                "user": smtp_user,
                "pass": smtp_pass,
                "source": ".streamlit/secrets.toml"
            }
    except Exception:
        pass

    # 3. Try environment variables
    try:
        smtp_server = os.environ.get("SMTP_SERVER")
        smtp_port = os.environ.get("SMTP_PORT", "587")
        smtp_user = os.environ.get("SMTP_USER")
        smtp_pass = os.environ.get("SMTP_PASS")
        if smtp_server and smtp_user and smtp_pass:
            return {
                "server": smtp_server,
                "port": int(smtp_port) if smtp_port else 587,
                "user": smtp_user,
                "pass": smtp_pass,
                "source": "Environment"
            }
    except Exception:
        pass
        
    return None

def send_otp_email(to_email, otp_code):
    config = get_smtp_config()
    if not config:
        return False, "SMTP server credentials are not configured. Please use the <b>SMTP OTP Server Settings</b> form below to set them up."
        
    smtp_server = config["server"]
    smtp_port = config["port"]
    smtp_user = config["user"]
    smtp_pass = config["pass"]
    
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"Verification Code: {otp_code} - Smart Hire AI"
        msg["From"] = f"Smart Hire AI <{smtp_user}>"
        msg["To"] = to_email
        
        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; background-color: #f8fafc; color: #334155; padding: 30px; margin: 0;">
            <div style="max-width: 550px; margin: 0 auto; background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 40px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);">
                <div style="text-align: center; margin-bottom: 25px;">
                    <h1 style="color: #1e40af; font-size: 28px; margin: 0; font-weight: 700; letter-spacing: 0.5px;">SMART HIRE AI</h1>
                    <p style="color: #64748b; margin: 5px 0 0 0; font-size: 14px; text-transform: uppercase; letter-spacing: 1px;">Interactive Assessment Platform</p>
                </div>
                <hr style="border: 0; height: 1px; background-color: #e2e8f0; margin: 25px 0;">
                <p style="font-size: 15px; line-height: 1.6; color: #334155;">Thank you for registering with Smart Hire AI. Please verify your email address to complete your account setup and proceed to your interactive assessment.</p>
                <div style="background-color: #f1f5f9; border: 1px solid #cbd5e1; border-radius: 8px; padding: 20px; text-align: center; margin: 30px 0;">
                    <div style="font-size: 12px; text-transform: uppercase; color: #64748b; font-weight: 700; letter-spacing: 1px; margin-bottom: 8px;">Verification Code</div>
                    <div style="font-size: 32px; font-weight: 700; color: #1e40af; letter-spacing: 5px; font-family: monospace;">{otp_code}</div>
                </div>
                <p style="font-size: 12px; color: #64748b; line-height: 1.5; margin-bottom: 20px;">This verification code is valid for 15 minutes. If you did not initiate this request, you can safely ignore this email.</p>
                <hr style="border: 0; height: 1px; background-color: #e2e8f0; margin: 25px 0;">
                <div style="text-align: center; font-size: 11px; color: #64748b;">
                    Secure Automated Verification System - Do Not Reply
                </div>
            </div>
        </body>
        </html>
        """
        msg.attach(MIMEText(html, "html"))
        
        # Connect with explicit 10 second timeout to prevent hanging indefinitely
        server = smtplib.SMTP(smtp_server, int(smtp_port), timeout=10)
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.sendmail(smtp_user, to_email, msg.as_string())
        server.quit()
        return True, "Email sent successfully!"
    except smtplib.SMTPAuthenticationError as e:
        return False, f"Authentication Failed: SMTP server rejected the password for <b>{smtp_user}</b>. <br>💡 If using Gmail, make sure you generated and entered a 16-character <b>Google App Password</b> instead of your standard Gmail password."
    except smtplib.SMTPConnectError as e:
        return False, f"Connection Failed: Could not establish a connection to <b>{smtp_server}:{smtp_port}</b>. Check server address, port, and your internet connection."
    except Exception as e:
        return False, f"SMTP error occurred: {str(e)}"


def send_password_reset_email(to_email, otp_code):
    config = get_smtp_config()
    if not config:
        return False, "SMTP server credentials are not configured. Please use the <b>SMTP OTP Server Settings</b> form below to set them up."
        
    smtp_server = config["server"]
    smtp_port = config["port"]
    smtp_user = config["user"]
    smtp_pass = config["pass"]
    
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"Password Reset Verification Code: {otp_code} - Smart Hire AI"
        msg["From"] = f"Smart Hire AI <{smtp_user}>"
        msg["To"] = to_email
        
        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; background-color: #f8fafc; color: #334155; padding: 30px; margin: 0;">
            <div style="max-width: 550px; margin: 0 auto; background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 40px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);">
                <div style="text-align: center; margin-bottom: 25px;">
                    <h1 style="color: #1e40af; font-size: 28px; margin: 0; font-weight: 700; letter-spacing: 0.5px;">SMART HIRE AI</h1>
                    <p style="color: #64748b; margin: 5px 0 0 0; font-size: 14px; text-transform: uppercase; letter-spacing: 1px;">Interactive Assessment Platform</p>
                </div>
                <hr style="border: 0; height: 1px; background-color: #e2e8f0; margin: 25px 0;">
                <p style="font-size: 15px; line-height: 1.6; color: #334155;">We received a request to reset the password for your Smart Hire AI account. Please use the verification code below to authorize this security update.</p>
                <div style="background-color: #f1f5f9; border: 1px solid #cbd5e1; border-radius: 8px; padding: 20px; text-align: center; margin: 30px 0;">
                    <div style="font-size: 12px; text-transform: uppercase; color: #64748b; font-weight: 700; letter-spacing: 1px; margin-bottom: 8px;">Verification Code</div>
                    <div style="font-size: 32px; font-weight: 700; color: #1e40af; letter-spacing: 5px; font-family: monospace;">{otp_code}</div>
                </div>
                <p style="font-size: 12px; color: #64748b; line-height: 1.5; margin-bottom: 20px;">This verification code is valid for 15 minutes. If you did not initiate this request, your credentials remain secure and you can safely ignore this email.</p>
                <hr style="border: 0; height: 1px; background-color: #e2e8f0; margin: 25px 0;">
                <div style="text-align: center; font-size: 11px; color: #64748b;">
                    Secure Automated Verification System - Do Not Reply
                </div>
            </div>
        </body>
        </html>
        """
        msg.attach(MIMEText(html, "html"))
        
        # Connect with explicit 10 second timeout to prevent hanging indefinitely
        server = smtplib.SMTP(smtp_server, int(smtp_port), timeout=10)
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.sendmail(smtp_user, to_email, msg.as_string())
        server.quit()
        return True, "Email sent successfully!"
    except smtplib.SMTPAuthenticationError as e:
        return False, f"Authentication Failed: SMTP server rejected the password for <b>{smtp_user}</b>. <br>💡 If using Gmail, make sure you generated and entered a 16-character <b>Google App Password</b> instead of your standard Gmail password."
    except smtplib.SMTPConnectError as e:
        return False, f"Connection Failed: Could not establish a connection to <b>{smtp_server}:{smtp_port}</b>. Check server address, port, and your internet connection."
    except Exception as e:
        return False, f"SMTP error occurred: {str(e)}"


import json

def send_deescalation_email(to_email, username, roadmap_json_str, applied_domain):
    config = get_smtp_config()
    if not config:
        return False, "SMTP server credentials are not configured. Please use the <b>SMTP OTP Server Settings</b> form in the sidebar/admin view to set them up."
        
    smtp_server = config["server"]
    smtp_port = config["port"]
    smtp_user = config["user"]
    smtp_pass = config["pass"]
    
    try:
        roadmap = json.loads(roadmap_json_str)
    except Exception as e:
        roadmap = {
            "strengths": ["General core attempt"],
            "weaknesses": ["Advanced core topics"],
            "gaps_analysis": "Assessment highlighted some gaps in technical and logic areas.",
            "weekly_plan": [],
            "recommended_resources": [],
            "custom_exercises": [],
            "encouragement": "Stay determined, keep practicing, and you will succeed!"
        }
        
    strengths_html = "".join([f"<li style='margin-bottom: 6px; color: #334155;'>{s}</li>" for s in roadmap.get("strengths", [])])
    weaknesses_html = "".join([f"<li style='margin-bottom: 6px; color: #334155;'>{w}</li>" for w in roadmap.get("weaknesses", [])])
    
    weekly_html = ""
    for idx, week_item in enumerate(roadmap.get("weekly_plan", [])):
        topics = "".join([f"<span style='display:inline-block; background-color: #eff6ff; border: 1px solid #bfdbfe; color: #1e40af; padding: 2px 8px; border-radius: 4px; font-size: 11px; margin-right: 5px; margin-top: 5px; font-weight: 500;'>{t}</span>" for t in week_item.get("topics", [])])
        actions = "".join([f"<li style='margin-bottom: 4px; color: #475569;'>• {a}</li>" for a in week_item.get("action_items", [])])
        weekly_html += f"""
        <div style="background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 18px; margin-bottom: 15px;">
            <h4 style="margin: 0; color: #1e40af; font-size: 15px; font-weight: 700;">{week_item.get("week", f"Week {idx+1}")}</h4>
            <p style="margin: 5px 0; color: #64748b; font-size: 13px; font-style: italic;">Focus: {week_item.get("focus", "")}</p>
            <div style="margin: 8px 0;">{topics}</div>
            <ul style="margin: 8px 0 0 0; padding-left: 20px; font-size: 13px; color: #334155; list-style-type: none;">
                {actions}
            </ul>
        </div>
        """
        
    resources_html = ""
    for r in roadmap.get("recommended_resources", []):
        resources_html += f"""
        <div style="background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px; margin-bottom: 10px; width: 100%; box-sizing: border-box;">
            <span style="font-size: 10px; padding: 2px 6px; background-color: #eff6ff; color: #1e40af; border-radius: 4px; font-weight: 600; text-transform: uppercase; border: 1px solid #bfdbfe;">{r.get("type", "Resource")}</span>
            <div style="font-weight: bold; color: #1e293b; font-size: 13.5px; margin-top: 6px;">{r.get("name", "")}</div>
            <div style="font-size: 12px; color: #64748b; margin-top: 2px;">{r.get("url_or_desc", "")}</div>
        </div>
        """
        
    exercises_html = ""
    for ex in roadmap.get("custom_exercises", []):
        difficulty = ex.get("difficulty", "Medium")
        difficulty_color = "#059669" if "easy" in difficulty.lower() else ("#d97706" if "medium" in difficulty.lower() else "#dc2626")
        difficulty_bg = "#ecfdf5" if "easy" in difficulty.lower() else ("#fffbeb" if "medium" in difficulty.lower() else "#fef2f2")
        difficulty_border = "#a7f3d0" if "easy" in difficulty.lower() else ("#fde68a" if "medium" in difficulty.lower() else "#fecaca")
        
        exercises_html += f"""
        <div style="background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px; margin-bottom: 10px;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-weight: bold; color: #1e293b; font-size: 13.5px;">{ex.get("title", "")}</span>
                <span style="font-size: 10px; padding: 2px 6px; background-color: {difficulty_bg}; color: {difficulty_color}; border-radius: 4px; font-weight: bold; border: 1px solid {difficulty_border};">{difficulty}</span>
            </div>
            <div style="font-size: 12.5px; color: #475569; margin-top: 6px; line-height: 1.4;">{ex.get("description", "")}</div>
        </div>
        """

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"Your Personalized Career Growth Roadmap - Smart Hire AI"
        msg["From"] = f"Smart Hire AI <{smtp_user}>"
        msg["To"] = to_email
        
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; background-color: #f8fafc; color: #334155; padding: 20px; margin: 0;">
            <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 35px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);">
                
                <div style="text-align: center; margin-bottom: 25px;">
                    <h1 style="color: #1e40af; font-weight: 700; font-size: 28px; margin: 0;">SMART HIRE AI</h1>
                    <p style="color: #64748b; margin: 5px 0 0 0; font-size: 14px; font-weight: 500; text-transform: uppercase; letter-spacing: 1px;">Personalized Growth Portal</p>
                </div>
                
                <hr style="border: 0; height: 1px; background-color: #e2e8f0; margin: 20px 0;">
                
                <p style="font-size: 15px; line-height: 1.6; color: #334155;">Dear <strong>{username}</strong>,</p>
                <p style="font-size: 15px; line-height: 1.6; color: #334155;">
                    Thank you for investing your time and effort in our interactive 4-round AI assessment for the <strong>{applied_domain}</strong> position. While we are currently moving forward with other profiles that more closely match the active team requirements, we were genuinely impressed by your diligence.
                </p>
                <p style="font-size: 15px; line-height: 1.6; color: #334155;">
                    At Smart Hire AI, we believe every interview is a stepping stone. Our evaluation engine has analyzed your assessment logs to compile a complete <b>Personalized Career Development Roadmap</b> to help you brush up your skills and conquer your next career milestone.
                </p>
                
                <div style="background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 20px; margin: 25px 0;">
                    <h3 style="margin-top: 0; color: #1e40af; font-size: 16px; font-weight: 700; text-transform: uppercase; border-bottom: 1px solid #e2e8f0; padding-bottom: 8px;">Skills Diagnostic</h3>
                    
                    <h4 style="margin: 12px 0 6px 0; color: #059669; font-size: 14px; font-weight: 700;">Identified Strengths</h4>
                    <ul style="margin: 0; padding-left: 20px; font-size: 13.5px; color: #334155; line-height: 1.5;">
                        {strengths_html if strengths_html else "<li>Demonstrated great foundational commitment.</li>"}
                    </ul>
                    
                    <h4 style="margin: 15px 0 6px 0; color: #d97706; font-size: 14px; font-weight: 700;">High-Priority Growth Areas</h4>
                    <ul style="margin: 0; padding-left: 20px; font-size: 13.5px; color: #334155; line-height: 1.5;">
                        {weaknesses_html if weaknesses_html else "<li>Enhance coding proficiency and core CS principles.</li>"}
                    </ul>
                    
                    <h4 style="margin: 15px 0 6px 0; color: #b91c1c; font-size: 14px; font-weight: 700;">AI Gaps Analysis</h4>
                    <p style="margin: 0; font-size: 13px; color: #475569; line-height: 1.5; font-style: italic;">
                        "{roadmap.get("gaps_analysis", "Assessment highlighted some gaps in technical and logic areas.")}"
                    </p>
                </div>
                
                <h3 style="color: #1e40af; font-size: 16px; font-weight: 700; text-transform: uppercase; margin: 25px 0 15px 0;">Recommended 4-Week Action Plan</h3>
                {weekly_html}
                
                <div style="margin-top: 25px;">
                    <div style="margin-bottom: 20px;">
                        <h3 style="color: #1e40af; font-size: 14px; font-weight: 700; text-transform: uppercase; margin-bottom: 12px; border-left: 3px solid #1e40af; padding-left: 8px;">Study Guide & Tools</h3>
                        {resources_html}
                    </div>
                    <div>
                        <h3 style="color: #1e40af; font-size: 14px; font-weight: 700; text-transform: uppercase; margin-bottom: 12px; border-left: 3px solid #1e40af; padding-left: 8px;">Practice Challenges</h3>
                        {exercises_html}
                    </div>
                </div>
                
                <div style="background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 20px; margin-top: 25px; text-align: center;">
                    <h4 style="margin: 0 0 8px 0; color: #1e40af; font-size: 15px; font-weight: 700;">Mentor Insight</h4>
                    <p style="margin: 0; color: #475569; font-size: 13.5px; line-height: 1.5; font-style: italic;">
                        "{roadmap.get("encouragement", "")}"
                    </p>
                </div>
                
                <p style="font-size: 14px; color: #64748b; margin-top: 25px; line-height: 1.5;">
                    Wishing you absolute success in your professional career. Maintain your momentum!
                    <br><br>
                    Warm regards,<br>
                    <strong>Smart Hire Recruitment Panel</strong>
                </p>
                
                <hr style="border: 0; height: 1px; background-color: #e2e8f0; margin: 25px 0;">
                
                <div style="text-align: center; font-size: 11px; color: #64748b;">
                    Smart Hire AI - Candidate De-escalation & Feedback Center
                </div>
            </div>
        </body>
        </html>
        """
        msg.attach(MIMEText(html_content, "html"))
        
        server = smtplib.SMTP(smtp_server, int(smtp_port), timeout=10)
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.sendmail(smtp_user, to_email, msg.as_string())
        server.quit()
        return True, "De-escalation roadmap email dispatched successfully!"
    except Exception as e:
        return False, f"SMTP dispatch failed: {str(e)}"

def send_selection_email(to_email, username, overall_avg, applied_domain):
    config = get_smtp_config()
    if not config:
        return False, "SMTP server credentials are not configured. Please configure them to proceed."
        
    smtp_server = config["server"]
    smtp_port = config["port"]
    smtp_user = config["user"]
    smtp_pass = config["pass"]
    
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"Congratulations: Selection Process Update - Smart Hire AI"
        msg["From"] = f"Smart Hire AI <{smtp_user}>"
        msg["To"] = to_email
        
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; background-color: #f8fafc; color: #334155; padding: 20px; margin: 0;">
            <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 35px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);">
                
                <div style="text-align: center; margin-bottom: 25px;">
                    <h1 style="color: #10b981; font-weight: 700; font-size: 28px; margin: 0;">SMART HIRE AI</h1>
                    <p style="color: #64748b; margin: 5px 0 0 0; font-size: 14px; font-weight: 500; text-transform: uppercase; letter-spacing: 1px;">Official Selection Notice</p>
                </div>
                
                <hr style="border: 0; height: 1px; background-color: #e2e8f0; margin: 20px 0;">
                
                <p style="font-size: 15px; line-height: 1.6; color: #334155;">Dear <strong>{username}</strong>,</p>
                <p style="font-size: 15px; line-height: 1.6; color: #334155;">
                    We are pleased to inform you that you have successfully passed our multi-dimensional interactive AI recruitment process for the <strong>{applied_domain}</strong> position.
                </p>
                
                <div style="background-color: #ecfdf5; border: 1px solid #a7f3d0; border-radius: 8px; padding: 20px; margin: 25px 0; text-align: center;">
                    <div style="font-size: 11px; text-transform: uppercase; color: #047857; font-weight: 700; letter-spacing: 0.5px;">Your Composite Performance Index</div>
                    <div style="font-size: 42px; font-weight: 800; color: #059669; margin: 10px 0;">{overall_avg:.1f}%</div>
                    <div style="font-size: 13.5px; color: #047857; font-weight: 600;">Status: Strongly Recommended for Hiring</div>
                </div>
                
                <p style="font-size: 15px; line-height: 1.6; color: #334155;">
                    Your outstanding demonstration of computer science fundamentals, analytical aptitude, solid programming logic, and professional verbal communication scored significantly above our selection benchmarks.
                </p>
                
                <p style="font-size: 15px; line-height: 1.6; color: #334155;">
                    Our HR talent acquisition team is currently reviewing your detailed assessment report and will connect with you within the next 48 hours to discuss compensation, onboarding structures, and next steps.
                </p>
                
                <p style="font-size: 15px; line-height: 1.6; color: #334155;">
                    Once again, congratulations on this superb performance. We look forward to welcoming you to our team.
                </p>
                
                <p style="font-size: 14px; color: #64748b; margin-top: 25px; line-height: 1.5;">
                    Best regards,<br>
                    <strong>Smart Hire Recruitment Panel</strong>
                </p>
                
                <hr style="border: 0; height: 1px; background-color: #e2e8f0; margin: 25px 0;">
                
                <div style="text-align: center; font-size: 11px; color: #64748b;">
                    Smart Hire AI - Talent Acquisition Center
                </div>
            </div>
        </body>
        </html>
        """
        msg.attach(MIMEText(html_content, "html"))
        
        server = smtplib.SMTP(smtp_server, int(smtp_port), timeout=10)
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.sendmail(smtp_user, to_email, msg.as_string())
        server.quit()
        return True, "Selection confirmation email dispatched successfully!"
    except Exception as e:
        return False, f"SMTP dispatch failed: {str(e)}"



# =====================================================
# DATABASE CONNECTION & SCHEMA INITIALIZATION
# =====================================================
def init_database():
    import sqlite3
    with sqlite3.connect("interview.db", timeout=30.0, check_same_thread=False) as conn:
        conn.execute("PRAGMA journal_mode=WAL;")
        c = conn.cursor()
        
        # Check if users table needs migration (missing user_id)
        needs_migration = False
        try:
            res = c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'").fetchone()
            if res:
                columns = [col[1] for col in c.execute("PRAGMA table_info(users)").fetchall()]
                if 'user_id' not in columns:
                    needs_migration = True
            else:
                needs_migration = True
        except Exception:
            needs_migration = True

        if needs_migration:
            # Drop all candidate related tables for a clean, normalized start
            tables_to_drop = [
                'users', 'user_emails', 'interview_data', 'r1_hr_intro', 
                'r2_english_comm', 'r3_technical_mcq', 'r4_aptitude_coding', 
                'final_results', 'candidate_feedback'
            ]
            for t in tables_to_drop:
                c.execute(f"DROP TABLE IF EXISTS {t}")
            conn.commit()

        # Recreate tables to 3NF standards
        c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            username TEXT UNIQUE,
            password TEXT,
            role TEXT,
            email TEXT
        )
        """)
        
        c.execute("""
        CREATE TABLE IF NOT EXISTS smtp_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            smtp_server TEXT,
            smtp_port INTEGER,
            smtp_user TEXT,
            smtp_pass TEXT
        )
        """)

        c.execute("""
        CREATE TABLE IF NOT EXISTS questions (
            question_id INTEGER PRIMARY KEY AUTOINCREMENT,
            round_name TEXT,
            question_type TEXT,
            question_text TEXT,
            correct_answer TEXT,
            subject_category TEXT
        )
        """)

        c.execute("""
        CREATE TABLE IF NOT EXISTS r1_hr_intro (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            question_id INTEGER,
            transcript TEXT,
            audio_path TEXT,
            timestamp TEXT,
            score REAL,
            confidence_score REAL,
            is_follow_up INTEGER DEFAULT 0,
            parent_question TEXT,
            knowledge_gap_noted TEXT,
            FOREIGN KEY(user_id) REFERENCES users(user_id),
            FOREIGN KEY(question_id) REFERENCES questions(question_id)
        )
        """)

        c.execute("""
        CREATE TABLE IF NOT EXISTS r2_english_comm (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            question_id INTEGER,
            selected_answer TEXT,
            audio_path TEXT,
            transcript TEXT,
            score REAL,
            fluency REAL,
            pronunciation REAL,
            confidence REAL,
            comm_quality REAL,
            speaking_consistency REAL,
            remarks TEXT,
            timestamp TEXT,
            FOREIGN KEY(user_id) REFERENCES users(user_id),
            FOREIGN KEY(question_id) REFERENCES questions(question_id)
        )
        """)

        c.execute("""
        CREATE TABLE IF NOT EXISTS r3_technical_mcq (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            question_id INTEGER,
            selected_answer TEXT,
            score REAL,
            timestamp TEXT,
            FOREIGN KEY(user_id) REFERENCES users(user_id),
            FOREIGN KEY(question_id) REFERENCES questions(question_id)
        )
        """)

        c.execute("""
        CREATE TABLE IF NOT EXISTS r4_aptitude_coding (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            question_id INTEGER,
            selected_answer TEXT,
            code_submitted TEXT,
            language TEXT,
            execution_output TEXT,
            score REAL,
            time_taken INTEGER,
            timestamp TEXT,
            FOREIGN KEY(user_id) REFERENCES users(user_id),
            FOREIGN KEY(question_id) REFERENCES questions(question_id)
        )
        """)

        c.execute("""
        CREATE TABLE IF NOT EXISTS final_results (
            user_id TEXT PRIMARY KEY,
            skills TEXT,
            comm_score REAL,
            tech_score REAL,
            apt_score REAL,
            code_score REAL,
            behavioral_score REAL,
            recommendation TEXT,
            timestamp TEXT,
            total_rounds_completed INTEGER,
            progress_completed REAL,
            applied_domain TEXT,
            alternative_domain TEXT,
            alternative_reason TEXT,
            growth_roadmap TEXT,
            email_sent INTEGER DEFAULT 0,
            FOREIGN KEY(user_id) REFERENCES users(user_id)
        )
        """)

        # Database Schema Migration for AI Career Path Matcher
        try:
            columns = [col[1] for col in c.execute("PRAGMA table_info(final_results)").fetchall()]
            if 'applied_domain' not in columns:
                c.execute("ALTER TABLE final_results ADD COLUMN applied_domain TEXT")
            if 'alternative_domain' not in columns:
                c.execute("ALTER TABLE final_results ADD COLUMN alternative_domain TEXT")
            if 'alternative_reason' not in columns:
                c.execute("ALTER TABLE final_results ADD COLUMN alternative_reason TEXT")
            if 'growth_roadmap' not in columns:
                c.execute("ALTER TABLE final_results ADD COLUMN growth_roadmap TEXT")
            if 'email_sent' not in columns:
                c.execute("ALTER TABLE final_results ADD COLUMN email_sent INTEGER DEFAULT 0")
        except Exception as e:
            print(f"Error executing final_results migration: {e}")

        # Database Schema Migration for AI "Stress Test" Interviewer
        try:
            columns_r1 = [col[1] for col in c.execute("PRAGMA table_info(r1_hr_intro)").fetchall()]
            if 'is_follow_up' not in columns_r1:
                c.execute("ALTER TABLE r1_hr_intro ADD COLUMN is_follow_up INTEGER DEFAULT 0")
            if 'parent_question' not in columns_r1:
                c.execute("ALTER TABLE r1_hr_intro ADD COLUMN parent_question TEXT")
            if 'knowledge_gap_noted' not in columns_r1:
                c.execute("ALTER TABLE r1_hr_intro ADD COLUMN knowledge_gap_noted TEXT")
        except Exception as e:
            print(f"Error executing r1_hr_intro migration: {e}")

        c.execute("""
        CREATE TABLE IF NOT EXISTS candidate_feedback (
            user_id TEXT PRIMARY KEY,
            overall_rating INTEGER,
            overall_comments TEXT,
            r1_rating INTEGER,
            r2_rating INTEGER,
            r3_rating INTEGER,
            r4_rating INTEGER,
            round_comments TEXT,
            timestamp TEXT,
            FOREIGN KEY(user_id) REFERENCES users(user_id)
        )
        """)
        conn.commit()

init_database()

# =====================================================
# PASSWORD SECURITY & REFERENCE LOGGER HELPERS
# =====================================================
import hashlib
import secrets

def hash_password(password: str) -> str:
    """Securely hash a password using PBKDF2-HMAC-SHA256 with a unique salt."""
    salt = secrets.token_hex(16)
    hash_bytes = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        100000  # Number of iterations
    )
    hash_hex = hash_bytes.hex()
    return f"pbkdf2_sha256$100000${salt}${hash_hex}"

def verify_password(stored_password: str, provided_password: str) -> bool:
    """Verify a password against a stored hashed password or plaintext fallback."""
    if not stored_password:
        return False
    # If the stored password does not match our hash format, treat it as plaintext (fallback for existing users)
    if not stored_password.startswith("pbkdf2_sha256$"):
        return stored_password == provided_password
    
    try:
        parts = stored_password.split("$")
        if len(parts) != 4:
            return False
        _, iterations_str, salt, hash_hex = parts
        iterations = int(iterations_str)
        hash_bytes = hashlib.pbkdf2_hmac(
            'sha256',
            provided_password.encode('utf-8'),
            salt.encode('utf-8'),
            iterations
        )
        return hash_bytes.hex() == hash_hex
    except Exception:
        return False

# Automatic Database Hashing Migration
try:
    with sqlite3.connect("interview.db", timeout=30.0, check_same_thread=False) as conn_migration:
        conn_migration.execute("PRAGMA journal_mode=WAL;")
        cursor_migration = conn_migration.cursor()
        # Fetch all users
        all_users = cursor_migration.execute("SELECT username, password FROM users").fetchall()
        for username, password in all_users:
            if password and not password.startswith("pbkdf2_sha256$"):
                # Hash it and update in database
                hashed = hash_password(password)
                cursor_migration.execute("UPDATE users SET password=? WHERE username=?", (hashed, username))
        conn_migration.commit()
except Exception as e:
    print(f"Error during password auto-migration: {e}")

# =====================================================
# PREMIUM HELPERS
# =====================================================
def show_error(message):
    st.markdown(
        f"""
        <div class="auth-error-banner">
            <span style="font-size: 18px;">⚠️</span>
            <span>{message}</span>
        </div>
        """,
        unsafe_allow_html=True
    )

def show_success(message):
    st.markdown(
        f"""
        <div class="auth-success-banner">
            <span style="font-size: 18px;">✅</span>
            <span>{message}</span>
        </div>
        """,
        unsafe_allow_html=True
    )

# =====================================================
# AUTH PAGE
# =====================================================
def show_auth_page():
    if "auth_page" not in st.session_state:
        st.session_state.auth_page = "login"
    if "otp_stage" not in st.session_state:
        st.session_state.otp_stage = "details"
    if "forgot_otp_stage" not in st.session_state:
        st.session_state.forgot_otp_stage = "details"
    
    # Pre-initialize registration state keys to prevent initialization glitches
    if "reg_user" not in st.session_state:
        st.session_state.reg_user = ""
    if "reg_email" not in st.session_state:
        st.session_state.reg_email = ""
    if "reg_pwd" not in st.session_state:
        st.session_state.reg_pwd = ""
    if "reg_confirm" not in st.session_state:
        st.session_state.reg_confirm = ""
    if "reg_role" not in st.session_state:
        st.session_state.reg_role = "Applicant"
    if "reg_admin_code" not in st.session_state:
        st.session_state.reg_admin_code = ""

    # Pre-initialize forgot password state keys
    if "forgot_user" not in st.session_state:
        st.session_state.forgot_user = ""
    if "forgot_pwd" not in st.session_state:
        st.session_state.forgot_pwd = ""
    if "forgot_confirm" not in st.session_state:
        st.session_state.forgot_confirm = ""

    # Inject targeted custom CSS for supreme modern styles
    st.markdown(
        """
        <style>
        /* --- Premium Auth CSS override --- */
        .auth-card-container {
            background: rgba(15, 23, 42, 0.45) !important;
            backdrop-filter: blur(25px) !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            border-radius: 24px !important;
            padding: 35px !important;
            box-shadow: 0 20px 45px rgba(0, 0, 0, 0.35) !important;
            position: relative;
            overflow: hidden;
            margin-bottom: 20px;
        }
        
        /* Subtle glow border */
        .auth-card-container::after {
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0; bottom: 0;
            border-radius: 24px;
            border: 1px solid transparent;
            background: linear-gradient(135deg, rgba(6, 182, 212, 0.15), rgba(99, 102, 241, 0.15)) border-box;
            -webkit-mask: linear-gradient(#fff 0 0) padding-box, linear-gradient(#fff 0 0);
            -webkit-mask-composite: destination-out;
            mask-composite: exclude;
            pointer-events: none;
        }

        /* Segmented Controller navigation tab buttons override */
        button[data-testid="baseButton-secondary"] {
            background: rgba(30, 41, 59, 0.35) !important;
            border: 1px solid rgba(255, 255, 255, 0.06) !important;
            color: #94A3B8 !important;
            font-weight: 600 !important;
            text-transform: capitalize !important;
            letter-spacing: 0.5px !important;
            box-shadow: none !important;
            border-radius: 12px !important;
            transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1) !important;
        }
        button[data-testid="baseButton-secondary"]:hover {
            border-color: rgba(6, 182, 212, 0.35) !important;
            color: #06B6D4 !important;
            background: rgba(15, 23, 42, 0.5) !important;
        }

        button[data-testid="baseButton-primary"] {
            background: linear-gradient(135deg, #4f46e5 0%, #06b6d4 100%) !important;
            border: none !important;
            color: #ffffff !important;
            font-weight: 700 !important;
            text-transform: uppercase !important;
            letter-spacing: 1px !important;
            box-shadow: 0 4px 15px rgba(6, 182, 212, 0.25) !important;
            border-radius: 12px !important;
            transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1) !important;
        }
        button[data-testid="baseButton-primary"]:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 8px 20px rgba(6, 182, 212, 0.4) !important;
        }

        /* Modern input headers inside form */
        .stTextInput label, .stSelectbox label {
            font-weight: 600 !important;
            color: #E2E8F0 !important;
            font-size: 13px !important;
            letter-spacing: 0.5px !important;
            text-transform: uppercase !important;
            margin-bottom: 6px !important;
        }

        /* Glassmorphic alerts styling */
        .auth-error-banner {
            background: rgba(239, 68, 68, 0.08) !important;
            border: 1px solid rgba(239, 68, 68, 0.3) !important;
            padding: 12px 18px !important;
            border-radius: 12px !important;
            color: #F87171 !important;
            font-size: 14px !important;
            font-weight: 500 !important;
            margin-bottom: 20px !important;
            display: flex;
            align-items: center;
            gap: 10px;
            box-shadow: 0 4px 15px rgba(239, 68, 68, 0.03);
            animation: slideUpFade 0.4s ease forwards;
        }

        .auth-success-banner {
            background: rgba(16, 185, 129, 0.08) !important;
            border: 1px solid rgba(16, 185, 129, 0.3) !important;
            padding: 12px 18px !important;
            border-radius: 12px !important;
            color: #34D399 !important;
            font-size: 14px !important;
            font-weight: 500 !important;
            margin-bottom: 20px !important;
            display: flex;
            align-items: center;
            gap: 10px;
            box-shadow: 0 4px 15px rgba(16, 185, 129, 0.03);
            animation: slideUpFade 0.4s ease forwards;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Input Validation Helpers
    def mask_email(email):
        if not email:
            return ""
        parts = email.split("@")
        if len(parts) != 2:
            return email
        username, domain = parts[0], parts[1]
        if len(username) <= 2:
            masked_username = username[0] + "*" * (len(username) - 1)
        else:
            masked_username = username[0] + "*" * (len(username) - 2) + username[-1]
        return f"{masked_username}@{domain}"

    def check_password_strength(password):
        missing = []
        if len(password) < 8:
            missing.append("At least 8 characters in length")
        if not any(c.isupper() for c in password):
            missing.append("At least one uppercase letter (A-Z)")
        if not any(c.islower() for c in password):
            missing.append("At least one lowercase letter (a-z)")
        if not any(c.isdigit() for c in password):
            missing.append("At least one digit (0-9)")
        if not any(c in '!@#$%^&*()_+-=[]{}|;:\',./<>?' for c in password):
            missing.append("At least one special character (e.g. !@#$%^&*)")
        return missing

    def validate(username, password, email):
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            return False, "Username should contain only letters, numbers, and underscores (_)"
        
        if not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email):
            return False, "Please enter a valid email address (e.g., user@domain.com)"
        
        missing_criteria = check_password_strength(password)
        if missing_criteria:
            msg = "Password does not meet complexity requirements:<br>" + "".join(f"• {item}<br>" for item in missing_criteria)
            return False, msg
        return True, ""

    # Navigation Tabs (Pill selectors styled via Streamlit buttons)
    nav_col1, nav_col2, nav_col3 = st.columns(3)
    menu = st.session_state.auth_page

    with nav_col1:
        if st.button("🔐 Access Login", use_container_width=True, key="btn_goto_login", 
                     type="primary" if menu == "login" else "secondary"):
            st.session_state.auth_page = "login"
            st.rerun()

    with nav_col2:
        if st.button("📝 Create Account", use_container_width=True, key="btn_goto_reg", 
                     type="primary" if menu == "register" else "secondary"):
            st.session_state.auth_page = "register"
            st.session_state.otp_stage = "details"
            st.session_state.reg_user = ""
            st.session_state.reg_email = ""
            st.session_state.reg_pwd = ""
            st.session_state.reg_confirm = ""
            st.session_state.temp_reg_data = None
            st.rerun()

    with nav_col3:
        if st.button("🔑 Reset Pass", use_container_width=True, key="btn_goto_forgot", 
                     type="primary" if menu == "forgot" else "secondary"):
            st.session_state.auth_page = "forgot"
            st.session_state.forgot_otp_stage = "details"
            st.session_state.forgot_user = ""
            st.session_state.forgot_pwd = ""
            st.session_state.forgot_confirm = ""
            st.session_state.temp_forgot_data = None
            st.rerun()

    st.write("")

    # =================================================
    # LOGIN SECTION
    # =================================================
    if menu == "login":
        # Custom outer card div
        st.markdown('<div class="auth-card-container">', unsafe_allow_html=True)
        
        st.markdown(
            """
            <div style='text-align: center; margin-bottom: 25px;'>
                <h2 style='color:#00ADB5; margin:0; font-weight:700; font-size:26px;'>Welcome Back</h2>
                <p style='color:#94A3B8; margin:5px 0 0 0;'>Sign in to continue your smart assessment</p>
            </div>
            """,
            unsafe_allow_html=True
        )

        with st.form("login_form", clear_on_submit=False):
            user = st.text_input("👤 Username", placeholder="Enter your username", key="login_user")
            role = st.selectbox("💼 Access Role", ["Applicant", "HR Admin"], key="login_role")
            pwd = st.text_input("🔑 Password", type="password", placeholder="••••••••", key="login_pwd")

            st.write("")

            submit_login = st.form_submit_button("🚀 Sign In", type="primary", use_container_width=True)

        if submit_login:
            user_val = st.session_state.get("login_user", "").strip()
            pwd_val = st.session_state.get("login_pwd", "")
            role_val = st.session_state.get("login_role", "Applicant")

            if not user_val or not pwd_val:
                show_error("Please fill in all credential fields before signing in.")
            else:
                # 1. First verify if username exists
                with sqlite3.connect("interview.db", timeout=30.0, check_same_thread=False) as conn_db:
                    conn_db.execute("PRAGMA journal_mode=WAL;")
                    cursor_db = conn_db.cursor()
                    existing_user = cursor_db.execute("SELECT * FROM users WHERE username=?", (user_val,)).fetchone()
                    
                    if not existing_user:
                        show_error(f"Account '{user_val}' does not exist. Please navigate to 'Create Account' above to register.")
                    else:
                        # 2. Fetch stored credentials for role
                        res = cursor_db.execute(
                            "SELECT password, user_id FROM users WHERE username=? AND role=?",
                            (user_val, role_val)
                        ).fetchone()

                    # Verify matching credentials
                    if res and verify_password(res[0], pwd_val):
                        show_success("Login Successful! Preparing workspace... ✅")
                        st.session_state.logged_in = True
                        st.session_state.username = user_val
                        st.session_state.user_id = res[1]
                        st.session_state.role = role_val

                        if role_val == "HR Admin":
                            st.session_state.stage = "hr"
                        else:
                            st.session_state.stage = "instructions"
                        st.rerun()
                    else:
                        # Password or Role incorrect
                        # Columns are (user_id, username, password, role, email)
                        stored_pwd = existing_user[2]
                        stored_role = existing_user[3]
                        if stored_role != role_val:
                            show_error(f"Access Role '{role_val}' does not match registered profile role.")
                        elif not verify_password(stored_pwd, pwd_val):
                            show_error("Incorrect Password entered. Please verify details and try again.")
                        else:
                            show_error("Authentication failed. Please verify your credentials.")

        st.markdown('</div>', unsafe_allow_html=True)

    # =================================================
    # REGISTER SECTION
    # =================================================
    elif menu == "register":
        # Ensure otp_stage is initialized
        if "otp_stage" not in st.session_state:
            st.session_state.otp_stage = "details"

        if st.session_state.otp_stage == "details":
            st.markdown('<div class="auth-card-container">', unsafe_allow_html=True)
            
            st.markdown(
                """
                <div style='text-align: center; margin-bottom: 25px;'>
                    <h2 style='color:#6366F1; margin:0; font-weight:700; font-size:26px;'>Create Account</h2>
                    <p style='color:#94A3B8; margin:5px 0 0 0;'>Get set up for your interactive assessment</p>
                </div>
                """,
                unsafe_allow_html=True
            )

            with st.form("register_form", clear_on_submit=False):
                # Bind inputs to session_state directly without value parameter to prevent reset bugs
                user = st.text_input(
                    "👤 Choose Username", 
                    key="reg_user", 
                    placeholder="Use letters, numbers, or underscores"
                )
                
                role_options = ["Applicant", "HR Admin"]
                role = st.selectbox(
                    "💼 Register As", 
                    role_options, 
                    key="reg_role"
                )
                
                admin_passcode = st.text_input(
                    "🔑 Admin Passcode (Required for HR Admin role)", 
                    type="password", 
                    key="reg_admin_code", 
                    placeholder="Required only if registering as HR Admin"
                )
                
                email = st.text_input(
                    "✉️ Email Address",
                    key="reg_email",
                    placeholder="e.g. yourname@example.com"
                )
                
                pwd = st.text_input(
                    "🔑 Set Password", 
                    type="password", 
                    key="reg_pwd", 
                    placeholder="Minimum 8 characters"
                )
                
                confirm = st.text_input(
                    "🔄 Confirm Password", 
                    type="password", 
                    key="reg_confirm", 
                    placeholder="Repeat your password"
                )

                st.write("")

                submit_register = st.form_submit_button("✨ Sign Up", type="primary", use_container_width=True)

            if submit_register:
                user_val = st.session_state.get("reg_user", "").strip()
                email_val = st.session_state.get("reg_email", "").strip()
                pwd_val = st.session_state.get("reg_pwd", "")
                confirm_val = st.session_state.get("reg_confirm", "")
                role_val = st.session_state.get("reg_role", "Applicant")
                admin_code_val = st.session_state.get("reg_admin_code", "").strip()

                if not user_val or not email_val or not pwd_val or not confirm_val:
                    show_error("All fields are required to establish an account.")
                elif role_val == "HR Admin" and not admin_code_val:
                    show_error("Admin Passcode is required to register as an HR Admin.")
                elif role_val == "HR Admin" and admin_code_val != os.environ.get("ADMIN_PASSCODE", "SmartHireAdmin2026!").strip():
                    show_error("Unauthorized Role Registration: The provided Admin Security Code is invalid.")
                elif pwd_val != confirm_val:
                    show_error("Passwords do not match! Please check password confirmation.")
                else:
                    valid, msg = validate(user_val, pwd_val, email_val)
                    if not valid:
                        show_error(msg)
                    else:
                        # Check duplicate username or email in database
                        try:
                            with sqlite3.connect("interview.db", timeout=30.0, check_same_thread=False) as conn_db:
                                conn_db.execute("PRAGMA journal_mode=WAL;")
                                cursor_db = conn_db.cursor()
                                
                                # Check if username already exists
                                existing_user = cursor_db.execute(
                                    "SELECT 1 FROM users WHERE username=?", (user_val,)
                                ).fetchone()
                                
                                # Check if email already exists in users
                                existing_email_users = cursor_db.execute(
                                    "SELECT 1 FROM users WHERE email=?", (email_val,)
                                ).fetchone()
                                
                                if existing_user:
                                    show_error(f"Username '{user_val}' is already registered. Please choose a different name.")
                                elif existing_email_users:
                                    show_error(f"Email address '{email_val}' is already associated with an account.")
                                else:
                                    # Generate 6-digit OTP code
                                    otp_code = f"{random.randint(100000, 999999)}"
                                    
                                    # Save data to session state
                                    st.session_state.temp_reg_data = {
                                        "username": user_val,
                                        "password": pwd_val,
                                        "role": role_val,
                                        "email": email_val
                                    }
                                    st.session_state.reg_otp = otp_code
                                    
                                    # Attempt to send OTP email
                                    with st.spinner("Sending verification code to your email..."):
                                        otp_sent, smtp_msg = send_otp_email(email_val, otp_code)
                                        
                                    if not otp_sent:
                                        show_error(f"❌ <b>Email Dispatch Failure:</b> {smtp_msg}")
                                    else:
                                        st.session_state.otp_sent = True
                                        st.session_state.otp_stage = "verify"
                                        st.rerun()
                        except Exception as e:
                            show_error(f"Database/System Error: {str(e)}")

            st.markdown('</div>', unsafe_allow_html=True)

        elif st.session_state.otp_stage == "verify":
            st.markdown('<div class="auth-card-container">', unsafe_allow_html=True)
            
            st.markdown(
                """
                <div style='text-align: center; margin-bottom: 25px;'>
                    <h2 style='color:#06B6D4; margin:0; font-weight:700; font-size:26px;'>Verify Your Email</h2>
                    <p style='color:#94A3B8; margin:5px 0 0 0;'>We have sent a 6-digit verification code to your email</p>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            temp_email = st.session_state.temp_reg_data.get("email", "")
            st.markdown(
                f"""
                <div style='text-align: center; margin-bottom: 20px;'>
                    <span style='color: #E2E8F0; font-size: 15px;'>Sent to: <b>{temp_email}</b></span>
                </div>
                """,
                unsafe_allow_html=True
            )

            otp_input = st.text_input("🎯 Enter 6-Digit Code", max_chars=6, placeholder="e.g. 123456", key="reg_otp_input")

            st.write("")

            col_verify, col_cancel = st.columns(2)
            
            with col_verify:
                if st.button("✅ Verify OTP", use_container_width=True, type="primary", key="btn_confirm_otp"):
                    if not otp_input:
                        show_error("Please enter the 6-digit verification code.")
                    elif otp_input != st.session_state.reg_otp:
                        show_error("Invalid verification code. Please check the code and try again.")
                    else:
                        # Success! Write to database
                        temp_data = st.session_state.temp_reg_data
                        reg_user = temp_data["username"]
                        reg_pwd = temp_data["password"]
                        reg_role = temp_data["role"]
                        reg_email = temp_data["email"]
                        
                        try:
                            # Generate unique USR-XXXXXX user_id
                            import uuid
                            reg_user_id = f"USR-{uuid.uuid4().hex[:6].upper()}"

                            # Hash the password securely
                            hashed_pwd = hash_password(reg_pwd)

                            with sqlite3.connect("interview.db", timeout=30.0, check_same_thread=False) as conn_db:
                                conn_db.execute("PRAGMA journal_mode=WAL;")
                                cursor_db = conn_db.cursor()
                                
                                # Insert into users with unique user_id
                                cursor_db.execute(
                                    "INSERT INTO users (user_id, username, password, role, email) VALUES (?, ?, ?, ?, ?)",
                                    (reg_user_id, reg_user, hashed_pwd, reg_role, reg_email)
                                )
                                conn_db.commit()
                            
                            st.toast("Verification successful! Account created. 🎉")
                            
                            # Clean up session state
                            st.session_state.otp_stage = "details"
                            st.session_state.temp_reg_data = None
                            st.session_state.reg_otp = None
                            st.session_state.otp_sent = None
                            
                            # Switch to login tab
                            st.session_state.auth_page = "login"
                            st.rerun()
                        except sqlite3.IntegrityError:
                            show_error("An account with this username was registered while you were verifying. Please start over.")
                        except Exception as e:
                            show_error(f"Error establishing account: {str(e)}")

            with col_cancel:
                if st.button("↩️ Cancel & Edit", use_container_width=True, type="secondary", key="btn_cancel_otp"):
                    st.session_state.otp_stage = "details"
                    if st.session_state.temp_reg_data:
                        st.session_state.reg_user = st.session_state.temp_reg_data.get("username", "")
                        st.session_state.reg_email = st.session_state.temp_reg_data.get("email", "")
                        st.session_state.reg_pwd = st.session_state.temp_reg_data.get("password", "")
                        st.session_state.reg_confirm = st.session_state.temp_reg_data.get("password", "")
                        st.session_state.reg_role = st.session_state.temp_reg_data.get("role", "Applicant")
                    st.session_state.reg_otp = None
                    st.session_state.otp_sent = None
                    st.rerun()

            st.markdown('</div>', unsafe_allow_html=True)

    # =================================================
    # FORGOT PASSWORD SECTION
    # =================================================
    else:
        # Ensure forgot_otp_stage is initialized
        if "forgot_otp_stage" not in st.session_state:
            st.session_state.forgot_otp_stage = "details"

        if st.session_state.forgot_otp_stage == "details":
            st.markdown('<div class="auth-card-container">', unsafe_allow_html=True)
            
            st.markdown(
                """
                <div style='text-align: center; margin-bottom: 25px;'>
                    <h2 style='color:#EC4899; margin:0; font-weight:700; font-size:26px;'>Reset Password</h2>
                    <p style='color:#94A3B8; margin:5px 0 0 0;'>Securely update your login credentials</p>
                </div>
                """,
                unsafe_allow_html=True
            )

            with st.form("forgot_form", clear_on_submit=False):
                # Bind inputs to session_state keys directly to prevent Streamlit value-reset bugs
                user = st.text_input("👤 Enter Username", placeholder="Your account username", key="forgot_user")
                new_pwd = st.text_input("🔑 New Password", type="password", placeholder="Minimum 8 characters", key="forgot_pwd")
                confirm = st.text_input("🔄 Confirm New Password", type="password", placeholder="Repeat new password", key="forgot_confirm")

                st.write("")

                submit_forgot = st.form_submit_button("🔄 Update Password", type="primary", use_container_width=True)

            if submit_forgot:
                user_val = st.session_state.get("forgot_user", "").strip()
                new_pwd_val = st.session_state.get("forgot_pwd", "")
                confirm_val = st.session_state.get("forgot_confirm", "")

                if not user_val or not new_pwd_val or not confirm_val:
                    show_error("All credentials and fields are required for security updates.")
                elif new_pwd_val != confirm_val:
                    show_error("Confirmation mismatch. New passwords do not match!")
                else:
                    missing_criteria = check_password_strength(new_pwd_val)
                    if missing_criteria:
                        msg = "Password does not meet complexity requirements:<br>" + "".join(f"• {item}<br>" for item in missing_criteria)
                        show_error(msg)
                    else:
                        # Verify if user exists and fetch email
                        try:
                            with sqlite3.connect("interview.db", timeout=30.0, check_same_thread=False) as conn_db:
                                conn_db.execute("PRAGMA journal_mode=WAL;")
                                cursor_db = conn_db.cursor()
                                res = cursor_db.execute("SELECT email FROM users WHERE username=?", (user_val,)).fetchone()
                                
                                if not res:
                                    show_error(f"Account for user '{user_val}' was not found. Cannot perform reset.")
                                else:
                                    user_email = res[0]
                                    if not user_email:
                                        show_error("This account does not have a registered email address. Please contact support.")
                                    else:
                                        # Generate 6-digit OTP code
                                        otp_code = f"{random.randint(100000, 999999)}"
                                        
                                        # Save data to session state
                                        st.session_state.temp_forgot_data = {
                                            "username": user_val,
                                            "new_password": new_pwd_val,
                                            "email": user_email
                                        }
                                        st.session_state.forgot_otp = otp_code
                                        
                                        # Attempt to send OTP email
                                        with st.spinner("Sending verification code to your registered email..."):
                                            otp_sent, smtp_msg = send_password_reset_email(user_email, otp_code)
                                            
                                        if not otp_sent:
                                            show_error(f"❌ <b>Email Dispatch Failure:</b> {smtp_msg}")
                                        else:
                                            st.session_state.forgot_otp_sent = True
                                            st.session_state.forgot_otp_stage = "verify"
                                            st.rerun()
                        except Exception as e:
                            show_error(f"Database/System Error: {str(e)}")

            st.markdown('</div>', unsafe_allow_html=True)

        elif st.session_state.forgot_otp_stage == "verify":
            st.markdown('<div class="auth-card-container">', unsafe_allow_html=True)
            
            st.markdown(
                """
                <div style='text-align: center; margin-bottom: 25px;'>
                    <h2 style='color:#06B6D4; margin:0; font-weight:700; font-size:26px;'>Verify OTP Code</h2>
                    <p style='color:#94A3B8; margin:5px 0 0 0;'>Verify your identity to reset password</p>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            temp_email = st.session_state.temp_forgot_data.get("email", "")
            masked = mask_email(temp_email)
            st.markdown(
                f"""
                <div style='text-align: center; margin-bottom: 20px;'>
                    <span style='color: #E2E8F0; font-size: 15px;'>Sent to registered email: <b>{masked}</b></span>
                </div>
                """,
                unsafe_allow_html=True
            )

            otp_input = st.text_input("🎯 Enter 6-Digit Code", max_chars=6, placeholder="e.g. 123456", key="forgot_otp_input")

            st.write("")

            col_verify, col_cancel = st.columns(2)
            
            with col_verify:
                if st.button("✅ Verify OTP & Reset", use_container_width=True, type="primary", key="btn_confirm_forgot_otp"):
                    if not otp_input:
                        show_error("Please enter the 6-digit verification code.")
                    elif otp_input != st.session_state.forgot_otp:
                        show_error("Invalid verification code. Please check the code and try again.")
                    else:
                        # Success! Update password in DB
                        temp_data = st.session_state.temp_forgot_data
                        forgot_user = temp_data["username"]
                        new_pwd = temp_data["new_password"]
                        
                        try:
                            # Hash the new password securely
                            hashed_new_pwd = hash_password(new_pwd)

                            with sqlite3.connect("interview.db", timeout=30.0, check_same_thread=False) as conn_db:
                                conn_db.execute("PRAGMA journal_mode=WAL;")
                                cursor_db = conn_db.cursor()
                                
                                # Update password
                                cursor_db.execute(
                                    "UPDATE users SET password=? WHERE username=?",
                                    (hashed_new_pwd, forgot_user)
                                )
                                conn_db.commit()
                            
                            st.toast("Password reset successful! 🎉")
                            
                            # Clean up session state
                            st.session_state.forgot_otp_stage = "details"
                            st.session_state.temp_forgot_data = None
                            st.session_state.forgot_otp = None
                            st.session_state.forgot_otp_sent = None
                            
                            # Switch to login tab
                            st.session_state.auth_page = "login"
                            st.rerun()
                        except Exception as e:
                            show_error(f"Error resetting password: {str(e)}")

            with col_cancel:
                if st.button("↩️ Cancel & Edit", use_container_width=True, type="secondary", key="btn_cancel_forgot_otp"):
                    st.session_state.forgot_otp_stage = "details"
                    if st.session_state.temp_forgot_data:
                        st.session_state.forgot_user = st.session_state.temp_forgot_data.get("username", "")
                        st.session_state.forgot_pwd = st.session_state.temp_forgot_data.get("new_password", "")
                        st.session_state.forgot_confirm = st.session_state.temp_forgot_data.get("new_password", "")
                    st.session_state.forgot_otp = None
                    st.session_state.forgot_otp_sent = None
                    st.rerun()
