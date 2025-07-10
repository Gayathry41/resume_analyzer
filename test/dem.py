import google.generativeai as genai

genai.configure(api_key="AIzaSyCEKD82E7jqN-Y_BlqiHbLZijPsHOmQIKU")

models = genai.list_models()
for m in models:
    print(m.name)
