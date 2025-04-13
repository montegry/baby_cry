import requests

def get_coordinates(city):
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": city, "format": "json"}
    response = requests.get(url, params=params)
    data = response.json()
    if data:
        return float(data[0]["lat"]), float(data[0]["lon"])
    return None, None

def get_weather_data(city):
    lat, lon = get_coordinates(city)
    if lat is None or lon is None:
        return {"temperature": None, "pressure": None}

    url = f"https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current_weather": True,
        "hourly": "pressure_msl",
        "timezone": "auto"
    }

    response = requests.get(url, params=params)
    data = response.json()

    temperature = data.get("current_weather", {}).get("temperature")
    pressure = data.get("hourly", {}).get("pressure_msl", [None])[0]

    return {
        "temperature": temperature,
        "pressure": pressure
    }
