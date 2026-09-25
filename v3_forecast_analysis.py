import requests


# ============================================================
# WEATHERFUSION-AWX
# V3 - FORECAST COMPARISON & ERROR ANALYSIS
# ============================================================

print("=" * 70)
print("              WEATHERFUSION-AWX")
print("       V3 - FORECAST ANALYSIS ENGINE")
print("=" * 70)


# ------------------------------------------------------------
# LOCATION
# ------------------------------------------------------------

latitude = 26.2183
longitude = 78.1828


# ------------------------------------------------------------
# FORECAST SOURCE 1
# ------------------------------------------------------------

url_1 = (
    "https://api.open-meteo.com/v1/forecast"
    f"?latitude={latitude}"
    f"&longitude={longitude}"
    "&hourly=temperature_2m,"
    "precipitation_probability,"
    "precipitation,"
    "wind_speed_10m"
    "&forecast_days=1"
)


# ------------------------------------------------------------
# FORECAST SOURCE 2
# ------------------------------------------------------------

url_2 = (
    "https://api.open-meteo.com/v1/forecast"
    f"?latitude={latitude}"
    f"&longitude={longitude}"
    "&hourly=temperature_2m,"
    "precipitation_probability,"
    "precipitation,"
    "wind_speed_10m"
    "&forecast_days=1"
    "&temperature_unit=fahrenheit"
)


# ------------------------------------------------------------
# GET DATA
# ------------------------------------------------------------

def get_data(url):

    response = requests.get(url, timeout=15)

    if response.status_code == 200:
        return response.json()

    return None


print("\nCollecting forecast data...")

data_1 = get_data(url_1)
data_2 = get_data(url_2)


# ------------------------------------------------------------
# CHECK CONNECTION
# ------------------------------------------------------------

if data_1 is None or data_2 is None:

    print("\n✗ Forecast collection failed.")

    exit()


print("✓ Both forecast sources collected successfully")


# ------------------------------------------------------------
# EXTRACT DATA
# ------------------------------------------------------------

source_1 = data_1["hourly"]
source_2 = data_2["hourly"]


# First forecast point

temp_1 = source_1["temperature_2m"][0]

rain_prob_1 = source_1["precipitation_probability"][0]

rain_1 = source_1["precipitation"][0]

wind_1 = source_1["wind_speed_10m"][0]


# Source 2 temperature is Fahrenheit

temp_2_f = source_2["temperature_2m"][0]

temp_2 = (temp_2_f - 32) * 5 / 9

rain_prob_2 = source_2["precipitation_probability"][0]

rain_2 = source_2["precipitation"][0]

wind_2 = source_2["wind_speed_10m"][0]


# ------------------------------------------------------------
# DIFFERENCE CALCULATIONS
# ------------------------------------------------------------

temperature_difference = abs(temp_1 - temp_2)

rain_probability_difference = abs(
    rain_prob_1 - rain_prob_2
)

precipitation_difference = abs(
    rain_1 - rain_2
)

wind_difference = abs(
    wind_1 - wind_2
)


# ------------------------------------------------------------
# DISPLAY SOURCE DATA
# ------------------------------------------------------------

print("\n")
print("=" * 70)
print("                    SOURCE DATA")
print("=" * 70)


print("\nSOURCE 1")
print("-" * 70)

print(f"Temperature       : {temp_1:.2f} °C")
print(f"Rain Probability  : {rain_prob_1:.2f} %")
print(f"Precipitation     : {rain_1:.2f} mm")
print(f"Wind Speed        : {wind_1:.2f} km/h")


print("\nSOURCE 2")
print("-" * 70)

print(f"Temperature       : {temp_2:.2f} °C")
print(f"Rain Probability  : {rain_prob_2:.2f} %")
print(f"Precipitation     : {rain_2:.2f} mm")
print(f"Wind Speed        : {wind_2:.2f} km/h")


# ------------------------------------------------------------
# DIFFERENCE ANALYSIS
# ------------------------------------------------------------

print("\n")
print("=" * 70)
print("                 DISAGREEMENT ANALYSIS")
print("=" * 70)


print(
    f"\nTemperature Difference      : "
    f"{temperature_difference:.2f} °C"
)

print(
    f"Rain Probability Difference : "
    f"{rain_probability_difference:.2f} %"
)

print(
    f"Precipitation Difference     : "
    f"{precipitation_difference:.2f} mm"
)

print(
    f"Wind Speed Difference        : "
    f"{wind_difference:.2f} km/h"
)


# ------------------------------------------------------------
# AGREEMENT SCORE
# ------------------------------------------------------------

# Normalize temperature difference

temperature_score = max(
    0,
    100 - (temperature_difference * 10)
)


# Normalize rain probability difference

rain_score = max(
    0,
    100 - rain_probability_difference
)


# Normalize precipitation difference

precipitation_score = max(
    0,
    100 - (precipitation_difference * 20)
)


# Normalize wind difference

wind_score = max(
    0,
    100 - (wind_difference * 5)
)


# Overall agreement

agreement_score = (
    temperature_score
    + rain_score
    + precipitation_score
    + wind_score
) / 4


# ------------------------------------------------------------
# DISPLAY AGREEMENT
# ------------------------------------------------------------

print("\n")
print("=" * 70)
print("                 FORECAST AGREEMENT")
print("=" * 70)


print(
    f"\nTemperature Agreement : "
    f"{temperature_score:.2f}%"
)

print(
    f"Rain Agreement        : "
    f"{rain_score:.2f}%"
)

print(
    f"Precipitation Agree.  : "
    f"{precipitation_score:.2f}%"
)

print(
    f"Wind Agreement        : "
    f"{wind_score:.2f}%"
)

print(
    f"\nOverall Agreement     : "
    f"{agreement_score:.2f}%"
)


# ------------------------------------------------------------
# SYSTEM STATUS
# ------------------------------------------------------------

print("\n")
print("=" * 70)
print("                  SYSTEM STATUS")
print("=" * 70)

print("\nMulti-source collection : ACTIVE")
print("Forecast comparison     : ACTIVE")
print("Disagreement analysis   : ACTIVE")
print("Agreement scoring       : ACTIVE")
print("Adaptive weighting      : NEXT VERSION")
print("Forecast fusion         : NEXT VERSION")

print("\n✓ WEATHERFUSION-AWX V3 COMPLETE")

print("=" * 70)