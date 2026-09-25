import requests
import math
from datetime import datetime, timedelta


print("=" * 70)
print("              WEATHERFUSION-AWX")
print("       V9 - FORECAST VERIFICATION ENGINE")
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
# VERIFICATION PERIOD
# ============================================================

end_date = datetime.now().date() - timedelta(days=1)
start_date = end_date - timedelta(days=6)

print("\n")
print("=" * 70)
print("             VERIFICATION PERIOD")
print("=" * 70)

print(f"\nStart Date : {start_date}")
print(f"End Date   : {end_date}")


# ============================================================
# HISTORICAL FORECAST API
# ============================================================

forecast_url = (
    "https://historical-forecast-api.open-meteo.com/v1/forecast"
)


def get_forecast(model, name):

    print("\n")
    print("=" * 70)
    print(f"COLLECTING {name} HISTORICAL FORECAST")
    print("=" * 70)

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": str(start_date),
        "end_date": str(end_date),
        "hourly": "temperature_2m",
        "models": model,
        "timezone": "auto"
    }

    try:

        response = requests.get(
            forecast_url,
            params=params,
            timeout=60
        )

        print(
            f"\nHTTP Status : "
            f"{response.status_code}"
        )

        if response.status_code != 200:

            print("API error:")
            print(response.text[:500])

            return None

        print(
            f"✓ {name} forecast data received"
        )

        return response.json()

    except requests.exceptions.RequestException as error:

        print("\n✗ Connection error:")
        print(error)

        return None


# ============================================================
# OBSERVATION / REFERENCE DATA
# ============================================================

observation_url = (
    "https://archive-api.open-meteo.com/v1/archive"
)


def get_observations():

    print("\n")
    print("=" * 70)
    print("COLLECTING OBSERVED WEATHER")
    print("=" * 70)

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": str(start_date),
        "end_date": str(end_date),
        "hourly": "temperature_2m",
        "timezone": "auto"
    }

    try:

        response = requests.get(
            observation_url,
            params=params,
            timeout=60
        )

        print(
            f"\nHTTP Status : "
            f"{response.status_code}"
        )

        if response.status_code != 200:

            print("Observation API error:")
            print(response.text[:500])

            return None

        print(
            "✓ Historical reference data received"
        )

        return response.json()

    except requests.exceptions.RequestException as error:

        print("\n✗ Connection error:")
        print(error)

        return None


# ============================================================
# DOWNLOAD DATA
# ============================================================

ifs_data = get_forecast(
    "ecmwf_ifs025",
    "ECMWF IFS HRES"
)

gfs_data = get_forecast(
    "gfs_global",
    "NCEP GFS GLOBAL"
)

observation_data = get_observations()


# ============================================================
# STATUS
# ============================================================

print("\n")
print("=" * 70)
print("                 DATA STATUS")
print("=" * 70)

print(
    "\nIFS Forecast : "
    + ("AVAILABLE" if ifs_data else "UNAVAILABLE")
)

print(
    "GFS Forecast : "
    + ("AVAILABLE" if gfs_data else "UNAVAILABLE")
)

print(
    "Reference    : "
    + (
        "AVAILABLE"
        if observation_data
        else "UNAVAILABLE"
    )
)


if (
    ifs_data is None
    or gfs_data is None
    or observation_data is None
):

    print(
        "\n✗ Verification cannot continue."
    )

    exit()


# ============================================================
# EXTRACT HOURLY DATA
# ============================================================

ifs_hourly = ifs_data.get(
    "hourly",
    {}
)

gfs_hourly = gfs_data.get(
    "hourly",
    {}
)

obs_hourly = observation_data.get(
    "hourly",
    {}
)


ifs_times = ifs_hourly.get(
    "time",
    []
)

gfs_times = gfs_hourly.get(
    "time",
    []
)

obs_times = obs_hourly.get(
    "time",
    []
)


ifs_temp = ifs_hourly.get(
    "temperature_2m",
    []
)

gfs_temp = gfs_hourly.get(
    "temperature_2m",
    []
)

obs_temp = obs_hourly.get(
    "temperature_2m",
    []
)


# ============================================================
# CREATE LOOKUP TABLES
# ============================================================

def create_lookup(times, values):

    lookup = {}

    for index, timestamp in enumerate(times):

        if index >= len(values):

            continue

        value = values[index]

        if value is None:

            continue

        lookup[timestamp] = float(value)

    return lookup


ifs_lookup = create_lookup(
    ifs_times,
    ifs_temp
)

