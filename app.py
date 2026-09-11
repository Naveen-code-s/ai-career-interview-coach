import streamlit as st
from pypdf import PdfReader
from google import genai
import sqlite3
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import re


# ---------------- DATABASE ----------------

def create_database():
    connection = sqlite3.connect("career_coach.db")
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS interview_attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_role TEXT,
            question TEXT,
            score REAL,
            attempted_at TEXT
        )
    """)

    connection.commit()
    connection.close()


def save_interview_attempt(job_role, question, score):
    connection = sqlite3.connect("career_coach.db")
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO interview_attempts (job_role, question, score, attempted_at)
        VALUES (?, ?, ?, ?)
    """, (
        job_role,
        question,
        score,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    connection.commit()
    connection.close()


def get_interview_attempts():
    connection = sqlite3.connect("career_coach.db")

    dataframe = pd.read_sql_query(
        "SELECT * FROM interview_attempts ORDER BY id DESC",
        connection
    )

    connection.close()
    return dataframe


# ---------------- RESUME FUNCTIONS ----------------

def extract_skills(resume_text):
    skill_list = [
        "python", "java", "c++", "sql", "html", "css", "javascript",
        "react", "node.js", "django", "flask", "pandas", "numpy",
        "matplotlib", "machine learning", "deep learning",
        "tensorflow", "pytorch", "streamlit", "git", "github",
        "excel", "power bi", "mysql", "sqlite", "aws", "api"
    ]

    resume_text = resume_text.lower()
    found_skills = []

    for skill in skill_list:
        if skill in resume_text:
            found_skills.append(skill.title())

    return found_skills


def get_required_skills(job_role):
    role_skills = {
        "Python Developer": [
            "Python", "SQL", "Git", "GitHub", "API",
            "Flask", "Django", "SQLite"
        ],
        "AI/ML Developer": [
            "Python", "Pandas", "NumPy", "Machine Learning",
            "Deep Learning", "TensorFlow", "PyTorch",
            "SQL", "Git", "GitHub"
        ],
        "Data Analyst": [
            "Python", "SQL", "Pandas", "NumPy", "Excel",
            "Power BI", "Matplotlib", "Git", "GitHub"
        ],
        "Software Developer": [
            "Python", "Java", "C++", "SQL", "Git",
            "GitHub", "API", "HTML", "CSS", "JavaScript"
        ]
    }

    return role_skills.get(job_role, [])


def get_learning_resource(skill):
    resources = {
        "Python": "Learn Python basics, functions, OOP, and file handling.",
        "SQL": "Practice SELECT, JOIN, GROUP BY, and subqueries.",
        "Git": "Learn git init, add, commit, branch, merge, and push.",
        "GitHub": "Create repositories and upload projects to GitHub.",
        "API": "Learn REST APIs, HTTP methods, JSON, and Python requests.",
        "Flask": "Build a small CRUD web application using Flask.",
        "Django": "Learn Django models, views, templates, and authentication.",
        "SQLite": "Practice database tables and CRUD operations.",
        "Pandas": "Practice DataFrames, filtering, groupby, merge, and cleaning.",
        "NumPy": "Learn arrays, indexing, reshaping, and mathematical operations.",
        "Machine Learning": "Learn regression, classification, training, and testing.",
        "Deep Learning": "Learn neural networks and activation functions.",
        "TensorFlow": "Build a beginner neural-network project.",
        "PyTorch": "Learn tensors, datasets, models, and training loops.",
        "Excel": "Practice formulas, pivot tables, charts, and lookups.",
        "Power BI": "Create dashboards and reports using Power BI.",
        "Matplotlib": "Create line charts, bar charts, and histograms.",
        "Java": "Learn Java OOP, collections, and exception handling.",
        "C++": "Practice C++ syntax, OOP, pointers, and STL.",
        "HTML": "Build structured web pages using HTML.",
        "CSS": "Learn Flexbox, Grid, responsive design, and layouts.",
        "JavaScript": "Learn functions, DOM manipulation, and events."
    }

    return resources.get(
        skill,
        f"Learn the basics of {skill} and build a mini project."
    )


# ---------------- INTERVIEW QUESTIONS ----------------

def get_interview_questions(job_role):
    questions = {
        "Python Developer": [
            "What is the difference between a list and a tuple in Python?",
            "What is an API?",
            "What is the difference between GET and POST methods?",
            "What is exception handling in Python?",
            "What is the difference between a module and a package in Python?",
            "What is a decorator in Python?"
        ],
        "AI/ML Developer": [
            "What is the difference between supervised and unsupervised learning?",
            "What is overfitting in machine learning?",
            "What is the difference between classification and regression?",
            "What is a confusion matrix?",
            "What is the purpose of train-test split?",
            "What is feature engineering?"
        ],
        "Data Analyst": [
            "What is the difference between Pandas and NumPy?",
            "What is data cleaning?",
            "What is the difference between INNER JOIN and LEFT JOIN in SQL?",
            "What is the difference between mean, median, and mode?",
            "What is a KPI?",
            "How do you handle missing values in a dataset?"
        ],
        "Software Developer": [
            "What is object-oriented programming?",
            "What is version control?",
            "What is the difference between frontend and backend development?",
            "What is a database?",
            "What is debugging?",
            "What is the difference between authentication and authorization?"
        ]
    }

    return questions.get(job_role, [])


# ---------------- GEMINI AI ----------------

def get_gemini_client():
    api_key = st.secrets["GEMINI_API_KEY"]
    return genai.Client(api_key=api_key)


def get_ai_resume_feedback(resume_text, job_role):
    prompt = f"""
You are an expert career coach.

Analyze this resume for the target role: {job_role}.

Give feedback using these headings:
1. Resume Strengths
2. Missing or Weak Skills
3. Improvement Suggestions
4. ATS Suggestions
5. Final Career Advice

Keep the answer practical, clear, and student-friendly.

Resume:
{resume_text[:9000]}
"""

    client = get_gemini_client()

    response = client.interactions.create(
        model="gemini-3.8-flash",
        input=prompt
    )

    return response.output_text


def evaluate_answer_with_ai(job_role, question, answer):
    prompt = f"""
You are a strict but supportive technical interviewer.

Target role: {job_role}
Interview question: {question}
Student answer: {answer}

Evaluate the student's answer accurately.

Return exactly in this format:

SCORE: number from 0 to 100
CORRECTNESS: Explain whether the answer is correct.
TECHNICAL FEEDBACK: Mention missing technical concepts.
COMMUNICATION: Comment on clarity and structure.
BETTER ANSWER: Give a concise improved answer.

Do not add any heading before SCORE.
"""

    client = get_gemini_client()

    response = client.interactions.create(
        model="gemini-3.8-flash",
        input=prompt
    )

    ai_feedback = response.output_text

    score_match = re.search(r"SCORE:\s*(\d+)", ai_feedback)

    if score_match:
        score = min(int(score_match.group(1)), 100)
    else:
        score = 0

    return score, ai_feedback


# ---------------- STREAMLIT APP ----------------

create_database()

st.set_page_config(
    page_title="AI Career & Interview Coach",
    page_icon="🚀",
    layout="wide"
)

st.title("🚀 AI Career & Interview Coach")
st.write(
    "Analyze your resume, identify skill gaps, receive AI interview "
    "feedback, and track your learning progress."
)

job_role = st.selectbox(
    "Choose your target role",
    [
        "Python Developer",
        "AI/ML Developer",
        "Data Analyst",
        "Software Developer"
    ]
)

tab1, tab2, tab3 = st.tabs([
    "📄 Resume Analyzer",
    "🎤 AI Interview Practice",
    "📊 Progress Dashboard"
])


# ---------------- RESUME ANALYZER ----------------

with tab1:
    st.header("Resume Analyzer")

    uploaded_resume = st.file_uploader(
        "Upload your Resume (PDF)",
        type=["pdf"]
    )

    if uploaded_resume:
        try:
            pdf_reader = PdfReader(uploaded_resume)
            resume_text = ""

            for page in pdf_reader.pages:
                resume_text += (page.extract_text() or "") + "\n"

            skills = extract_skills(resume_text)
            required_skills = get_required_skills(job_role)

            user_skills_lower = [skill.lower() for skill in skills]

            matched_skills = [
                skill for skill in required_skills
                if skill.lower() in user_skills_lower
            ]

            missing_skills = [
                skill for skill in required_skills
                if skill.lower() not in user_skills_lower
            ]

            match_percentage = (
                len(matched_skills) / len(required_skills)
            ) * 100

            st.success("Resume text extracted successfully!")

            col1, col2, col3 = st.columns(3)
            col1.metric("Identified Skills", len(skills))
            col2.metric("Job Match Score", f"{match_percentage:.0f}%")
            col3.metric("Missing Skills", len(missing_skills))

            st.subheader("Extracted Resume Content")
            st.text_area("Resume text", resume_text, height=220)

            st.subheader("Your Identified Skills")
            st.write(", ".join(skills) if skills else "No matching skills found.")

            st.subheader("Job Role Match Analysis")
            st.write(f"**Target Role:** {job_role}")
            st.progress(int(match_percentage))

            st.write(
                "✅ **Matching Skills:**",
                ", ".join(matched_skills) if matched_skills else "None"
            )

            st.write(
                "❌ **Missing Skills:**",
                ", ".join(missing_skills)
                if missing_skills else "None — great match!"
            )

            st.subheader("🗺️ Learning Roadmap")

            if missing_skills:
                for number, skill in enumerate(missing_skills, start=1):
                    st.write(
                        f"**{number}. {skill}** — "
                        f"{get_learning_resource(skill)}"
                    )
            else:
                st.success("Great! Your resume matches all core skills.")

            st.subheader("🤖 AI Resume Feedback")

            if st.button("Get AI Resume Feedback"):
                with st.spinner("Gemini is analyzing your resume..."):
                    try:
                        ai_resume_feedback = get_ai_resume_feedback(
                            resume_text,
                            job_role
                        )

                        st.success("AI resume analysis completed!")
                        st.markdown(ai_resume_feedback)

                    except Exception as error:
                        st.error(f"Gemini API error: {error}")

        except Exception as error:
            st.error(f"Unable to read this PDF: {error}")

    else:
        st.info("Upload a resume PDF to begin analysis.")


# ---------------- AI INTERVIEW PRACTICE ----------------

with tab2:
    st.header("AI Interview Practice")

    interview_questions = get_interview_questions(job_role)

    selected_question = st.selectbox(
        "Choose an interview question",
        interview_questions
    )

    st.write(f"**Question:** {selected_question}")

    user_answer = st.text_area(
        "Write your answer",
        placeholder="Type your answer in your own words...",
        height=180
    )

    if st.button("Evaluate My Answer with AI"):
        if not user_answer.strip():
            st.warning("Please type an answer before evaluation.")

        else:
            with st.spinner("Gemini is evaluating your answer..."):
                try:
                    score, ai_feedback = evaluate_answer_with_ai(
                        job_role,
                        selected_question,
                        user_answer
                    )

                    save_interview_attempt(
                        job_role,
                        selected_question,
                        score
                    )

                    st.metric("AI Interview Score", f"{score}%")
                    st.success("AI evaluation completed!")
                    st.markdown(ai_feedback)

                except Exception as error:
                    st.error(f"Gemini API error: {error}")


# ---------------- PROGRESS DASHBOARD ----------------

with tab3:
    st.header("Your Progress Dashboard")

    attempts_dataframe = get_interview_attempts()

    if attempts_dataframe.empty:
        st.info("No interview attempts yet. Complete an AI interview question first.")

    else:
        total_attempts = len(attempts_dataframe)
        average_score = attempts_dataframe["score"].mean()
        highest_score = attempts_dataframe["score"].max()

        col1, col2, col3 = st.columns(3)
        col1.metric("Questions Answered", total_attempts)
        col2.metric("Average Score", f"{average_score:.0f}%")
        col3.metric("Highest Score", f"{highest_score:.0f}%")

        st.subheader("Interview Score Progress")

        chart_data = attempts_dataframe.iloc[::-1].copy()
        chart_data["Attempt"] = range(1, len(chart_data) + 1)

        figure, axis = plt.subplots()

        axis.plot(
            chart_data["Attempt"],
            chart_data["score"],
            marker="o",
            color="blue"
        )

        axis.set_xlabel("Attempt Number")
        axis.set_ylabel("Score (%)")
        axis.set_title("Interview Score Over Time")
        axis.set_ylim(0, 100)

        st.pyplot(figure)

        st.subheader("Past Interview Attempts")

        st.dataframe(
            attempts_dataframe[
                ["job_role", "question", "score", "attempted_at"]
            ],
            use_container_width=True
        )