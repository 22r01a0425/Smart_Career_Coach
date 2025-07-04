import os
import re
import pandas as pd
import PyPDF2

# Load job role data
job_roles_df = pd.read_csv("../data/job_roles.csv")

# Known skills to compare against
KNOWN_SKILLS = list(set(
    skill.strip().lower()
    for skills in job_roles_df["Required Skills"]
    for skill in skills.split(";")
))

def extract_text_from_pdf(file_path):
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = "".join(page.extract_text() or "" for page in reader.pages)
    return text.lower()

def extract_email(text):
    match = re.search(r'\b\S+@\S+\b', text)
    return match.group() if match else None

def extract_phone(text):
    match = re.search(r'(\+91)?[\s\-]?[6-9]\d{9}', text)
    return match.group() if match else None

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

# Main loop
resume_folder = "../data/resumes"
for file in os.listdir(resume_folder):
    if file.endswith(".pdf"):
        path = os.path.join(resume_folder, file)
        print(f"\n📄 Resume: {file}")
        text = extract_text_from_pdf(path)
        email = extract_email(text)
        phone = extract_phone(text)
        skills = extract_skills(text)

        print(f"📧 Email: {email}")
        print(f"📱 Phone: {phone}")
        print(f"💼 Extracted Skills: {skills}")

        top_matches = match_job_roles(skills)
        for role in top_matches[:2]:
            print(f"\n🎯 Suggested Role: {role['Job Role']}")
            print(f"✅ Match %: {role['Match %']}%")
            print(f"✔️ Matched Skills: {role['Matched Skills']}")
            print(f"❌ Missing Skills: {role['Missing Skills']}")



output = []  # List to store each resume's results

# 🔁 Loop through each resume
for file in os.listdir(resume_folder):
    if file.endswith(".pdf"):
        path = os.path.join(resume_folder, file)
        text = extract_text_from_pdf(path)
        email = extract_email(text)
        phone = extract_phone(text)
        skills = extract_skills(text)

        top_role = match_job_roles(skills)[0]  # Best matched job role

        output.append({
            "Resume": file,
            "Email": email,
            "Phone": phone,
            "Top Role": top_role["Job Role"],
            "Match %": top_role["Match %"],
            "Matched Skills": ", ".join(top_role["Matched Skills"]),
            "Missing Skills": ", ".join(top_role["Missing Skills"])
        })

# 📝 Save all results to a CSV file
results_df = pd.DataFrame(output)
results_df.to_csv("../data/resume_results.csv", index=False)

print("\n✅ All resume results saved to: data/resume_results.csv")
