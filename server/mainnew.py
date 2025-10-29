import requests
from datetime import datetime, timedelta

def fetch_weather(api_key):
    """
    Fetch the next day's weather forecast using OpenWeatherMap API.

    Parameters:
        api_key (str): Your OpenWeatherMap API key.

    Returns:
        str: Weather condition for the next day ("Clear", "Clouds", "Rain", etc.)
    """

    if not api_key:
        print("⚠️ Warning: No API key provided. Please add your OpenWeatherMap API key.")
        return "Clouds"  # Default fallback condition

    # ---- 1️⃣ Set your location ----
    # You can replace this with your location coordinates
    latitude = 12.9716    # Example: Bangalore
    longitude = 77.5946

    # ---- 2️⃣ Build API URL ----
    url = (
        f"https://api.openweathermap.org/data/2.5/forecast?"
        f"lat={latitude}&lon={longitude}&appid={api_key}&units=metric"
    )

    try:
        # ---- 3️⃣ Fetch data from OpenWeatherMap ----
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        # ---- 4️⃣ Determine tomorrow’s date ----
        tomorrow = datetime.utcnow() + timedelta(days=1)
        tomorrow_date = tomorrow.date()

        # ---- 5️⃣ Extract tomorrow's weather ----
        tomorrow_forecasts = [
            item for item in data["list"]
            if datetime.utcfromtimestamp(item["dt"]).date() == tomorrow_date
        ]

        if not tomorrow_forecasts:
            print("⚠️ No forecast data found for tomorrow.")
            return "Clouds"

        # ---- 6️⃣ Take the most common weather condition of tomorrow ----
        weather_conditions = [item["weather"][0]["main"] for item in tomorrow_forecasts]
        most_common_condition = max(set(weather_conditions), key=weather_conditions.count)

        print(f"✅ Tomorrow's predicted weather: {most_common_condition}")
        return most_common_condition

    except requests.exceptions.RequestException as e:
        print(f"❌ API request error: {e}")
        return "Clouds"
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return "Clouds"
