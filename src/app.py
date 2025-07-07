from dotenv import load_dotenv
import os
import openai  # ✅ Ensure API is set before using it
import streamlit as st
import pandas as pd
import PyPDF2
import re
import io


# --- Load API Key ---
load_dotenv()
openai.api_key = st.secrets["OPENAI_API_KEY"]
if not openai.api_key:
    st.warning("⚠️ OpenAI API key not found. Please set it in the `.env` file.")

# --- Streamlit Config & Styling ---
st.set_page_config(page_title="Smart Career Coach", layout="centered")
st.markdown("""
    <style>
    /* Set sea blue gradient for app background */
    .stApp {
        background: linear-gradient(to right, #a8edea, #fed6e3); /* light sea/aqua gradient */
        padding: 0;
        margin: 0;
    }

    .main {
        background-color: rgba(255, 255, 255, 0.95);
        padding: 30px;
        border-radius: 12px;
        margin: 2rem auto;
        max-width: 900px;
        box-shadow: 0px 0px 15px rgba(0,0,0,0.1);
    }

    /* Sidebar appearance */
    .css-1d391kg, .css-1lcbmhc {
        background-color: #e0f7fa !important;
        color: black !important;
    }

    /* Text, font, inputs */
    html, body, [class*="css"] {
        font-family: 'Segoe UI', sans-serif;
        color: #222;
    }

    .stTextInput > div > input,
    .stTextArea > div > textarea {
        border-radius: 8px;
        border: 1px solid #ccc;
    }

    .stButton > button {
        background-color: #00bcd4;
        color: white;
        font-weight: bold;
        border-radius: 8px;
        height: 3em;
        font-size: 16px;
    }

    h1, h2 {
        text-align: center;
        color: #004d40;
    }
    </style>
""", unsafe_allow_html=True)



st.markdown("""
    <h1 style='
        text-align: center;
        font-size: 3em;
        color: #222;
        font-family: "Segoe UI", sans-serif;
        font-weight: 800;
        margin-bottom: 0.5em;
    '>
        🚀 Smart Career Coach
    </h1>
""", unsafe_allow_html=True)


# --- Sidebar Navigation ---
page = st.sidebar.radio("📂 Navigation", ["Upload Resume", "Cover Letter Generator", "About"])



