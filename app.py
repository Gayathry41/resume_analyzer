from flask import Flask, render_template, request, redirect, url_for, flash
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

@app.route("/analyze", methods=["GET", "POST"])
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
    result = None  # This will store the result text for display

    if request.method == "POST":
        job_desc = request.form.get("job_desc")
        resume_file = request.files.get("resume")
        mode = request.form.get("mode")  # "review" or "match"

        if resume_file and allowed_file(resume_file.filename):
            filename = secure_filename(resume_file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            resume_file.save(filepath)

            # Simulate a result for now
            if mode == "review":
                result = f"📝 Resume uploaded successfully for review.<br><strong>Job Description:</strong><br>{job_desc}"
            elif mode == "match":
                result = f"✅ Simulated Match Score: 87%<br><strong>Job Description:</strong><br>{job_desc}"
        else:
            result = "❌ Invalid file type. Please upload a PDF."

    return render_template("analyze.html", result=result)


if __name__ == "__main__":
    app.run(debug=True)
