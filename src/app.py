from dotenv import load_dotenv
import os
import openai  # ✅ Make sure this is above openai.api_key

# Load variables from .env
load_dotenv()

# Get API key
openai.api_key = os.getenv("OPENAI_API_KEY")



import streamlit as st
import pandas as pd
import PyPDF2
import re
import io
import os

st.set_page_config(page_title="Smart Career Coach", layout="centered")

st.title("📤 Upload Your Resume - Smart Career Coach")


# Load job roles
job_roles_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'job_roles.csv')
job_roles_df = pd.read_csv("data/job_roles.csv")


# Build known skills list from CSV
KNOWN_SKILLS = list(set(
    skill.strip().lower()
    for skills in job_roles_df["Required Skills"]
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
        required = [s.strip().lower() for s in row["Required Skills"].split(";")]
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

# Upload UI
uploaded_file = st.file_uploader("📎 Upload your resume (PDF only)", type=["pdf"])

def get_course_recommendations(missing_skills):
    if not missing_skills:
        return "✅ You're all set!"
    return "\n".join([
        f"- Learn {skill.title()}: *Intro to {skill.title()}* – Coursera/Udemy"
        for skill in missing_skills
    ])

if uploaded_file:
    text = extract_text(uploaded_file)
    email = extract_email(text)
    phone = extract_phone(text)
    skills = extract_skills(text)
    matched = match_job_roles(skills)

    # Show details
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
        st.subheader("📚 Recommended Learning Resources")
        with st.spinner("🔍 Generating course recommendations..."):
            course_recs = get_course_recommendations(role["Missing Skills"])
            st.markdown(course_recs)
        st.markdown("---")
        # Save to resume_results.csv
    save_data = {
        "Resume": uploaded_file.name,
        "Email": email,
        "Phone": phone,
        "Top Role": matched[0]["Job Role"],
        "Match %": matched[0]["Match %"],
        "Matched Skills": ", ".join(matched[0]["Matched Skills"]),
        "Missing Skills": ", ".join(matched[0]["Missing Skills"])
    }
    # Load existing CSV or create new one
    os.makedirs("../data", exist_ok=True)

    csv_path = "../data/resume_results.csv"
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        df = pd.concat([df, pd.DataFrame([save_data])], ignore_index=True)
    else:
        df = pd.DataFrame([save_data])
    df.to_csv(csv_path, index=False)
    st.success("✅ Your resume analysis has been saved!")
