import re

# =====================================================
# TECHNICAL SKILL DICTIONARY (Lowercase -> Beautiful Display Name)
# =====================================================
skill_map = {
    # Programming Languages
    "python": "Python",
    "java": "Java",
    "c": "C",
    "c++": "C++",
    "c#": "C#",
    "rust": "Rust",
    "go": "Go",
    "golang": "Go",
    "ruby": "Ruby",
    "php": "PHP",
    "swift": "Swift",
    "kotlin": "Kotlin",
    "typescript": "TypeScript",
    "javascript": "JavaScript",
    "js": "JavaScript",
    "ts": "TypeScript",
    "scala": "Scala",
    "dart": "Dart",
    "clojure": "Clojure",
    "haskell": "Haskell",
    "lua": "Lua",
    "perl": "Perl",
    "julia": "Julia",
    "r": "R",
    "shell": "Shell Scripting",
    "bash": "Bash",
    "powershell": "PowerShell",

    # Frontend Frameworks & UI
    "react": "React",
    "react.js": "React",
    "reactjs": "React",
    "vue": "Vue.js",
    "vue.js": "Vue.js",
    "vuejs": "Vue.js",
    "angular": "Angular",
    "angularjs": "Angular",
    "next.js": "Next.js",
    "nextjs": "Next.js",
    "nuxt": "Nuxt.js",
    "svelte": "Svelte",
    "jquery": "jQuery",
    "bootstrap": "Bootstrap",
    "tailwind": "Tailwind CSS",
    "tailwindcss": "Tailwind CSS",
    "sass": "Sass",
    "scss": "Sass",
    "html": "HTML5",
    "css": "CSS3",
    "html5": "HTML5",
    "css3": "CSS3",

    # Backend & Web Frameworks
    "django": "Django",
    "fastapi": "FastAPI",
    "flask": "Flask",
    "spring boot": "Spring Boot",
    "springboot": "Spring Boot",
    "express": "Express.js",
    "express.js": "Express.js",
    "expressjs": "Express.js",
    "nest.js": "Nest.js",
    "nestjs": "Nest.js",
    "laravel": "Laravel",
    "ruby on rails": "Ruby on Rails",
    "rails": "Ruby on Rails",
    "asp.net": "ASP.NET",
    "dotnet": ".NET",
    ".net": ".NET",
    "nodejs": "Node.js",
    "node.js": "Node.js",
    "gin": "Gin",

    # Databases & Caching
    "mysql": "MySQL",
    "postgresql": "PostgreSQL",
    "postgres": "PostgreSQL",
    "mongodb": "MongoDB",
    "redis": "Redis",
    "sqlite": "SQLite",
    "oracle": "Oracle DB",
    "mariadb": "MariaDB",
    "cassandra": "Cassandra",
    "dynamodb": "DynamoDB",
    "firebase": "Firebase",
    "firestore": "Firestore",
    "elasticsearch": "Elasticsearch",

    # Cloud, DevOps & Systems
    "aws": "AWS",
    "azure": "Azure",
    "gcp": "GCP",
    "google cloud": "GCP",
    "docker": "Docker",
    "kubernetes": "Kubernetes",
    "k8s": "Kubernetes",
    "jenkins": "Jenkins",
    "git": "Git",
    "github": "GitHub",
    "gitlab": "GitLab",
    "ansible": "Ansible",
    "terraform": "Terraform",
    "ci/cd": "CI/CD",
    "cicd": "CI/CD",
    "linux": "Linux",
    "nginx": "Nginx",
    "apache": "Apache",

    # AI, Machine Learning & Data Science
    "machine learning": "Machine Learning",
    "deep learning": "Deep Learning",
    "data science": "Data Science",
    "natural language processing": "NLP",
    "nlp": "NLP",
    "computer vision": "Computer Vision",
    "opencv": "OpenCV",
    "pandas": "Pandas",
    "numpy": "NumPy",
    "tensorflow": "TensorFlow",
    "pytorch": "PyTorch",
    "keras": "Keras",
    "scikit-learn": "Scikit-Learn",
    "sklearn": "Scikit-Learn",
    "tableau": "Tableau",
    "power bi": "Power BI",
    "powerbi": "Power BI",
    "hadoop": "Hadoop",
    "spark": "Apache Spark",
    "llm": "LLMs",
    "langchain": "LangChain",
    "hugging face": "Hugging Face",

    # Architectural Concepts & Methodologies
    "system design": "System Design",
    "data structures": "Data Structures & Algorithms",
    "algorithms": "Data Structures & Algorithms",
    "rest api": "REST APIs",
    "restful api": "REST APIs",
    "graphql": "GraphQL",
    "grpc": "gRPC",
    "microservices": "Microservices",
    "agile": "Agile",
    "scrum": "Scrum",
    "devops": "DevOps",
    "cyber security": "Cybersecurity",
    "cryptography": "Cryptography"
}

