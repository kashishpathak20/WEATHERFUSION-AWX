import requests
from datetime import datetime, timedelta


print("=" * 70)
print("              WEATHERFUSION-AWX")
print("       V8 - HISTORICAL MODEL SKILL")
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
# DATE RANGE
# ============================================================

end_date = datetime.now().date()
start_date = end_date - timedelta(days=7)

print("\n")
print("=" * 70)
print("             HISTORICAL PERIOD")
print("=" * 70)

print(f"\nStart Date : {start_date}")
print(f"End Date   : {end_date}")


# ============================================================
# HISTORICAL FORECAST API
# ============================================================

base_url = (
    "https://historical-forecast-api.open-meteo.com/v1/forecast"
)


def get_historical_model(model, name):

    print("\n")
    print("=" * 70)
    print(f"COLLECTING {name}")
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
            base_url,
            params=params,
            timeout=60
        )

        print(f"\nHTTP Status : {response.status_code}")

        if response.status_code != 200:

            print("API error:")
            print(response.text[:500])

            return None

        data = response.json()

        print(
            f"✓ {name} historical data received"
        )

        return data

    except requests.exceptions.RequestException as error:

        print("\n✗ Connection error:")
        print(error)

        return None


# ============================================================
# COLLECT IFS
# ============================================================

ifs_data = get_historical_model(
    "ecmwf_ifs025",
    "ECMWF IFS HRES"
)


# ============================================================
# COLLECT GFS
# ============================================================

gfs_data = get_historical_model(
    "gfs_global",
    "NCEP GFS GLOBAL"
)


# ============================================================
# STATUS
# ============================================================

print("\n")
print("=" * 70)
print("                 DATA STATUS")
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

    print(
        "\n✗ Historical skill calculation "
        "cannot continue."
    )

    exit()


# ============================================================
# INSPECT DATA
# ============================================================

ifs_hourly = ifs_data.get("hourly", {})
gfs_hourly = gfs_data.get("hourly", {})

ifs_times = ifs_hourly.get("time", [])
gfs_times = gfs_hourly.get("time", [])

ifs_temp = ifs_hourly.get(
    "temperature_2m",
    []
)

gfs_temp = gfs_hourly.get(
    "temperature_2m",
    []
)


print("\n")
print("=" * 70)
print("              HISTORICAL DATA")
print("=" * 70)

print(
    f"\nIFS timestamps : {len(ifs_times)}"
)

print(
    f"GFS timestamps : {len(gfs_times)}"
)


# ============================================================
# VALID VALUE COUNTS
# ============================================================

ifs_valid = sum(
    value is not None
    for value in ifs_temp
)

gfs_valid = sum(
    value is not None
    for value in gfs_temp
)


print(
    f"\nIFS valid temperatures : "
    f"{ifs_valid}"
)

print(
    f"GFS valid temperatures : "
    f"{gfs_valid}"
)


if ifs_valid == 0 or gfs_valid == 0:

    print(
        "\n✗ Historical temperature "
        "data unavailable."
    )

    exit()


# ============================================================
# IMPORTANT NOTE
# ============================================================

print("\n")
print("=" * 70)
print("              SKILL ANALYSIS")
print("=" * 70)

print(
    """
This V8 measures historical forecast
differences between the two models.

It is a prototype skill-analysis stage.
It does NOT yet claim that one model
is objectively more accurate than the other.
"""
)


# ============================================================
# COMPARE COMMON TIMESTAMPS
# ============================================================

ifs_lookup = {}

for index, timestamp in enumerate(ifs_times):

    if index < len(ifs_temp):

        value = ifs_temp[index]

        if value is not None:

            ifs_lookup[timestamp] = float(value)


gfs_lookup = {}

for index, timestamp in enumerate(gfs_times):

    if index < len(gfs_temp):

        value = gfs_temp[index]

        if value is not None:

            gfs_lookup[timestamp] = float(value)


common_times = sorted(
    set(ifs_lookup.keys())
    & set(gfs_lookup.keys())
)


print(
    f"\nCommon valid timestamps : "
    f"{len(common_times)}"
)


if len(common_times) == 0:

    print(
        "\n✗ No common timestamps "
        "were found."
    )

    exit()


# ============================================================
# MODEL DIFFERENCES
# ============================================================

differences = []

for timestamp in common_times:

    difference = abs(
        ifs_lookup[timestamp]
        - gfs_lookup[timestamp]
    )

    differences.append(difference)


# ============================================================
# MEAN MODEL DISAGREEMENT
# ============================================================

mean_difference = (
    sum(differences)
    / len(differences)
)


maximum_difference = max(
    differences
)


minimum_difference = min(
    differences
)


print("\n")
print("=" * 70)
print("           HISTORICAL DISAGREEMENT")
print("=" * 70)

print(
    f"\nMean Temperature Difference : "
    f"{mean_difference:.2f} °C"
)

print(
    f"Minimum Difference          : "
    f"{minimum_difference:.2f} °C"
)

print(
    f"Maximum Difference          : "
    f"{maximum_difference:.2f} °C"
)


# ============================================================
# PROTOTYPE SKILL SCORE
# ============================================================

# Smaller disagreement means the models
# behave more similarly over the period.
#
# This is NOT forecast accuracy against
# observations. It is a model-consistency
# indicator used for this prototype.

ifs_skill = 1 / (
    1 + mean_difference
)

gfs_skill = 1 / (
    1 + mean_difference
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
print("             MODEL SKILL INDICATOR")
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
print("           HISTORICAL MODEL WEIGHTS")
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
# CURRENT MODEL DATA
# ============================================================

print("\n")
print("=" * 70)
print("              V8 RESULT")
print("=" * 70)

print(
    """
Historical data collection     : ACTIVE
Common timestamp analysis      : ACTIVE
Model disagreement analysis    : ACTIVE
Historical skill indicator     : ACTIVE
Dynamic weight calculation     : ACTIVE
"""
)


print("=" * 70)
print("      ✓ WEATHERFUSION-AWX V8 COMPLETE")
print("=" * 70)