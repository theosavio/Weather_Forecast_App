from flask import Flask, request, render_template
import requests
import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
import io
import base64
import os

# Flask app setup
app = Flask(__name__, 
            template_folder=os.path.join(os.path.dirname(__file__), '..', 'frontend'),  # Adjust to point to frontend folder
            static_folder=os.path.join(os.path.dirname(__file__), '..', 'frontend'))  # Adjust static folder to frontend

# Your WeatherAPI key
API_KEY = "cece4523694c407ab16165549241012"
BASE_URL = "http://api.weatherapi.com/v1/"

# Fetch current weather data
def get_current_weather(city):
    endpoint = f"{BASE_URL}current.json"
    params = {"key": API_KEY, "q": city}
    response = requests.get(endpoint, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        return None

# Generate temperature trend plot
def plot_forecast(forecast):
    dates = [day['date'] for day in forecast['forecast']['forecastday']]
    max_temps = [day['day']['maxtemp_c'] for day in forecast['forecast']['forecastday']]
    min_temps = [day['day']['mintemp_c'] for day in forecast['forecast']['forecastday']]

    plt.figure(figsize=(8, 4))
    plt.plot(dates, max_temps, marker='o', label='Max Temp')
    plt.plot(dates, min_temps, marker='o', label='Min Temp', linestyle='--')
    plt.xlabel('Date')
    plt.ylabel('Temperature (°C)')
    plt.title('Temperature Trends')
    plt.legend()
    plt.grid(True)

    # Convert plot to PNG image
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plt.close()
    return base64.b64encode(img.getvalue()).decode('utf-8')

# Fetch forecast data for the next 3 days
def get_forecast(city, days=3):
    endpoint = f"{BASE_URL}forecast.json"
    params = {"key": API_KEY, "q": city, "days": days}
    response = requests.get(endpoint, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        return None

# Flask route for handling requests
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        city = request.form.get('city')

        # Fetch current weather
        current_weather = get_current_weather(city)
        if not current_weather:
            return render_template('index.html', error="Unable to fetch weather data. Please try again.")

        # Fetch forecast (next 3 days)
        forecast = get_forecast(city, days=3)
        if not forecast:
            return render_template('index.html', error="Unable to fetch forecast data. Please try again.")

        # Generate weather details and plot
        weather_details = {
            "city": current_weather['location']['name'],
            "country": current_weather['location']['country'],
            "temperature": f"{current_weather['current']['temp_c']}°C",
            "condition": current_weather['current']['condition']['text'],
            "humidity": f"{current_weather['current']['humidity']}%",
            "wind": f"{current_weather['current']['wind_kph']} kph",
        }

        temp_chart = plot_forecast(forecast)

        return render_template('index.html', weather=weather_details, chart=temp_chart)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
