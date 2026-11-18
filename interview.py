import streamlit as st
import sqlite3
from gtts import gTTS
import os
import re
import speech_recognition as sr
from audio_recorder_streamlit import audio_recorder
import google.generativeai as genai
import base64
import json
import time
import random
import datetime

# =====================================================
# GEMINI AI CONFIG
# =====================================================
try:
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
        model = genai.GenerativeModel(model_name="models/gemini-2.5-flash")
    else:
        model = None
except Exception as e:
    model = None

# =====================================================
# TAB + FULLSCREEN SECURITY DETECTION (PERSISTENT VIA SESSIONSTORAGE)
# =====================================================
def inject_proctoring_security():
    st.markdown("""
<script>
// Initialize warning count from sessionStorage so it survives Streamlit reruns
if (!sessionStorage.getItem("warningCount")) {
    sessionStorage.setItem("warningCount", "0");
}

function getWarnings() {
    return parseInt(sessionStorage.getItem("warningCount") || "0");
}

function addWarning(reason) {
    let current = getWarnings();
    current++;
    sessionStorage.setItem("warningCount", current.toString());
    
    alert("⚠ SECURITY WARNING (" + current + "/3): " + reason + "\\n\\nSwitching tabs, exiting fullscreen, or minimizing the window is strictly prohibited.");
    
    if (current >= 3) {
        alert("❌ ASSESSMENT TERMINATED\\n\\nYou have exceeded the maximum allowed security violations. Your session will be closed.");
        sessionStorage.setItem("warningCount", "0");
        window.location.reload();
    }
}

// Fullscreen force function
function forceFullscreen() {
    let elem = document.documentElement;
    if (elem.requestFullscreen && !document.fullscreenElement) {
        elem.requestFullscreen().catch(err => {
            console.log("Fullscreen request failed: " + err.message);
        });
    }
}

// Track visibility change (tab switching)
document.addEventListener("visibilitychange", function () {
    if (document.hidden) {
        addWarning("Tab switch detected!");
    }
});

// Track exit from fullscreen
document.addEventListener("fullscreenchange", function () {
    if (!document.fullscreenElement) {
        addWarning("Exit from Fullscreen mode detected!");
        // Re-request fullscreen after a slight delay
        setTimeout(forceFullscreen, 1000);
    }
});

// Click to re-engage fullscreen if lost
document.addEventListener("click", forceFullscreen);

</script>
""", unsafe_allow_html=True)

# =====================================================
# DATABASE INITIALIZATION
# =====================================================
import auth
auth.init_database()

# =====================================================
# AUDIO FOLDER INITIALIZATION
# =====================================================
if not os.path.exists("audio_files"):
    os.makedirs("audio_files")

# =====================================================
# QUESTION BANKS AND FALLBACKS
# =====================================================
FALLBACK_QUESTIONS = {
    "python": [
        "What is the difference between list and tuple in Python, and when would you use a generator?",
        "Explain how memory management and garbage collection work in Python.",
        "How do decorators work in Python? Can you describe a real-world scenario where you would write a custom decorator?",
        "What are list comprehensions and generator expressions, and how do they differ in memory utilization?",
        "Explain the difference between deep copy and shallow copy in Python with an example."
    ],
    "java": [
        "What is the difference between Interfaces and Abstract Classes in Java 8+, and when do you use which?",
        "Explain the Java Memory Model, specifically Heap vs Stack, and how garbage collection functions.",
        "What is the difference between fail-fast and fail-safe iterators in Java? Give examples.",
        "How does class loading work in Java, and what are the different types of class loaders?",
        "Describe the synchronization mechanisms in Java and the difference between synchronized block and ReentrantLock."
    ],
    "sql": [
        "What is the difference between INNER JOIN, LEFT JOIN, and RIGHT JOIN? How does a FULL OUTER JOIN differ?",
        "What are indexes in SQL, and how do they speed up queries? Are there any downsides?",
        "Explain SQL injections and describe three different methods to prevent them in database applications.",
        "What are database transactions, and what does the ACID property stand for? Give an example.",
        "What is the difference between the WHERE and HAVING clauses in a SQL statement?"
    ],
    "machine learning": [
        "What is the difference between supervised and unsupervised learning? Can you give real-world use cases for both?",
        "Explain the bias-variance tradeoff and how it relates to overfitting and underfitting.",
        "How do you handle missing or imbalanced data in a machine learning dataset before feeding it to a model?",
        "Describe how a Random Forest classifier works, and explain how it prevents overfitting compared to a single Decision Tree.",
        "What are the common evaluation metrics for classification and regression models? When would you use F1-score over Accuracy?"
    ]
}

FALLBACK_PROJECT_QUESTIONS = [
    "Describe a complex technical challenge you faced in a recent software project. How did you diagnose it, what trade-offs did you consider, and how did you resolve it?",
    "If you had to scale a web application or system you built to handle 100x more concurrent traffic, where would the bottlenecks occur and how would you redesign it?",
    "Tell me about a time you had to debug a difficult, intermittent production issue. What steps and tools did you take to isolate the root cause?"
]

FALLBACK_GENERAL_QUESTIONS = [
    "What are the key differences between monolithic and microservice architectures? What are the trade-offs of each?",
    "Explain the concept of RESTful APIs and what HTTP status codes like 200, 201, 400, 401, 404, and 500 signify.",
    "How does caching improve system performance? Discuss different caching strategies like CDN, Redis, and In-Memory."
]

ENGLISH_MCQ_BANK = [
    {
        "question": "Choose the word that is closest in meaning to 'diligent':",
        "options": ["A) Lazy", "B) Careless", "C) Hardworking", "D) Ignorant"],
        "answer": "C) Hardworking"
    },
    {
        "question": "Which of the following sentences is grammatically CORRECT?",
        "options": [
            "A) Neither of the candidates were selected.",
            "B) Each of the students has submitted their assignment.",
            "C) The team have won the championship.",
            "D) She sings beautiful than her sister."
        ],
        "answer": "B) Each of the students has submitted their assignment."
    },
    {
        "question": "Identify the antonym of the word 'fragile':",
        "options": ["A) Delicate", "B) Strong", "C) Weak", "D) Soft"],
        "answer": "B) Strong"
    },
    {
        "question": "Fill in the blank: 'If I _____ you, I would have accepted the offer immediately.'",
        "options": ["A) was", "B) am", "C) were", "D) had been"],
        "answer": "C) were"
    },
    {
        "question": "Select the correct spelling of the word denoting a decorative arrangement of flowers:",
        "options": ["A) Bouquet", "B) Boquet", "C) Bouquette", "D) Boquett"],
        "answer": "A) Bouquet"
    },
    {
        "question": "Identify the passive form of: 'The developer wrote the clean code.'",
        "options": [
            "A) Clean code is written by the developer.",
            "B) Clean code was written by the developer.",
            "C) Clean code was being written by the developer.",
            "D) Clean code had been written by the developer."
        ],
        "answer": "B) Clean code was written by the developer."
    },
    {
        "question": "What is the meaning of the idiom 'burn the midnight oil'?",
        "options": [
            "A) Wasting resource unnecessarily",
            "B) Work or study late into the night",
            "C) Create electric energy",
            "D) Causing a fire hazard at night"
        ],
        "answer": "B) Work or study late into the night"
    }
]

TECHNICAL_MCQ_BANK = {
    "Computer Networks": [
        {
            "question": "Which of the following layers of the OSI model is responsible for routing packets across network boundaries?",
            "options": ["A) Physical Layer", "B) Data Link Layer", "C) Network Layer", "D) Transport Layer"],
            "answer": "C) Network Layer"
        },
        {
            "question": "What is the primary protocol used to resolve a domain name like google.com into an IP address?",
            "options": ["A) HTTP", "B) FTP", "C) DNS", "D) DHCP"],
            "answer": "C) DNS"
        },
        {
            "question": "Which TCP/IP protocol is responsible for establishing a reliable, connection-oriented byte stream between hosts?",
            "options": ["A) UDP", "B) IP", "C) TCP", "D) ICMP"],
            "answer": "C) TCP"
        },
        {
            "question": "What is the primary purpose of the Address Resolution Protocol (ARP) in a local area network?",
            "options": ["A) Map domain name to IP", "B) Map IP address to MAC address", "C) Control traffic congestion", "D) Assign dynamic IP addresses"],
            "answer": "B) Map IP address to MAC address"
        },
        {
            "question": "Which of the following port numbers is the default standard for secure HTTP traffic (HTTPS)?",
            "options": ["A) 80", "B) 21", "C) 443", "D) 8080"],
            "answer": "C) 443"
        }
    ],
    "Database Management System": [
        {
            "question": "What normalization form eliminates partial dependency, ensuring all non-key attributes are fully dependent on the primary key?",
            "options": ["A) 1NF", "B) 2NF", "C) 3NF", "D) BCNF"],
            "answer": "B) 2NF"
        },
        {
            "question": "In database transactions, which ACID property ensures that all operations in a transaction are completed successfully, or none are?",
            "options": ["A) Atomicity", "B) Consistency", "C) Isolation", "D) Durability"],
            "answer": "A) Atomicity"
        },
        {
            "question": "Which of the following SQL joins returns all records from the left table, and the matched records from the right table?",
            "options": ["A) INNER JOIN", "B) FULL JOIN", "C) LEFT JOIN", "D) RIGHT JOIN"],
            "answer": "C) LEFT JOIN"
        },
        {
            "question": "What is the main purpose of a database Index in DBMS architectures?",
            "options": [
                "A) To ensure referential integrity constraints",
                "B) To compress the physical storage space on disk",
                "C) To speed up retrieval of rows by avoiding full table scans",
                "D) To automate trigger evaluations"
            ],
            "answer": "C) To speed up retrieval of rows by avoiding full table scans"
        },
        {
            "question": "Which database anomaly occurs when a change to one data record requires making multiple duplicate changes throughout the database?",
            "options": ["A) Insertion Anomaly", "B) Deletion Anomaly", "C) Update Anomaly", "D) Isolation Anomaly"],
            "answer": "C) Update Anomaly"
        }
    ],
    "Operating Systems": [
        {
            "question": "Which CPU scheduling algorithm is non-preemptive and assigns the CPU to the process that requests it first?",
            "options": ["A) Shortest Job First (SJF)", "B) Round Robin (RR)", "C) First-Come, First-Served (FCFS)", "D) Priority Scheduling"],
            "answer": "C) First-Come, First-Served (FCFS)"
        },
        {
            "question": "Which of the following is NOT one of the Coffman conditions required for a system deadlock to occur?",
            "options": ["A) Mutual Exclusion", "B) Hold and Wait", "C) Preemption allowed", "D) Circular Wait"],
            "answer": "C) Preemption allowed"
        },
        {
            "question": "What OS concept refers to keeping multiple programs in memory at the same time to increase CPU utilization?",
            "options": ["A) Multithreading", "B) Multiprocessing", "C) Multiprogramming", "D) Paging"],
            "answer": "C) Multiprogramming"
        },
        {
            "question": "In virtual memory systems, what is a Page Fault?",
            "options": [
                "A) A hardware error in physical memory chips",
                "B) An illegal memory reference by a user process",
                "C) An event that occurs when a requested page is not in physical RAM",
                "D) A sector read failure on secondary disk"
            ],
            "answer": "C) An event that occurs when a requested page is not in physical RAM"
        },
        {
            "question": "What is the main function of the Operating System Kernel?",
            "options": [
                "A) Rendering the graphical user interface",
                "B) Providing core hardware abstractions, process management, and memory isolation",
                "C) Managing internet browser cookies and caching",
                "D) Compiling source code files"
            ],
            "answer": "B) Providing core hardware abstractions, process management, and memory isolation"
        }
    ]
}

APTITUDE_MCQ_BANK = [
    {
        "question": "A can complete a piece of work in 12 days and B can do it in 24 days. Working together, how many days will they take to complete the work?",
        "options": ["A) 6 days", "B) 8 days", "C) 10 days", "D) 12 days"],
        "answer": "B) 8 days"
    },
    {
        "question": "A bag contains 3 red, 5 green, and 4 blue balls. If one ball is drawn at random, what is the probability that it is green?",
        "options": ["A) 5/12", "B) 1/4", "C) 1/3", "D) 5/7"],
        "answer": "A) 5/12"
    },
    {
        "question": "If the price of a commodity increases by 25%, by how much percentage must a household reduce its consumption so that its expenditure remains unchanged?",
        "options": ["A) 20%", "B) 25%", "C) 15%", "D) 30%"],
        "answer": "A) 20%"
    },
    {
        "question": "In a sequence: 3, 8, 15, 24, 35, what is the next number?",
        "options": ["A) 44", "B) 48", "C) 49", "D) 50"],
        "answer": "B) 48"
    },
    {
        "question": "A train 120 meters long passes a telegraph post in 6 seconds. What is the speed of the train in kilometers per hour?",
        "options": ["A) 60 km/h", "B) 72 km/h", "C) 80 km/h", "D) 90 km/h"],
        "answer": "B) 72 km/h"
    },
    {
        "question": "If 12 men can build a wall in 20 days, how many men are required to build the same wall in 15 days?",
        "options": ["A) 15", "B) 16", "C) 18", "D) 20"],
        "answer": "B) 16"
    }
]

