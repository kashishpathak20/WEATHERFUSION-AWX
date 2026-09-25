import requests

# ==============================================================
# WEATHERFUSION-AWX
# V11 - CONTEXT-AWARE ADAPTIVE FUSION
# ==============================================================

LATITUDE = 26.2183
LONGITUDE = 78.1828

FORECAST_HOURS = 24

API_URL = "https://api.open-meteo.com/v1/forecast"

# ==============================================================
# V9 VERIFIED BASE WEIGHTS
# ==============================================================

BASE_IFS_WEIGHT = 0.5671
BASE_GFS_WEIGHT = 0.4329


# ==============================================================
# GET LIVE FORECAST
# ==============================================================

def get_forecast(model_name, model_code):

    params = {
        "latitude": LATITUDE,
        "longitude": LONGITUDE,
        "hourly": (
            "temperature_2m,"
            "precipitation_probability,"
            "precipitation,"
            "wind_speed_10m"
        ),
        "models": model_code,
        "forecast_hours": FORECAST_HOURS,
        "timezone": "auto"
    }

    print()
    print(f"Collecting {model_name}")
    print("-" * 70)

    try:

        response = requests.get(
            API_URL,
            params=params,
            timeout=60
        )

        print("HTTP Status :", response.status_code)

        if response.status_code != 200:
            print(f"X {model_name} request failed")
            return None

        data = response.json()

        hourly = data.get("hourly", {})

        times = hourly.get("time", [])
        temperatures = hourly.get("temperature_2m", [])
        rain_probability = hourly.get(
            "precipitation_probability", []
        )
        precipitation = hourly.get(
            "precipitation", []
        )
        wind = hourly.get(
            "wind_speed_10m", []
        )

        if not times or not temperatures:
            print(f"X {model_name} returned no data")
            return None

        valid_index = None

        for i, temperature in enumerate(temperatures):

            if temperature is not None:
                valid_index = i
                break

        if valid_index is None:
            print(f"X {model_name} has no valid temperature")
            return None

        result = {
            "time": times[valid_index],

            "temperature": temperatures[valid_index],

            "rain_probability": (
                rain_probability[valid_index]
                if valid_index < len(rain_probability)
                and rain_probability[valid_index] is not None
                else 0
            ),

            "precipitation": (
                precipitation[valid_index]
                if valid_index < len(precipitation)
                and precipitation[valid_index] is not None
                else 0
            ),

            "wind": (
                wind[valid_index]
                if valid_index < len(wind)
                and wind[valid_index] is not None
                else 0
            )
        }

        print(f"OK {model_name} forecast received")

        return result

    except Exception as error:

        print(f"X Error collecting {model_name}")
        print("Error :", error)

        return None


# ==============================================================
# WEATHER REGIME DETECTION
# ==============================================================

def detect_weather_regime(ifs, gfs):

    average_rain = (
        ifs["rain_probability"]
        + gfs["rain_probability"]
    ) / 2

    average_wind = (
        ifs["wind"]
        + gfs["wind"]
    ) / 2

    average_temperature = (
        ifs["temperature"]
        + gfs["temperature"]
    ) / 2

    average_precipitation = (
        ifs["precipitation"]
        + gfs["precipitation"]
    ) / 2

    if average_rain >= 70 or average_precipitation >= 5:

        return "HEAVY RAIN / PRECIPITATION"

    elif average_rain >= 40:

        return "RAIN / UNSTABLE WEATHER"

    elif average_wind >= 30:

        return "HIGH WIND"

    elif average_temperature >= 40:

        return "HIGH TEMPERATURE"

    else:

        return "NORMAL WEATHER"


# ==============================================================
# CONTEXT ADAPTATION
# ==============================================================

def calculate_context_factor(
    temperature_difference,
    rain_difference,
    wind_difference
):

    # Large disagreement means more uncertainty.
    #
    # Therefore we reduce the dominance of the
    # historically stronger model and move slightly
    # toward a balanced ensemble.

    disagreement_score = (
        min(temperature_difference / 5, 1)
        + min(rain_difference / 50, 1)
        + min(wind_difference / 20, 1)
    ) / 3

    return disagreement_score


