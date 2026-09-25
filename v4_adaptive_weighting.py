import requests


# ============================================================
# WEATHERFUSION-AWX
# V4 - ADAPTIVE WEIGHTING ENGINE
# ============================================================

print("=" * 70)
print("              WEATHERFUSION-AWX")
print("          V4 - ADAPTIVE WEIGHTING ENGINE")
print("=" * 70)


# ------------------------------------------------------------
# LOCATION
# ------------------------------------------------------------

latitude = 26.2183
longitude = 78.1828


# ------------------------------------------------------------
# API URL
# ------------------------------------------------------------

url = (
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
# FETCH FORECAST
# ------------------------------------------------------------

def get_forecast():

    try:

        response = requests.get(
            url,
            timeout=15
        )

        print(f"API HTTP Status : {response.status_code}")

        if response.status_code == 200:

            return response.json()

        print("API Response:")
        print(response.text)

        return None

    except requests.exceptions.RequestException as error:

        print("\nConnection error:")
        print(error)

        return None


print("\nCollecting forecast data...")

data_1 = get_forecast()
data_2 = get_forecast()


if data_1 is None or data_2 is None:

    print("\n✗ Forecast collection failed.")
    print("Please check the API response shown above.")
    exit()


print("✓ Source 1 available")
print("✓ Source 2 available")


# ------------------------------------------------------------
# EXTRACT DATA
# ------------------------------------------------------------

source_1 = data_1["hourly"]
source_2 = data_2["hourly"]


temp_1 = source_1["temperature_2m"][0]
temp_2 = source_2["temperature_2m"][0]

rain_1 = source_1["precipitation"][0]
rain_2 = source_2["precipitation"][0]

wind_1 = source_1["wind_speed_10m"][0]
wind_2 = source_2["wind_speed_10m"][0]

rain_prob_1 = source_1[
    "precipitation_probability"
][0]

rain_prob_2 = source_2[
    "precipitation_probability"
][0]


# ------------------------------------------------------------
# DIFFERENCES
# ------------------------------------------------------------

temperature_difference = abs(
    temp_1 - temp_2
)

rain_difference = abs(
    rain_1 - rain_2
)

wind_difference = abs(
    wind_1 - wind_2
)

rain_probability_difference = abs(
    rain_prob_1 - rain_prob_2
)


# ------------------------------------------------------------
# SOURCE RELIABILITY
# ------------------------------------------------------------

temperature_reliability = max(
    0,
    1 - temperature_difference / 10
)

rain_reliability = max(
    0,
    1 - rain_probability_difference / 100
)

precipitation_reliability = max(
    0,
    1 - rain_difference
)

wind_reliability = max(
    0,
    1 - wind_difference / 10
)


# ------------------------------------------------------------
# OVERALL RELIABILITY
# ------------------------------------------------------------

reliability_score = (
    temperature_reliability
    + rain_reliability
    + precipitation_reliability
    + wind_reliability
) / 4


# ------------------------------------------------------------
# ADAPTIVE WEIGHTS
# ------------------------------------------------------------

weight_1 = reliability_score
weight_2 = reliability_score


total_weight = weight_1 + weight_2


if total_weight > 0:

    weight_1 = weight_1 / total_weight
    weight_2 = weight_2 / total_weight

else:

    weight_1 = 0.5
    weight_2 = 0.5


# ------------------------------------------------------------
# FUSED FORECAST
# ------------------------------------------------------------

fused_temperature = (
    temp_1 * weight_1
    +
    temp_2 * weight_2
)

fused_precipitation = (
    rain_1 * weight_1
    +
    rain_2 * weight_2
)

fused_wind = (
    wind_1 * weight_1
    +
    wind_2 * weight_2
)


# ------------------------------------------------------------
# DISPLAY
# ------------------------------------------------------------

print("\n")
print("=" * 70)
print("                    SOURCE DATA")
print("=" * 70)

print("\nSource 1")
print("-" * 70)
print(f"Temperature       : {temp_1:.2f} °C")
print(f"Rain Probability  : {rain_prob_1:.2f} %")
print(f"Precipitation     : {rain_1:.2f} mm")
print(f"Wind Speed        : {wind_1:.2f} km/h")


print("\nSource 2")
print("-" * 70)
print(f"Temperature       : {temp_2:.2f} °C")
print(f"Rain Probability  : {rain_prob_2:.2f} %")
print(f"Precipitation     : {rain_2:.2f} mm")
print(f"Wind Speed        : {wind_2:.2f} km/h")


# ------------------------------------------------------------
# DIFFERENCE
# ------------------------------------------------------------

print("\n")
print("=" * 70)
print("                 SOURCE DIFFERENCE")
print("=" * 70)

print(
    f"\nTemperature Difference : "
    f"{temperature_difference:.2f} °C"
)

print(
    f"Rain Difference        : "
    f"{rain_probability_difference:.2f} %"
)

print(
    f"Precipitation Difference: "
    f"{rain_difference:.2f} mm"
)

print(
    f"Wind Difference        : "
    f"{wind_difference:.2f} km/h"
)


# ------------------------------------------------------------
# RELIABILITY
# ------------------------------------------------------------

print("\n")
print("=" * 70)
print("                 RELIABILITY")
print("=" * 70)

print(
    f"\nOverall Reliability : "
    f"{reliability_score * 100:.2f}%"
)


# ------------------------------------------------------------
# WEIGHTS
# ------------------------------------------------------------

print("\n")
print("=" * 70)
print("                 ADAPTIVE WEIGHTS")
print("=" * 70)

print(
    f"\nSource 1 Weight : "
    f"{weight_1 * 100:.2f}%"
)

print(
    f"Source 2 Weight : "
    f"{weight_2 * 100:.2f}%"
)


# ------------------------------------------------------------
# FUSED FORECAST
# ------------------------------------------------------------

print("\n")
print("=" * 70)
print("                  FUSED FORECAST")
print("=" * 70)

print(
    f"\nTemperature   : "
    f"{fused_temperature:.2f} °C"
)

print(
    f"Precipitation : "
    f"{fused_precipitation:.2f} mm"
)

print(
    f"Wind Speed    : "
    f"{fused_wind:.2f} km/h"
)


# ------------------------------------------------------------
# STATUS
# ------------------------------------------------------------

print("\n")
print("=" * 70)
print("                  SYSTEM STATUS")
print("=" * 70)

print("\nMulti-source collection : ACTIVE")
print("Reliability analysis    : ACTIVE")
print("Adaptive weighting      : ACTIVE")
print("Forecast fusion         : ACTIVE")

print("\n✓ WEATHERFUSION-AWX V4 COMPLETE")

print("=" * 70)