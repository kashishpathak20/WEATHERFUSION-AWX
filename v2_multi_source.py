import requests
from datetime import datetime


# ============================================================
# WEATHERFUSION-AWX
# V2 - MULTI-SOURCE FORECAST COLLECTOR
# ============================================================

print("=" * 70)
print("              WEATHERFUSION-AWX")
print("         V2 - MULTI-SOURCE FORECAST")
print("                COLLECTION ENGINE")
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
# SOURCE 1
# BASE FORECAST
# ------------------------------------------------------------

source_1 = (
    "https://api.open-meteo.com/v1/forecast"
    f"?latitude={latitude}"
    f"&longitude={longitude}"
    "&hourly=temperature_2m,precipitation_probability,"
    "precipitation,wind_speed_10m"
    "&forecast_days=1"
)

# ------------------------------------------------------------
# SOURCE 2
# SECOND FORECAST CONFIGURATION
# ------------------------------------------------------------

source_2 = (
    "https://api.open-meteo.com/v1/forecast"
    f"?latitude={latitude}"
    f"&longitude={longitude}"
    "&hourly=temperature_2m,precipitation_probability,"
    "precipitation,wind_speed_10m"
    "&forecast_days=1"
    "&temperature_unit=fahrenheit"
)


# ------------------------------------------------------------
# FUNCTION TO COLLECT DATA
# ------------------------------------------------------------

def collect_forecast(url, source_name):

    print(f"\nConnecting to {source_name}...")

    try:

        response = requests.get(url, timeout=15)

        if response.status_code == 200:

            data = response.json()

            print(f"✓ {source_name} connection successful")

            return data

        else:

            print(
                f"✗ {source_name} failed "
                f"(HTTP {response.status_code})"
            )

            return None

    except requests.exceptions.RequestException as error:

        print(f"✗ {source_name} connection error")
        print(error)

        return None


# ------------------------------------------------------------
# COLLECT FORECASTS
# ------------------------------------------------------------

forecast_1 = collect_forecast(
    source_1,
    "FORECAST SOURCE 1"
)

forecast_2 = collect_forecast(
    source_2,
    "FORECAST SOURCE 2"
)


# ------------------------------------------------------------
# DATA PROCESSING
# ------------------------------------------------------------

if forecast_1 is not None and forecast_2 is not None:

    hourly_1 = forecast_1["hourly"]
    hourly_2 = forecast_2["hourly"]

    print("\n")
    print("=" * 70)
    print("             MULTI-SOURCE FORECAST DATA")
    print("=" * 70)

    print("\nSOURCE 1")
    print("-" * 70)

    print(
        f"First forecast temperature : "
        f"{hourly_1['temperature_2m'][0]} °C"
    )

    print(
        f"Precipitation probability  : "
        f"{hourly_1['precipitation_probability'][0]} %"
    )

    print(
        f"Precipitation              : "
        f"{hourly_1['precipitation'][0]} mm"
    )

    print(
        f"Wind speed                 : "
        f"{hourly_1['wind_speed_10m'][0]} km/h"
    )


    print("\nSOURCE 2")
    print("-" * 70)

    # Source 2 uses Fahrenheit
    temperature_f = hourly_2["temperature_2m"][0]

    # Convert Fahrenheit to Celsius
    temperature_c = (temperature_f - 32) * 5 / 9

    print(
        f"First forecast temperature : "
        f"{temperature_f:.2f} °F"
    )

    print(
        f"Converted temperature      : "
        f"{temperature_c:.2f} °C"
    )

    print(
        f"Precipitation probability  : "
        f"{hourly_2['precipitation_probability'][0]} %"
    )

    print(
        f"Precipitation              : "
        f"{hourly_2['precipitation'][0]} mm"
    )

    print(
        f"Wind speed                 : "
        f"{hourly_2['wind_speed_10m'][0]} km/h"
    )


    # --------------------------------------------------------
    # SOURCE COMPARISON
    # --------------------------------------------------------

    print("\n")
    print("=" * 70)
    print("                 SOURCE COMPARISON")
    print("=" * 70)

    temp_1 = hourly_1["temperature_2m"][0]
    temp_2 = temperature_c

    difference = abs(temp_1 - temp_2)

    print(f"\nSource 1 Temperature : {temp_1:.2f} °C")
    print(f"Source 2 Temperature : {temp_2:.2f} °C")
    print(f"Difference           : {difference:.2f} °C")


    # --------------------------------------------------------
    # SYSTEM STATUS
    # --------------------------------------------------------

    print("\n")
    print("=" * 70)
    print("                  SYSTEM STATUS")
    print("=" * 70)

    print("\nSources Available     : 2")
    print("Successful Sources    : 2")
    print("Multi-source Mode     : ACTIVE")
    print("Comparison Engine     : ACTIVE")
    print("Adaptive Weighting    : NOT YET IMPLEMENTED")
    print("Fusion Engine         : NOT YET IMPLEMENTED")

    print("\nCollection Time:")
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    print("\n✓ WEATHERFUSION-AWX V2 COMPLETE")

else:

    print("\n")
    print("=" * 70)
    print("ERROR: One or more forecast sources failed.")
    print("=" * 70)