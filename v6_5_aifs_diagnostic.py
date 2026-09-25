import requests

print("=" * 70)
print("              WEATHERFUSION-AWX")
print("        V6.5 - AIFS DIAGNOSTIC ENGINE")
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
# AIFS API REQUEST
# ============================================================

url = (
    "https://api.open-meteo.com/v1/forecast"
    f"?latitude={latitude}"
    f"&longitude={longitude}"
    "&hourly=temperature_2m,precipitation_probability,"
    "precipitation,wind_speed_10m"
    "&models=ecmwf_aifs025"
    "&forecast_hours=24"
    "&timezone=auto"
)


print("\n")
print("=" * 70)
print("              AIFS API CONNECTION")
print("=" * 70)

print("\nConnecting to ECMWF AIFS...")


# ============================================================
# API REQUEST
# ============================================================

try:

    response = requests.get(
        url,
        timeout=60
    )

    print(f"HTTP Status : {response.status_code}")

except requests.exceptions.RequestException as error:

    print("\n✗ API CONNECTION FAILED")
    print(error)
    exit()


# ============================================================
# HTTP STATUS CHECK
# ============================================================

if response.status_code != 200:

    print("\n✗ AIFS API returned an error.")
    print("\nSERVER RESPONSE:")
    print(response.text[:2000])
    exit()


print("✓ AIFS API responded successfully")


# ============================================================
# JSON PARSING
# ============================================================

try:

    data = response.json()

except ValueError:

    print("\n✗ Response is not valid JSON.")
    print(response.text[:2000])
    exit()


# ============================================================
# RESPONSE STRUCTURE
# ============================================================

print("\n")
print("=" * 70)
print("             RESPONSE STRUCTURE")
print("=" * 70)

print("\nTop-level keys:")

for key in data.keys():

    print(f"  - {key}")


# ============================================================
# API ERROR / MESSAGE
# ============================================================

if "reason" in data:

    print("\nAPI MESSAGE:")
    print(data["reason"])


if "error" in data:

    print("\nAPI ERROR:")
    print(data["error"])


# ============================================================
# HOURLY DATA
# ============================================================

if "hourly" not in data:

    print("\n✗ No 'hourly' section found.")
    print("\nFULL RESPONSE:")
    print(data)
    exit()


hourly = data["hourly"]


print("\n")
print("=" * 70)
print("                HOURLY DATA")
print("=" * 70)

print("\nHourly keys:")

for key in hourly.keys():

    print(f"  - {key}")


# ============================================================
# TIME DATA
# ============================================================

times = hourly.get("time", [])

print("\nNumber of forecast timestamps:")
print(len(times))


if len(times) > 0:

    print("\nFirst 10 timestamps:")

    for time_value in times[:10]:

        print(f"  {time_value}")


# ============================================================
# TEMPERATURE CHECK
# ============================================================

temperature = hourly.get(
    "temperature_2m",
    None
)


print("\n")
print("=" * 70)
print("             TEMPERATURE CHECK")
print("=" * 70)


if temperature is None:

    print("\n✗ temperature_2m DOES NOT EXIST")

else:

    print("\ntemperature_2m exists.")

    print(
        f"Number of values : {len(temperature)}"
    )

    valid_values = [
        value
        for value in temperature
        if value is not None
    ]

    print(
        f"Valid values     : {len(valid_values)}"
    )

    print(
        f"Missing values   : "
        f"{len(temperature) - len(valid_values)}"
    )

    print("\nFirst 10 temperature values:")

    for value in temperature[:10]:

        print(f"  {value}")


# ============================================================
# OTHER VARIABLES
# ============================================================

print("\n")
print("=" * 70)
print("            OTHER VARIABLE CHECK")
print("=" * 70)


variables = [
    "precipitation_probability",
    "precipitation",
    "wind_speed_10m"
]


for variable in variables:

    values = hourly.get(
        variable,
        None
    )

    print(f"\n{variable}")

    if values is None:

        print("  ✗ NOT FOUND")

    else:

        valid = [
            value
            for value in values
            if value is not None
        ]

        print(
            f"  Total values : {len(values)}"
        )

        print(
            f"  Valid values : {len(valid)}"
        )

        print(
            f"  First values : {values[:5]}"
        )


# ============================================================
# FINAL DIAGNOSIS
# ============================================================

print("\n")
print("=" * 70)
print("                 DIAGNOSTIC RESULT")
print("=" * 70)


if temperature is None:

    print("\n❌ TEMPERATURE VARIABLE NOT RETURNED")

elif len(temperature) == 0:

    print("\n❌ TEMPERATURE ARRAY IS EMPTY")

else:

    valid_temperature = [
        value
        for value in temperature
        if value is not None
    ]

    if len(valid_temperature) == 0:

        print(
            "\n❌ TEMPERATURE ARRAY EXISTS "
            "BUT ALL VALUES ARE NONE"
        )

    else:

        print(
            "\n✓ AIFS TEMPERATURE DATA IS AVAILABLE"
        )

        print(
            f"Valid temperature points : "
            f"{len(valid_temperature)}"
        )


# ============================================================
# COMPLETE
# ============================================================

print("\n")
print("=" * 70)
print("      ✓ WEATHERFUSION-AWX V6.5 COMPLETE")
print("=" * 70)