# =====================================================
# ADVANCED SKILL EXTRACTION ENGINE
# =====================================================
def extract_skills(text):
    """
    Parses clean text to extract all standard skills.
    Uses negative lookbehinds and lookaheads to handle symbols
    like C++, C#, and .NET correctly and avoid partial substring matches.
    """
    text = text.lower()
    found_display = []

    # Sort keywords by length descending to match longer multi-word phrases first
    sorted_keywords = sorted(skill_map.keys(), key=len, reverse=True)

    for keyword in sorted_keywords:
        # Create lookahead and lookbehind regex to isolate the keyword from surrounding letters/symbols
        # [a-zA-Z0-9_#+] represents standard alphanumeric, plus C++ and C# characters
        pattern = r'(?<![a-zA-Z0-9_#+])' + re.escape(keyword) + r'(?![a-zA-Z0-9_#+])'
        
        if re.search(pattern, text):
            display_name = skill_map[keyword]
            if display_name not in found_display:
                found_display.append(display_name)

    return found_display

# =====================================================
# DOMAIN SKILLS MAPPING FOR 26 TARGET DOMAINS
# =====================================================
domain_skills_map = {
    "Artificial Intelligence": ["Python", "NLP", "Computer Vision", "LLMs", "LangChain", "Hugging Face", "TensorFlow", "PyTorch", "Keras", "Machine Learning", "Deep Learning"],
    "Machine Learning": ["Python", "R", "Julia", "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch", "Keras", "Scikit-Learn", "NumPy", "Pandas"],
    "Data Science": ["Python", "R", "Data Science", "Pandas", "NumPy", "Tableau", "Power BI", "MySQL", "PostgreSQL", "Hadoop", "Apache Spark"],
    "Web Development": ["HTML5", "CSS3", "JavaScript", "TypeScript", "React", "Vue.js", "Angular", "Next.js", "Node.js", "Express.js", "Django", "Flask", "Tailwind CSS", "Bootstrap", "REST APIs", "GraphQL"],
    "Cyber Security": ["Cybersecurity", "Cryptography", "Linux", "Shell Scripting", "Bash", "Networking"],
    "Cloud Computing": ["AWS", "Azure", "GCP", "Docker", "Kubernetes", "Terraform", "Nginx", "Linux"],
    "Software Engineering": ["Python", "Java", "C++", "C#", "Go", "Rust", "Data Structures & Algorithms", "System Design", "Git", "GitHub", "Agile", "Scrum"],
    "Mobile App Development": ["Swift", "Kotlin", "Dart", "JavaScript", "React", "TypeScript"],
    "Blockchain": ["Cryptography", "Go", "Rust", "C++", "JavaScript", "TypeScript", "System Design"],
    "DevOps": ["Docker", "Kubernetes", "Jenkins", "Ansible", "Terraform", "CI/CD", "Git", "GitHub", "GitLab", "Linux", "Shell Scripting", "Bash", "Nginx"],
    "Game Development": ["C++", "C#", "Rust", "Data Structures & Algorithms", "Computer Vision"],
    "UI/UX Design": ["HTML5", "CSS3", "Sass", "Bootstrap", "Tailwind CSS"],
    "Database Management": ["MySQL", "PostgreSQL", "MongoDB", "Redis", "SQLite", "Oracle DB", "MariaDB", "Cassandra", "DynamoDB", "Firebase", "Firestore", "Elasticsearch"],
    "Networking": ["Networking", "Linux", "Shell Scripting", "Bash", "PowerShell"],
    "Embedded Systems": ["C", "C++", "Rust", "Linux"],
    "Big Data": ["Hadoop", "Apache Spark", "Scala", "Python", "Cassandra", "Elasticsearch"],
    "Robotics": ["Python", "C++", "Computer Vision", "OpenCV"],
    "IoT": ["C", "C++", "Python", "Networking", "Linux", "Bash"],
    "AR/VR": ["C++", "C#", "Computer Vision", "OpenCV"],
    "Digital Marketing": ["Digital Marketing"],
    "Business Analytics": ["Tableau", "Power BI", "Python", "R", "Pandas", "NumPy"],
    "Full Stack Development": ["HTML5", "CSS3", "JavaScript", "TypeScript", "React", "Vue.js", "Angular", "Next.js", "Node.js", "Express.js", "Django", "FastAPI", "Flask", "MySQL", "PostgreSQL", "MongoDB", "REST APIs", "GraphQL"],
    "Backend Development": ["Python", "Java", "C++", "C#", "Go", "Rust", "Node.js", "Express.js", "Django", "FastAPI", "Flask", "Spring Boot", "Nest.js", "Laravel", "Ruby on Rails", "ASP.NET", ".NET", "MySQL", "PostgreSQL", "MongoDB", "Redis", "REST APIs", "GraphQL", "gRPC", "Microservices", "System Design"],
    "Frontend Development": ["HTML5", "CSS3", "JavaScript", "TypeScript", "React", "Vue.js", "Angular", "Next.js", "Svelte", "jQuery", "Bootstrap", "Tailwind CSS", "Sass", "REST APIs", "GraphQL"],
    "Testing & QA": ["Python", "Java", "JavaScript", "TypeScript", "Git", "GitHub", "Agile", "Scrum"],
    "System Design": ["System Design", "Microservices", "REST APIs", "GraphQL", "gRPC", "Data Structures & Algorithms", "Docker", "Kubernetes", "AWS", "Azure", "GCP", "Redis"]
}

