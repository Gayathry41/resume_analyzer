# 📄 CViator: Intelligent Resume Analyzer and Generator

CViator is an end-to-end resume intelligence toolkit that leverages **Gemini-1.5 Flash** and **fine-tuned BERT models** to analyze, extract, and compare resume data against job descriptions. It also provides a modern user interface to build LaTeX-based resumes with drag-and-drop features and export them as polished PDF documents.

---

## 🚀 Features

- ✅ **Resume Parsing with Gemini-1.5-Flash**
  - Extract structured information (skills, education, experience) from uploaded PDF resumes
  - Output provided as JSON

- ✅ **Job Description Matching with Gemini**
  - Compare uploaded resume against a provided job description using Gemini-1.5 Flash
  - Get AI-generated insights and relevance scores

- ✅ **Skill Extraction with Fine-Tuned BERT**
  - Custom-trained `bert-base-cased` model on CoNLL-formatted dataset
  - Extracts **only the explicitly mentioned** skills from a job description
  - BIO tagging format used for high-quality token-level classification

- ✅ **Interactive Resume Builder**
  - Drag and drop from extracted data and skill suggestions
  - Add sections, bullets, titles, and paragraphs
  - Dynamically build LaTeX content without manual coding

- ✅ **PDF Resume Generation**
  - Render the generated LaTeX content to a professional resume PDF
  - Supports 1-column and 2-column layouts, subheadings, rules, etc.

---

## 🧠 Models Used

| Task                    | Model                       |
|-------------------------|-----------------------------|
| Resume Parsing          | `gemini-1.5-flash-latest`   |
| Resume–JD Comparison    | `gemini-1.5-flash-latest`   |
| Skill Extraction (JD)   | `bert-base-cased` (fine-tuned) |

---

## 🗂️ Data Preparation

- **Resume Skill Extraction:**
  - Done using Gemini with prompt engineering
- **Job Description Skill Extraction:**
  - Custom dataset in **CoNLL format**
  - Labels: `B-SKILL`, `I-SKILL`, `O`

---

## 🖥️ User Interfaces

- 📥 Upload resume (PDF) → Extract JSON
- 📝 Paste Job Description → Extract BERT skills
- 📊 Drag and drop resume/job skills into resume builder
- 📄 Convert structured blocks into **LaTeX code**
- 📤 Export as professional **PDF Resume**

---

## 💡 Tech Stack

- **Frontend**: HTML, CSS, Bootstrap 4/5, JS
- **Backend**: Flask
- **AI Models**: Gemini API, HuggingFace Transformers
- **PDF/LaTeX**: pdflatex, custom editor UI

---

## 📌 How to Run

1. Clone the repo and install dependencies
2. Add your Gemini API key to `.env`
3. Train (or load) the fine-tuned BERT model
4. Run the Flask server:
   ```bash
   python app.py
```


Access localhost:5000 in your browser

## 📷 Screenshots
Resume Upload Page

## JD Skill Extractor (BERT)

Interactive LaTeX Resume Builder

Final Resume PDF Output

## 🛠️ Future Enhancements
Add support for multiple resume templates

Integrate OpenAI GPT-based suggestions

Improve drag-and-drop editor UX

Add dark mode for builder interface

## 🙌 Credits
Google Gemini API

HuggingFace Transformers

scikit-learn, seqeval

Flask, Bootstrap, pdflatex

css
Copy
Edit
