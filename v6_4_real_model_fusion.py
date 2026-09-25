import requests
import time
from datetime import datetime


print("=" * 70)
print("              WEATHERFUSION-AWX")
print("       V6.4 - REAL MODEL FUSION ENGINE")
print("=" * 70)


# ============================================================
# LOCATION
# ============================================================

latitude = 26.2183
longitude = 78.1828

print("\nLOCATION")
print("-" * 70)
print(f"Latitude  : {latitude}")
print(f"Longitude : {longitude}")


# ============================================================
# VARIABLES
# ============================================================

variables = (
    "temperature_2m,"
    "precipitation_probability,"
    "precipitation,"
    "wind_speed_10m"
)


# ============================================================
# BUILD API URL
# ============================================================

def build_url(model):

    return (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={latitude}"
        f"&longitude={longitude}"
        f"&hourly={variables}"
        f"&models={model}"
        "&forecast_hours=24"
        "&timezone=auto"
    )


# ============================================================
# DOWNLOAD MODEL DATA
# ============================================================

def get_model(model, name, attempts=3):

    url = build_url(model)

    for attempt in range(1, attempts + 1):

        print(f"\nConnecting to {name}...")
        print("-" * 70)
        print(f"Attempt : {attempt}/{attempts}")

        try:

            response = requests.get(
                url,
                timeout=60
            )

            print(f"HTTP Status : {response.status_code}")

            if response.status_code == 200:

                print(f"✓ {name} data received")

                return response.json()

            else:

                print("API returned an error.")
                print(response.text[:300])

        except requests.exceptions.Timeout:

            print(f"⚠ {name} request timed out.")

        except requests.exceptions.RequestException as error:

            print("⚠ Connection error:")
            print(error)

        if attempt < attempts:

            print("Retrying in 3 seconds...")
            time.sleep(3)

    print(f"\n✗ Could not retrieve {name}")

    return None


# ============================================================
# COLLECT REAL MODELS
# ============================================================

ecmwf_data = get_model(
    "ecmwf_ifs025",
    "ECMWF IFS HRES"
)

aifs_data = get_model(
    "ecmwf_aifs025",
    "ECMWF AIFS"
)


# ============================================================
# SOURCE STATUS
# ============================================================

print("\n")
print("=" * 70)
print("                 SOURCE STATUS")
print("=" * 70)

print(
    "\nECMWF IFS HRES : "
    + ("AVAILABLE" if ecmwf_data else "UNAVAILABLE")
)

print(
    "ECMWF AIFS     : "
    + ("AVAILABLE" if aifs_data else "UNAVAILABLE")
)


if ecmwf_data is None or aifs_data is None:

    print("\n✗ Real model fusion cannot continue.")

    print("No simulated values will be created.")

    exit()


# ============================================================
# EXTRACT HOURLY DATA
# ============================================================

ecmwf = ecmwf_data["hourly"]
aifs = aifs_data["hourly"]

ecmwf_times = ecmwf["time"]
aifs_times = aifs["time"]


# ============================================================
# FIND FIRST VALID FORECAST POINT
# ============================================================

def find_valid_point(data, times):

    temperature = data["temperature_2m"]

    for index, value in enumerate(temperature):

        if value is not None:

            return index

    return None


ifs_index = find_valid_point(
    ecmwf,
    ecmwf_times
)

aifs_index = find_valid_point(
    aifs,
    aifs_times
)


# ============================================================
# VALIDATION
# ============================================================

if ifs_index is None:

    print("\n✗ ECMWF IFS HRES has no valid temperature data.")

    exit()


if aifs_index is None:

    print("\n✗ ECMWF AIFS has no valid temperature data.")

    exit()


# ============================================================
# SELECTED FORECAST TIMES
# ============================================================

ifs_time = ecmwf_times[ifs_index]

aifs_time = aifs_times[aifs_index]


print("\n")
print("=" * 70)
print("             FORECAST TIME ALIGNMENT")
print("=" * 70)

print(f"\nIFS Forecast Time  : {ifs_time}")
print(f"AIFS Forecast Time : {aifs_time}")


# ============================================================
# CALCULATE TIME DIFFERENCE
# ============================================================

try:

    ifs_datetime = datetime.fromisoformat(
        ifs_time
    )

    aifs_datetime = datetime.fromisoformat(
        aifs_time
    )

    time_difference = abs(
        (ifs_datetime - aifs_datetime).total_seconds()
    )

    print(
        f"Time Difference    : "
        f"{time_difference / 3600:.1f} hours"
    )

except ValueError:

    time_difference = None

    print("Time Difference    : Could not calculate")


print("\n✓ Both models contain valid forecast data")


# ============================================================
# SAFE VALUE FUNCTION
# ============================================================

def get_value(data, variable, index):

    value = data[variable][index]

    if value is None:

        return None

    return float(value)


# ============================================================
# IFS VALUES
# ============================================================

ifs_temp = get_value(
    ecmwf,
    "temperature_2m",
    ifs_index
)

ifs_rain_probability = get_value(
    ecmwf,
    "precipitation_probability",
    ifs_index
)

ifs_precipitation = get_value(
    ecmwf,
    "precipitation",
    ifs_index
)

ifs_wind = get_value(
    ecmwf,
    "wind_speed_10m",
    ifs_index
)


# ============================================================
# AIFS VALUES
# ============================================================

aifs_temp = get_value(
    aifs,
    "temperature_2m",
    aifs_index
)

aifs_rain_probability = get_value(
    aifs,
    "precipitation_probability",
    aifs_index
)

aifs_precipitation = get_value(
    aifs,
    "precipitation",
    aifs_index
)

