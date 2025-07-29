from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import os,subprocess
import base64
import io
from PIL import Image
import pdf2image
import google.generativeai as genai
import datetime
import json
import torch
from transformers import BertTokenizerFast, BertForTokenClassification
import re
# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Initialize Flask app
app = Flask(__name__, static_folder="static")
app.secret_key = 'your_secret_key'

# Upload settings
UPLOAD_FOLDER = 'static'
ALLOWED_EXTENSIONS = {'pdf'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# -----------------------------
# BERT Skill Extraction Config
# -----------------------------
model_path = "./ner_model"
labels_list = ["O", "B-SKILL", "I-SKILL"]
label2id = {label: i for i, label in enumerate(labels_list)}
id2label = {i: label for label, i in label2id.items()}

# Load BERT model and tokenizer once
bert_model = BertForTokenClassification.from_pretrained(model_path)
bert_tokenizer = BertTokenizerFast.from_pretrained(model_path)
bert_model.eval()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# -----------------------------
# BERT Prediction Logic
# -----------------------------
def predict_tokens_from_text(text):
    words = text.strip().split()
    tokenized = bert_tokenizer(
        words,
        is_split_into_words=True,
        return_tensors="pt",
        truncation=True
    )
    word_ids = tokenized.word_ids(0)

    with torch.no_grad():
        outputs = bert_model(**tokenized)
    predictions = torch.argmax(outputs.logits, dim=2)[0].tolist()

    result = []
    previous_word_idx = None
    for idx, word_idx in enumerate(word_ids):
        if word_idx is None or word_idx == previous_word_idx:
            continue
        word = words[word_idx]
        label_id = predictions[idx]
        result.append((word, id2label[label_id]))
        previous_word_idx = word_idx
    return result

def extract_skills(predictions):
    skills = []
    current_skill = []
    for word, tag in predictions:
        if tag == "B-SKILL":
            if current_skill:
                skills.append(" ".join(current_skill))
                current_skill = []
            current_skill.append(word)
        elif tag == "I-SKILL":
            current_skill.append(word)
        else:
            if current_skill:
                skills.append(" ".join(current_skill))
                current_skill = []
    if current_skill:
        skills.append(" ".join(current_skill))
    return skills

# -----------------------------
# ROUTES
# -----------------------------

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/bert", methods=["GET", "POST"])
def bert():
    skills = []
    if request.method == "POST":
        job_desc = request.form["jobdesc"]

        # Run prediction and extract skills
        predictions = predict_tokens_from_text(job_desc)
        skills = extract_skills(predictions)

        # Save to JSON
        output = {"extracted_skills": skills}
        output_path = os.path.join("static", "skills_output.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=4)

    return render_template("bert.html", skills=skills)


@app.route("/generate", methods=["GET", "POST"])
def generate():
    result = None

    if request.method == "POST":
        resume_file = request.files.get("resume")
        if resume_file and allowed_file(resume_file.filename):
            try:
                images = pdf2image.convert_from_bytes(resume_file.read())
                first_page = images[0]

                img_byte_arr = io.BytesIO()
                first_page.save(img_byte_arr, format='JPEG')
                img_byte_arr = img_byte_arr.getvalue()

                pdf_parts = [{
                    "mime_type": "image/jpeg",
                    "data": base64.b64encode(img_byte_arr).decode()
                }]

                prompt = """
                You are a smart resume parser. Extract and organize the resume content into a structured JSON format.

                Mandatory fields to extract (if available):
                - name
                - email
                - phone
                - location
                - linkedin or github
                - summary or objective
                - skills
                - education
                - experience
                - certifications

                Additionally, detect and include any other sections present in the resume that are not listed above.
                """

                model = genai.GenerativeModel("gemini-1.5-flash-latest")
                response = model.generate_content([prompt, pdf_parts[0]])
                text_response = response.text.strip()

                match = re.search(r"```(?:json)?\s*(.*?)```", text_response, re.DOTALL)
                cleaned_text = match.group(1).strip() if match else text_response

                try:
                    parsed_json = json.loads(cleaned_text)
                    result = json.dumps(parsed_json, indent=4)
                    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    json_filename = "data.json"
                    json_path = os.path.join(app.config["UPLOAD_FOLDER"], json_filename)

                    with open(json_path, "w", encoding="utf-8") as f:
                        json.dump(parsed_json, f, indent=4)
                except json.JSONDecodeError:
                    result = f"⚠️ Gemini response not valid JSON. Raw output:\n\n{text_response}"
            except Exception as e:
                result = f"❌ Error: {str(e)}"
        else:
            result = "❌ Invalid file type. Please upload a PDF."

    return render_template("sample.html", result=result)


@app.route("/analyze", methods=["GET", "POST"])
def analyze():
    result = None
    if request.method == "POST":
        job_desc = request.form.get("job_desc")
        resume_file = request.files.get("resume")
        mode = request.form.get("mode")

        if resume_file and allowed_file(resume_file.filename):
            try:
                images = pdf2image.convert_from_bytes(resume_file.read())
                first_page = images[0]

                img_byte_arr = io.BytesIO()
                first_page.save(img_byte_arr, format='JPEG')
                img_byte_arr = img_byte_arr.getvalue()

                pdf_parts = [{
                    "mime_type": "image/jpeg",
                    "data": base64.b64encode(img_byte_arr).decode()
                }]

                prompt = """
                You are an experienced Technical Human Resource Manager. Review the provided resume against the job description.
                Please share whether the candidate's profile aligns with the role. Highlight strengths and weaknesses.
                """ if mode == "review" else """
                You are a skilled ATS (Applicant Tracking System) scanner with a deep understanding of data science and ATS functionality.
                Evaluate the resume against the job description. Give the percentage match, list missing keywords, and provide final thoughts.
                """

                model = genai.GenerativeModel('gemini-1.5-flash-latest')
                response = model.generate_content([prompt, pdf_parts[0], job_desc])
                result = response.text
            except Exception as e:
                result = f"❌ Error while processing resume: {str(e)}"
        else:
            result = "❌ Invalid file type. Please upload a PDF."

    return render_template("analyze.html", result=result)



@app.route("/resume_gen", methods=["GET", "POST"])
def resume_gen():
    return render_template("resume_gen.html")


@app.route("/render", methods=["POST"])
def generate_pdf():
    latex_content = request.form["latex_content"]

    full_tex = f"""
\\documentclass[a4paper,10pt]{{article}}
\\usepackage[a4paper,margin=1in]{{geometry}}
\\usepackage{{multicol}}
\\usepackage{{parskip}}
\\usepackage{{titlesec}}
\\usepackage{{xcolor}}
\\usepackage{{enumitem}}
\\usepackage{{hyperref}}
\\pagestyle{{empty}}
\\setlength{{\\parindent}}{{0pt}}
\\titleformat{{\\section}}{{\\large\\bfseries}}{{}}{{0em}}{{}}[\\titlerule]

\\begin{{document}}

{latex_content}

\\end{{document}}
    """

    os.makedirs("output", exist_ok=True)
    tex_path = "output/resume.tex"
    with open(tex_path, "w") as f:
        f.write(full_tex)

    try:
        subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", "-output-directory", "output", tex_path],
            check=True
        )
    except subprocess.CalledProcessError:
        return "PDF generation failed", 500

    return send_file("output/resume.pdf", as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
