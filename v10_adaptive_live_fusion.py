import requests

# ==============================================================
# WEATHERFUSION-AWX
# V10 - DATA-DRIVEN ADAPTIVE LIVE FUSION
# ==============================================================

LATITUDE = 26.2183
LONGITUDE = 78.1828

FORECAST_HOURS = 24

API_URL = "https://api.open-meteo.com/v1/forecast"

# V9 VERIFIED WEIGHTS
IFS_WEIGHT = 0.5671
GFS_WEIGHT = 0.4329


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
        rain_prob = hourly.get(
            "precipitation_probability", []
        )
        precipitation = hourly.get(
            "precipitation", []
        )
        wind = hourly.get(
            "wind_speed_10m", []
        )

        if not times or not temperatures:
            print(f"X {model_name} returned no forecast data")
            return None

        # Find first valid temperature
        valid_index = None

        for i, temp in enumerate(temperatures):

            if temp is not None:
                valid_index = i
                break

        if valid_index is None:
            print(f"X {model_name} has no valid temperature")
            return None

        result = {
            "time": times[valid_index],

            "temperature": temperatures[valid_index],

            "rain_probability": (
                rain_prob[valid_index]
                if valid_index < len(rain_prob)
                and rain_prob[valid_index] is not None
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

        print(f"X Error while collecting {model_name}")
        print("Error :", error)

        return None


# ==============================================================
# WEIGHTED AVERAGE
# ==============================================================

def weighted_average(value1, value2, weight1, weight2):

    return (
        value1 * weight1
        + value2 * weight2
    )


# ==============================================================
# HEADER
# ==============================================================

print("=" * 70)
print("                 WEATHERFUSION-AWX")
print("        V10 - DATA-DRIVEN ADAPTIVE LIVE FUSION")
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
# V9 WEIGHTS
# ==============================================================

print()
print("=" * 70)
print("             V9 VERIFIED MODEL WEIGHTS")
print("=" * 70)

print()
print(
    "ECMWF IFS HRES : {:.2f}%".format(
        IFS_WEIGHT * 100
    )
)

print(
    "NCEP GFS       : {:.2f}%".format(
        GFS_WEIGHT * 100
    )
)

print()
print("Weight source : Historical forecast verification")
print("Metric        : Temperature MAE")


# ==============================================================
# COLLECT LIVE FORECASTS
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


# ==============================================================
# CHECK DATA
# ==============================================================

if ifs is None or gfs is None:

    print()
    print("X Fusion cannot continue.")
    print("Both forecast models are required.")

    raise SystemExit


# ==============================================================
# LIVE MODEL FORECASTS
# ==============================================================

print()
print("=" * 70)
print("                 LIVE MODEL FORECASTS")
print("=" * 70)


print()
print("ECMWF IFS HRES")
print("-" * 70)

print("Forecast Time    :", ifs["time"])

print(
    "Temperature      : {:.2f} C".format(
        ifs["temperature"]
    )
)

print(
    "Rain Probability : {:.2f}%".format(
        ifs["rain_probability"]
    )
)

print(
    "Precipitation    : {:.2f} mm".format(
        ifs["precipitation"]
    )
)

print(
    "Wind Speed       : {:.2f} km/h".format(
        ifs["wind"]
    )
)


print()
print("NCEP GFS GLOBAL")
print("-" * 70)

print("Forecast Time    :", gfs["time"])

print(
    "Temperature      : {:.2f} C".format(
        gfs["temperature"]
    )
)

print(
    "Rain Probability : {:.2f}%".format(
        gfs["rain_probability"]
    )
)

print(
    "Precipitation    : {:.2f} mm".format(
        gfs["precipitation"]
    )
)

print(
    "Wind Speed       : {:.2f} km/h".format(
        gfs["wind"]
    )
)


# ==============================================================
# MODEL DIFFERENCE
# ==============================================================

temperature_difference = abs(
    ifs["temperature"] - gfs["temperature"]
)

rain_difference = abs(
    ifs["rain_probability"]
    - gfs["rain_probability"]
)

precip_difference = abs(
    ifs["precipitation"]
    - gfs["precipitation"]
)

wind_difference = abs(
    ifs["wind"] - gfs["wind"]
)


print()
print("=" * 70)
print("                 MODEL DISAGREEMENT")
print("=" * 70)

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
    "Precipitation Diff     : {:.2f} mm".format(
        precip_difference
    )
)

print(
    "Wind Difference        : {:.2f} km/h".format(
        wind_difference
    )
)


# ==============================================================
# ADAPTIVE FUSION
# ==============================================================

fused_temperature = weighted_average(
    ifs["temperature"],
    gfs["temperature"],
    IFS_WEIGHT,
    GFS_WEIGHT
)

fused_rain_probability = weighted_average(
    ifs["rain_probability"],
    gfs["rain_probability"],
    IFS_WEIGHT,
    GFS_WEIGHT
)

fused_precipitation = weighted_average(
    ifs["precipitation"],
    gfs["precipitation"],
    IFS_WEIGHT,
    GFS_WEIGHT
)

fused_wind = weighted_average(
    ifs["wind"],
    gfs["wind"],
    IFS_WEIGHT,
    GFS_WEIGHT
)


# ==============================================================
# MODEL AGREEMENT
# ==============================================================

temperature_agreement = max(
    0,
    100 - temperature_difference * 10
)

rain_agreement = max(
    0,
    100 - rain_difference
)

precip_agreement = max(
    0,
    100 - precip_difference * 20
)

wind_agreement = max(
    0,
    100 - wind_difference * 5
)

overall_agreement = (
    temperature_agreement
    + rain_agreement
    + precip_agreement
    + wind_agreement
) / 4


# ==============================================================
# FINAL FUSED FORECAST
# ==============================================================

print()
print("=" * 70)
print("              ADAPTIVE FUSED FORECAST")
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
        fused_rain_probability
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
# FUSION ANALYSIS
# ==============================================================

print()
print("=" * 70)
print("                  FUSION ANALYSIS")
print("=" * 70)

print()
print("Historical Data-Driven Weights")

print(
    "  ECMWF IFS : {:.2f}%".format(
        IFS_WEIGHT * 100
    )
)

print(
    "  NCEP GFS  : {:.2f}%".format(
        GFS_WEIGHT * 100
    )
)

print()
print(
    "Current Model Agreement : {:.2f}%".format(
        overall_agreement
    )
)


# ==============================================================
# STATUS
# ==============================================================

if overall_agreement >= 85:

    status = "HIGH MODEL AGREEMENT"

elif overall_agreement >= 70:

    status = "MODERATE MODEL AGREEMENT"

else:

    status = "LOW MODEL AGREEMENT"


print()
print("Status :", status)


# ==============================================================
# SUMMARY
# ==============================================================

print()
print("=" * 70)
print("                    V10 SUMMARY")
print("=" * 70)

print()
print("OK Historical model verification loaded")
print("OK Data-driven weights loaded")
print("OK ECMWF IFS live forecast received")
print("OK NCEP GFS live forecast received")
print("OK Model disagreement calculated")
print("OK Weighted adaptive fusion completed")
print("OK Final fused forecast generated")

print()
print("V10 COMPLETE")
print("=" * 70)