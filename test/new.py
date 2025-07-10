import google.generativeai as genai

# Replace with your valid API key (keep it secret!)
genai.configure(api_key="AIzaSyCEKD82E7jqN-Y_BlqiHbLZijPsHOmQIKU")

# Use Gemini 2.5 Pro model
model = genai.GenerativeModel("models/gemini-2.5-pro")

# Generate content
response = model.generate_content("Explain quantum computing in simple terms.")
print(response.text)
