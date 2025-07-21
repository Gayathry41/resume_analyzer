from flask import Flask, render_template, request, redirect, url_for, flash,send_file
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import os
import base64
import io
from PIL import Image
import pdf2image
import google.generativeai as genai

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Upload settings
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create uploads folder if not exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/generate", methods=["GET", "POST"])
def generate():
    return render_template("generate.html")
@app.route("/download-latex", methods=["POST"])
def download_latex():
    latex_code = request.form.get("latex_code")
    file_path = os.path.join("uploads", "resume.tex")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(latex_code)
    return send_file(file_path, as_attachment=True)

# @app.route("/analyze", methods=["GET", "POST"])

# def analyze():
#     if request.method == "POST":
#         job_desc = request.form.get("job_desc")
#         resume_file = request.files.get("resume")
#         mode = request.form.get("mode")  # "review" or "match"

#         if resume_file and allowed_file(resume_file.filename):
#             filename = secure_filename(resume_file.filename)
#             filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
#             resume_file.save(filepath)

#             # TODO: Process the PDF and job description here
#             # For now, just print debug info
#             print("Job Description:", job_desc)
#             print("Resume saved to:", filepath)
#             print("Mode selected:", mode)

#             flash(f"{mode.capitalize()} submitted successfully!", "success")
#             return redirect(url_for("analyze"))
#         else:
#             flash("Invalid file type. Please upload a PDF.", "danger")
#             return redirect(url_for("analyze"))

#     return render_template("analyze.html")

@app.route("/analyze", methods=["GET", "POST"])
def analyze():
    result = None  # For passing result to the template

    if request.method == "POST":
        job_desc = request.form.get("job_desc")
        resume_file = request.files.get("resume")
        mode = request.form.get("mode")  # "review" or "match"

        if resume_file and allowed_file(resume_file.filename):
            try:
                # Convert resume PDF to image (first page only)
                images = pdf2image.convert_from_bytes(resume_file.read())
                first_page = images[0]

                img_byte_arr = io.BytesIO()
                first_page.save(img_byte_arr, format='JPEG')
                img_byte_arr = img_byte_arr.getvalue()

                pdf_parts = [{
                    "mime_type": "image/jpeg",
                    "data": base64.b64encode(img_byte_arr).decode()
                }]

                # Choose prompt
                if mode == "review":
                    prompt = """
                    You are an experienced Technical Human Resource Manager. Review the provided resume against the job description.
                    Please share whether the candidate's profile aligns with the role. Highlight strengths and weaknesses.
                    """
                else:
                    prompt = """
                    You are a skilled ATS (Applicant Tracking System) scanner with a deep understanding of data science and ATS functionality.
                    Evaluate the resume against the job description. Give the percentage match, list missing keywords, and provide final thoughts.
                    """

                # Get Gemini response gemini-pro-vision   gemini-1.5-flash-latest
                model = genai.GenerativeModel('gemini-1.5-flash-latest')
                response = model.generate_content([prompt, pdf_parts[0], job_desc])
                result = response.text

            except Exception as e:
                result = f"❌ Error while processing resume: {str(e)}"
        else:
            result = "❌ Invalid file type. Please upload a PDF."

    return render_template("analyze.html", result=result)

if __name__ == "__main__":
    app.run(debug=True)
