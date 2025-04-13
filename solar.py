import requests
from datetime import datetime, timezone

def get_solar_activity():
    try:
        url = "https://services.swpc.noaa.gov/json/planetary_k_index_1m.json"
        response = requests.get(url)
        data = response.json()

        # Возьмем последнее значение, ближайшее к текущему времени
        now = datetime.now(timezone.utc)

        latest = max(
            data,
            key=lambda x: abs(datetime.fromisoformat(x["time_tag"].replace("Z", "+00:00")) - now)
        )

        return latest.get("k_index", None)
    except Exception as e:
        print("Ошибка при получении солнечной активности:", e)
        return None
