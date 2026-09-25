import requests
import time


print("=" * 70)
print("              WEATHERFUSION-AWX")
print("       V7 - MULTI-MODEL REAL FUSION")
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
# WEATHER VARIABLES
# ============================================================

variables = (
    "temperature_2m,"
    "precipitation_probability,"
    "precipitation,"
    "wind_speed_10m"
)


# ============================================================
# API URL
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
# MODEL DOWNLOAD
# ============================================================

def get_model(model, name):

    url = build_url(model)

    for attempt in range(1, 4):

        print(f"\nConnecting to {name}...")
        print("-" * 70)
        print(f"Attempt : {attempt}/3")

        try:

            response = requests.get(
                url,
                timeout=60
            )

            print(
                f"HTTP Status : "
                f"{response.status_code}"
            )

            if response.status_code == 200:

                data = response.json()

                print(
                    f"✓ {name} data received"
                )

                return data

            print("API returned an error.")

        except requests.exceptions.Timeout:

            print(
                f"⚠ {name} request timed out."
            )

        except requests.exceptions.RequestException as error:

            print("⚠ Connection error:")
            print(error)

        if attempt < 3:

            print("Retrying in 3 seconds...")
            time.sleep(3)

    return None


# ============================================================
# COLLECT MODELS
# ============================================================

ifs_data = get_model(
    "ecmwf_ifs025",
    "ECMWF IFS HRES"
)

gfs_data = get_model(
    "gfs_global",
    "NCEP GFS GLOBAL"
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
    + ("AVAILABLE" if ifs_data else "UNAVAILABLE")
)

print(
    "NCEP GFS       : "
    + ("AVAILABLE" if gfs_data else "UNAVAILABLE")
)


if ifs_data is None or gfs_data is None:

    print("\n✗ Real model fusion cannot continue.")
    print("No simulated values will be created.")

    exit()


# ============================================================
# EXTRACT HOURLY DATA
# ============================================================

ifs = ifs_data["hourly"]
gfs = gfs_data["hourly"]

ifs_times = ifs["time"]
gfs_times = gfs["time"]


# ============================================================
# FIND FIRST VALID POINT
# ============================================================

def find_valid_index(data):

    temperatures = data.get(
        "temperature_2m",
        []
    )

    for index, value in enumerate(temperatures):

        if value is not None:

            return index

    return None


ifs_index = find_valid_index(ifs)
gfs_index = find_valid_index(gfs)


if ifs_index is None:

    print(
        "\n✗ IFS contains no valid "
        "temperature data."
    )

    exit()


if gfs_index is None:

    print(
        "\n✗ GFS contains no valid "
        "temperature data."
    )

    exit()


# ============================================================
# SELECT FORECAST POINTS
# ============================================================

ifs_time = ifs_times[ifs_index]
gfs_time = gfs_times[gfs_index]


print("\n")
print("=" * 70)
print("             MODEL FORECAST TIMES")
print("=" * 70)

print(
    f"\nIFS Forecast Time : "
    f"{ifs_time}"
)

print(
    f"GFS Forecast Time : "
    f"{gfs_time}"
)


# ============================================================
# SAFE VALUE
# ============================================================

def get_value(data, variable, index):

    values = data.get(variable, [])

    if index >= len(values):

        return None

    value = values[index]

    if value is None:

        return None

    return float(value)


# ============================================================
# IFS VALUES
# ============================================================

ifs_temp = get_value(
    ifs,
    "temperature_2m",
    ifs_index
)

ifs_rain_probability = get_value(
    ifs,
    "precipitation_probability",
    ifs_index
)

ifs_precipitation = get_value(
    ifs,
    "precipitation",
    ifs_index
)

ifs_wind = get_value(
    ifs,
    "wind_speed_10m",
    ifs_index
)


# ============================================================
# GFS VALUES
# ============================================================

gfs_temp = get_value(
    gfs,
    "temperature_2m",
    gfs_index
)

gfs_rain_probability = get_value(
    gfs,
    "precipitation_probability",
    gfs_index
)

gfs_precipitation = get_value(
    gfs,
    "precipitation",
    gfs_index
)

