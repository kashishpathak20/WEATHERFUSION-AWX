import streamlit as st
import requests
import pandas as pd


# ==============================================================
# WEATHERFUSION-AWX
# V12 - LIVE ADAPTIVE FORECAST DASHBOARD
# ==============================================================

LATITUDE = 26.2183
LONGITUDE = 78.1828

API_URL = "https://api.open-meteo.com/v1/forecast"

# V9 verified historical weights
BASE_IFS_WEIGHT = 0.5671
BASE_GFS_WEIGHT = 0.4329


# ==============================================================
# PAGE CONFIG
# ==============================================================

st.set_page_config(
    page_title="WEATHERFUSION-AWX",
    page_icon="🌦️",
    layout="wide"
)


# ==============================================================
# TITLE
# ==============================================================

st.title("🌦️ WEATHERFUSION-AWX")

st.subheader(
    "Adaptive AI-NWP Forecast Blending System"
)

st.caption(
    "Live multi-model forecasting • Historical verification • "
    "Context-aware adaptive fusion"
)


# ==============================================================
# FORECAST FUNCTION
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
        "forecast_hours": 24,
        "timezone": "auto"
    }

    try:

        response = requests.get(
            API_URL,
            params=params,
            timeout=60
        )

        if response.status_code != 200:
            return None

        data = response.json()

        hourly = data.get("hourly", {})

        times = hourly.get("time", [])
        temperature = hourly.get(
            "temperature_2m", []
        )
        rain = hourly.get(
            "precipitation_probability", []
        )
        precipitation = hourly.get(
            "precipitation", []
        )
        wind = hourly.get(
            "wind_speed_10m", []
        )

        if not times or not temperature:
            return None

        index = None

        for i, value in enumerate(temperature):

            if value is not None:
                index = i
                break

        if index is None:
            return None

        return {
            "name": model_name,
            "time": times[index],
            "temperature": temperature[index],
            "rain": (
                rain[index]
                if rain[index] is not None
                else 0
            ),
            "precipitation": (
                precipitation[index]
                if precipitation[index] is not None
                else 0
            ),
            "wind": (
                wind[index]
                if wind[index] is not None
                else 0
            )
        }

    except Exception:

        return None


# ==============================================================
# WEATHER REGIME
# ==============================================================

def detect_regime(ifs, gfs):

    avg_rain = (
        ifs["rain"] + gfs["rain"]
    ) / 2

    avg_precip = (
        ifs["precipitation"]
        + gfs["precipitation"]
    ) / 2

    avg_wind = (
        ifs["wind"] + gfs["wind"]
    ) / 2

    avg_temp = (
        ifs["temperature"]
        + gfs["temperature"]
    ) / 2

    if avg_rain >= 70 or avg_precip >= 5:
        return "Heavy Rain"

    if avg_rain >= 40:
        return "Rain / Unstable"

    if avg_wind >= 30:
        return "High Wind"

    if avg_temp >= 40:
        return "High Temperature"

    return "Normal Weather"


# ==============================================================
# CONTEXT ADAPTATION
# ==============================================================

def calculate_weights(ifs, gfs):

    temp_diff = abs(
        ifs["temperature"]
        - gfs["temperature"]
    )

    rain_diff = abs(
        ifs["rain"]
        - gfs["rain"]
    )

    wind_diff = abs(
        ifs["wind"]
        - gfs["wind"]
    )

    disagreement = (
        min(temp_diff / 5, 1)
        + min(rain_diff / 50, 1)
        + min(wind_diff / 20, 1)
    ) / 3

    adaptation = 0.35 * disagreement

    ifs_weight = (
        BASE_IFS_WEIGHT * (1 - adaptation)
        + 0.50 * adaptation
    )

    gfs_weight = (
        BASE_GFS_WEIGHT * (1 - adaptation)
        + 0.50 * adaptation
    )

    total = ifs_weight + gfs_weight

    ifs_weight /= total
    gfs_weight /= total

    agreement = max(
        0,
        100 - disagreement * 100
    )

    return (
        ifs_weight,
        gfs_weight,
        agreement,
        temp_diff,
        rain_diff,
        wind_diff
    )


# ==============================================================
# LOAD DATA
# ==============================================================

with st.spinner("Collecting live model forecasts..."):

    ifs = get_forecast(
        "ECMWF IFS HRES",
        "ecmwf_ifs025"
    )

    gfs = get_forecast(
        "NCEP GFS GLOBAL",
        "gfs_global"
    )


# ==============================================================
# ERROR HANDLING
# ==============================================================

if ifs is None or gfs is None:

    st.error(
        "Unable to collect one or more live model forecasts."
    )

    st.stop()


# ==============================================================
# CALCULATE ADAPTIVE SYSTEM
# ==============================================================

regime = detect_regime(
    ifs,
    gfs
)

(
    ifs_weight,
    gfs_weight,
    agreement,
    temp_diff,
    rain_diff,
    wind_diff
) = calculate_weights(
    ifs,
    gfs
)


# ==============================================================
# FUSED FORECAST
# ==============================================================

fused_temperature = (
    ifs["temperature"] * ifs_weight
    + gfs["temperature"] * gfs_weight
)

fused_rain = (
    ifs["rain"] * ifs_weight
    + gfs["rain"] * gfs_weight
)

fused_precipitation = (
    ifs["precipitation"] * ifs_weight
    + gfs["precipitation"] * gfs_weight
)