# --- Resume Upload & Analysis ---
if page == "Upload Resume":
    # Load job roles
    job_roles_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'job_roles.csv')
    job_roles_df = pd.read_csv("src/data/job_roles.csv")
    job_roles_df.columns = job_roles_df.columns.str.strip()

    if "Required Skills" not in job_roles_df.columns:
        st.error("❌ 'Required Skills' column not found in job_roles.csv. Check if the file is using tabs or commas and the header name is correct.")
        st.stop()

    KNOWN_SKILLS = list(set(
        skill.strip().lower()
        for skills in job_roles_df["Required Skills"].dropna()
        for skill in skills.split(";")
    ))

    def extract_text(file):
        reader = PyPDF2.PdfReader(file)
        text = "".join(page.extract_text() or "" for page in reader.pages)
        return text.lower()

    def extract_email(text):
        match = re.search(r'\b\S+@\S+\b', text)
        return match.group() if match else "Not found"

    def extract_phone(text):
        match = re.search(r'(\+91)?[\s\-]?[6-9]\d{9}', text)
        return match.group() if match else "Not found"

    def extract_skills(text):
        return [skill for skill in KNOWN_SKILLS if re.search(r'\b' + re.escape(skill) + r'\b', text)]

    def match_job_roles(resume_skills):
        matched_roles = []
        for _, row in job_roles_df.iterrows():
            role = row["Job Role"]
            required_skills_raw = row["Required Skills"]
            if pd.isna(required_skills_raw):
                continue
            required = [s.strip().lower() for s in required_skills_raw.split(";")]
            matched = list(set(resume_skills).intersection(required))
            missing = list(set(required) - set(resume_skills))
            match_pct = round(len(matched) / len(required) * 100, 2)
            matched_roles.append({
                "Job Role": role,
                "Match %": match_pct,
                "Matched Skills": matched,
                "Missing Skills": missing
            })
        return sorted(matched_roles, key=lambda x: x["Match %"], reverse=True)

    def get_course_recommendations(missing_skills):
        if not missing_skills:
            return "✅ You're all set!"
        return "\n".join([
            f"- Learn {skill.title()}: *Intro to {skill.title()}* – Coursera/Udemy"
            for skill in missing_skills
        ])

    uploaded_file = st.file_uploader("📌 Upload your resume (PDF only)", type=["pdf"])

    if uploaded_file:
        text = extract_text(uploaded_file)
        email = extract_email(text)
        phone = extract_phone(text)
        skills = extract_skills(text)
        matched = match_job_roles(skills)

        st.markdown("---")
        st.subheader("📄 Resume Insights")
        st.write(f"**📧 Email:** {email}")
        st.write(f"**📱 Phone:** {phone}")
        st.write(f"**💼 Skills:** {', '.join(skills) if skills else 'None found'}")

        st.subheader("🎯 Top Role Matches")
        for role in matched[:2]:
            st.markdown(f"**✅ Suggested Role:** {role['Job Role']}")
            st.write(f"Match %: {role['Match %']}%")
            st.write(f"✔️ Matched Skills: {', '.join(role['Matched Skills'])}")
            st.write(f"❌ Missing Skills: {', '.join(role['Missing Skills'])}")

            with st.expander("🎓 View Learning Recommendations"):
                with st.spinner("🔍 Generating course recommendations..."):
                    course_recs = get_course_recommendations(role["Missing Skills"])
                    st.write(course_recs)

            st.markdown("---")

        save_data = {
            "Resume": uploaded_file.name,
            "Email": email,
            "Phone": phone,
            "Top Role": matched[0]["Job Role"],
            "Match %": matched[0]["Match %"],
            "Matched Skills": ", ".join(matched[0]["Matched Skills"]),
            "Missing Skills": ", ".join(matched[0]["Missing Skills"])
        }

        csv_path = "src/data/resume_results.csv"
        os.makedirs(os.path.dirname(csv_path), exist_ok=True)

        if os.path.exists(csv_path) and os.path.getsize(csv_path) > 0:
            try:
                df = pd.read_csv(csv_path)
            except pd.errors.EmptyDataError:
                df = pd.DataFrame()
        else:
            df = pd.DataFrame()

        df = pd.concat([df, pd.DataFrame([save_data])], ignore_index=True)

        try:
            df.to_csv(csv_path, index=False)
            st.success("✅ Your resume analysis has been saved!")
        except PermissionError:
            st.error("❌ Cannot write to 'resume_results.csv'. Please close it if it's open and try again.")

# --- Cover Letter Generator ---
# --- Cover Letter Generator ---
elif page == "Cover Letter Generator":
    st.header("Cover Letter Generator")
    company_name = st.text_input("🏢 Enter the Company Name")
    user_name = st.text_input("🧑 Your Name", value="Your Name")
    user_role = st.text_input("🌟 Target Role", value="Your Target Role")
    top_skills = st.text_area("💼 Top Skills (comma-separated)", value="Python, SQL, Teamwork")

    # Generate only when clicked
    if st.button("Generate Cover Letter"):
        st.session_state["cover_letter"] = f"""
Dear Hiring Manager at {company_name},

I am writing to express my keen interest in the position of **{user_role}** at your esteemed organization. With a solid foundation in **{top_skills}**, I bring a unique blend of technical skills and passion to every opportunity.

Throughout my academic and project experiences, I have demonstrated the ability to quickly adapt, collaborate effectively in teams, and apply problem-solving skills to real-world challenges.

Thank you for considering my application. I look forward to the opportunity to contribute to {company_name} and grow together.

Sincerely,  
{user_name}
        """.strip()

    # Display if already generated
    if "cover_letter" in st.session_state:
        edited_letter = st.text_area("📄 Generated Cover Letter", st.session_state["cover_letter"], height=300)
        st.download_button("⬇ Download Cover Letter", edited_letter, file_name="cover_letter.txt")
        st.info("✏️ *Note: This is a sample cover letter. You can edit and download it.*")


# --- About Page ---
elif page == "About":
    st.header("About This App")
    st.write("""
    This Smart Career Coach helps you:
    - 📄 Analyze your resume
    - 🔍 Match it with suitable job roles
    - 🎓 Suggest learning paths
    - ✍️ Generate cover letters

    Built using Streamlit, pandas, and a touch of AI magic.
    """)

