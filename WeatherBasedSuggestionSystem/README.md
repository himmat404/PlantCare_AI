# Plant Prediction API

This API predicts the top 5 most suitable plants to grow based on location data, including latitude, longitude, and elevation. It uses historical weather data, soil information, and machine learning to make these predictions.

## Features

- Fetches real-time soil data based on latitude and longitude
- Retrieves and analyzes historical weather data
- Uses machine learning to predict suitable plants
- Provides recommendations for the next 15 days

## Prerequisites

- Python 3.7+
- pip (Python package installer)

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/plant-prediction-api.git
   cd plant-prediction-api
   ```

2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

3. Ensure you have the following files in your project directory:
   - `plant_prediction_api.py` (main API file)
   - `plants_data.csv` (dataset of plant information)

## Usage

1. Start the API server:
   ```
   python plant_prediction_api.py
   ```

2. The server will start running on `http://0.0.0.0:10000`

3. To make a prediction, send a POST request to the `/predict_plants` endpoint with the following JSON payload:

   ```json
   {
     "latitude": 40.7128,
     "longitude": -74.0060,
     "elevation": 10
   }
   ```

   You can use tools like cURL, Postman, or any programming language to make the request.

4. The API will respond with a JSON object containing the predictions:

   ```json
   {
     "location": {
       "latitude": 40.7128,
       "longitude": -74.006,
       "elevation": 10
     },
     "soil_info": {
       "type": "Loamy",
       "ph": 6.5
     },
     "recommendations": [
       {
         "rank": 1,
         "plant": "Tomato",
         "frequency": 12
       },
       {
         "rank": 2,
         "plant": "Pepper",
         "frequency": 10
       },
       {
         "rank": 3,
         "plant": "Cucumber",
         "frequency": 8
       },
       {
         "rank": 4,
         "plant": "Lettuce",
         "frequency": 7
       },
       {
         "rank": 5,
         "plant": "Spinach",
         "frequency": 6
       }
     ]
   }
   ```

## Deployment

This API is designed to be easily deployed on Render. To deploy:

1. Push your code to a GitHub repository.
2. Create a new Web Service on Render.
3. Connect your GitHub repository.
4. Use the following settings:
   - Environment: Python
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python plant_prediction_api.py`
5. Add any necessary environment variables.
6. Deploy the service.

## API Endpoints

### POST /predict_plants

Predicts the top 5 most suitable plants based on location data.

#### Request Body

| Parameter | Type   | Description                    |
|-----------|--------|--------------------------------|
| latitude  | float  | Latitude of the location       |
| longitude | float  | Longitude of the location      |
| elevation | float  | Elevation in meters            |

#### Response

| Field            | Type   | Description                               |
|------------------|--------|-------------------------------------------|
| location         | object | Contains input location data              |
| soil_info        | object | Contains soil type and pH                 |
| recommendations  | array  | List of top 5 recommended plants          |

Each recommendation in the array contains:
- rank: Position in the recommendation list
- plant: Name of the recommended plant
- frequency: How often this plant was recommended over the 15-day forecast

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
