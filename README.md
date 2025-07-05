# 🧠 Smart Career Coach

A resume analyzer and career guidance web app built using **Streamlit**, **Python**, and a touch of **Generative AI**.

This tool helps users:
- 📄 Extract key information from resumes (skills, email, phone).
- 🔍 Match their skills to suitable job roles from a predefined dataset.
- ❌ Identify missing skills for target roles.
- 📚 Get learning resource recommendations (powered by Gen AI).

---

## 🚀 Features

- Upload your **PDF resume**.
- Automatically extract:
  - ✉️ Email ID
  - 📞 Phone number
  - 🛠 Skills
- Match with top job roles based on skill similarity.
- Display missing skills and recommend learning resources.
- Saves the analysis to a CSV file for tracking.

---

## 🗂 Project Structure

Smart_Career_Coach/
│
├── src/
│ ├── app.py # Main Streamlit app
│ ├── test_openai_env.py # Optional: test OpenAI key
│ └── data/
│ └── job_roles.csv # CSV with job roles and required skills
│
├── .gitignore
├── .env # Contains OpenAI API key (DO NOT COMMIT)
├── README.md
└── requirements.txt


---

## 🧠 Technologies Used

- **Python 3.10+**
- **Streamlit** – for building the web app
- **PyPDF2** – to extract resume content
- **Pandas** – for data processing
- **OpenAI API** – for course recommendations (optional)

---
