from flask import Flask, render_template, request
import datetime
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import os
import base64
import io
from PIL import Image
import pdf2image
import google.generativeai as genai
import json

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Flask app setup
app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Upload folder setup
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/", methods=["GET", "POST"])
def index():
    result = None

    if request.method == "POST":
        resume_file = request.files.get("resume")

        if resume_file and allowed_file(resume_file.filename):
            try:
                # Convert first page of PDF to image
                images = pdf2image.convert_from_bytes(resume_file.read())
                first_page = images[0]

                img_byte_arr = io.BytesIO()
                first_page.save(img_byte_arr, format='JPEG')
                img_byte_arr = img_byte_arr.getvalue()

                pdf_parts = [{
                    "mime_type": "image/jpeg",
                    "data": base64.b64encode(img_byte_arr).decode()
                }]

                # Prompt for structured JSON extraction
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
                These may include but are not limited to: projects, languages, awards, publications, volunteering, hobbies, tools & technologies.

                Use the section title as the JSON key and store its value appropriately (string, list, or nested object).
                Do not include any explanation—only return valid, clean JSON.
                """

                # Gemini API call
                model = genai.GenerativeModel("gemini-1.5-flash-latest")
                response = model.generate_content([prompt, pdf_parts[0]])

                # Format/validate JSON
                text_response = response.text.strip()
                try:
                    parsed_json = json.loads(text_response)
                    result = json.dumps(parsed_json, indent=4)
                    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    json_filename = f"resume_{timestamp}.json"
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

if __name__ == "__main__":
    app.run(debug=True)
