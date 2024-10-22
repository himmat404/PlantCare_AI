from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder, LabelEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from xgboost import XGBClassifier
import joblib
from datetime import datetime, timedelta
from statsmodels.tsa.seasonal import seasonal_decompose
from meteostat import Point, Daily
from collections import Counter
import requests

def fetch_soil_data(latitude, longitude):
    url = f"https://rest.isric.org/soilgrids/v2.0/properties/query?lat={latitude}&lon={longitude}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            clay_content = data['properties']['layers'][3]['depths'][0]['values']['mean']
            ph_value = data['properties']['layers'][7]['depths'][0]['values']['mean']
            
            soil_type = 'Sandy' if clay_content < 200 else 'Loamy' if 200 <= clay_content < 300 else 'Clayey'
            soil_ph = ph_value / 10 if ph_value is not None else 6.5
            
            return soil_type, soil_ph
    except Exception:
        pass
    
    return 'Loamy', 6.5

def fetch_weather_data(location, end_date):
    latitude, longitude, elevation = location
    start_date = end_date - timedelta(days=365*5)
    location_point = Point(latitude, longitude, elevation)
    
    weather_data = Daily(location_point, start_date, end_date)
    weather_data = weather_data.fetch()

    weather_df = weather_data[['tavg', 'prcp', 'wspd']].reset_index()
    weather_df.rename(columns={'time': 'time', 'tavg': 'temperature', 'prcp': 'precipitation', 'wspd': 'wind_speed'}, inplace=True)

    weather_df['temperature'] = weather_df['temperature'].fillna(weather_df['temperature'].mean())
    weather_df['precipitation'] = weather_df['precipitation'].fillna(0)
    weather_df['wind_speed'] = weather_df['wind_speed'].fillna(weather_df['wind_speed'].mean())

    return weather_df

def augment_data(X, y, n_samples=5):
    X_augmented = []
    y_augmented = []
    
    for class_label in np.unique(y):
        class_samples = X[y == class_label]
        n_orig_samples = len(class_samples)
        
        for _ in range(n_samples):
            new_samples = class_samples.copy()
            noise = np.random.normal(0, 0.1, new_samples.shape)
            new_samples.iloc[:, :5] += noise[:, :5]
            
            X_augmented.append(new_samples)
            y_augmented.extend([class_label] * n_orig_samples)
    
    return pd.concat(X_augmented), np.array(y_augmented)

def determine_sunlight(wind_speed):
    if wind_speed < 2:
        return 'Full Sun'
    elif wind_speed < 5:
        return 'Partial Shade'
    else:
        return 'Full Shade'

def train_plant_model(data_file):
    data = pd.read_csv(data_file)

    required_columns = ['Min Temp (°C)', 'Max Temp (°C)', 'Min Rainfall (mm/month)', 
                        'Max Rainfall (mm/month)', 'Preferred Soil pH', 
                        'Soil Type', 'Sunlight Requirement', 'Growing Season', 'Plant Name']
    for col in required_columns:
        if col not in data.columns:
            raise ValueError(f"Missing column in data: {col}")

    features = ['Min Temp (°C)', 'Max Temp (°C)', 'Min Rainfall (mm/month)', 
                'Max Rainfall (mm/month)', 'Preferred Soil pH', 
                'Soil Type', 'Sunlight Requirement', 'Growing Season']
    
    X = data[features]
    y = data['Plant Name']

    le = LabelEncoder()
    y_encoded = le.fit_transform(y)

    X_augmented, y_augmented = augment_data(X, y_encoded, n_samples=5)

    X_train, X_test, y_train, y_test = train_test_split(X_augmented, y_augmented, test_size=0.2, random_state=42, stratify=y_augmented)

    numeric_features = ['Min Temp (°C)', 'Max Temp (°C)', 
                        'Min Rainfall (mm/month)', 'Max Rainfall (mm/month)', 
                        'Preferred Soil pH']
    data[numeric_features] = data[numeric_features].astype(float)

    categorical_features = ['Soil Type', 'Sunlight Requirement', 'Growing Season']

    numeric_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ])

    categorical_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='constant', fill_value='missing')),
        ('onehot', OneHotEncoder(handle_unknown='ignore'))
    ])

    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, numeric_features),
            ('cat', categorical_transformer, categorical_features)
        ])

    model = Pipeline([
        ('preprocessor', preprocessor),
        ('classifier', XGBClassifier(n_estimators=100, learning_rate=0.1, objective='multi:softprob'))
    ])

    model.fit(X_train, y_train)

    joblib.dump(model, 'plant_prediction_model.joblib')
    joblib.dump(le, 'label_encoder.joblib')

    return model, le

