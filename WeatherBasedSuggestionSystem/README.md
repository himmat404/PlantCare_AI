# Plant Prediction API

This API predicts the top 5 most suitable plants to grow based on location data, including latitude, longitude, and elevation. It uses historical weather data, soil information, and machine learning to make these predictions.

## Features

- Fetches real-time soil data based on latitude and longitude
- Retrieves and analyzes historical weather data
- Uses machine learning to predict suitable plants
- Provides recommendations for the next 15 days

## Live API

The API is live and accessible at: https://plantcare-ai.onrender.com

## Prerequisites

- Python 3.7+
- pip (Python package installer)

## Installation

1. Clone the repository:
   ```
   https://github.com/himmat404/PlantCare_AI.git
   cd PlantCare_AI
   ```

2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

3. Ensure you have the following files in your project directory:
   - `app.py` (main API file)
   - `plants_data.csv` (dataset of plant information)

## Usage

1. If running locally, start the API server:
   ```
   python app.py
   ```

2. The server will start running on `http://0.0.0.0:10000` when run locally, or on the Render-provided URL when deployed.

3. To make a prediction, send a POST request to the `/predict` endpoint with the following JSON payload:

   ```json
   {
     "latitude": 40.7128,
     "longitude": -74.0060,
     "elevation": 10
   }
   ```

   You can use tools like cURL, Postman, or any programming language to make the request.

4. The API will respond with a JSON array containing the top 5 recommended plants:

   ```json
   [
     "Tomato",
     "Pepper",
     "Cucumber",
     "Lettuce",
     "Spinach"
   ]
   ```

## Deployment

This API is deployed on Render. To deploy your own instance:

1. Push your code to a GitHub repository.
2. Create a new Web Service on Render.
3. Connect your GitHub repository.
4. Use the following settings:
   - Environment: Python
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
5. Add any necessary environment variables.
6. Deploy the service.

## API Endpoints

### GET /

Returns a welcome message and basic instructions.

### POST /predict

Predicts the top 5 most suitable plants based on location data.

#### Request Body

| Parameter | Type   | Description                    |
|-----------|--------|--------------------------------|
| latitude  | float  | Latitude of the location       |
| longitude | float  | Longitude of the location      |
| elevation | float  | Elevation in meters            |

#### Response

An array of strings representing the top 5 recommended plants.

## Error Handling

The API will return appropriate error messages for:
- Missing required parameters
- Invalid parameter types
- Internal server errors

## Data Sources

- Soil data: ISRIC SoilGrids
- Weather data: Meteostat

## License

[MIT License](https://opensource.org/licenses/MIT)

## Contributing

Contributions, issues, and feature requests are welcome. Feel free to check issues page if you want to contribute.

## Contact

If you have any questions or concerns, please open an issue in the GitHub repository.