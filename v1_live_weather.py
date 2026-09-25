import requests
from datetime import datetime


# ============================================================
# WEATHERFUSION-AWX
# V1 - LIVE WEATHER DATA COLLECTOR
# ============================================================

print("=" * 65)
print("        WEATHERFUSION-AWX")
print("     V1 - LIVE WEATHER DATA COLLECTOR")
print("=" * 65)


# ------------------------------------------------------------
# LOCATION
# ------------------------------------------------------------

latitude = 26.2183
longitude = 78.1828

print("\nLocation")
print("-" * 65)
print(f"Latitude  : {latitude}")
print(f"Longitude : {longitude}")


# ------------------------------------------------------------
# WEATHER API
# ------------------------------------------------------------

url = (
    "https://api.open-meteo.com/v1/forecast"
    f"?latitude={latitude}"
    f"&longitude={longitude}"
    "&current=temperature_2m,"
    "relative_humidity_2m,"
    "precipitation,"
    "weather_code,"
    "wind_speed_10m"
)


print("\nConnecting to live weather API...")

try:

    response = requests.get(url, timeout=10)

    if response.status_code == 200:

        data = response.json()

        print("✓ API connection successful")

        # ----------------------------------------------------
        # CURRENT WEATHER
        # ----------------------------------------------------

        current = data["current"]

        temperature = current["temperature_2m"]
        humidity = current["relative_humidity_2m"]
        precipitation = current["precipitation"]
        weather_code = current["weather_code"]
        wind_speed = current["wind_speed_10m"]

        timestamp = current["time"]

        # ----------------------------------------------------
        # DISPLAY DATA
        # ----------------------------------------------------

        print("\nLIVE WEATHER DATA")
        print("-" * 65)

        print(f"Time                 : {timestamp}")
        print(f"Temperature          : {temperature} °C")
        print(f"Relative Humidity    : {humidity} %")
        print(f"Precipitation        : {precipitation} mm")
        print(f"Weather Code         : {weather_code}")
        print(f"Wind Speed           : {wind_speed} km/h")

        # ----------------------------------------------------
        # VERIFICATION
        # ----------------------------------------------------

        print("\nDATA VERIFICATION")
        print("-" * 65)

        print("API Status           : SUCCESS")
        print("Data Format          : JSON")
        print("Live Data            : YES")
        print("Collection Time      :", datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ))

        print("\n✓ WEATHERFUSION-AWX V1 COMPLETE")

    else:

        print("✗ API connection failed")
        print(f"HTTP Status Code : {response.status_code}")


except requests.exceptions.RequestException as error:

    print("✗ Connection error")
    print(error)


print("\n" + "=" * 65)