def perform_time_series_analysis(historical_data):
    historical_data['time'] = pd.to_datetime(historical_data['time'])
    ts = historical_data.set_index('time')['temperature']
    result = seasonal_decompose(ts, model='additive', period=365)
    forecast = ts.rolling(window=30).mean()
    last_date = ts.index[-1]
    date_range = pd.date_range(start=last_date + timedelta(days=1), periods=15)
    forecast_df = pd.DataFrame({'ds': date_range, 'yhat': np.nan})

    for i in range(len(date_range)):
        if i < len(forecast):
            forecast_df.at[i, 'yhat'] = forecast.iloc[-len(date_range) + i]

    forecast_df['yhat'] = forecast_df['yhat'].interpolate(method='linear')

    if forecast_df['yhat'].isnull().any():
        forecast_df['yhat'].fillna(ts.mean(), inplace=True)

    return forecast_df

def predict_plants(model, le, weather_data, soil_ph, soil_type, sunlight):
    min_temp = float(weather_data['temp_min'])
    max_temp = float(weather_data['temp_max'])
    rainfall = float(weather_data['rain']) * 30
    soil_ph = float(soil_ph)
    sunlight = str(sunlight)
    soil_type = str(soil_type)
    growing_season = determine_season(weather_data['date'])

    input_data = pd.DataFrame({
        'Min Temp (°C)': [min_temp],
        'Max Temp (°C)': [max_temp],
        'Min Rainfall (mm/month)': [rainfall],
        'Max Rainfall (mm/month)': [rainfall],
        'Preferred Soil pH': [soil_ph],
        'Soil Type': [soil_type],
        'Sunlight Requirement': [sunlight],
        'Growing Season': [growing_season]
    })

    numeric_columns = ['Min Temp (°C)', 'Max Temp (°C)', 'Min Rainfall (mm/month)', 
                       'Max Rainfall (mm/month)', 'Preferred Soil pH']
    input_data[numeric_columns] = input_data[numeric_columns].astype(float)

    try:
        probabilities = model.predict_proba(input_data)[0]
        top_5_indices = np.argsort(probabilities)[-5:][::-1]
        top_5_plants = le.inverse_transform(top_5_indices)
        return top_5_plants.tolist()
    except Exception:
        return []

def determine_season(date):
    month = date.month
    if 3 <= month <= 5:
        return 'Spring'
    elif 6 <= month <= 8:
        return 'Summer'
    elif 9 <= month <= 11:
        return 'Fall'
    else:
        return 'Winter'

app = Flask(__name__)

@app.route('/')
def home():
    return "Welcome to the Plant Prediction API. Use the /predict endpoint to get plant recommendations."

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    latitude = float(data['latitude'])
    longitude = float(data['longitude'])
    elevation = float(data['elevation'])
    
    location = (latitude, longitude, elevation)
    end_date = datetime.now()
    plants_data_file = 'plants_data.csv'

    soil_type, soil_ph = fetch_soil_data(latitude, longitude)
    historical_data = fetch_weather_data(location, end_date)
    model, le = train_plant_model(plants_data_file)
    seasonal_forecast = perform_time_series_analysis(historical_data)

    today = datetime.now()
    all_recommendations = []
    for i in range(15):
        forecast_date = today + timedelta(days=i)
        forecast_temp = seasonal_forecast.loc[seasonal_forecast['ds'].dt.date == forecast_date.date(), 'yhat'].mean()
        
        if pd.isna(forecast_temp):
            forecast_temp = historical_data['temperature'].mean()

        forecast_wind = historical_data['wind_speed'].mean()
        sunlight = determine_sunlight(forecast_wind)

        weather_data = {
            'date': forecast_date,
            'temp_min': forecast_temp - 5,
            'temp_max': forecast_temp + 5,
            'rain': historical_data.loc[pd.to_datetime(historical_data['time']).dt.month == forecast_date.month, 'precipitation'].mean()
        }
        recommendations = predict_plants(model, le, weather_data, soil_ph, soil_type, sunlight)
        all_recommendations.extend(recommendations)

    plant_counts = Counter(all_recommendations)
    top_5_plants = plant_counts.most_common(5)

    return jsonify([plant for plant, _ in top_5_plants])

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)