def calculate_adaptive_weights(
    base_ifs,
    base_gfs,
    disagreement_score
):

    # 0 = models agree
    # 1 = strong disagreement

    # Preserve historical skill when models agree.
    #
    # Move toward 50/50 as uncertainty increases.

    adaptation_strength = 0.35 * disagreement_score

    adaptive_ifs = (
        base_ifs * (1 - adaptation_strength)
        + 0.50 * adaptation_strength
    )

    adaptive_gfs = (
        base_gfs * (1 - adaptation_strength)
        + 0.50 * adaptation_strength
    )

    total = adaptive_ifs + adaptive_gfs

    adaptive_ifs = adaptive_ifs / total
    adaptive_gfs = adaptive_gfs / total

    return adaptive_ifs, adaptive_gfs


# ==============================================================
# WEIGHTED FUSION
# ==============================================================

def weighted_average(
    value1,
    value2,
    weight1,
    weight2
):

    return (
        value1 * weight1
        + value2 * weight2
    )


# ==============================================================
# HEADER
# ==============================================================

print("=" * 70)
print("                 WEATHERFUSION-AWX")
print("          V11 - CONTEXT-AWARE ADAPTIVE FUSION")
print("=" * 70)


# ==============================================================
# LOCATION
# ==============================================================

print()
print("LOCATION")
print("-" * 70)

print("Latitude  :", LATITUDE)
print("Longitude :", LONGITUDE)


# ==============================================================
# BASE WEIGHTS
# ==============================================================

print()
print("=" * 70)
print("                 V9 BASE WEIGHTS")
print("=" * 70)

print()
print(
    "ECMWF IFS HRES : {:.2f}%".format(
        BASE_IFS_WEIGHT * 100
    )
)

print(
    "NCEP GFS       : {:.2f}%".format(
        BASE_GFS_WEIGHT * 100
    )
)


# ==============================================================
# LIVE FORECASTS
# ==============================================================

ifs = get_forecast(
    "ECMWF IFS HRES",
    "ecmwf_ifs025"
)

gfs = get_forecast(
    "NCEP GFS GLOBAL",
    "gfs_global"
)


# ==============================================================
# DATA STATUS
# ==============================================================

print()
print("=" * 70)
print("                    DATA STATUS")
print("=" * 70)

print(
    "ECMWF IFS HRES :",
    "AVAILABLE" if ifs else "FAILED"
)

print(
    "NCEP GFS       :",
    "AVAILABLE" if gfs else "FAILED"
)


if ifs is None or gfs is None:

    print()
    print("X V11 cannot continue.")
    print("Both models are required.")

    raise SystemExit


# ==============================================================
# MODEL FORECASTS
# ==============================================================

print()
print("=" * 70)
print("                 CURRENT FORECASTS")
print("=" * 70)

print()
print("ECMWF IFS HRES")
print("-" * 70)

print("Time              :", ifs["time"])
print("Temperature       :", round(ifs["temperature"], 2), "C")
print("Rain Probability  :", round(ifs["rain_probability"], 2), "%")
print("Precipitation     :", round(ifs["precipitation"], 2), "mm")
print("Wind Speed        :", round(ifs["wind"], 2), "km/h")


print()
print("NCEP GFS GLOBAL")
print("-" * 70)

print("Time              :", gfs["time"])
print("Temperature       :", round(gfs["temperature"], 2), "C")
print("Rain Probability  :", round(gfs["rain_probability"], 2), "%")
print("Precipitation     :", round(gfs["precipitation"], 2), "mm")
print("Wind Speed        :", round(gfs["wind"], 2), "km/h")


# ==============================================================
# WEATHER REGIME
# ==============================================================

weather_regime = detect_weather_regime(
    ifs,
    gfs
)

print()
print("=" * 70)
print("                 WEATHER CONTEXT")
print("=" * 70)

print()
print("Detected Regime :", weather_regime)


# ==============================================================
# MODEL DISAGREEMENT
# ==============================================================

temperature_difference = abs(
    ifs["temperature"]
    - gfs["temperature"]
)

rain_difference = abs(
    ifs["rain_probability"]
    - gfs["rain_probability"]
)

wind_difference = abs(
    ifs["wind"]
    - gfs["wind"]
)


print()
print("=" * 70)
print("                 MODEL DISAGREEMENT")
print("=" * 70)