gfs_wind = get_value(
    gfs,
    "wind_speed_10m",
    gfs_index
)


# ============================================================
# VALIDATION
# ============================================================

all_values = [
    ifs_temp,
    ifs_rain_probability,
    ifs_precipitation,
    ifs_wind,
    gfs_temp,
    gfs_rain_probability,
    gfs_precipitation,
    gfs_wind
]


if any(value is None for value in all_values):

    print(
        "\n✗ One or more required "
        "model values are missing."
    )

    print(
        "Fusion stopped to prevent "
        "invalid results."
    )

    exit()


# ============================================================
# REAL MODEL DATA
# ============================================================

print("\n")
print("=" * 70)
print("                 REAL MODEL DATA")
print("=" * 70)


print("\nECMWF IFS HRES")
print("-" * 70)

print(
    f"Temperature       : "
    f"{ifs_temp:.2f} °C"
)

print(
    f"Rain Probability  : "
    f"{ifs_rain_probability:.2f} %"
)

print(
    f"Precipitation     : "
    f"{ifs_precipitation:.2f} mm"
)

print(
    f"Wind Speed        : "
    f"{ifs_wind:.2f} km/h"
)


print("\nNCEP GFS GLOBAL")
print("-" * 70)

print(
    f"Temperature       : "
    f"{gfs_temp:.2f} °C"
)

print(
    f"Rain Probability  : "
    f"{gfs_rain_probability:.2f} %"
)

print(
    f"Precipitation     : "
    f"{gfs_precipitation:.2f} mm"
)

print(
    f"Wind Speed        : "
    f"{gfs_wind:.2f} km/h"
)


# ============================================================
# MODEL DIFFERENCES
# ============================================================

temperature_difference = abs(
    ifs_temp - gfs_temp
)

rain_difference = abs(
    ifs_rain_probability
    - gfs_rain_probability
)

precipitation_difference = abs(
    ifs_precipitation
    - gfs_precipitation
)

wind_difference = abs(
    ifs_wind - gfs_wind
)


print("\n")
print("=" * 70)
print("              MODEL DISAGREEMENT")
print("=" * 70)

print(
    f"\nTemperature Difference : "
    f"{temperature_difference:.2f} °C"
)

print(
    f"Rain Probability Diff  : "
    f"{rain_difference:.2f} %"
)

print(
    f"Precipitation Difference : "
    f"{precipitation_difference:.2f} mm"
)

print(
    f"Wind Difference        : "
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
    1 - rain_difference / 100
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
# ADAPTIVE WEIGHTING
# ============================================================

ifs_weight = 0.55
gfs_weight = 0.45


if agreement_score < 0.70:

    ifs_weight = 0.50
    gfs_weight = 0.50

elif agreement_score < 0.85:

    ifs_weight = 0.52
    gfs_weight = 0.48


# ============================================================
# FUSION
# ============================================================

fused_temperature = (
    ifs_temp * ifs_weight
    + gfs_temp * gfs_weight
)

fused_rain_probability = (
    ifs_rain_probability * ifs_weight
    + gfs_rain_probability * gfs_weight
)

fused_precipitation = (
    ifs_precipitation * ifs_weight
    + gfs_precipitation * gfs_weight
)

fused_wind = (
    ifs_wind * ifs_weight
    + gfs_wind * gfs_weight
)


# ============================================================
# MODEL WEIGHTS
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
    f"NCEP GFS       : "
    f"{gfs_weight * 100:.2f}%"
)


# ============================================================
# FINAL FORECAST
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
    f"{confidence:.2f}%"
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

print("\nLive Model Data        : ACTIVE")
print("ECMWF IFS HRES        : ACTIVE")
print("NCEP GFS              : ACTIVE")
print("Model Comparison      : ACTIVE")
print("Adaptive Weighting    : ACTIVE")
print("Forecast Fusion       : ACTIVE")
print("Confidence Estimation : ACTIVE")


print("\n")
print("=" * 70)
print("      ✓ WEATHERFUSION-AWX V7 COMPLETE")
print("=" * 70)