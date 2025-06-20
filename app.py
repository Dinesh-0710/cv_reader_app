import streamlit as st
import pandas as pd
import fitz  # PyMuPDF for PDFs
from docx import Document
import io

# -------------------- UI Settings --------------------
st.set_page_config(page_title="Smart CV Reader", layout="wide")
st.title("🚀 Smart CV Reader")
st.markdown("Upload resumes, extract skills, rank them by match score, and download as Excel.")

# -------------------- Skill Matching --------------------
def match_score(extracted_skills, required_skills):
    matched = [skill for skill in required_skills if skill.lower() in [s.lower() for s in extracted_skills]]
    score = len(matched) / len(required_skills) if required_skills else 0
    return round(score * 100, 2), matched

# -------------------- Extract Text from PDF --------------------
def extract_text_from_pdf(file):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

# -------------------- Extract Text from DOCX --------------------
def extract_text_from_docx(file):
    doc = Document(file)
    return '\n'.join([p.text for p in doc.paragraphs])

# -------------------- Mock Resume Parser --------------------
def parse_resume(text):
    keywords = ['python', 'sql', 'machine learning', 'data analysis', 'communication',
                'deep learning', 'excel', 'django', 'html', 'css', 'power bi']
    found = [kw for kw in keywords if kw.lower() in text.lower()]
    return {
        "Name": "Unknown",
        "Skills": found
    }

# -------------------- App UI --------------------
uploaded_files = st.file_uploader("📄 Upload resumes (.pdf or .docx)", accept_multiple_files=True, type=['pdf', 'docx'])

required_skills_input = st.text_input("🛠️ Enter required skills (comma-separated)", "Python, SQL, Machine Learning")

if uploaded_files and required_skills_input:
    required_skills_list = [s.strip() for s in required_skills_input.split(',')]
    results = []

    for file in uploaded_files:
        ext = file.name.split('.')[-1].lower()

        # Extract resume text
        if ext == 'pdf':
            text = extract_text_from_pdf(file)
        elif ext == 'docx':
            text = extract_text_from_docx(file)
        else:
            st.warning(f"Unsupported file: {file.name}")
            continue

        # Parse and score
        data = parse_resume(text)
        score, matched = match_score(data['Skills'], required_skills_list)

        results.append({
            "Filename": file.name,
            "Extracted Skills": ', '.join(data['Skills']),
            "Matched Skills": ', '.join(matched),
            "Score (%)": score
        })

    # Display results
    df = pd.DataFrame(results).sort_values(by="Score (%)", ascending=False)
    st.subheader("📊 Resume Ranking")
    st.dataframe(df)

    # Download Excel
    output = io.BytesIO()
    df.to_excel(output, index=False, engine='openpyxl')
    st.download_button("⬇️ Download Excel", data=output.getvalue(), file_name="ranked_resumes.xlsx", mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
