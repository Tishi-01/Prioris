import requests
from config import OWM_API_KEY


def get_city_if_rain_predicted(city_name):
    """Check if rain is predicted in next 24 hours (using OpenWeather FREE API v2.5)."""
    try:
        # latitude and longitude for the city
        geo_url = (
            f"http://api.openweathermap.org/geo/1.0/direct"
            f"?q={city_name}&limit=1&appid={OWM_API_KEY}"
        )
        geo_resp = requests.get(geo_url, timeout=8).json()
        if not geo_resp:
            print(f"⚠️ City not found: {city_name}")
            return False

        lat, lon = geo_resp[0]["lat"], geo_resp[0]["lon"]

        # 5-day / 3-hour forecast
        url = (
            f"http://api.openweathermap.org/data/2.5/forecast"
            f"?lat={lat}&lon={lon}&appid={OWM_API_KEY}&units=metric"
        )
        resp = requests.get(url, timeout=8).json()
        if "list" not in resp:
            print(f"⚠️ Weather data unavailable for {city_name}")
            return False

        # next 8 forecast entries (≈24 hours)
        for entry in resp["list"][:8]:
            weather_desc = entry["weather"][0]["main"].lower()
            rain_amt = entry.get("rain", {}).get("3h", 0)
            if "rain" in weather_desc or rain_amt > 20:
                print(f"🌧️ Rain predicted in {city_name}")
                return True

        print(f"☀️ No rain predicted in {city_name}")
        return False

    except Exception as e:
        print("Weather check failed:", e)
        return False
