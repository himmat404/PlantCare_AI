# Plant Identification API

This API uses Google's Generative AI to identify plants from images and provide detailed information about them, including care instructions and fertilizer recommendations.

## Table of Contents

1. [Features](#features)
2. [Setup](#setup)
3. [API Usage](#api-usage)
4. [Response Format](#response-format)
5. [Deployment](#deployment)
6. [Error Handling](#error-handling)

## Features

- Identify plants from uploaded image files or image URLs
- Provide detailed information about the plant, including:
  - Common and scientific names
  - Plant type
  - Health status
  - Key characteristics
  - Care instructions
  - Fertilizer recommendations

## Setup

1. Clone this repository
2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```
3. Set up your Google API key as an environment variable:
   ```
   export GOOGLE_API_KEY='your_api_key_here'
   ```

## API Usage

The API has a single endpoint: `/identify`

### Using with Image File Upload

Send a POST request to `/identify` with the image file in the request body:

```python
import requests

url = 'https://your-api-url.com/identify'
files = {'file': open('path/to/your/image.jpg', 'rb')}
response = requests.post(url, files=files)
print(response.json())
```

### Using with Image URL

Send a POST request to `/identify` with the image URL in the form data:

```python
import requests

url = 'https://your-api-url.com/identify'
data = {'url': 'https://example.com/path/to/image.jpg'}
response = requests.post(url, data=data)
print(response.json())
```

## Response Format

The API returns a JSON object with the following structure:

```json
{
  "1. Plant Name": "Common name of the plant",
  "2. Scientific Name": "Scientific name of the plant",
  "3. Plant Type": "Type of plant (e.g., Herb, Shrub, Tree)",
  "4. Health Status": "Healthy or Unhealthy",
  "5. Key Characteristics": "Brief description of notable features",
  "6. Possible Issue": "Name of disease or problem (if unhealthy)",
  "7. Symptoms": "Visible signs of the issue (if unhealthy)",
  "8. Cause": "Likely reasons for the problem (if unhealthy)",
  "9. Treatment": "Simple steps to address the issue (if unhealthy)",
  "10. Sunlight Needs": "Sunlight requirements",
  "11. Watering": "Watering frequency and amount",
  "12. Soil Type": "Best soil for this plant",
  "13. Fertilizer Recommendations": [
    {
      "Fertilizer Name": "Name of recommended fertilizer",
      "NPK Ratio": "Ratio of Nitrogen, Phosphorus, and Potassium",
      "Application Frequency": "How often to apply",
      "Application Amount": "How much to use"
    },
    // ... (2-3 fertilizer recommendations)
  ]
}
```

Note: Fields 6-9 will only be present if the plant is identified as unhealthy.

## Deployment

This API is designed to be deployed on Render. Follow these steps:

1. Push your code to a GitHub repository
2. Create a new Web Service on Render
3. Connect your GitHub repository
4. Set the build command to: `pip install -r requirements.txt`
5. Set the start command to: `gunicorn app:app`
6. Add the environment variable: `GOOGLE_API_KEY` with your actual API key
7. Deploy the service

## Error Handling

The API returns JSON responses for errors:

- If no file is uploaded or URL is provided:
  ```json
  {"error": "No file uploaded or URL provided"}
  ```

- If there's an error processing the image or generating the response:
  ```json
  {"error": "Description of the error"}
  ```

For any other issues, please check the server logs on Render.