# =====================================================
# SPEAK FUNCTION (TTS)
# =====================================================
def speak(text):
    try:
        tts = gTTS(text)
        tts.save("voice.mp3")
        with open("voice.mp3", "rb") as f:
            audio_bytes = f.read()
        b64_audio = base64.b64encode(audio_bytes).decode("utf-8")
        audio_html = f"""
        <audio autoplay="true" style="display:none;">
            <source src="data:audio/mp3;base64,{b64_audio}" type="audio/mp3">
        </audio>
        """
        st.markdown(audio_html, unsafe_allow_html=True)
    except Exception:
        st.warning("🎙 Voice narration is currently unavailable. Text displayed below.")

# =====================================================
# SPEECH TO TEXT
# =====================================================
def speech_to_text(file):
    r = sr.Recognizer()
    try:
        with sr.AudioFile(file) as source:
            audio = r.record(source)
        return r.recognize_google(audio)
    except Exception:
        return "Speech could not be transcribed clearly by the engine."

# =====================================================
# DYNAMIC AI ANSWER EVALUATION
# =====================================================
def evaluate_r1_spoken_answer(question, answer, q_type="HR"):
    if model:
        try:
            prompt = f"""
            You are a professional Introduction and Technical Interviewer.
            Evaluate this candidate's spoken response.
            Question Type: {q_type}
            Question: {question}
            Candidate's Answer: {answer}
            
            Provide:
            1. An integer score out of 6 for accuracy, depth, and communication.
            2. A confidence score between 1 and 10 based on structure, phrasing, and articulation confidence.
            
            Return strictly a JSON object:
            {{
              "score": 5,
              "confidence": 8.5
            }}
            Do not write any markdown blocks (```json) or other text.
            """
            response = model.generate_content(prompt)
            clean_text = response.text.strip()
            if clean_text.startswith("```"):
                lines = clean_text.splitlines()
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines[-1].startswith("```"):
                    lines = lines[:-1]
                clean_text = "\n".join(lines).strip()
            data = json.loads(clean_text)
            return float(data["score"]), float(data["confidence"])
        except Exception:
            pass
            
    # Fallback heuristic
    score = 3.0
    conf = 6.5
    wc = len(answer.split())
    if wc > 40:
        score += 1.0
        conf += 1.0
    if q_type == "Technical" and any(w in answer.lower() for w in ["use", "code", "example", "problem", "solve", "design"]):
        score += 1.0
        conf += 1.0
    return min(6.0, score), min(10.0, conf)

def generate_stress_test_followup(question, answer, skills):
    """
    Analyzes the candidate's response to a core technical question, extracts technical claims,
    and generates a customized, deeper follow-up question.
    """
    skills_str = ", ".join(skills) if skills else "general software engineering"
    
    if model:
        try:
            prompt = f"""
            You are an elite, highly technical AI interviewer stress-testing a candidate.
            The candidate's core skills are: {skills_str}.
            They were asked: "{question}"
            They answered: "{answer}"
            
            Your goal:
            1. Extract any technical claims, systems, tools, algorithms, or architectures they claim to have built or used (e.g., "RAG chatbot", "Redis cache", "microservices", "JWT authentication", etc.).
            2. If they have made technical claims, generate a highly targeted, deeper probing technical follow-up question that tests the depth of their knowledge. (For example, if they mention a vector database, ask about their choice of distance metrics and chunking strategy. If they mention Redis, ask about eviction policies or cache consistency).
            
            Return strictly a JSON object:
            {{
              "has_technical_claims": true or false,
              "followup_question": "Your highly targeted deeper probing follow-up question, or empty string if has_technical_claims is false."
            }}
            Do not write any markdown blocks (```json) or extra explanation. Return raw JSON.
            """
            response = model.generate_content(prompt)
            clean_text = response.text.strip()
            if clean_text.startswith("```"):
                lines = clean_text.splitlines()
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines[-1].startswith("```"):
                    lines = lines[:-1]
                clean_text = "\n".join(lines).strip()
            data = json.loads(clean_text)
            if data.get("has_technical_claims") and data.get("followup_question"):
                return True, data["followup_question"]
        except Exception:
            pass

    # Local Rule-Based Fallback Engine
    answer_lower = answer.lower()
    local_rules = [
        ("rag", "What distance metric (like Cosine similarity or L2 distance) did you choose for vector similarity search, and how did you manage text chunking overlaps?"),
        ("vector", "Which distance metric did you choose for similarity search in your vector database, and how did you choose your embedding dimensions?"),
        ("redis", "What cache eviction policy did you select for Redis, and how did you handle cache consistency with the primary database?"),
        ("cache", "What cache eviction policy did you select, and how did you handle cache consistency or cache stampede?"),
        ("microservice", "How did you manage service discovery, distributed tracing, and communication protocols (REST vs gRPC) in your microservices?"),
        ("docker", "How did you design your container image size, handle persistent storage, and secure communications between your containers?"),
        ("kubernetes", "What ingress controller did you configure, and how did you set up resource limits, liveness probes, and horizontal pod autoscaling?"),
        ("jwt", "How did you securely store JWT tokens, and what was your token expiration and blacklisting/refresh strategy?"),
        ("auth", "How did you handle authentication security, rate limiting, and password hashing salts?"),
        ("api", "How did you implement API security, rate limiting, and standard error propagation?"),
        ("rest", "How did you handle API versioning, CORS restrictions, and payload size optimization?"),
        ("react", "How did you manage client state, and what strategies did you use to prevent unnecessary component re-renders?"),
        ("sql", "How did you optimize slow-running database queries, and how did you choose between indexing vs query partitioning?"),
        ("database", "How did you manage connection pooling, transaction isolation levels, and indexes?"),
        ("django", "How did you optimize Django's ORM N+1 query problem, and how did you manage migrations safely?"),
        ("flask", "How did you handle application context, secure database connections, and session storage?"),
        ("spring", "How did you manage Spring Bean scopes, dependency injection cycles, and JPA query optimization?"),
    ]
    
    for keyword, probe in local_rules:
        if keyword in answer_lower:
            return True, probe

    # General Fallback Probe
    if len(answer.split()) > 15:
        return True, "Can you walk me through the exact database or architectural trade-offs you had to consider while building this feature?"
        
    return False, ""

def evaluate_r1_followup_answer(parent_q, followup_q, transcript, skills):
    """
    Evaluates the candidate's answer to a stress-test follow-up question.
    Checks if they have a knowledge gap (shallow, generic, or copied answer).
    """
    skills_str = ", ".join(skills) if skills else "general software engineering"
    
    if model:
        try:
            prompt = f"""
            You are a rigorous technical interviewer.
            The candidate previously answered a question about "{parent_q}".
            You probed deeper with the follow-up question: "{followup_q}"
            Their response to your follow-up is: "{transcript}"
            
            Evaluate if this response is shallow, generic, evasive, or copied, indicating they don't actually know the depth of what they claimed.
            For example:
            - Good response: explains specific implementation details, choices made, or trade-offs.
            - Shallow/Gap response: says "I used standard settings", "I don't remember", "I followed a tutorial", or gives a very generic definition without actual implementation details.
            
            Return strictly a JSON object:
            {{
              "score": 1 to 6 (grading accuracy & depth),
              "confidence": 1 to 10 (articulation confidence),
              "knowledge_gap_noted": "A concise professional explanation of the specific knowledge gap if one is identified, otherwise null.",
              "polite_gap_msg": "A polite, positive, and encouraging feedback snippet highlighting the gap as an area of growth, or null if no gap is identified."
            }}
            Do not write any markdown blocks (```json) or extra commentary. Return raw JSON.
            """
            response = model.generate_content(prompt)
            clean_text = response.text.strip()
            if clean_text.startswith("```"):
                lines = clean_text.splitlines()
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines[-1].startswith("```"):
                    lines = lines[:-1]
                clean_text = "\n".join(lines).strip()
            data = json.loads(clean_text)
            return {
                "score": float(data.get("score", 3.0)),
                "confidence": float(data.get("confidence", 6.5)),
                "knowledge_gap_noted": data.get("knowledge_gap_noted"),
                "polite_gap_msg": data.get("polite_gap_msg")
            }
        except Exception:
            pass

    # Heuristic Fallback Engine
    wc = len(transcript.split())
    transcript_lower = transcript.lower()
    
    # Check for evasive phrases or very short answers
    evasive_keywords = ["don't know", "dont know", "not sure", "forgot", "standard", "default", "tutorial", "copied", "simple", "basic", "just used", "no idea", "co-pilot", "copilot", "chatgpt"]
    is_evasive = any(kw in transcript_lower for kw in evasive_keywords) or wc < 20
    
    if is_evasive:
        gap_desc = "Candidate gave a shallow or generic response with insufficient technical detail regarding their implementation choice."
        polite_msg = "Your response gives a high-level summary, though providing more technical depth on the implementation details and distance metrics is always recommended!"
        return {
            "score": 2.0,
            "confidence": 5.0,
            "knowledge_gap_noted": gap_desc,
            "polite_gap_msg": polite_msg
        }
        
    return {
        "score": 4.5,
        "confidence": 8.0,
        "knowledge_gap_noted": None,
        "polite_gap_msg": None
    }

def evaluate_r2_spoken_eval(question, answer):
    if model:
        try:
            prompt = f"""
            You are a professional speech and communications analyst.
            Evaluate this candidate's spoken response.
            Question: {question}
            Candidate's Answer: {answer}
            
            Provide ratings (out of 6):
            - "score": general communication score (1-6)
            - "fluency": fluency of speaking (1-6)
            - "pronunciation": grammar and word clarity (1-6)
            - "confidence": posture/vibe confidence (1-6)
            - "comm_quality": explanation logic and structure (1-6)
            - "speaking_consistency": consistency and speed pacing (1-6)
            - "remarks": brief professional analytical feedback (1 sentence)
            
            Return strictly a JSON object matching this schema. Do not write any markdown blocks (```json) or extra text.
            """
            response = model.generate_content(prompt)
            clean_text = response.text.strip()
            if clean_text.startswith("```"):
                lines = clean_text.splitlines()
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines[-1].startswith("```"):
                    lines = lines[:-1]
                clean_text = "\n".join(lines).strip()
            data = json.loads(clean_text)
            return data
        except Exception:
            pass
            
    # Heuristic fallback
    wc = len(answer.split())
    score = 3.0
    if wc > 35:
        score += 1.0
    return {
        "score": min(6.0, score),
        "fluency": min(6.0, score),
        "pronunciation": min(6.0, score),
        "confidence": min(6.0, score + 1.0),
        "comm_quality": min(6.0, score),
        "speaking_consistency": min(6.0, score),
        "remarks": "Response was clear and coherent. Fluid explanations of communication styles."
    }

def run_python_subprocess(code_str):
    from sandbox import run_python_sandbox
    _, output = run_python_sandbox(code_str, timeout=5.0)
    return output

def run_code_sandbox(problem, code, language):
    if language.lower() == "python":
        return run_python_subprocess(code)
        
    if model:
        try:
            prompt = f"""
            You are a secure compiler and execution sandbox simulator.
            Your task is to compile and run the candidate's code for a debugging challenge, and return the execution output exactly as a real compiler/runner would.
            
            Context:
            Language: {language}
            Problem Statement: {problem}
            Candidate's Code Solution:
            {code}
            
            Rules:
            1. If the code has syntax errors, compilation errors, or runtime exceptions, output the exact compiler/runtime error message and traceback.
            2. If the code compiles and runs successfully, simulate running it against standard test cases implied by the problem. Output the standard console output (stdout) and standard error output (stderr) just like a real terminal console.
            3. Do not include any conversational filler, notes, or markdown styling (like ```bash or ```c++). Start directly with the program's output.
            4. Keep output concise and realistic.
            """
            response = model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            return f"Simulated Sandbox Environment Connection Error: {str(e)}"
            
    # Fallback if Gemini is offline
    return f"Compiler execution for {language} is temporarily offline. Please submit your solution for review."

def evaluate_coding_solution(problem, code, correct_code="", language=""):
    if model:
        try:
            prompt = f"""
            You are an expert software engineer and technical interviewer.
            Evaluate the candidate's debugged code solution for this debugging challenge:
            
            Language: {language}
            Problem & Bug Context:
            {problem}
            
            Reference Correct Code:
            {correct_code}
            
            Candidate's Debugged Code:
            {code}
            
            Evaluate if the candidate successfully identified and fixed the bug. Check for correctness, edge cases, and code style.
            Provide:
            1. An integer score out of 6 based on correctness of the fix. (6/6 if the bug is completely resolved and code is robust).
            2. A very brief professional code feedback (under 3 lines) addressing their fix.
            
            Return the output strictly in a JSON format matching:
            {{
              "score": 5,
              "feedback": "Great job fixing the off-by-one boundary! Your loop boundary check is correct now."
            }}
            Do not write any other text or markdown block backticks.
            """
            response = model.generate_content(prompt)
            clean_text = response.text.strip()
            if clean_text.startswith("```"):
                lines = clean_text.splitlines()
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines[-1].startswith("```"):
                    lines = lines[:-1]
                clean_text = "\n".join(lines).strip()
            data = json.loads(clean_text)
            return int(data["score"]), data["feedback"]
        except Exception:
            pass

    # Heuristic fallback grading
    score = 1
    code_lower = code.lower()
    if len(code) > 10:
        score += 1
    # Simple check for keywords based on language/patterns
    if "equals" in code_lower or "let " in code_lower or "virtual" in code_lower or "+ 1" in code_lower or "None" in code_lower or "<" in code_lower:
        score += 3
    feedback = "Code parsed successfully by fallback engine. Good logical attempts at resolving the bug."
    return min(6, score), feedback