print()
print(
    "Temperature Difference : {:.2f} C".format(
        temperature_difference
    )
)

print(
    "Rain Probability Diff  : {:.2f}%".format(
        rain_difference
    )
)

print(
    "Wind Difference        : {:.2f} km/h".format(
        wind_difference
    )
)


# ==============================================================
# CONTEXT FACTOR
# ==============================================================

disagreement_score = calculate_context_factor(
    temperature_difference,
    rain_difference,
    wind_difference
)

print()
print("=" * 70)
print("                CONTEXT ADAPTATION")
print("=" * 70)

print()
print(
    "Disagreement Score : {:.3f}".format(
        disagreement_score
    )
)


# ==============================================================
# ADAPTIVE WEIGHTS
# ==============================================================

adaptive_ifs, adaptive_gfs = calculate_adaptive_weights(
    BASE_IFS_WEIGHT,
    BASE_GFS_WEIGHT,
    disagreement_score
)


print()
print("V9 Base Weights")
print(
    "  IFS : {:.2f}%".format(
        BASE_IFS_WEIGHT * 100
    )
)

print(
    "  GFS : {:.2f}%".format(
        BASE_GFS_WEIGHT * 100
    )
)

print()
print("V11 Context-Adjusted Weights")

print(
    "  IFS : {:.2f}%".format(
        adaptive_ifs * 100
    )
)

print(
    "  GFS : {:.2f}%".format(
        adaptive_gfs * 100
    )
)


# ==============================================================
# FINAL FUSION
# ==============================================================

fused_temperature = weighted_average(
    ifs["temperature"],
    gfs["temperature"],
    adaptive_ifs,
    adaptive_gfs
)

fused_rain = weighted_average(
    ifs["rain_probability"],
    gfs["rain_probability"],
    adaptive_ifs,
    adaptive_gfs
)

fused_precipitation = weighted_average(
    ifs["precipitation"],
    gfs["precipitation"],
    adaptive_ifs,
    adaptive_gfs
)

fused_wind = weighted_average(
    ifs["wind"],
    gfs["wind"],
    adaptive_ifs,
    adaptive_gfs
)


# ==============================================================
# FINAL OUTPUT
# ==============================================================

print()
print("=" * 70)
print("              CONTEXT-ADAPTIVE FORECAST")
print("=" * 70)

print()
print("Temperature")
print(
    "  Fused Value       : {:.2f} C".format(
        fused_temperature
    )
)

print()
print("Rain Probability")
print(
    "  Fused Value       : {:.2f}%".format(
        fused_rain
    )
)

print()
print("Precipitation")
print(
    "  Fused Value       : {:.2f} mm".format(
        fused_precipitation
    )
)

print()
print("Wind Speed")
print(
    "  Fused Value       : {:.2f} km/h".format(
        fused_wind
    )
)


# ==============================================================
# CONFIDENCE
# ==============================================================

agreement = max(
    0,
    100 - disagreement_score * 100
)

print()
print("=" * 70)
print("                  FUSION CONFIDENCE")
print("=" * 70)

print()
print(
    "Model Agreement : {:.2f}%".format(
        agreement
    )
)

if agreement >= 85:

    status = "HIGH CONFIDENCE"

elif agreement >= 70:

    status = "MODERATE CONFIDENCE"

else:

    status = "LOW CONFIDENCE"

print()
print("Status :", status)


# ==============================================================
# SCIENTIFIC NOTE
# ==============================================================

print()
print("=" * 70)
print("                    V11 NOTE")
print("=" * 70)

print()
print("V11 uses historical skill from V9 as the base.")
print("Current model disagreement controls the adaptation.")
print()
print("The context adjustment is a prototype heuristic.")
print("It is NOT a learned regime-specific skill model.")


# ==============================================================
# SUMMARY
# ==============================================================

print()
print("=" * 70)
print("                    V11 SUMMARY")
print("=" * 70)

print()
print("OK V9 historical weights loaded")
print("OK Live IFS forecast loaded")
print("OK Live GFS forecast loaded")
print("OK Weather regime detected")
print("OK Model disagreement calculated")
print("OK Context adjustment calculated")
print("OK Adaptive weights generated")
print("OK Context-adaptive forecast generated")

print()
print("V11 COMPLETE")
print("=" * 70)