gfs_lookup = create_lookup(
    gfs_times,
    gfs_temp
)

obs_lookup = create_lookup(
    obs_times,
    obs_temp
)


# ============================================================
# COMMON VERIFICATION TIMES
# ============================================================

ifs_common = (
    set(ifs_lookup.keys())
    & set(obs_lookup.keys())
)

gfs_common = (
    set(gfs_lookup.keys())
    & set(obs_lookup.keys())
)


ifs_times_common = sorted(
    ifs_common
)

gfs_times_common = sorted(
    gfs_common
)


print("\n")
print("=" * 70)
print("              VERIFICATION DATA")
print("=" * 70)

print(
    f"\nIFS vs Reference points : "
    f"{len(ifs_times_common)}"
)

print(
    f"GFS vs Reference points : "
    f"{len(gfs_times_common)}"
)


if len(ifs_times_common) == 0:

    print(
        "\n✗ No common IFS/reference "
        "timestamps."
    )

    exit()


if len(gfs_times_common) == 0:

    print(
        "\n✗ No common GFS/reference "
        "timestamps."
    )

    exit()


# ============================================================
# ERROR CALCULATION
# ============================================================

def calculate_errors(
    forecast_lookup,
    observation_lookup,
    timestamps
):

    absolute_errors = []

    squared_errors = []

    for timestamp in timestamps:

        forecast = forecast_lookup[
            timestamp
        ]

        observation = observation_lookup[
            timestamp
        ]

        error = forecast - observation

        absolute_error = abs(error)

        squared_error = error ** 2

        absolute_errors.append(
            absolute_error
        )

        squared_errors.append(
            squared_error
        )

    mae = (
        sum(absolute_errors)
        / len(absolute_errors)
    )

    mse = (
        sum(squared_errors)
        / len(squared_errors)
    )

    rmse = math.sqrt(mse)

    return mae, rmse


# ============================================================
# CALCULATE MODEL ERRORS
# ============================================================

ifs_mae, ifs_rmse = calculate_errors(
    ifs_lookup,
    obs_lookup,
    ifs_times_common
)

gfs_mae, gfs_rmse = calculate_errors(
    gfs_lookup,
    obs_lookup,
    gfs_times_common
)


# ============================================================
# DISPLAY ERRORS
# ============================================================

print("\n")
print("=" * 70)
print("              FORECAST ERROR")
print("=" * 70)

print("\nECMWF IFS HRES")
print("-" * 70)

print(
    f"MAE  : {ifs_mae:.3f} °C"
)

print(
    f"RMSE : {ifs_rmse:.3f} °C"
)


print("\nNCEP GFS GLOBAL")
print("-" * 70)

print(
    f"MAE  : {gfs_mae:.3f} °C"
)

print(
    f"RMSE : {gfs_rmse:.3f} °C"
)


# ============================================================
# SKILL SCORE
# ============================================================

# Lower error = higher skill.
#
# This converts the error into a simple
# prototype skill indicator.

ifs_skill = 1 / (
    1 + ifs_mae
)

gfs_skill = 1 / (
    1 + gfs_mae
)


total_skill = (
    ifs_skill
    + gfs_skill
)


ifs_weight = (
    ifs_skill
    / total_skill
)

gfs_weight = (
    gfs_skill
    / total_skill
)


# ============================================================
# DISPLAY SKILL
# ============================================================

print("\n")
print("=" * 70)
print("             VERIFIED MODEL SKILL")
print("=" * 70)

print(
    f"\nIFS Skill Indicator : "
    f"{ifs_skill:.4f}"
)

print(
    f"GFS Skill Indicator : "
    f"{gfs_skill:.4f}"
)


print("\n")
print("=" * 70)
print("          DATA-DRIVEN MODEL WEIGHTS")
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
# INTERPRETATION
# ============================================================

print("\n")
print("=" * 70)
print("                 INTERPRETATION")
print("=" * 70)

if ifs_mae < gfs_mae:

    print(
        "\nIFS has the lower historical "
        "temperature MAE for this period."
    )

elif gfs_mae < ifs_mae:

    print(
        "\nGFS has the lower historical "
        "temperature MAE for this period."
    )

else:

    print(
        "\nBoth models have the same "
        "historical temperature MAE."
    )


print(
    "\nThese weights are based on "
    "historical temperature error."
)

print(
    "They are not a calibrated probability "
    "of forecast correctness."
)


# ============================================================
# SYSTEM STATUS
# ============================================================

print("\n")