# =====================================================
# DOCK DATA PERSISTENCE HELPERS
# =====================================================
def resolve_user_id(user_ident):
    """Resolve username or other identifier to unique user_id."""
    if isinstance(user_ident, str) and user_ident.startswith("USR-"):
        return user_ident
    if "user_id" in st.session_state:
        return st.session_state.user_id
    try:
        with sqlite3.connect("interview.db", timeout=30.0, check_same_thread=False) as conn:
            c = conn.cursor()
            res = c.execute("SELECT user_id FROM users WHERE username = ?", (user_ident,)).fetchone()
            if res:
                return res[0]
    except Exception:
        pass
    return user_ident

def get_or_create_question(round_name, question_type, question_text, correct_answer=None, subject_category=None):
    """Retrieve question_id for a given question. Creates it in the catalog if it doesn't exist."""
    with sqlite3.connect("interview.db", timeout=30.0, check_same_thread=False) as conn:
        conn.execute("PRAGMA journal_mode=WAL;")
        c = conn.cursor()
        res = c.execute(
            "SELECT question_id FROM questions WHERE question_text = ? AND round_name = ?", 
            (question_text, round_name)
        ).fetchone()
        if res:
            return res[0]
        else:
            c.execute(
                "INSERT INTO questions (round_name, question_type, question_text, correct_answer, subject_category) VALUES (?, ?, ?, ?, ?)",
                (round_name, question_type, question_text, correct_answer, subject_category)
            )
            conn.commit()
            return c.lastrowid

def save_r1_spoken_answer(user, q_text, transcript, audio_path, score, confidence, q_type, is_follow_up=0, parent_question=None, knowledge_gap_noted=None):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    user_id = resolve_user_id(user)
    question_id = get_or_create_question("Round 1", q_type, q_text)
    with sqlite3.connect("interview.db", timeout=30.0, check_same_thread=False) as conn_db:
        conn_db.execute("PRAGMA journal_mode=WAL;")
        cursor = conn_db.cursor()
        cursor.execute("""
        INSERT INTO r1_hr_intro (user_id, question_id, transcript, audio_path, timestamp, score, confidence_score, is_follow_up, parent_question, knowledge_gap_noted)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_id, question_id, transcript, audio_path, ts, score, confidence, is_follow_up, parent_question, knowledge_gap_noted))
        conn_db.commit()

def save_r2_mcq_answer(user, q_text, selected, correct, score):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    user_id = resolve_user_id(user)
    question_id = get_or_create_question("Round 2", "MCQ", q_text, correct)
    with sqlite3.connect("interview.db", timeout=30.0, check_same_thread=False) as conn_db:
        conn_db.execute("PRAGMA journal_mode=WAL;")
        cursor = conn_db.cursor()
        cursor.execute("""
        INSERT INTO r2_english_comm (user_id, question_id, selected_answer, score, timestamp)
        VALUES (?, ?, ?, ?, ?)
        """, (user_id, question_id, selected, score, ts))
        conn_db.commit()

def save_r2_spoken_answer(user, q_text, transcript, audio_path, score, fluency, pronunciation, confidence, comm_quality, consistency, remarks):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    user_id = resolve_user_id(user)
    question_id = get_or_create_question("Round 2", "Voice", q_text)
    with sqlite3.connect("interview.db", timeout=30.0, check_same_thread=False) as conn_db:
        conn_db.execute("PRAGMA journal_mode=WAL;")
        cursor = conn_db.cursor()
        cursor.execute("""
        INSERT INTO r2_english_comm (user_id, question_id, audio_path, transcript, score, fluency, pronunciation, confidence, comm_quality, speaking_consistency, remarks, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_id, question_id, audio_path, transcript, score, fluency, pronunciation, confidence, comm_quality, consistency, remarks, ts))
        conn_db.commit()

def save_r3_mcq_answer(user, q_idx, q_text, selected, correct, score, category):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    user_id = resolve_user_id(user)
    question_id = get_or_create_question("Round 3", "MCQ", q_text, correct, category)
    with sqlite3.connect("interview.db", timeout=30.0, check_same_thread=False) as conn_db:
        conn_db.execute("PRAGMA journal_mode=WAL;")
        cursor = conn_db.cursor()
        cursor.execute("""
        INSERT INTO r3_technical_mcq (user_id, question_id, selected_answer, score, timestamp)
        VALUES (?, ?, ?, ?, ?)
        """, (user_id, question_id, selected, score, ts))
        conn_db.commit()

def save_r4_mcq_answer(user, q_idx, q_text, selected, correct, score):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    user_id = resolve_user_id(user)
    question_id = get_or_create_question("Round 4", "Aptitude", q_text, correct)
    with sqlite3.connect("interview.db", timeout=30.0, check_same_thread=False) as conn_db:
        conn_db.execute("PRAGMA journal_mode=WAL;")
        cursor = conn_db.cursor()
        cursor.execute("""
        INSERT INTO r4_aptitude_coding (user_id, question_id, selected_answer, score, timestamp)
        VALUES (?, ?, ?, ?, ?)
        """, (user_id, question_id, selected, score, ts))
        conn_db.commit()