fused_wind = (
    ifs["wind"] * ifs_weight
    + gfs["wind"] * gfs_weight
)


# ==============================================================
# TOP METRICS
# ==============================================================

st.markdown("## Live System Status")

col1, col2, col3, col4 = st.columns(4)

with col1:

    st.metric(
        "Fused Temperature",
        f"{fused_temperature:.2f} °C"
    )

with col2:

    st.metric(
        "Rain Probability",
        f"{fused_rain:.2f}%"
    )

with col3:

    st.metric(
        "Wind Speed",
        f"{fused_wind:.2f} km/h"
    )

with col4:

    st.metric(
        "Model Agreement",
        f"{agreement:.1f}%"
    )


# ==============================================================
# WEATHER CONTEXT
# ==============================================================

st.markdown("## Current Weather Context")

context_col1, context_col2 = st.columns(2)

with context_col1:

    st.info(
        f"Detected Regime: **{regime}**"
    )

with context_col2:

    if agreement >= 85:

        st.success(
            f"High Model Agreement: {agreement:.1f}%"
        )

    elif agreement >= 70:

        st.warning(
            f"Moderate Model Agreement: {agreement:.1f}%"
        )

    else:

        st.error(
            f"Low Model Agreement: {agreement:.1f}%"
        )


# ==============================================================
# MODEL COMPARISON
# ==============================================================

st.markdown("## Live Model Comparison")

comparison = pd.DataFrame({

    "Parameter": [
        "Temperature (°C)",
        "Rain Probability (%)",
        "Precipitation (mm)",
        "Wind Speed (km/h)"
    ],

    "ECMWF IFS": [
        ifs["temperature"],
        ifs["rain"],
        ifs["precipitation"],
        ifs["wind"]
    ],

    "NCEP GFS": [
        gfs["temperature"],
        gfs["rain"],
        gfs["precipitation"],
        gfs["wind"]
    ],

    "Fused Forecast": [
        fused_temperature,
        fused_rain,
        fused_precipitation,
        fused_wind
    ]
})

st.dataframe(
    comparison,
    use_container_width=True,
    hide_index=True
)


# ==============================================================
# MODEL WEIGHTS
# ==============================================================

st.markdown("## Adaptive Model Weights")

weight_data = pd.DataFrame({

    "Model": [
        "ECMWF IFS HRES",
        "NCEP GFS GLOBAL"
    ],

    "V9 Historical Weight (%)": [
        BASE_IFS_WEIGHT * 100,
        BASE_GFS_WEIGHT * 100
    ],

    "V11 Context-Adjusted Weight (%)": [
        ifs_weight * 100,
        gfs_weight * 100
    ]
})

st.dataframe(
    weight_data,
    use_container_width=True,
    hide_index=True
)


# ==============================================================
# WEIGHT CHART
# ==============================================================

st.bar_chart(
    weight_data.set_index("Model")[
        "V11 Context-Adjusted Weight (%)"
    ]
)


# ==============================================================
# MODEL DISAGREEMENT
# ==============================================================

st.markdown("## Model Disagreement")

disagreement_data = pd.DataFrame({

    "Parameter": [
        "Temperature",
        "Rain Probability",
        "Wind"
    ],

    "Difference": [
        temp_diff,
        rain_diff,
        wind_diff
    ]
})

st.bar_chart(
    disagreement_data.set_index("Parameter")
)


# ==============================================================
# FUSED FORECAST
# ==============================================================

st.markdown("## Final WEATHERFUSION Forecast")

forecast_col1, forecast_col2 = st.columns(2)

with forecast_col1:

    st.metric(
        "Temperature",
        f"{fused_temperature:.2f} °C"
    )

    st.metric(
        "Precipitation",
        f"{fused_precipitation:.2f} mm"
    )

with forecast_col2:

    st.metric(
        "Rain Probability",
        f"{fused_rain:.2f}%"
    )

    st.metric(
        "Wind",
        f"{fused_wind:.2f} km/h"
    )


# ==============================================================
# TECHNICAL PIPELINE
# ==============================================================

st.markdown("## Fusion Pipeline")

st.code(
    """
ECMWF IFS HRES ───────┐
                      │
                      ▼
                 Live Forecast
                      │
                      │
NCEP GFS GLOBAL ──────┤
                      │
                      ▼
              Model Comparison
                      │
                      ▼
             Weather Context
                      │
                      ▼
          Context-Aware Weighting
                      │
                      ▼
              Adaptive Fusion
                      │
                      ▼
            Final Forecast
""",
    language="text"
)


# ==============================================================
# SYSTEM INFORMATION
# ==============================================================

st.markdown("## System Information")

info = pd.DataFrame({

    "Component": [
        "Location",
        "ECMWF Model",
        "GFS Model",
        "Historical Verification",
        "Adaptive Weighting",
        "Weather Context"
    ],

    "Status": [
        f"{LATITUDE}, {LONGITUDE}",
        "Active",
        "Active",
        "V9 MAE-based",
        "V11 Context-Aware",
        regime
    ]
})

st.dataframe(
    info,
    use_container_width=True,
    hide_index=True
)


# ==============================================================
# FOOTER
# ==============================================================

st.divider()

st.caption(
    "WEATHERFUSION-AWX | Hybrid AI-NWP Forecast Blending Prototype"
)

st.caption(
    "Prototype note: adaptive context adjustment is heuristic "
    "and should be further trained and validated before operational use."
)