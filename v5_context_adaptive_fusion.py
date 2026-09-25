import requests

# ============================================================
# WEATHERFUSION-AWX
# V5 - CONTEXT-AWARE ADAPTIVE FUSION ENGINE
# ============================================================

print("=" * 70)
print("              WEATHERFUSION-AWX")
print("       V5 - CONTEXT-AWARE ADAPTIVE FUSION")
print("=" * 70)

# ------------------------------------------------------------
# LOCATION
# ------------------------------------------------------------

latitude = 26.2183
longitude = 78.1828

print("\nLOCATION")
print("-" * 70)
print(f"Latitude  : {latitude}")
print(f"Longitude : {longitude}")

# ------------------------------------------------------------
# LIVE WEATHER FORECAST
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
    "&hourly=temperature_2m,"
    "precipitation_probability,"
    "precipitation,"
    "wind_speed_10m"
    "&forecast_days=1"
)

print("\nCONNECTING TO LIVE WEATHER SOURCE...")
print("-" * 70)

try:
    response = requests.get(url, timeout=15)

    print(f"API HTTP Status : {response.status_code}")

    if response.status_code != 200:
        print("✗ API request failed.")
        print(response.text)
        exit()

    data = response.json()

    print("✓ Live weather data received")

except requests.exceptions.RequestException as error:
    print("✗ Connection failed")
    print(error)
    exit()

# ------------------------------------------------------------
# CURRENT CONDITIONS
# ------------------------------------------------------------

current = data["current"]

current_temperature = current["temperature_2m"]
current_humidity = current["relative_humidity_2m"]
current_precipitation = current["precipitation"]
current_weather_code = current["weather_code"]
current_wind = current["wind_speed_10m"]

print("\nCURRENT LIVE CONDITIONS")
print("-" * 70)

print(f"Temperature       : {current_temperature:.2f} °C")
print(f"Humidity          : {current_humidity:.2f} %")
print(f"Precipitation     : {current_precipitation:.2f} mm")
print(f"Weather Code      : {current_weather_code}")
print(f"Wind Speed        : {current_wind:.2f} km/h")

# ------------------------------------------------------------
# NEXT FORECAST POINT
# ------------------------------------------------------------

hourly = data["hourly"]

forecast_temperature = hourly["temperature_2m"][0]
forecast_rain_probability = hourly["precipitation_probability"][0]
forecast_precipitation = hourly["precipitation"][0]
forecast_wind = hourly["wind_speed_10m"][0]

print("\nLIVE FORECAST")
print("-" * 70)

print(f"Forecast Temperature      : {forecast_temperature:.2f} °C")
print(f"Rain Probability          : {forecast_rain_probability:.2f} %")
print(f"Forecast Precipitation    : {forecast_precipitation:.2f} mm")
print(f"Forecast Wind             : {forecast_wind:.2f} km/h")

# ------------------------------------------------------------
# WEATHER REGIME DETECTION
# ------------------------------------------------------------

print("\nWEATHER REGIME DETECTION")
print("-" * 70)

if forecast_rain_probability >= 70:
    weather_regime = "HEAVY RAIN / HIGH PRECIPITATION RISK"

elif forecast_rain_probability >= 40:
    weather_regime = "MODERATE RAIN RISK"

elif forecast_wind >= 30:
    weather_regime = "HIGH WIND CONDITION"

elif forecast_temperature >= 40:
    weather_regime = "HIGH TEMPERATURE"

else:
    weather_regime = "NORMAL WEATHER"

print(f"Detected Regime : {weather_regime}")

# ------------------------------------------------------------
# BASE SOURCE RELIABILITY
# ------------------------------------------------------------

# Source 1 and Source 2 are placeholders for two forecast
# sources in this prototype.

source_1_reliability = 0.70
source_2_reliability = 0.30

# ------------------------------------------------------------
# CONTEXT ADAPTATION
# ------------------------------------------------------------

if "RAIN" in weather_regime:

    source_1_reliability += 0.10
    source_2_reliability -= 0.10

elif "WIND" in weather_regime:

    source_1_reliability += 0.05
    source_2_reliability -= 0.05

elif "TEMPERATURE" in weather_regime:

    source_1_reliability += 0.05
    source_2_reliability -= 0.05

# Keep values inside valid range

source_1_reliability = max(0.0, min(1.0, source_1_reliability))
source_2_reliability = max(0.0, min(1.0, source_2_reliability))

# ------------------------------------------------------------
# NORMALIZE WEIGHTS
# ------------------------------------------------------------

total = source_1_reliability + source_2_reliability

weight_1 = source_1_reliability / total
weight_2 = source_2_reliability / total

# ------------------------------------------------------------
# SECOND SOURCE SIMULATION
# ------------------------------------------------------------

# Small variation is introduced to demonstrate fusion.

source_1_temperature = forecast_temperature
source_2_temperature = forecast_temperature + 0.8

source_1_precipitation = forecast_precipitation
source_2_precipitation = forecast_precipitation + 0.2

source_1_wind = forecast_wind
source_2_wind = forecast_wind + 1.5

# ------------------------------------------------------------
# FUSION
# ------------------------------------------------------------

fused_temperature = (
    source_1_temperature * weight_1
    + source_2_temperature * weight_2
)

fused_precipitation = (
    source_1_precipitation * weight_1
    + source_2_precipitation * weight_2
)

fused_wind = (
    source_1_wind * weight_1
    + source_2_wind * weight_2
)

# ------------------------------------------------------------
# DISPLAY ADAPTIVE WEIGHTS
# ------------------------------------------------------------

print("\nADAPTIVE WEIGHTING")
print("-" * 70)

print(f"Source 1 Reliability : {source_1_reliability * 100:.2f}%")
print(f"Source 2 Reliability : {source_2_reliability * 100:.2f}%")

print()

print(f"Source 1 Weight      : {weight_1 * 100:.2f}%")
print(f"Source 2 Weight      : {weight_2 * 100:.2f}%")

# ------------------------------------------------------------
# FINAL FUSED FORECAST
# ------------------------------------------------------------

print("\nFINAL FUSED FORECAST")
print("-" * 70)

print(f"Temperature   : {fused_temperature:.2f} °C")
print(f"Precipitation : {fused_precipitation:.2f} mm")
print(f"Wind Speed    : {fused_wind:.2f} km/h")

# ------------------------------------------------------------
# CONFIDENCE
# ------------------------------------------------------------

confidence = max(weight_1, weight_2) * 100

print("\nFORECAST CONFIDENCE")
print("-" * 70)

print(f"Fusion Confidence : {confidence:.2f}%")

# ------------------------------------------------------------
# SYSTEM STATUS
# ------------------------------------------------------------

print("\nSYSTEM STATUS")
print("-" * 70)

print("Live Data Collection       : ACTIVE")
print("Weather Regime Detection  : ACTIVE")
print("Context Adaptation         : ACTIVE")
print("Adaptive Weighting        : ACTIVE")
print("Forecast Fusion           : ACTIVE")
print("Confidence Estimation     : ACTIVE")

print("\n" + "=" * 70)
print("       ✓ WEATHERFUSION-AWX V5 COMPLETE")
print("=" * 70)