aifs_wind = get_value(
    aifs,
    "wind_speed_10m",
    aifs_index
)


# ============================================================
# CHECK REQUIRED VALUES
# ============================================================

values = [

    ifs_temp,
    ifs_rain_probability,
    ifs_precipitation,
    ifs_wind,

    aifs_temp,
    aifs_rain_probability,
    aifs_precipitation,
    aifs_wind

]


if any(value is None for value in values):

    print("\n✗ One or more required values are missing.")

    print("Fusion stopped to prevent invalid results.")

    exit()


# ============================================================
# DISPLAY REAL MODEL DATA
# ============================================================

print("\n")
print("=" * 70)
print("                 REAL MODEL DATA")
print("=" * 70)


print("\nECMWF IFS HRES")
print("-" * 70)

print(f"Temperature       : {ifs_temp:.2f} °C")
print(f"Rain Probability  : {ifs_rain_probability:.2f} %")
print(f"Precipitation     : {ifs_precipitation:.2f} mm")
print(f"Wind Speed        : {ifs_wind:.2f} km/h")


print("\nECMWF AIFS")
print("-" * 70)

print(f"Temperature       : {aifs_temp:.2f} °C")
print(f"Rain Probability  : {aifs_rain_probability:.2f} %")
print(f"Precipitation     : {aifs_precipitation:.2f} mm")
print(f"Wind Speed        : {aifs_wind:.2f} km/h")


# ============================================================
# MODEL DISAGREEMENT
# ============================================================

temperature_difference = abs(
    ifs_temp - aifs_temp
)

rain_probability_difference = abs(
    ifs_rain_probability -
    aifs_rain_probability
)

precipitation_difference = abs(
    ifs_precipitation -
    aifs_precipitation
)

wind_difference = abs(
    ifs_wind -
    aifs_wind
)


print("\n")
print("=" * 70)
print("              MODEL DISAGREEMENT")
print("=" * 70)

print(
    f"\nTemperature Difference    : "
    f"{temperature_difference:.2f} °C"
)

print(
    f"Rain Probability Difference : "
    f"{rain_probability_difference:.2f} %"
)

print(
    f"Precipitation Difference   : "
    f"{precipitation_difference:.2f} mm"
)

print(
    f"Wind Difference            : "
    f"{wind_difference:.2f} km/h"
)


# ============================================================
# AGREEMENT SCORE
# ============================================================

temperature_score = max(
    0,
    1 - temperature_difference / 10
)

rain_score = max(
    0,
    1 - rain_probability_difference / 100
)

precipitation_score = max(
    0,
    1 - precipitation_difference
)

wind_score = max(
    0,
    1 - wind_difference / 10
)


agreement_score = (

    temperature_score
    + rain_score
    + precipitation_score
    + wind_score

) / 4


# ============================================================
# ADAPTIVE WEIGHTS
# ============================================================

ifs_weight = 0.55
aifs_weight = 0.45


if agreement_score < 0.70:

    ifs_weight = 0.50
    aifs_weight = 0.50


elif agreement_score < 0.85:

    ifs_weight = 0.52
    aifs_weight = 0.48


# ============================================================
# FUSION
# ============================================================

fused_temperature = (

    ifs_temp * ifs_weight
    + aifs_temp * aifs_weight

)


fused_rain_probability = (

    ifs_rain_probability * ifs_weight
    + aifs_rain_probability * aifs_weight

)


fused_precipitation = (

    ifs_precipitation * ifs_weight
    + aifs_precipitation * aifs_weight

)


fused_wind = (

    ifs_wind * ifs_weight
    + aifs_wind * aifs_weight

)


# ============================================================
# DISPLAY WEIGHTS
# ============================================================

print("\n")
print("=" * 70)
print("             ADAPTIVE MODEL WEIGHTS")
print("=" * 70)

print(
    f"\nECMWF IFS HRES : "
    f"{ifs_weight * 100:.2f}%"
)

print(
    f"ECMWF AIFS     : "
    f"{aifs_weight * 100:.2f}%"
)


# ============================================================
# FINAL FUSED FORECAST
# ============================================================

print("\n")
print("=" * 70)
print("                FUSED FORECAST")
print("=" * 70)

print(
    f"\nTemperature       : "
    f"{fused_temperature:.2f} °C"
)

print(
    f"Rain Probability  : "
    f"{fused_rain_probability:.2f} %"
)

print(
    f"Precipitation     : "
    f"{fused_precipitation:.2f} mm"
)

print(
    f"Wind Speed        : "
    f"{fused_wind:.2f} km/h"
)


# ============================================================
# CONFIDENCE
# ============================================================

confidence = agreement_score * 100


print("\n")
print("=" * 70)
print("             FORECAST CONFIDENCE")
print("=" * 70)

print(
    f"\nModel Agreement   : "
    f"{agreement_score * 100:.2f}%"
)

print(
    f"Fusion Confidence : "
    f"{confidence:.2f}%"
)


# ============================================================
# SYSTEM STATUS
# ============================================================

print("\n")
print("=" * 70)
print("                  SYSTEM STATUS")
print("=" * 70)

print("\nLive Model Data         : ACTIVE")
print("ECMWF IFS HRES         : ACTIVE")
print("ECMWF AIFS             : ACTIVE")
print("Retry Mechanism        : ACTIVE")
print("Independent Data Read  : ACTIVE")
print("Model Comparison       : ACTIVE")
print("Adaptive Weighting     : ACTIVE")
print("Forecast Fusion        : ACTIVE")
print("Confidence Estimation  : ACTIVE")


print("\n")
print("=" * 70)
print("      ✓ WEATHERFUSION-AWX V6.4 COMPLETE")
print("=" * 70)