def save_r4_coding_answer(user, q_idx, q_text, code, lang, output, score, time_sec):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    user_id = resolve_user_id(user)
    question_id = get_or_create_question("Round 4", "Coding", q_text)
    with sqlite3.connect("interview.db", timeout=30.0, check_same_thread=False) as conn_db:
        conn_db.execute("PRAGMA journal_mode=WAL;")
        cursor = conn_db.cursor()
        cursor.execute("""
        INSERT INTO r4_aptitude_coding (user_id, question_id, code_submitted, language, execution_output, score, time_taken, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_id, question_id, code, lang, output, score, time_sec, ts))
        conn_db.commit()

# =====================================================
# MULTI-ROUND DYNAMIC GENERATION ROUTINES
# =====================================================
def generate_r1_questions(user, skills, seed):
    # Static Intro, Academics, Fitment, Role Fitment
    qs = [
        {"type": "spoken", "question": "Tell me about yourself", "badge": "Introduction", "question_type": "HR"},
        {"type": "spoken", "question": "Explain your academic background", "badge": "Academic Background", "question_type": "HR"},
        {"type": "spoken", "question": "Why should we hire you?", "badge": "Fitment & Value", "question_type": "HR"},
        {"type": "spoken", "question": "Why are you fit for this job role?", "badge": "Role Fitment", "question_type": "HR"}
    ]
    
    # 5 Dynamic skills-based technical questions
    tech_qs = []
    if model:
        try:
            skills_str = ", ".join(skills) if skills else "general software engineering"
            prompt = f"""
            You are a professional technical recruiter.
            Generate exactly 5 short, professional, clear, practical, and project-oriented interview questions for a candidate named '{user}' based on these resume-extracted skills: {skills_str}.
            Rules:
            - Avoid repeating questions.
            - Ask about practical concepts, debugging, or project-oriented tasks.
            - Return the output strictly in a JSON list of strings: ["Question 1", "Question 2", "Question 3", "Question 4", "Question 5"].
            - Use this seed for deterministic randomization: {seed}.
            - Do not write any markdown blocks (```json) or extra commentary.
            """
            response = model.generate_content(prompt)
            clean_text = response.text.strip()
            if clean_text.startswith("```"):
                lines = clean_text.splitlines()
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines[-1].startswith("```"):
                    lines = lines[:-1]
                clean_text = "\n".join(lines).strip()
            parsed = json.loads(clean_text)
            if isinstance(parsed, list) and len(parsed) == 5:
                for q in parsed:
                    tech_qs.append({"type": "spoken", "question": q, "badge": "Technical Profile Validation", "question_type": "Technical"})
        except Exception:
            pass
            
    if len(tech_qs) < 5:
        # Fallback local pool
        fallback_pool = []
        for s in skills:
            s_lower = s.lower()
            if s_lower in FALLBACK_QUESTIONS:
                fallback_pool.extend(FALLBACK_QUESTIONS[s_lower])
        if not fallback_pool:
            fallback_pool.extend(FALLBACK_GENERAL_QUESTIONS)
            fallback_pool.extend(FALLBACK_PROJECT_QUESTIONS)
            
        r = random.Random(f"{user}_{seed}_r1")
        selected = r.sample(fallback_pool, min(len(fallback_pool), 5))
        while len(selected) < 5:
            selected.append(r.choice(FALLBACK_GENERAL_QUESTIONS))
            
        for q in selected:
            tech_qs.append({"type": "spoken", "question": q, "badge": "Technical Profile Validation", "question_type": "Technical"})
            
    return qs + tech_qs

def generate_r2_questions(user, seed):
    # Section A: 5 English MCQs
    r = random.Random(f"{user}_{seed}_r2_mcq")
    selected_mcqs = r.sample(ENGLISH_MCQ_BANK, 5)
    
    mcq_qs = []
    for i, m in enumerate(selected_mcqs):
        mcq_qs.append({
            "type": "mcq",
            "badge": f"Section A: English MCQ {i+1}",
            "question": m["question"],
            "options": m["options"],
            "answer": m["answer"],
            "section": "A"
        })
        
    # Section B: 5 Voice Answer Questions
    voice_qs = [
        {"type": "spoken", "question": "Describe your strengths.", "badge": "Section B: Strengths", "section": "B"},
        {"type": "spoken", "question": "Explain your leadership skills.", "badge": "Section B: Leadership", "section": "B"},
        {"type": "spoken", "question": "Describe a difficult situation you handled.", "badge": "Section B: Resilience", "section": "B"},
        {"type": "spoken", "question": "Explain your teamwork experience.", "badge": "Section B: Collaboration", "section": "B"},
        {"type": "spoken", "question": "Describe your future goals.", "badge": "Section B: Future Goals", "section": "B"}
    ]
    
    return mcq_qs + voice_qs

def generate_r3_questions(user, seed):
    r = random.Random(f"{user}_{seed}_r3")
    
    nw_selected = r.sample(TECHNICAL_MCQ_BANK["Computer Networks"], 3)
    db_selected = r.sample(TECHNICAL_MCQ_BANK["Database Management System"], 3)
    os_selected = r.sample(TECHNICAL_MCQ_BANK["Operating Systems"], 4)
    
    all_selected = nw_selected + db_selected + os_selected
    r.shuffle(all_selected)
    
    mcq_qs = []
    for i, m in enumerate(all_selected):
        subject = "OS"
        if m in TECHNICAL_MCQ_BANK["Computer Networks"]:
            subject = "Computer Networks"
        elif m in TECHNICAL_MCQ_BANK["Database Management System"]:
            subject = "DBMS"
            
        mcq_qs.append({
            "type": "mcq",
            "badge": f"Round 3: Technical MCQ {i+1}",
            "question": m["question"],
            "options": m["options"],
            "answer": m["answer"],
            "subject": subject
        })
        
    return mcq_qs

def generate_fallback_r4_debugging_questions(user, seed):
    r = random.Random(f"{user}_{seed}_r4_debug_fallback")
    
    # We will pick 5 unique patterns out of our 7 patterns
    available_indices = [1, 2, 3, 4, 5, 6, 7]
    selected_patterns = r.sample(available_indices, 5)
    
    challenges = []
    for idx, pattern_num in enumerate(selected_patterns):
        if pattern_num == 1:
            # Mutable Default Argument (Python)
            func_name = r.choice(["add_to_collection", "append_record", "collect_scores", "gather_items"])
            item_name = r.choice(["val", "item", "entry", "score"])
            list_name = r.choice(["items", "records", "data_list", "container"])
            val1 = r.choice([10, "apple", 100])
            val2 = r.choice([20, "banana", 200])
            
            buggy_code = f"""def {func_name}({item_name}, {list_name}=[]):
    {list_name}.append({item_name})
    return {list_name}

# Testing the function
print({func_name}({repr(val1)}))
print({func_name}({repr(val2)}))
"""
            correct_code = f"""def {func_name}({item_name}, {list_name}=None):
    if {list_name} is None:
        {list_name} = []
    {list_name}.append({item_name})
    return {list_name}

# Testing the function
print({func_name}({repr(val1)}))
print({func_name}({repr(val2)}))
"""
            problem = f"This Python function is designed to append an item to a list and return the list. However, successive calls without passing an explicit list are sharing state. Diagnose the issue and rewrite the code using Python best practices for default arguments."
            title = f"Python: Default Mutable Argument in {func_name}"
            lang = "Python"
            
        elif pattern_num == 2:
            # Closure Scope var inside Loop (JavaScript)
            func_name = r.choice(["triggerNotifications", "setupIntervals", "launchCallbacks", "delayLoggers"])
            var_name = r.choice(["i", "idx", "counter", "seq"])
            limit = r.choice([3, 4, 5])
            
            buggy_code = f"""function {func_name}() {{
    for (var {var_name} = 0; {var_name} < {limit}; {var_name}++) {{
        setTimeout(function() {{
            console.log("Index: " + {var_name});
        }}, 100);
    }}
}}
{func_name}();
"""
            correct_code = f"""function {func_name}() {{
    for (let {var_name} = 0; {var_name} < {limit}; {var_name}++) {{
        setTimeout(function() {{
            console.log("Index: " + {var_name});
        }}, 100);
    }}
}}
{func_name}();
"""
            problem = f"This JavaScript function is supposed to log numbers from 0 to {limit - 1} after a 100ms delay. However, it prints the value '{limit}' multiple times. Fix the scope-related bug to output the correct sequential indices."
            title = f"JavaScript: Closure Loop Scope in {func_name}"
            lang = "JavaScript"
            
        elif pattern_num == 3:
            # Java String Comparison (Java)
            class_name = r.choice(["CredentialVerifier", "StringValidator", "SessionManager", "TokenMatcher"])
            method_name = r.choice(["verifyToken", "checkMatch", "validateInput"])
            var1 = r.choice(["userInput", "passedStr", "inputKey"])
            var2 = r.choice(["secretToken", "correctKey", "targetWord"])
            val_secret = r.choice(["ADMIN_123", "SECRET_KEY", "SECURE_PASS"])
            
            buggy_code = f"""public class {class_name} {{
    public static boolean {method_name}(String {var1}) {{
        String {var2} = new String("{val_secret}");
        // BUG: String references compared instead of values
        if ({var1} == {var2}) {{
            return true;
        }}
        return false;
    }}
}}
"""
            correct_code = f"""public class {class_name} {{
    public static boolean {method_name}(String {var1}) {{
        String {var2} = new String("{val_secret}");
        // FIX: Use .equals() for value comparison
        if ({var2}.equals({var1})) {{
            return true;
        }}
        return false;
    }}
}}
"""
            problem = f"In Java, comparing strings using reference check can fail even if their contents match. The method `{method_name}` checks if the input matches the target value, but it is returning `false` incorrectly. Rewrite it to perform content value comparison."
            title = f"Java: Reference vs Value Comparison in {class_name}"
            lang = "Java"
            
        elif pattern_num == 4:
            # C++ Off-by-one array loop boundary (C++)
            func_name = r.choice(["sumArray", "findMaxVal", "calculateTotal", "computeAverage"])
            arr_name = r.choice(["nums", "scores", "values", "data"])
            size_var = r.choice(["n", "size", "length"])
            
            buggy_code = f"""#include <iostream>
using namespace std;

int {func_name}(int {arr_name}[], int {size_var}) {{
    int total = 0;
    // BUG: Off-by-one error (accesses index equal to size)
    for (int i = 0; i <= {size_var}; i++) {{
        total += {arr_name}[i];
    }}
    return total;
}}
"""
            correct_code = f"""#include <iostream>
using namespace std;

int {func_name}(int {arr_name}[], int {size_var}) {{
    int total = 0;
    // FIX: strictly less than size_var
    for (int i = 0; i < {size_var}; i++) {{
        total += {arr_name}[i];
    }}
    return total;
}}
"""
            problem = f"This C++ function calculates the sum of elements in an array. However, it contains an off-by-one out-of-bounds array access boundary check error. Correct the loop guard to prevent memory faults."
            title = f"C++: Off-By-One Array Bound in {func_name}"
            lang = "C++"
            
        elif pattern_num == 5:
            # Python Binary Search (Python)
            func_name = r.choice(["binary_search", "find_index", "search_sorted", "locate_val"])
            low_var = r.choice(["low", "left", "start"])
            high_var = r.choice(["high", "right", "end"])
            
            buggy_code = f"""def {func_name}(nums, target):
    {low_var}, {high_var} = 0, len(nums) - 1
    while {low_var} <= {high_var}:
        mid = ({low_var} + {high_var}) // 2
        if nums[mid] == target:
            return mid
        elif nums[mid] < target:
            # BUG: Causes infinite loop when low and high are close
            {low_var} = mid
        else:
            {high_var} = mid - 1
    return -1
"""
            correct_code = f"""def {func_name}(nums, target):
    {low_var}, {high_var} = 0, len(nums) - 1
    while {low_var} <= {high_var}:
        mid = ({low_var} + {high_var}) // 2
        if nums[mid] == target:
            return mid
        elif nums[mid] < target:
            {low_var} = mid + 1
            # FIX: bounds properly updated
        else:
            {high_var} = mid - 1
    return -1
"""
            problem = f"This binary search function is prone to entering an infinite loop when the target element is in the upper half or not present in the sequence. Identify and correct the bound-updating error."
            title = f"Python: Binary Search Loop Bug in {func_name}"
            lang = "Python"
            
        elif pattern_num == 6:
            # JavaScript Shallow Copy Reference Mutation (JavaScript)
            func_name = r.choice(["updateUserProfile", "modifyRecord", "adjustSettings", "updateConfig"])
            prop_name = r.choice(["address", "metadata", "preferences", "config"])
            key_name = r.choice(["city", "role", "theme", "mode"])
            val_init = r.choice(["New York", "User", "dark", "production"])
            val_new = r.choice(["Boston", "Admin", "light", "development"])
            
            buggy_code = f"""function {func_name}() {{
    const original = {{
        id: 101,
        {prop_name}: {{
            {key_name}: "{val_init}"
        }}
    }};
    
    // BUG: Shallow copy via spread operator
    const copy = {{ ...original }};
    copy.{prop_name}.{key_name} = "{val_new}";
    
    console.log("Original: " + original.{prop_name}.{key_name});
    console.log("Copy: " + copy.{prop_name}.{key_name});
}}
{func_name}();
"""
            correct_code = f"""function {func_name}() {{
    const original = {{
        id: 101,
        {prop_name}: {{
            {key_name}: "{val_init}"
        }}
    }};
    
    // FIX: Deep copy or deep cloning/spreading
    const copy = {{
        ...original,
        {prop_name}: {{
            ...original.{prop_name},
            {key_name}: "{val_new}"
        }}
    }};
    copy.{prop_name}.{key_name} = "{val_new}";
    
    console.log("Original: " + original.{prop_name}.{key_name});
    console.log("Copy: " + copy.{prop_name}.{key_name});
}}
{func_name}();
"""
            problem = f"This JavaScript function creates a shallow copy of an object but accidentally mutates the nested property on the original object. Fix the bug so that mutating the copy does not modify the original's nested `{prop_name}`."
            title = f"JavaScript: Nested Shallow Copy in {func_name}"
            lang = "JavaScript"
            
        elif pattern_num == 7:
            # C++ Non-virtual destructor (C++)
            base_class = r.choice(["Shape", "Device", "Worker", "Account"])
            derived_class = r.choice(["Circle", "Printer", "Manager", "SavingsAccount"])
            
            buggy_code = f"""#include <iostream>
using namespace std;

class {base_class} {{
public:
    {base_class}() {{ cout << "Constructing Base\\n"; }}
    // BUG: Destructor is not virtual, leading to memory leaks
    ~{base_class}() {{ cout << "Destroying Base\\n"; }}
}};

class {derived_class} : public {base_class} {{
public:
    {derived_class}() {{ cout << "Constructing Derived\\n"; }}
    ~{derived_class}() {{ cout << "Destroying Derived\\n"; }}
}};

void run_test() {{
    {base_class}* ptr = new {derived_class}();
    delete ptr;
}}
"""
            correct_code = f"""#include <iostream>
using namespace std;

class {base_class} {{
public:
    {base_class}() {{ cout << "Constructing Base\\n"; }}
    // FIX: virtual destructor to ensure derived is deleted
    virtual ~{base_class}() {{ cout << "Destroying Base\\n"; }}
}};

class {derived_class} : public {base_class} {{
public:
    {derived_class}() {{ cout << "Constructing Derived\\n"; }}
    ~{derived_class}() {{ cout << "Destroying Derived\\n"; }}
}};

void run_test() {{
    {base_class}* ptr = new {derived_class}();
    delete ptr;
}}
"""
            problem = f"In this C++ inheritance setup, deleting a derived class pointer via a base class pointer causes a memory leak because the derived class destructor is never invoked. Add the correct keyword to ensure virtual destruction."
            title = f"C++: Non-Virtual Destructor Leak in {base_class}"
            lang = "C++"

        challenges.append({
            "type": "coding",
            "badge": f"Section B: Debugging Challenge {idx+1}",
            "question": f"[Debugging] {title}",
            "problem": problem,
            "buggy_code": buggy_code.strip(),
            "language": lang,
            "correct_code": correct_code.strip(),
            "section": "B"
        })
        
    return challenges

def generate_r4_questions(user, seed):
    r = random.Random(f"{user}_{seed}_r4")
    
    # Section A: 5 Aptitude MCQs
    selected_apt = r.sample(APTITUDE_MCQ_BANK, 5)
    apt_qs = []
    for i, m in enumerate(selected_apt):
        apt_qs.append({
            "type": "mcq",
            "badge": f"Section A: Aptitude MCQ {i+1}",
            "question": m["question"],
            "options": m["options"],
            "answer": m["answer"],
            "section": "A"
        })
        
    # Section B: 5 Coding Debugging Questions
    code_qs = []
    if model:
        try:
            prompt = f"""
            You are an elite coding interviewer. Generate exactly 5 unique and separate debugging challenges in different languages (Python, Java, C++, JavaScript) for an applicant named '{user}'.
            Each challenge must be a real, practical code debugging problem.
            
            Rules:
            1. Provide a variety of bug types: e.g., off-by-one errors, infinite loops, variable scope shadowing, list/array mutability traps, resource leaks, or type mismatch.
            2. The programming languages must be distributed among: Python, Java, C++, JavaScript.
            3. Each challenge must be completely custom and unique to this seed: {seed}.
            4. Make sure each buggy code has a logical bug that can be fixed.
            5. Return the response strictly as a JSON array of 5 objects matching this JSON schema:
            [
              {{
                "title": "Short descriptive title of the bug",
                "language": "Python" or "Java" or "C++" or "JavaScript",
                "problem": "Clear explanation of what the function is supposed to do, the inputs/outputs, and the bug description.",
                "buggy_code": "The exact source code containing the bug.",
                "correct_code": "The exact corrected source code."
              }}
            ]
            
            Return ONLY the valid JSON array. Do not wrap it in markdown backticks or write any other text.
            """
            response = model.generate_content(prompt)
            clean_text = response.text.strip()
            # Clean markdown code block if present
            if clean_text.startswith("```"):
                lines = clean_text.splitlines()
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines[-1].startswith("```"):
                    lines = lines[:-1]
                clean_text = "\n".join(lines).strip()
            
            parsed = json.loads(clean_text)
            if isinstance(parsed, list) and len(parsed) == 5:
                for idx, c in enumerate(parsed):
                    code_qs.append({
                        "type": "coding",
                        "badge": f"Section B: Debugging Challenge {idx+1}",
                        "question": f"[Debugging] {c['title']}",
                        "problem": c["problem"],
                        "buggy_code": c["buggy_code"].strip(),
                        "language": c["language"],
                        "correct_code": c.get("correct_code", "").strip(),
                        "section": "B"
                    })
        except Exception as e:
            # Fallback will trigger if there's any parsing/calling error
            pass
            
    if len(code_qs) < 5:
        # Trigger dynamic fallback
        code_qs = generate_fallback_r4_debugging_questions(user, seed)
        
    return apt_qs + code_qs

# =====================================================
# AGGREGATE FINAL SCORES CALCULATION
# =====================================================
def generate_local_fallback_roadmap(skills_str, comm_score, tech_score, apt_score, code_score, beh_score, applied_domain, gaps_str):
    scores = {
        "Communication": comm_score,
        "Technical CS": tech_score,
        "Aptitude": apt_score,
        "Coding Logic": code_score,
        "Behavioral": beh_score
    }
    lowest_metric = min(scores, key=scores.get)
    lowest_score = scores[lowest_metric]
    
    roadmap = {
        "strengths": [],
        "weaknesses": [f"{lowest_metric} skills need improvement (current average: {lowest_score:.1f}%)"],
        "gaps_analysis": f"Based on our evaluation, the candidate showed promise but has notable gaps in {lowest_metric}. Specific noted gaps: {gaps_str}",
        "weekly_plan": [],
        "recommended_resources": [],
        "custom_exercises": [],
        "encouragement": "Every successful career is built on persistence and continuous learning. Take this feedback as a powerful step forward!"
    }
    
    for metric, score in scores.items():
        if score >= 60:
            roadmap["strengths"].append(f"Strong foundational competence in {metric} ({score:.1f}%)")
    if not roadmap["strengths"]:
        roadmap["strengths"].append("Demonstrated solid determination and completion of all assessment rounds.")
        
    for metric, score in scores.items():
        if score < 50 and metric != lowest_metric:
            roadmap["weaknesses"].append(f"{metric} conceptual grasp is developing ({score:.1f}%)")
            
    if lowest_metric == "Coding Logic":
        roadmap["weekly_plan"] = [
            {
                "week": "Week 1: Data Structures Foundations",
                "focus": "Mastering core arrays, strings, and hash maps.",
                "topics": ["Arrays", "Strings", "Hash Maps", "Time Complexity"],
                "action_items": [
                    "Complete 10 Easy-level array questions on LeetCode.",
                    "Review Big-O notation and learn to calculate runtime bounds."
                ]
            },
            {
                "week": "Week 2: Recursive Thinking & Sorting",
                "focus": "Understanding basic algorithms and dynamic array handling.",
                "topics": ["Recursion", "Binary Search", "Two-Pointers", "Sorting"],
                "action_items": [
                    "Implement Binary Search manually in Python/Java.",
                    "Solve 5 recursion-based problems and map their execution trees."
                ]
            },
            {
                "week": "Week 3: Advanced Linear Structures & Trees",
                "focus": "Building confidence with linked lists, stacks, queues, and binary trees.",
                "topics": ["Linked Lists", "Stacks", "Queues", "Binary Trees"],
                "action_items": [
                    "Implement a Stack using an array and a linked list.",
                    "Solve Tree Pre-order, In-order, and Post-order traversals."
                ]
            },
            {
                "week": "Week 4: Mock Coding Assessments",
                "focus": "Simulating high-pressure technical programming rounds.",
                "topics": ["Problem-Solving", "Speed coding", "Boundary testing"],
                "action_items": [
                    "Take a 60-minute mock coding test under standard exam pressure.",
                    "Review and optimize all solutions for optimal space complexity."
                ]
            }
        ]
        roadmap["recommended_resources"] = [
            {"name": "NeetCode 150 roadmaps", "type": "Platform", "url_or_desc": "Excellent systematic coding questions list grouped by topic."},
            {"name": "Introduction to Algorithms (CLRS)", "type": "Book", "url_or_desc": "The gold-standard academic textbook for understanding algorithmic complexity."}
        ]
        roadmap["custom_exercises"] = [
            {"title": "Reverse a Linked List", "description": "Write an iterative and recursive solution to reverse a singly linked list in O(n) time.", "difficulty": "Medium"},
            {"title": "Valid Parentheses Checker", "description": "Use a Stack data structure to verify if a string of brackets is perfectly balanced.", "difficulty": "Easy"}
        ]
    elif lowest_metric == "Technical CS":
        roadmap["weekly_plan"] = [
            {
                "week": "Week 1: DBMS & SQL mastery",
                "focus": "Relational databases, indexing, normalization, and ACID properties.",
                "topics": ["SQL Queries", "Database Joins", "Normalization", "Indexing"],
                "action_items": [
                    "Write complex SQL queries involving INNER/LEFT joins and GROUP BY commands.",
                    "Study indexing mechanisms and explain how B-Trees optimize database searches."
                ]
            },
            {
                "week": "Week 2: Operating Systems core principles",
                "focus": "Process management, CPU scheduling, thread pools, and deadlocks.",
                "topics": ["CPU Scheduling", "Virtual Memory", "Deadlocks", "Semaphores"],
                "action_items": [
                    "Implement and simulate Shortest Job First (SJF) scheduling algorithms.",
                    "Draft an explanation of the four banker conditions required for deadlocks."
                ]
            },
            {
                "week": "Week 3: Computer Networks layers & protocols",
                "focus": "Understanding TCP/IP models, routing protocols, DNS, and HTTP.",
                "topics": ["TCP/IP Layering", "DNS lookup", "Three-Way Handshake", "HTTP/HTTPS"],
                "action_items": [
                    "Map out every single step in a standard TCP Three-Way Handshake connection.",
                    "Explain the difference between Symmetric and Asymmetric encryption in HTTPS."
                ]
            },
            {
                "week": "Week 4: System Design foundational blocks",
                "focus": "Architectural principles, load balancers, caching, and rate limiting.",
                "topics": ["Load Balancing", "Caching (Redis)", "CDNs", "Horizontal Scaling"],
                "action_items": [
                    "Design a basic architectural diagram for a scalable URL Shortening service.",
                    "Read whitepapers on standard Redis caching strategies (Cache-Aside, Write-Through)."
                ]
            }
        ]
        roadmap["recommended_resources"] = [
            {"name": "Gate Smashers CS Playlists", "type": "YouTube Channel", "url_or_desc": "Incredible step-by-step visual breakdowns of DBMS, OS, and CN lectures."},
            {"name": "System Design Primer (GitHub)", "type": "Repository", "url_or_desc": "Highly recommended repository mapping all system design concepts."}
        ]
        roadmap["custom_exercises"] = [
            {"title": "Optimize the Missing Index Query", "description": "Given a slow-running query with multiple joins, rewrite the query and outline exactly where to add indexes.", "difficulty": "Medium"},
            {"title": "OS Deadlock Avoidance Case", "description": "Solve a custom banker's algorithm table to find if the system remains in a safe state.", "difficulty": "Medium"}
        ]
    elif lowest_metric == "Communication":
        roadmap["weekly_plan"] = [
            {
                "week": "Week 1: Speech Flow & Pronunciation",
                "focus": "Developing vocabulary structure and clear syllable pacing.",
                "topics": ["Pacing", "Articulation", "Clarity", "Tone Control"],
                "action_items": [
                    "Record yourself speaking on a general topic for 2 minutes and evaluate your pacing.",
                    "Practice standard syllable exercises to polish tricky sounds."
                ]
            },
            {
                "week": "Week 2: Professional Scenario Handling",
                "focus": "Structuring cohesive and professional answers for workplace dynamics.",
                "topics": ["Cohesion", "Professional Ethics", "Conflict Dialogue"],
                "action_items": [
                    "Write down and practice verbal scripts for handling late client deliverables.",
                    "Study active listening response techniques."
                ]
            },
            {
                "week": "Week 3: Confident Presentation Pacing",
                "focus": "Managing speaker anxiety and maintaining steady vocal dynamics.",
                "topics": ["Vocal Variety", "Anxiety Reduction", "Pause Management"],
                "action_items": [
                    "Deliver a 5-minute presentation in front of a mirror, using pauses instead of filler words.",
                    "Practice breathing control techniques to maintain a steady vocal pitch."
                ]
            },
            {
                "week": "Week 4: Mock Verbal Interviews",
                "focus": "Testing speaking consistency under active recruiter pressure.",
                "topics": ["Fluency", "Response Speed", "Interactive Listening"],
                "action_items": [
                    "Perform a simulated mock interview with a peer, recording and transcribing the audio.",
                    "Analyze transcription records to eliminate filler words (like 'um', 'ah', 'like')."
                ]
            }
        ]
        roadmap["recommended_resources"] = [
            {"name": "Toastmasters International", "type": "Community Platform", "url_or_desc": "Public speaking clubs around the world providing structured speaking feedback."},
            {"name": "Speak with Confidence - Harvard Guide", "type": "Online Article", "url_or_desc": "Excellent guidelines on voice modulation and vocabulary improvement."}
        ]
        roadmap["custom_exercises"] = [
            {"title": "The Elevator Pitch Challenge", "description": "Prepare and record a 60-second verbal summary of your best technical project, keeping pacing at precisely 130 words per minute.", "difficulty": "Easy"},
            {"title": "STAR Response Construction", "description": "Write down a structured STAR response for a time when you managed a complex team conflict.", "difficulty": "Easy"}
        ]
    else:
        roadmap["weekly_plan"] = [
            {
                "week": "Week 1: Logical Reasoning & Math Patterns",
                "focus": "Speed calculation, sequence patterns, and quantitative aptitude.",
                "topics": ["Quantitative Math", "Sequence Patterns", "Permutations", "Puzzles"],
                "action_items": [
                    "Solve 20 aptitude puzzles testing profit-loss, time-work, and speed relations.",
                    "Review shortcuts for mental math calculations."
                ]
            },
            {
                "week": "Week 2: STAR Interview Framework",
                "focus": "Structuring narrative responses using Situation, Task, Action, and Result.",
                "topics": ["STAR Method", "Behavioral Alignment", "Leadership Stories"],
                "action_items": [
                    "Draft three detailed STAR answers focusing on problem-solving under pressure.",
                    "Review standard Amazon/Netflix leadership principle questions."
                ]
            },
            {
                "week": "Week 3: Time Management & Speed Tests",
                "focus": "Improving analytical speed under strict time boundaries.",
                "topics": ["Speed Math", "Logical Puzzles", "Aptitude Mock Exams"],
                "action_items": [
                    "Take three timed 30-minute logical reasoning practice exams.",
                    "Analyze wrong choices and review correct mathematical proofs."
                ]
            },
            {
                "week": "Week 4: Executive Presence & Closure",
                "focus": "Synthesizing professional background and behavioral confidence.",
                "topics": ["Executive Speaking", "STAR Polishing", "Interviewer Engagement"],
                "action_items": [
                    "Perform a complete mock behavioral test with simulated high-stress scenarios.",
                    "Review body language, voice modulation, and positive closing remarks."
                ]
            }
        ]
        roadmap["recommended_resources"] = [
            {"name": "IndiaBIX Aptitude Tutorials", "type": "Platform", "url_or_desc": "Extremely detailed quantitative math questions, categorized by topics."},
            {"name": "Brilliant.org Interactive Puzzles", "type": "Platform", "url_or_desc": "Superb interactive learning courses on logic, math, and problem-solving."}
        ]
        roadmap["custom_exercises"] = [
            {"title": "STAR Framework Structuring", "description": "Draft a perfect 250-word STAR response for a time you had to adapt quickly to changing project scopes.", "difficulty": "Easy"},
            {"title": "Quantitative Speed Drills", "description": "Solve 15 time-distance and work rate problems, maintaining a solving speed of under 45 seconds per question.", "difficulty": "Medium"}
        ]
        
    return json.dumps(roadmap)

# =====================================================
# AGGREGATE FINAL SCORES CALCULATION
# =====================================================
def calculate_and_save_final_results(username):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    user_id = resolve_user_id(username)
    
    with sqlite3.connect("interview.db", timeout=30.0, check_same_thread=False) as conn_db:
        conn_db.execute("PRAGMA journal_mode=WAL;")
        cursor = conn_db.cursor()
        
        # Gather R1 using INNER JOIN on questions
        r1_rows = cursor.execute("""
            SELECT r.score, r.confidence_score, q.question_type 
            FROM r1_hr_intro r
            INNER JOIN questions q ON r.question_id = q.question_id
            WHERE r.user_id=?
        """, (user_id,)).fetchall()
        r1_hr_scores = [r[0] for r in r1_rows if r[2] == "HR"]
        r1_tech_scores = [r[0] for r in r1_rows if r[2] == "Technical"]
        r1_hr_conf = [r[1] for r in r1_rows if r[2] == "HR"]
        
        # Gather R2 using INNER JOIN on questions
        r2_rows = cursor.execute("""
            SELECT r.score, r.confidence, q.question_type 
            FROM r2_english_comm r
            INNER JOIN questions q ON r.question_id = q.question_id
            WHERE r.user_id=?
        """, (user_id,)).fetchall()
        r2_mcq_scores = [r[0] for r in r2_rows if r[2] == "MCQ"]
        r2_voice_scores = [r[0] for r in r2_rows if r[2] == "Voice"]
        r2_voice_conf = [r[1] for r in r2_rows if r[2] == "Voice"]
        
        # Gather R3
        r3_rows = cursor.execute("SELECT score FROM r3_technical_mcq WHERE user_id=?", (user_id,)).fetchall()
        r3_scores = [r[0] for r in r3_rows]
        
        # Gather R4 using INNER JOIN on questions
        r4_rows = cursor.execute("""
            SELECT r.score, q.question_type 
            FROM r4_aptitude_coding r
            INNER JOIN questions q ON r.question_id = q.question_id
            WHERE r.user_id=?
        """, (user_id,)).fetchall()
        r4_apt_scores = [r[0] for r in r4_rows if r[1] == "Aptitude"]
        r4_code_scores = [r[0] for r in r4_rows if r[1] == "Coding"]
        
    # comm score (out of 100)
    comm_sum = sum(r1_hr_scores) + sum(r2_voice_scores) + sum(r2_mcq_scores)
    comm_max = (len(r1_hr_scores) + len(r2_voice_scores) + len(r2_mcq_scores)) * 6
    comm_score = (comm_sum / comm_max) * 100 if comm_max > 0 else 50.0
    
    # tech score (out of 100)
    tech_sum = sum(r1_tech_scores) + sum(r3_scores)
    tech_max = (len(r1_tech_scores) + len(r3_scores)) * 6
    tech_score = (tech_sum / tech_max) * 100 if tech_max > 0 else 50.0
    
    # apt score (out of 100)
    apt_sum = sum(r4_apt_scores)
    apt_max = len(r4_apt_scores) * 6
    apt_score = (apt_sum / apt_max) * 100 if apt_max > 0 else 50.0
    
    # code score (out of 100)
    code_sum = sum(r4_code_scores)
    code_max = len(r4_code_scores) * 6
    code_score = (code_sum / code_max) * 100 if code_max > 0 else 50.0
    
    # behavioral score (out of 100)
    conf_1 = sum(r1_hr_conf)
    conf_1_max = len(r1_hr_conf) * 10.0
    conf_2 = sum(r2_voice_conf)
    conf_2_max = len(r2_voice_conf) * 6.0
    
    beh_score = 50.0
    if conf_1_max > 0 and conf_2_max > 0:
        beh_score = ((conf_1 / conf_1_max) * 50.0) + ((conf_2 / conf_2_max) * 50.0)
    elif conf_1_max > 0:
        beh_score = (conf_1 / conf_1_max) * 100
    elif conf_2_max > 0:
        beh_score = (conf_2 / conf_2_max) * 100
        
    overall_avg = (comm_score + tech_score + apt_score + code_score + beh_score) / 5.0
    if overall_avg >= 75.0:
        recom = "Selected"
    elif overall_avg >= 50.0:
        recom = "Average"
    else:
        recom = "Rejected"
        
    # Get candidate skills from session state
    skills_list = st.session_state.get("skills", [])
    skills_str = ", ".join(skills_list) if skills_list else ""

    # Retrieve or dynamically calculate Career Matching fields
    applied_domain = st.session_state.get("domain", "Software Engineering")
    alternative_domain = st.session_state.get("alternative_domain", None)
    alternative_reason = st.session_state.get("alternative_reason", None)

    if not alternative_domain and skills_list:
        from skills import match_career_path
        alt_d, alt_r = match_career_path(skills_list, applied_domain)
        if alt_d:
            alternative_domain = alt_d
            alternative_reason = alt_r

    # AI CANDIDATE FEEDBACK LOOP: Generate personalized growth roadmap for rejected candidates
    growth_roadmap_json = None
    if recom == "Rejected":
        gaps_str = "None explicitly noted."
        try:
            with sqlite3.connect("interview.db", timeout=30.0, check_same_thread=False) as conn_gaps:
                conn_gaps.execute("PRAGMA journal_mode=WAL;")
                c_gaps = conn_gaps.cursor()
                gaps_rows = c_gaps.execute(
                    "SELECT knowledge_gap_noted FROM r1_hr_intro WHERE user_id=? AND knowledge_gap_noted IS NOT NULL AND knowledge_gap_noted != ''",
                    (user_id,)
                ).fetchall()
                if gaps_rows:
                    gaps_str = "; ".join([r[0] for r in gaps_rows])
        except Exception:
            pass
            
        gemini_success = False
        if model:
            prompt = f"""
            You are the elite AI Talent Development & Career Coach at Smart Hire.
            Your task is to generate a premium, highly actionable, and encouraging **Personalized Career Growth Roadmap** in valid JSON format for a candidate who was not selected for the {applied_domain} position.
            
            Here are the candidate's metrics:
            - Candidate Name: {username}
            - Applied Domain: {applied_domain}
            - Candidate Skillset: {skills_str}
            - Communication Average: {comm_score:.1f}%
            - Technical CS Average: {tech_score:.1f}%
            - Quantitative Aptitude Average: {apt_score:.1f}%
            - Coding Logic Average: {code_score:.1f}%
            - Behavioral/Confidence Index: {beh_score:.1f}%
            - AI Identified Knowledge Gaps (from verbal rounds): {gaps_str}
            
            You MUST return a JSON object with the following schema:
            {{
              "strengths": ["list of 2-3 specific strength pillars based on their high scores or attempts"],
              "weaknesses": ["list of 2-3 specific growth areas targeting their lower-scoring categories"],
              "gaps_analysis": "a concise qualitative summary analysis of their assessment logs, CS conceptual gaps, or coding/speaking issues in 2-3 sentences",
              "weekly_plan": [
                {{
                  "week": "Week 1: [Strategic Title for their lowest score category]",
                  "focus": "[Concise description of the weekly goal]",
                  "topics": ["[Topic A]", "[Topic B]", "[Topic C]"],
                  "action_items": ["[Action Item 1]", "[Action Item 2]"]
                }},
                {{
                  "week": "Week 2: [Strategic Title]",
                  "focus": "[Focus area]",
                  "topics": ["[Topic D]", "[Topic E]"],
                  "action_items": ["[Action Item 3]", "[Action Item 4]"]
                }},
                {{
                  "week": "Week 3: [Strategic Title]",
                  "focus": "[Focus area]",
                  "topics": ["[Topic F]", "[Topic G]"],
                  "action_items": ["[Action Item 5]", "[Action Item 6]"]
                }},
                {{
                  "week": "Week 4: [Strategic Title]",
                  "focus": "[Focus area]",
                  "topics": ["[Topic H]", "[Topic I]"],
                  "action_items": ["[Action Item 7]", "[Action Item 8]"]
                }}
              ],
              "recommended_resources": [
                {{
                  "name": "[Platform/Book/Course Name]",
                  "type": "[Book / Platform / Video Channel / Interactive Course]",
                  "url_or_desc": "[Short description or link]"
                }},
                {{
                  "name": "[Resource 2]",
                  "type": "[Type]",
                  "url_or_desc": "[Short description]"
                }}
              ],
              "custom_exercises": [
                {{
                  "title": "[Challenge Title]",
                  "description": "[Concrete scenario or coding task tailored to their weak area]",
                  "difficulty": "[Easy / Medium / Hard]"
                }},
                {{
                  "title": "[Challenge Title 2]",
                  "description": "[Concrete scenario]",
                  "difficulty": "[Easy / Medium / Hard]"
                }}
              ],
              "encouragement": "[A warm, highly supportive, motivational message to boost their spirits and encourage persistent practice in 2 sentences]"
            }}
            
            IMPORTANT:
            - Return ONLY valid JSON.
            - Do not put Markdown headers, ```json, or other prose before or after the JSON block.
            - Ensure all keys and strings are properly enclosed in double quotes.
            - Tailor the week-by-week plan dynamically to address their lowest scored metric(s) and their applied domain.
            """
            try:
                response = model.generate_content(prompt)
                res_text = response.text.strip()
                if res_text.startswith("```"):
                    res_text = re.sub(r"^```(?:json)?\n", "", res_text)
                    res_text = re.sub(r"\n```$", "", res_text)
                res_text = res_text.strip()
                
                parsed_json = json.loads(res_text)
                if all(k in parsed_json for k in ["strengths", "weaknesses", "weekly_plan", "recommended_resources", "custom_exercises"]):
                    growth_roadmap_json = json.dumps(parsed_json)
                    gemini_success = True
            except Exception:
                pass
                
        if not gemini_success:
            growth_roadmap_json = generate_local_fallback_roadmap(skills_str, comm_score, tech_score, apt_score, code_score, beh_score, applied_domain, gaps_str)

    with sqlite3.connect("interview.db", timeout=30.0, check_same_thread=False) as conn_db:
        conn_db.execute("PRAGMA journal_mode=WAL;")
        cursor = conn_db.cursor()
        cursor.execute("""
        INSERT OR REPLACE INTO final_results (
            user_id, skills, comm_score, tech_score, apt_score, code_score, 
            behavioral_score, recommendation, timestamp, total_rounds_completed, 
            progress_completed, applied_domain, alternative_domain, alternative_reason,
            growth_roadmap, email_sent
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
        """, (
            user_id, skills_str, comm_score, tech_score, apt_score, code_score, 
            beh_score, recom, ts, 4, 100.0, applied_domain, alternative_domain, alternative_reason,
            growth_roadmap_json
        ))
        conn_db.commit()

# =====================================================
# UPGRADED 4-ROUND STAGES & DURATIONS
# =====================================================
ROUNDS = [
    {
        "title": "ROUND 1 — INTRODUCTION ROUND",
        "desc": "This round evaluates your personal introduction, academic background, job fitment, and resume skills.",
        "duration": 1200  # 20 minutes
    },
    {
        "title": "ROUND 2 — ENGLISH & COMMUNICATION ROUND",
        "desc": "This round evaluates your core English literacy (MCQs) and verbal articulation (Voice Answers).",
        "duration": 900  # 15 minutes
    },
    {
        "title": "ROUND 3 — TECHNICAL MCQ ROUND",
        "desc": "This round tests your foundational Computer Science concepts in Database Management, Operating Systems, and Networks.",
        "duration": 900  # 15 minutes
    },
    {
        "title": "ROUND 4 — APTITUDE & CODING ROUND",
        "desc": "This round challenges your quantitative/logical reasoning (Aptitude) and real hands-on development skills (Coding editor).",
        "duration": 1200  # 20 minutes
    }
]

# =====================================================
# MAIN INTERVIEW MODULE
# =====================================================
def interview_module():
    inject_proctoring_security()
    skills = st.session_state.get("skills", [])
    user = st.session_state.get("username", "Candidate")
    domain = st.session_state.get("domain", "Software Engineering")

    if not skills:
        st.markdown(
            """
            <div style="background: rgba(239, 68, 68, 0.15); border: 1px solid rgba(239, 68, 68, 0.4); padding: 20px; border-radius: 12px; text-align: center;">
                <h3 style="color:#EF4444; margin:0;">📄 No Skills Detected</h3>
                <p style="color:#94A3B8; margin: 10px 0 0 0;">Please complete the resume upload and skill extraction process first.</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        return

    # 1. Initialize Multi-Round State
    if "current_round" not in st.session_state:
        st.session_state.current_round = 0
    if "round_q_idx" not in st.session_state:
        st.session_state.round_q_idx = 0
    if "section_questions" not in st.session_state or not isinstance(st.session_state.section_questions, dict):
        st.session_state.section_questions = {}
    if "section_start_time" not in st.session_state:
        st.session_state.section_start_time = None
    if "last_spoken_round_q" not in st.session_state:
        st.session_state.last_spoken_round_q = (-1, -1)

    round_idx = st.session_state.current_round

    if round_idx < 4 and round_idx not in st.session_state.section_questions:
        with st.spinner(f"Preparing assessment environment for {ROUNDS[round_idx]['title']}..."):
            # Derived seed from username
            seed = sum(ord(c) for c in user) + int(time.time()) % 10000

            if round_idx == 0:
                st.session_state.section_questions[0] = generate_r1_questions(user, skills, seed)
            elif round_idx == 1:
                st.session_state.section_questions[1] = generate_r2_questions(user, seed)
            elif round_idx == 2:
                st.session_state.section_questions[2] = generate_r3_questions(user, seed)
            elif round_idx == 3:
                st.session_state.section_questions[3] = generate_r4_questions(user, seed)

    # Render Feedback Page if they completed all 4 rounds
    if round_idx == 4:
        st.markdown(
            """
            <div style='text-align: center; margin-bottom: 25px;'>
                <h1 class='glowing-title' style='margin:0; font-size:32px;'>🎯 Candidate Experience Feedback</h1>
                <p style='color:#94A3B8; margin:5px 0 0 0;'>Please tell us about your overall interview and your experience during specific rounds</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        with st.container(border=True):
            st.markdown("<h3 style='color:#06B6D4; margin-top:0;'>✨ Rate Your Experience</h3>", unsafe_allow_html=True)
            
            # Star Ratings
            f_col1, f_col2 = st.columns(2)
            with f_col1:
                ov_rate = st.radio("Overall Interview Rating", ["⭐ 1", "⭐ 2", "⭐ 3", "⭐ 4", "⭐ 5"], horizontal=True, key="feedback_ov")
                r1_rate = st.radio("Round 1 (Introduction Round) Rating", ["⭐ 1", "⭐ 2", "⭐ 3", "⭐ 4", "⭐ 5"], horizontal=True, key="feedback_r1")
                r2_rate = st.radio("Round 2 (English & Comm) Rating", ["⭐ 1", "⭐ 2", "⭐ 3", "⭐ 4", "⭐ 5"], horizontal=True, key="feedback_r2")
            with f_col2:
                r3_rate = st.radio("Round 3 (Technical MCQ) Rating", ["⭐ 1", "⭐ 2", "⭐ 3", "⭐ 4", "⭐ 5"], horizontal=True, key="feedback_r3")
                r4_rate = st.radio("Round 4 (Aptitude & Coding) Rating", ["⭐ 1", "⭐ 2", "⭐ 3", "⭐ 4", "⭐ 5"], horizontal=True, key="feedback_r4")
                
            st.write("")
            st.markdown("<hr style='margin: 10px 0;'>", unsafe_allow_html=True)
            
            # Written Feedback
            ov_comment = st.text_area("What did you think of the overall platform experience?", placeholder="Share your thoughts...", height=90, key="feedback_ov_cmt")
            round_comment = st.text_area("Any specific feedback about the questions, difficulty, or structure of the rounds?", placeholder="Write your comments...", height=90, key="feedback_rd_cmt")
            
            st.write("")
            
            if st.button("🚀 SUBMIT FEEDBACK & SEAL ASSESSMENT", use_container_width=True, type="primary"):
                # Save to candidate_feedback table
                ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                user_id = resolve_user_id(user)
                with sqlite3.connect("interview.db", timeout=30.0, check_same_thread=False) as conn_db:
                    conn_db.execute("PRAGMA journal_mode=WAL;")
                    cursor = conn_db.cursor()
                    cursor.execute("""
                    INSERT OR REPLACE INTO candidate_feedback (user_id, overall_rating, overall_comments, r1_rating, r2_rating, r3_rating, r4_rating, round_comments, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        user_id,
                        int(ov_rate.split()[-1]),
                        ov_comment,
                        int(r1_rate.split()[-1]),
                        int(r2_rate.split()[-1]),
                        int(r3_rate.split()[-1]),
                        int(r4_rate.split()[-1]),
                        round_comment,
                        ts
                    ))
                    conn_db.commit()
                    
                # Calculate and write aggregate final metrics to SQLite
                with st.spinner("Analyzing performance logs and generating AI Recruiter fitment score..."):
                    calculate_and_save_final_results(user)
                    
                st.success("Feedback submitted successfully! Your responses have been sealed.")
                st.session_state.stage = "completed"
                st.rerun()
        return

    # Fully completed and sealed stage router
    if round_idx > 4:
        st.session_state.stage = "completed"
        st.rerun()

    # Get active round questions
    questions_list = st.session_state.section_questions[round_idx]
    curr_q_idx = st.session_state.round_q_idx

    # If active round is finished, advance
    if curr_q_idx >= len(questions_list):
        st.session_state.current_round += 1
        st.session_state.round_q_idx = 0
        st.session_state.section_start_time = None
        st.rerun()

    # Initialize section timer
    if st.session_state.section_start_time is None:
        st.session_state.section_start_time = time.time()

    # Calculate remaining seconds
    elapsed_time = time.time() - st.session_state.section_start_time
    remaining_seconds = max(0, ROUNDS[round_idx]["duration"] - elapsed_time)

    # 2. Python-side Auto-Submit Check (if time has expired)
    if remaining_seconds <= 0:
        with st.spinner("Time expired! Finalizing submissions..."):
            for i in range(st.session_state.round_q_idx, len(questions_list)):
                uq = questions_list[i]
                q_text = uq["question"]
                
                if round_idx == 0:
                    save_r1_spoken_answer(user, q_text, "[Time Expired - No Response]", "Skipped / Time Expired", 0, 0, uq.get("question_type", "HR"))
                elif round_idx == 1:
                    if uq["type"] == "mcq":
                        save_r2_mcq_answer(user, q_text, "None - Skipped", uq["answer"], 0)
                    else:
                        save_r2_spoken_answer(user, q_text, "[Time Expired - No Response]", "Skipped / Time Expired", 0, 0, 0, 0, 0, 0, "Time Expired")
                elif round_idx == 2:
                    save_r3_mcq_answer(user, i + 1, q_text, "None - Skipped", uq["answer"], 0, uq.get("subject", "OS"))
                elif round_idx == 3:
                    if uq["type"] == "mcq":
                        save_r4_mcq_answer(user, i + 1, q_text, "None - Skipped", uq["answer"], 0)
                    else:
                        save_r4_coding_answer(user, i + 1, q_text, "# Time Expired", uq.get("language", "Python"), "[Time Expired]", 0, 0)
                        
        st.session_state.current_round += 1
        st.session_state.round_q_idx = 0
        st.session_state.section_start_time = None
        st.rerun()

    # 3. Dynamic Real-time Floating Glassmorphic Timer Overlay
    st.markdown(
        f"""
        <div id="sticky-timer-bar" style="
            position: fixed;
            top: 15px;
            right: 20px;
            z-index: 10000;
            background: rgba(15, 23, 42, 0.7);
            backdrop-filter: blur(15px);
            border: 1px solid rgba(6, 182, 212, 0.35);
            padding: 8px 18px;
            border-radius: 12px;
            box-shadow: 0 8px 25px rgba(6, 182, 212, 0.15);
            display: flex;
            align-items: center;
            gap: 12px;
        ">
            <span style="font-size: 16px;">⏱️</span>
            <div>
                <div style="font-size: 9px; text-transform: uppercase; color: #94A3B8; font-weight: 700; letter-spacing: 0.5px;">Round Time Left</div>
                <div id="timer-display" style="font-size: 16px; font-weight: 800; color: #06B6D4; font-family: monospace;">15:00</div>
            </div>
        </div>

        <script>
        (function() {{
            var totalSeconds = Math.max(0, {int(remaining_seconds)});
            
            function updateTimer() {{
                if (totalSeconds <= 0) {{
                    clearInterval(timerInterval);
                    var display = document.getElementById("timer-display");
                    if (display) display.innerHTML = "00:00";
                    
                    var clicked = false;
                    try {{
                        var buttons = window.parent.document.querySelectorAll("button");
                        for (var btn of buttons) {{
                            if (btn.innerText && btn.innerText.includes("Submit Section (Time Expired)")) {{
                                btn.click();
                                clicked = true;
                                break;
                            }}
                        }}
                    }} catch (e) {{
                        console.log("Cross-origin parent DOM access blocked: " + e.message);
                    }}
                    
                    if (!clicked) {{
                        try {{
                            window.parent.location.href = window.parent.location.href;
                        }} catch (e) {{
                            window.location.reload();
                        }}
                    }}
                    return;
                }}
                
                var minutes = Math.floor(totalSeconds / 60);
                var seconds = totalSeconds % 60;
                
                var minStr = minutes < 10 ? "0" + minutes : minutes;
                var secStr = seconds < 10 ? "0" + seconds : seconds;
                
                var formatted = minStr + ":" + secStr;
                
                var display = document.getElementById("timer-display");
                if (display) display.innerHTML = formatted;
                
                totalSeconds--;
            }}
            
            if (window.timerInterval) {{
                clearInterval(window.timerInterval);
            }}
            window.timerInterval = setInterval(updateTimer, 1000);
            updateTimer();
        }})();
        </script>
        """,
        unsafe_allow_html=True
    )

    # 4. Hidden Auto-Submit Button for JS timeout trigger
    st.markdown('<div style="display:none;">', unsafe_allow_html=True)
    if st.button("Submit Section (Time Expired)", key="hidden_time_expired_btn"):
        # Handle time expiration: insert remaining questions as blank and transition
        with st.spinner("Time expired! Finalizing submissions..."):
            for i in range(st.session_state.round_q_idx, len(questions_list)):
                uq = questions_list[i]
                q_text = uq["question"]
                
                if round_idx == 0:
                    save_r1_spoken_answer(user, q_text, "[Time Expired - No Response]", "Skipped / Time Expired", 0, 0, uq.get("question_type", "HR"))
                elif round_idx == 1:
                    if uq["type"] == "mcq":
                        save_r2_mcq_answer(user, q_text, "None - Skipped", uq["answer"], 0)
                    else:
                        save_r2_spoken_answer(user, q_text, "[Time Expired - No Response]", "Skipped / Time Expired", 0, 0, 0, 0, 0, 0, "Time Expired")
                elif round_idx == 2:
                    save_r3_mcq_answer(user, i + 1, q_text, "None - Skipped", uq["answer"], 0, uq.get("subject", "OS"))
                elif round_idx == 3:
                    if uq["type"] == "mcq":
                        save_r4_mcq_answer(user, i + 1, q_text, "None - Skipped", uq["answer"], 0)
                    else:
                        save_r4_coding_answer(user, i + 1, q_text, "# Time Expired", uq.get("language", "Python"), "[Time Expired]", 0, 0)
                        
        st.session_state.current_round += 1
        st.session_state.round_q_idx = 0
        st.session_state.section_start_time = None
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # 5. UI Layout Header
    st.markdown(
        f"""
        <div style="background: rgba(30, 41, 59, 0.4); border: 1px solid rgba(255,255,255,0.06); padding: 22px 30px; border-radius: 18px; margin-bottom: 25px; box-shadow: 0 10px 30px rgba(0,0,0,0.15);">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="font-size: 11px; padding: 4px 12px; background: rgba(6, 182, 212, 0.15); border-radius: 20px; color: #06B6D4; font-weight: bold; border: 1px solid rgba(6,182,212,0.3); text-transform: uppercase;">
                    ROUND {round_idx + 1} OF 4
                </span>
                <span style="font-size:12px; color:#64748B; font-weight:600;">{ROUNDS[round_idx]['duration'] // 60} MINUTE LIMIT</span>
            </div>
            <h2 style="color: #ffffff; margin: 10px 0 5px 0; font-weight: 700; font-size:24px;">{ROUNDS[round_idx]['title']}</h2>
            <p style="color: #94A3B8; margin: 0; font-size: 14px; line-height:1.4;">{ROUNDS[round_idx]['desc']}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Clear polite message on core question change
    if round_idx == 0:
        if "r1_in_followup" not in st.session_state:
            st.session_state.r1_in_followup = False
            st.session_state.r1_followup_question = ""
            st.session_state.r1_followup_hop = 0
            st.session_state.r1_followup_parent_q = ""
            st.session_state.r1_polite_gap_msg = None
            st.session_state.r1_last_cleared_q_idx = -1
        
        if st.session_state.r1_last_cleared_q_idx != curr_q_idx:
            st.session_state.r1_polite_gap_msg = None
            st.session_state.r1_last_cleared_q_idx = curr_q_idx

    # Local Round Progress Indicator
    q_obj = questions_list[curr_q_idx]
    q = q_obj["question"]
    q_type = q_obj.get("type", "spoken")
    q_badge = q_obj.get("badge", "Core Assessment")

    if round_idx == 0 and st.session_state.get("r1_in_followup"):
        q = st.session_state.r1_followup_question
        q_badge = f"AI Stress Test — Probe {st.session_state.r1_followup_hop}/2"

    col_lbl, col_pct = st.columns([3, 5])
    with col_lbl:
        st.markdown(f"<h3 style='margin:0; font-size:18px; color:#06B6D4;'>Question {curr_q_idx + 1} of {len(questions_list)}</h3>", unsafe_allow_html=True)
    with col_pct:
        st.progress((curr_q_idx + 1) / len(questions_list))

    st.write("")

    # Question Display Card
    with st.container(border=True):
        st.markdown(
            f"""
            <div style="margin-bottom: 8px;">
                <span style="font-size: 10px; padding: 2px 8px; background: rgba(99, 102, 241, 0.15); border-radius: 20px; color: #818cf8; font-weight: bold; border: 1px solid rgba(99,102,241,0.2); text-transform: uppercase;">
                    {q_badge}
                </span>
            </div>
            <h3 style="color: #F8FAFC; line-height: 1.5; margin: 8px 0 0 0; font-weight: 500; font-size:18px;">{q}</h3>
            """,
            unsafe_allow_html=True
        )
        if q_type == "coding" and "problem" in q_obj:
            st.markdown(
                f"""
                <div style="background: rgba(15, 23, 42, 0.5); border: 1px solid rgba(255,255,255,0.06); padding: 18px; border-radius: 10px; margin-top: 15px; font-family: 'Courier New', monospace; font-size:13px; color:#CBD5E1; line-height:1.5; white-space: pre-wrap;">
                    {q_obj['problem']}
                </div>
                """,
                unsafe_allow_html=True
            )

    st.write("")

    # Speak spoken questions
    curr_speak_key = (round_idx, curr_q_idx)
    if round_idx == 0 and st.session_state.get("r1_in_followup"):
        curr_speak_key = (round_idx, curr_q_idx, st.session_state.r1_followup_hop)

    if st.session_state.last_spoken_round_q != curr_speak_key and q_type == "spoken":
        speak(q)
        st.session_state.last_spoken_round_q = curr_speak_key

    # 7. Action Console UI
    if q_type == "spoken":
        if round_idx == 0 and st.session_state.get("r1_polite_gap_msg"):
            st.markdown(
                f"""
                <div style="
                    background: rgba(245, 158, 11, 0.15);
                    backdrop-filter: blur(10px);
                    border: 1px solid rgba(245, 158, 11, 0.35);
                    padding: 15px 20px;
                    border-radius: 12px;
                    margin-bottom: 20px;
                    box-shadow: 0 4px 20px rgba(245, 158, 11, 0.15);
                    display: flex;
                    align-items: center;
                    gap: 12px;
                ">
                    <span style="font-size: 20px;">💡</span>
                    <div>
                        <div style="font-size: 11px; text-transform: uppercase; color: #F59E0B; font-weight: 700; letter-spacing: 0.5px;">AI Performance Insight</div>
                        <div style="font-size: 13px; color: #FFE4E6; font-weight: 500; margin-top: 2px;">{st.session_state.r1_polite_gap_msg}</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with st.container(border=True):
            st.markdown(
                """
                <div style="text-align: center; margin-bottom: 15px;">
                    <h4 style="color:#94A3B8; margin:0; font-size:15px; font-weight:600;">🎙 Voice Response Cockpit</h4>
                    <p style="color:#64748B; font-size:12px; margin:4px 0 0 0;">Click the microphone below to start speaking. Click it again to finalize your audio.</p>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            rec_col1, rec_col2, rec_col3 = st.columns([3, 2, 3])
            with rec_col2:
                st.markdown("""
                <style>
                @keyframes pulseGlow {
                    0% { box-shadow: 0 0 0 0 rgba(6, 182, 212, 0.3); border-color: rgba(6, 182, 212, 0.3); }
                    50% { box-shadow: 0 0 20px 8px rgba(6, 182, 212, 0.15); border-color: rgba(99, 102, 241, 0.5); }
                    100% { box-shadow: 0 0 0 0 rgba(6, 182, 212, 0.3); border-color: rgba(6, 182, 212, 0.3); }
                }
                .mic-cockpit-wrapper {
                    background: rgba(15, 23, 42, 0.55) !important;
                    border: 2px solid rgba(6, 182, 212, 0.3) !important;
                    border-radius: 50% !important;
                    width: 90px !important;
                    height: 90px !important;
                    margin: 10px auto !important;
                    display: flex !important;
                    justify-content: center !important;
                    align-items: center !important;
                    animation: pulseGlow 2.5s infinite ease-in-out !important;
                    transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1) !important;
                }
                .mic-cockpit-wrapper:hover {
                    transform: scale(1.08) !important;
                    border-color: rgba(6, 182, 212, 0.8) !important;
                }
                </style>
                <div class="mic-cockpit-wrapper">
                """, unsafe_allow_html=True)
                
                rec_key = f"audio_rec_{round_idx}_{curr_q_idx}"
                if round_idx == 0 and st.session_state.get("r1_in_followup"):
                    rec_key += f"_hop{st.session_state.r1_followup_hop}"

                audio_bytes = audio_recorder(
                    pause_threshold=12.0,
                    sample_rate=41000,
                    recording_color="#EF4444",
                    neutral_color="#06B6D4",
                    icon_name="microphone",
                    icon_size="3x",
                    key=rec_key
                )
                st.markdown("</div>", unsafe_allow_html=True)

            if audio_bytes:
                st.audio(audio_bytes, format="audio/wav")
                st.markdown("<div style='text-align:center;'><span style='color:#10B981; font-weight:600; font-size:13px;'>✓ Response recorded successfully. Playback ready.</span></div>", unsafe_allow_html=True)

        st.write("")

        sub_key = f"submit_ans_{round_idx}_{curr_q_idx}"
        if round_idx == 0 and st.session_state.get("r1_in_followup"):
            sub_key += f"_hop{st.session_state.r1_followup_hop}"

        if st.button("Submit Answer ✓", use_container_width=True, key=sub_key):
            if not audio_bytes:
                st.error("🎤 Audio response required. Please record before submitting.")
                return

            with st.spinner("Processing speech, transcribing audio, and scoring response via AI..."):
                file_path = f"audio_files/{user}_r{round_idx}_q{curr_q_idx}.wav"
                if round_idx == 0 and st.session_state.get("r1_in_followup"):
                    file_path = f"audio_files/{user}_r{round_idx}_q{curr_q_idx}_hop{st.session_state.r1_followup_hop}.wav"

                with open(file_path, "wb") as f:
                    f.write(audio_bytes)

                transcript = speech_to_text(file_path)
                
                # Grading based on round
                if round_idx == 0:
                    if st.session_state.get("r1_in_followup"):
                        evals = evaluate_r1_followup_answer(
                            parent_q=st.session_state.r1_followup_parent_q,
                            followup_q=st.session_state.r1_followup_question,
                            transcript=transcript,
                            skills=skills
                        )
                        score = evals.get("score", 3.0)
                        conf = evals.get("confidence", 6.5)
                        gap = evals.get("knowledge_gap_noted")
                        
                        save_r1_spoken_answer(
                            user=user,
                            q_text=st.session_state.r1_followup_question,
                            transcript=transcript,
                            audio_path=file_path,
                            score=score,
                            confidence=conf,
                            q_type="Technical",
                            is_follow_up=1,
                            parent_question=st.session_state.r1_followup_parent_q,
                            knowledge_gap_noted=gap
                        )
                        st.success("Follow-up response recorded and graded!")
                        
                        if gap:
                            st.session_state.r1_polite_gap_msg = evals.get("polite_gap_msg")
                            st.session_state.r1_in_followup = False
                            st.session_state.round_q_idx += 1
                        else:
                            if st.session_state.r1_followup_hop == 1:
                                has_probe, probe_q = generate_stress_test_followup(
                                    question=st.session_state.r1_followup_question,
                                    answer=transcript,
                                    skills=skills
                                )
                                if has_probe and probe_q:
                                    st.session_state.r1_followup_question = probe_q
                                    st.session_state.r1_followup_hop = 2
                                else:
                                    st.session_state.r1_in_followup = False
                                    st.session_state.round_q_idx += 1
                            else:
                                st.session_state.r1_in_followup = False
                                st.session_state.round_q_idx += 1
                        st.rerun()
                    else:
                        score, conf = evaluate_r1_spoken_answer(q, transcript, q_obj.get("question_type", "HR"))
                        save_r1_spoken_answer(user, q, transcript, file_path, score, conf, q_obj.get("question_type", "HR"))
                        st.success("Spoken response recorded and graded!")
                        
                        # Check for technical claim and trigger stress-test
                        if q_obj.get("question_type", "HR") == "Technical":
                            has_probe, probe_q = generate_stress_test_followup(q, transcript, skills)
                            if has_probe and probe_q:
                                st.session_state.r1_in_followup = True
                                st.session_state.r1_followup_question = probe_q
                                st.session_state.r1_followup_hop = 1
                                st.session_state.r1_followup_parent_q = q
                                st.rerun()
                                
                        st.session_state.round_q_idx += 1
                        st.rerun()
                elif round_idx == 1:
                    evals = evaluate_r2_spoken_eval(q, transcript)
                    save_r2_spoken_answer(
                        user, q, transcript, file_path,
                        evals.get("score", 3.0),
                        evals.get("fluency", 3.0),
                        evals.get("pronunciation", 3.0),
                        evals.get("confidence", 3.0),
                        evals.get("comm_quality", 3.0),
                        evals.get("speaking_consistency", 3.0),
                        evals.get("remarks", "Clear articulation.")
                    )

                st.success("Spoken response recorded and graded!")
                st.session_state.round_q_idx += 1
                st.rerun()

    elif q_type == "mcq":
        options = q_obj.get("options", [])
        correct_answer = q_obj.get("answer", "")

        with st.container(border=True):
            st.markdown(
                """
                <div style="margin-bottom: 15px;">
                    <h4 style="color:#94A3B8; margin:0; font-size:15px; font-weight:600;">✍️ Multiple Choice Question</h4>
                    <p style="color:#64748B; font-size:12px; margin:4px 0 0 0;">Review options and select the correct response.</p>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            st.markdown("""
            <style>
            div[data-testid="stRadio"] > label { color: #F8FAFC !important; font-weight: 500 !important; }
            div[data-testid="stRadio"] div[role="radiogroup"] { gap: 12px !important; }
            div[data-testid="stRadio"] div[role="radiogroup"] > label {
                background: rgba(30, 41, 59, 0.4) !important;
                border: 1px solid rgba(255, 255, 255, 0.08) !important;
                padding: 12px 18px !important;
                border-radius: 12px !important;
                cursor: pointer !important;
                transition: all 0.3s ease !important;
                display: flex !important;
                align-items: center !important;
                width: 100% !important;
            }
            div[data-testid="stRadio"] div[role="radiogroup"] > label:hover {
                background: rgba(6, 182, 212, 0.08) !important;
                border-color: rgba(6, 182, 212, 0.3) !important;
                transform: translateY(-1px) !important;
            }
            </style>
            """, unsafe_allow_html=True)

            selected_option = st.radio(
                "Options",
                options,
                index=None,
                label_visibility="collapsed",
                key=f"mcq_radio_{round_idx}_{curr_q_idx}"
            )

        st.write("")

        if st.button("Submit Choice ✓", use_container_width=True, key=f"submit_mcq_{round_idx}_{curr_q_idx}"):
            if selected_option is None:
                st.error("✍️ Please select an option before submitting.")
                return

            is_correct = (selected_option == correct_answer)
            score = 6 if is_correct else 1
            
            if round_idx == 1:
                save_r2_mcq_answer(user, q, selected_option, correct_answer, score)
            elif round_idx == 2:
                save_r3_mcq_answer(user, curr_q_idx + 1, q, selected_option, correct_answer, score, q_obj.get("subject", "OS"))
            elif round_idx == 3:
                save_r4_mcq_answer(user, curr_q_idx + 1, q, selected_option, correct_answer, score)

            st.success("MCQ Response recorded!")
            st.session_state.round_q_idx += 1
            st.rerun()

    elif q_type == "coding":
        # Pre-populate code editor with buggy code if not already in session state
        editor_key = f"code_editor_{round_idx}_{curr_q_idx}"
        if editor_key not in st.session_state:
            st.session_state[editor_key] = q_obj.get("buggy_code", "")

        with st.container(border=True):
            col_lang, col_tit = st.columns([2, 5])
            with col_lang:
                # Pre-fill language dropdown and disable it to preserve debugging coherence
                avail_langs = ["Python", "Java", "C++", "JavaScript"]
                default_lang = q_obj.get("language", "Python")
                default_lang_idx = avail_langs.index(default_lang) if default_lang in avail_langs else 0
                lang = st.selectbox(
                    "Programming Language", 
                    avail_langs, 
                    index=default_lang_idx, 
                    disabled=True, 
                    key=f"coding_lang_{round_idx}_{curr_q_idx}"
                )
            with col_tit:
                st.markdown(f"<div style='margin-top:25px;'><span style='color:#64748B;'>Language locked: debug the code snippet in {lang}</span></div>", unsafe_allow_html=True)
                
            st.write("")
            st.markdown(
                """
                <div style="margin-bottom: 12px;">
                    <h4 style="color:#94A3B8; margin:0; font-size:15px; font-weight:600;">💻 Code Editor Workspace</h4>
                </div>
                """,
                unsafe_allow_html=True
            )

            st.markdown("""
            <style>
            textarea[aria-label="💻 CODE EDITOR WORKSPACE"] {
                font-family: 'Consolas', 'Courier New', monospace !important;
                background-color: #090d16 !important;
                color: #A5F3FC !important;
                border: 1px solid rgba(6,182,212,0.25) !important;
                border-radius: 10px !important;
                padding: 15px !important;
                line-height: 1.5 !important;
            }
            </style>
            """, unsafe_allow_html=True)

            code_input = st.text_area(
                "💻 CODE EDITOR WORKSPACE",
                height=300,
                label_visibility="collapsed",
                key=editor_key
            )
            
            # Persistent Sandbox Output Console
            sandbox_out_key = f"sandbox_out_{round_idx}_{curr_q_idx}"
            if sandbox_out_key not in st.session_state:
                st.session_state[sandbox_out_key] = ""
                
            run_btn = st.button("⚙ Run Code & Test Output", key=f"run_code_{round_idx}_{curr_q_idx}")
            if run_btn:
                with st.spinner("Executing syntax and compiler checks..."):
                    output_res = run_code_sandbox(q_obj.get("problem", ""), code_input, lang)
                    st.session_state[sandbox_out_key] = output_res
                    
            if st.session_state[sandbox_out_key]:
                st.markdown("<h5 style='color:#06B6D4; margin: 15px 0 5px 0;'>🖥️ Compiler Sandbox Output</h5>", unsafe_allow_html=True)
                st.code(st.session_state[sandbox_out_key], language="bash")

        st.write("")

        if st.button("Submit Code Solution ✓", use_container_width=True, key=f"submit_code_{round_idx}_{curr_q_idx}"):
            if not code_input or code_input.strip() == q_obj.get("buggy_code", ""):
                st.error("💻 Please attempt to fix the bug in the code editor before submitting.")
                return

            with st.spinner("AI Engine running static analysis and grading your code solution..."):
                score, feedback = evaluate_coding_solution(
                    problem=q_obj.get("problem", q),
                    code=code_input,
                    correct_code=q_obj.get("correct_code", ""),
                    language=lang
                )
                output_log = st.session_state.get(sandbox_out_key, "")
                if not output_log:
                    output_log = "Status: Code Submitted | Feedback: " + feedback
                else:
                    output_log = f"Console Run Log:\n{output_log}\n\nFeedback:\n{feedback}"
                
                save_r4_coding_answer(user, curr_q_idx + 1, q, code_input, lang, output_log, score, int(elapsed_time))

                st.success("Coding Challenge successfully compiled and recorded! ✅")
                st.session_state.round_q_idx += 1
                st.rerun()

    # Skip Section / Early Submission Action Card
    st.write("")
    st.markdown("<hr style='margin:15px 0 !important; opacity:0.05;'>", unsafe_allow_html=True)
    with st.container():
        ec1, ec2 = st.columns([5, 2])
        with ec1:
            st.markdown(
                """
                <p style="color:#64748B; font-size:12px; margin:8px 0 0 0;">
                    Finished answering this round early? You can finalize this section and advance. 
                    <b>Note:</b> Unanswered questions in this round will receive 0 marks.
                </p>
                """,
                unsafe_allow_html=True
            )
        with ec2:
            if st.button("➡️ Finalize Round Early", key=f"skip_round_{round_idx}", use_container_width=True):
                # Write skipped entries
                with st.spinner("Skipping remainder of questions and moving to next round..."):
                    for i in range(st.session_state.round_q_idx, len(questions_list)):
                        uq = questions_list[i]
                        q_text = uq["question"]
                        
                        if round_idx == 0:
                            save_r1_spoken_answer(user, q_text, "[Skipped by Candidate]", "Skipped / Early Submission", 0, 0, uq.get("question_type", "HR"))
                        elif round_idx == 1:
                            if uq["type"] == "mcq":
                                save_r2_mcq_answer(user, q_text, "Skipped", uq["answer"], 0)
                            else:
                                save_r2_spoken_answer(user, q_text, "[Skipped by Candidate]", "Skipped / Early Submission", 0, 0, 0, 0, 0, 0, "Skipped")
                        elif round_idx == 2:
                            save_r3_mcq_answer(user, i + 1, q_text, "Skipped", uq["answer"], 0, uq.get("subject", "OS"))
                        elif round_idx == 3:
                            if uq["type"] == "mcq":
                                save_r4_mcq_answer(user, i + 1, q_text, "Skipped", uq["answer"], 0)
                            else:
                                save_r4_coding_answer(user, i + 1, q_text, "# Skipped", uq.get("language", "Python"), "[Skipped]", 0, 0)
                                
                st.session_state.current_round += 1
                st.session_state.round_q_idx = 0
                st.session_state.section_start_time = None
                st.rerun()