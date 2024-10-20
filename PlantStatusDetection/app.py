import os
import google.generativeai as genai
import json
from PIL import Image
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import requests
from io import BytesIO

app = Flask(__name__)

# Configure the API
GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
genai.configure(api_key=GOOGLE_API_KEY)

# Set up the model globally
model = genai.GenerativeModel('gemini-1.5-flash')

def preprocess_image(image, max_size=1024):
    image.thumbnail((max_size, max_size))
    return image

def identify_plant(image):
    try:
        prompt = """
        Analyze this plant image and provide the following information in an easy-to-understand format:

        1. Plant Name: [Common name]
        2. Scientific Name: [Latin name]
        3. Plant Type: [e.g., Herb, Shrub, Tree, Succulent, etc.]
        4. Health Status: [Healthy or Unhealthy]
        5. Key Characteristics: [Brief description of notable features]

        If the plant appears unhealthy:
        6. Possible Issue: [Name of disease or problem]
        7. Symptoms: [Visible signs of the issue]
        8. Cause: [Likely reasons for the problem]
        9. Treatment: [Simple steps to address the issue]

        Care Instructions:
        10. Sunlight Needs: [e.g., Full sun, Partial shade, etc.]
        11. Watering: [How often and how much]
        12. Soil Type: [Best soil for this plant]

        Fertilizer Recommendations:
        13. Provide 2-3 specific fertilizer options with:
           - Fertilizer Name
           - NPK Ratio (explain what this means)
           - How often to apply
           - How much to use

        Please use simple language and avoid jargon. If technical terms are necessary, provide brief explanations.
        Format the response as a JSON object with these numbered sections as keys.
        """

        response = model.generate_content([prompt, image])
        result = json.loads(response.text)
        return result

    except json.JSONDecodeError:
        return {"error": "Failed to parse JSON response", "raw_response": response.text}
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}

@app.route('/identify', methods=['POST'])
def identify():
    if 'file' in request.files:
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400
        if file:
            image = Image.open(file.stream)
    elif 'url' in request.form:
        url = request.form['url']
        response = requests.get(url)
        image = Image.open(BytesIO(response.content))
    else:
        return jsonify({"error": "No file uploaded or URL provided"}), 400

    processed_image = preprocess_image(image)
    result = identify_plant(processed_image)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))