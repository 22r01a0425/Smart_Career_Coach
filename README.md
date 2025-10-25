# 🚀 Smart Career Coach

An intelligent AI-powered web app that helps students and job seekers align their resume with the most relevant job roles, suggests missing skills, and recommends courses — all through a clean Streamlit interface.

## 🔍 Features

- 📄 Resume Upload & Parsing (PDF)
- 🎯 Job Role Matching using AI
- 🚫 Missing Skills Detection
- 📚 Course Recommendations
- 💡 Generative AI for Resume Line Suggestions
- 📊 Simple, interactive Streamlit UI

## 🖼 Demo

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://smartcareercoach-22r01a0425.streamlit.app/)


## 📁 Folder Structure

smart_career_coach/
│
├── .streamlit/
│   └── config.toml              # Streamlit app settings
│
├── src/
│   ├── app.py                   # Main Streamlit app code
│   └── data/
│       ├── job_roles.csv        # Job role to skill mapping
│       └── resume_results.csv   # Parsed resume data (optional / generated)
│
├── requirements.txt             # Python dependencies
├── README.md                    # Project documentation
└── LICENSE                      # License file (optional)


🧠 Tech Stack

Python

Streamlit

Pandas

Scikit-learn

PyPDF2

OpenAI API (for Generative AI tasks)

✨ Future Improvements
User authentication & login

Database for saving user history

Advanced NLP for resume understanding

## 📦 Installation

```bash
git clone https://github.com/yourusername/smart_career_coach.git
cd smart_career_coach
pip install -r requirements.txt
streamlit run src/app.py


---