# =====================================================
# AI CAREER PATH MATCHING ENGINE
# =====================================================
def match_career_path(skills, applied_domain):
    """
    Compares candidate skills against all 26 domains to see if they fit another track better.
    Returns (alternative_domain, rationale) or (None, None).
    """
    if not skills:
        return None, None

    # Calculate intersection counts for each domain
    scores = {}
    for d, d_skills in domain_skills_map.items():
        matched = set(s.lower() for s in skills) & set(ds.lower() for ds in d_skills)
        scores[d] = len(matched)

    applied_score = scores.get(applied_domain, 0)
    
    best_alt_domain = None
    best_alt_score = 0
    
    # Sort all domains by score descending
    sorted_domains = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    
    for d, score in sorted_domains:
        if d == applied_domain:
            continue
        if score > best_alt_score:
            best_alt_score = score
            best_alt_domain = d

    # We suggest an alternative domain if it is strictly a better fit and has at least 2 matching skills
    if best_alt_domain and best_alt_score > applied_score and best_alt_score >= 2:
        matched_skills = list(set(skills) & set(domain_skills_map[best_alt_domain]))
        matched_str = ", ".join(matched_skills)
        applied_matched = list(set(skills) & set(domain_skills_map.get(applied_domain, [])))
        applied_matched_str = ", ".join(applied_matched) if applied_matched else "none"

        reason = None
        try:
            import os
            from dotenv import load_dotenv
            load_dotenv()
        except Exception:
            pass

        try:
            import google.generativeai as genai
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                try:
                    import streamlit as st
                    api_key = st.secrets.get("GEMINI_API_KEY")
                except Exception:
                    pass
            if api_key:
                genai.configure(api_key=api_key)
                gemini_model = genai.GenerativeModel(model_name="models/gemini-2.5-flash")
            else:
                gemini_model = None
            
            prompt = f"""
            You are an expert AI Career Matcher and Talent Acquisition specialist.
            A candidate has applied for the domain '{applied_domain}' but their resume shows exceptionally strong skills in '{best_alt_domain}'.
            
            Candidate's detected skills: {', '.join(skills)}
            Skills matching '{best_alt_domain}': {matched_str}
            Skills matching '{applied_domain}': {applied_matched_str}
            
            Write a professional, highly encouraging, and brief (2-3 sentences) career matching verdict and recommendation. 
            Explain clearly why their skills are a better and more premium fit for the '{best_alt_domain}' track compared to the '{applied_domain}' track.
            Mention the key matching skills like {matched_skills[0] if len(matched_skills) > 0 else 'their experience'}.
            Do not include any greeting, markdown formatting (no bold **, no bullet points), or extra text. Return ONLY the 2-3 sentence recommendation paragraph.
            """
            
            response = gemini_model.generate_content(prompt)
            if response and response.text:
                reason = response.text.strip()
        except Exception:
            pass
            
        if not reason:
            reason = (
                f"While you applied for {applied_domain}, your profile displays excellent synergy with our {best_alt_domain} track. "
                f"Your hands-on command of {matched_str} provides a powerful foundation for the advanced challenges in this sector. "
                f"We strongly recommend aligning with this track to maximize your professional impact and performance."
            )
            
        return best_alt_domain, reason

    return None, None