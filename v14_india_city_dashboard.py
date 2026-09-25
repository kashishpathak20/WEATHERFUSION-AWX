import requests
import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go
from datetime import datetime


# ============================================================
# WEATHERFUSION-AWX V14
# INDIA-WIDE CITY FORECAST DASHBOARD
# ============================================================

st.set_page_config(
    page_title="WEATHERFUSION-AWX V14",
    page_icon="🌦️",
    layout="wide"
)


# ============================================================
# CONFIGURATION
# ============================================================

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

IFS_MODEL = "ecmwf_ifs025"
GFS_MODEL = "gfs_global"

REQUEST_TIMEOUT = 30


# ============================================================
# PAGE HEADER
# ============================================================

st.title("🌦️ WEATHERFUSION-AWX")

st.subheader(
    "India-Wide Hybrid AI-NWP Multi-Model Forecast Fusion System"
)

st.markdown(
    """
    Enter any Indian city or town to generate a live fused weather forecast
    using ECMWF IFS and NCEP GFS model data with adaptive model weighting.
    """
)


# ============================================================
# CITY SEARCH
# ============================================================

st.markdown("## 📍 Select Indian Location")

city_input = st.text_input(
    "Enter city / town name",
    value="Indore",
    placeholder="Example: Delhi, Mumbai, Bhopal, Gwalior..."
)

search_button = st.button(
    "🔍 Get Forecast",
    type="primary"
)


# ============================================================
# GEOCODING FUNCTION
# ============================================================

@st.cache_data(ttl=3600)
def search_indian_city(city):

    params = {
        "name": city,
        "count": 10,
        "language": "en",
        "format": "json"
    }

    try:

        response = requests.get(
            GEOCODING_URL,
            params=params,
            timeout=REQUEST_TIMEOUT
        )

        if response.status_code != 200:
            return []

        data = response.json()

        results = data.get("results", [])

        indian_results = []

        for location in results:

            country_code = location.get("country_code", "")

            if country_code.upper() == "IN":

                indian_results.append({
                    "name": location.get("name", ""),
                    "latitude": location.get("latitude"),
                    "longitude": location.get("longitude"),
                    "state": location.get("admin1", ""),
                    "district": location.get("admin2", ""),
                    "country": location.get("country", "India"),
                })

        return indian_results

    except Exception as e:

        st.error(f"Geocoding error: {e}")

        return []


# ============================================================
# FETCH MODEL DATA
# ============================================================

@st.cache_data(ttl=300)
def fetch_model_forecast(latitude, longitude, model):

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": (
            "temperature_2m,"
            "precipitation_probability,"
            "precipitation,"
            "wind_speed_10m"
        ),
        "models": model,
        "forecast_days": 2,
        "timezone": "auto"
    }

    try:

        response = requests.get(
            FORECAST_URL,
            params=params,
            timeout=REQUEST_TIMEOUT
        )

        if response.status_code != 200:
            return None

        data = response.json()

        hourly = data.get("hourly", {})

        if not hourly:
            return None

        df = pd.DataFrame({
            "time": hourly.get("time", []),
            "temperature": hourly.get("temperature_2m", []),
            "rain_probability": hourly.get(
                "precipitation_probability", []
            ),
            "precipitation": hourly.get(
                "precipitation", []
            ),
            "wind": hourly.get(
                "wind_speed_10m", []
            )
        })

        if df.empty:
            return None

        df["time"] = pd.to_datetime(df["time"])

        numeric_columns = [
            "temperature",
            "rain_probability",
            "precipitation",
            "wind"
        ]

        for column in numeric_columns:
            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            )

        return df.head(24)

    except Exception:

        return None


# ============================================================
# WEATHER REGIME
# ============================================================

def detect_weather_regime(rain_probability, precipitation, wind, temperature):

    if rain_probability >= 70 or precipitation >= 5:

        return "🌧️ HEAVY RAIN / PRECIPITATION"

    elif rain_probability >= 40:

        return "🌦️ RAIN / UNSTABLE WEATHER"

    elif wind >= 30:

        return "💨 HIGH WIND"

    elif temperature >= 40:

        return "🔥 HIGH TEMPERATURE"

    else:

        return "☀️ NORMAL WEATHER"


# ============================================================
# MODEL AGREEMENT
# ============================================================

def calculate_agreement(ifs_row, gfs_row):

    temp_difference = abs(
        ifs_row["temperature"] -
        gfs_row["temperature"]
    )

    rain_difference = abs(
        ifs_row["rain_probability"] -
        gfs_row["rain_probability"]
    )

    wind_difference = abs(
        ifs_row["wind"] -
        gfs_row["wind"]
    )

    temp_score = max(
        0,
        100 - temp_difference * 10
    )

    rain_score = max(
        0,
        100 - rain_difference
    )

    wind_score = max(
        0,
        100 - wind_difference * 3
    )

    agreement = (
        temp_score * 0.45 +
        rain_score * 0.35 +
        wind_score * 0.20
    )

    return agreement


# ============================================================
# ADAPTIVE WEIGHTS
# ============================================================

def calculate_adaptive_weights(
    base_ifs,
    base_gfs,
    agreement
):

    if agreement >= 90:

        adjustment = 0.00

    elif agreement >= 80:

        adjustment = 0.03

    elif agreement >= 70:

        adjustment = 0.06

    else:

        adjustment = 0.10

    ifs_weight = base_ifs * (1 - adjustment) + 0.50 * adjustment
    gfs_weight = base_gfs * (1 - adjustment) + 0.50 * adjustment

    total = ifs_weight + gfs_weight

    ifs_weight /= total
    gfs_weight /= total

    return ifs_weight, gfs_weight


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("⚙️ SYSTEM")

st.sidebar.markdown(
    """
    **WEATHERFUSION-AWX V14**

    Hybrid AI-NWP Forecast Fusion
    """
)

st.sidebar.write("")

st.sidebar.info(
    """
    **Forecast Models**

    🛰️ ECMWF IFS HRES

    🛰️ NCEP GFS GLOBAL

    **Fusion**

    Historical skill + adaptive
    model agreement
    """
)


# ============================================================
# SEARCH EXECUTION
# ============================================================

if search_button or city_input:

    locations = search_indian_city(city_input)

    if not locations:

        st.error(
            f"❌ No Indian location found for **{city_input}**."
        )

        st.info(
            "Try another spelling, such as Delhi, Mumbai, "
            "Bhopal, Indore, Gwalior, Jaipur, etc."
        )

        st.stop()


    # ========================================================
    # LOCATION SELECTION
    # ========================================================

    if len(locations) > 1:

        location_labels = []

        for location in locations:

            label = location["name"]

            if location["state"]:
                label += f", {location['state']}"

            if location["district"]:
                label += f" ({location['district']})"

            location_labels.append(label)

        selected_index = st.selectbox(
            "📍 Multiple Indian locations found. Select one:",
            range(len(location_labels)),
            format_func=lambda x: location_labels[x]
        )

        selected_location = locations[selected_index]

    else:

        selected_location = locations[0]


    # ========================================================
    # LOCATION INFORMATION
    # ========================================================

    city_name = selected_location["name"]
    state_name = selected_location["state"]
    district_name = selected_location["district"]

    latitude = selected_location["latitude"]
    longitude = selected_location["longitude"]


    st.markdown("---")

    st.markdown(
        f"## 📍 {city_name}"
    )

    location_text = ""

    if district_name:
        location_text += f"{district_name}, "

    if state_name:
        location_text += f"{state_name}, "

    location_text += "India"

    st.write(location_text)

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Latitude",
        f"{latitude:.4f}°"
    )

    col2.metric(
        "Longitude",
        f"{longitude:.4f}°"
    )

    col3.metric(
        "Location",
        city_name
    )


    # ========================================================
    # FETCH ECMWF
    # ========================================================

    with st.spinner("🛰️ Fetching ECMWF IFS forecast..."):

        ifs_df = fetch_model_forecast(
            latitude,
            longitude,
            IFS_MODEL
        )


    # ========================================================
    # FETCH GFS
    # ========================================================

    with st.spinner("🛰️ Fetching NCEP GFS forecast..."):

        gfs_df = fetch_model_forecast(
            latitude,
            longitude,
            GFS_MODEL
        )


    # ========================================================
    # DATA VALIDATION
    # ========================================================

    if ifs_df is None:

        st.error(
            "❌ ECMWF IFS forecast could not be retrieved."
        )

        st.stop()


    if gfs_df is None:

        st.error(
            "❌ NCEP GFS forecast could not be retrieved."
        )

        st.stop()


    # ========================================================
    # COMMON TIMESTAMPS
    # ========================================================

    common_times = sorted(
        set(ifs_df["time"]) &
        set(gfs_df["time"])
    )


    if not common_times:

        st.error(
            "❌ No common forecast timestamps found."
        )

        st.stop()


    ifs_df = ifs_df[
        ifs_df["time"].isin(common_times)
    ].reset_index(drop=True)

    gfs_df = gfs_df[
        gfs_df["time"].isin(common_times)
    ].reset_index(drop=True)


    # ========================================================
    # BASE HISTORICAL WEIGHTS
    # ========================================================

    # Based on your V9 verification result
    base_ifs_weight = 0.5671
    base_gfs_weight = 0.4329


    # ========================================================
    # CURRENT FORECAST
    # ========================================================

    ifs_current = ifs_df.iloc[0]
    gfs_current = gfs_df.iloc[0]


    # ========================================================
    # MODEL AGREEMENT
    # ========================================================

    agreement = calculate_agreement(
        ifs_current,
        gfs_current
    )


    # ========================================================
    # ADAPTIVE WEIGHTS
    # ========================================================

    ifs_weight, gfs_weight = calculate_adaptive_weights(
        base_ifs_weight,
        base_gfs_weight,
        agreement
    )


    # ========================================================
    # FUSED FORECAST
    # ========================================================

    fused_temperature = (
        ifs_current["temperature"] * ifs_weight +
        gfs_current["temperature"] * gfs_weight
    )

    fused_rain = (
        ifs_current["rain_probability"] * ifs_weight +
        gfs_current["rain_probability"] * gfs_weight
    )

    fused_precipitation = (
        ifs_current["precipitation"] * ifs_weight +
        gfs_current["precipitation"] * gfs_weight
    )

    fused_wind = (
        ifs_current["wind"] * ifs_weight +
        gfs_current["wind"] * gfs_weight
    )


    # ========================================================
    # WEATHER REGIME
    # ========================================================

    regime = detect_weather_regime(
        fused_rain,
        fused_precipitation,
        fused_wind,
        fused_temperature
    )


    # ========================================================
    # MAIN DASHBOARD
    # ========================================================

    st.markdown("---")

    st.markdown("## 🌦️ Fused Forecast")


    m1, m2, m3, m4 = st.columns(4)


    m1.metric(
        "🌡️ Temperature",
        f"{fused_temperature:.1f} °C"
    )

    m2.metric(
        "🌧️ Rain Probability",
        f"{fused_rain:.1f}%"
    )

    m3.metric(
        "💨 Wind Speed",
        f"{fused_wind:.1f} km/h"
    )

    m4.metric(
        "🤝 Model Agreement",
        f"{agreement:.1f}%"
    )


    st.success(
        f"Current Weather Regime: **{regime}**"
    )


    # ========================================================
    # MODEL COMPARISON
    # ========================================================

    st.markdown("## 🛰️ Model Comparison")


    comparison_df = pd.DataFrame({

        "Parameter": [
            "Temperature",
            "Rain Probability",
            "Precipitation",
            "Wind Speed"
        ],

        "ECMWF IFS": [
            ifs_current["temperature"],
            ifs_current["rain_probability"],
            ifs_current["precipitation"],
            ifs_current["wind"]
        ],

        "NCEP GFS": [
            gfs_current["temperature"],
            gfs_current["rain_probability"],
            gfs_current["precipitation"],
            gfs_current["wind"]
        ],

        "Fused Forecast": [
            fused_temperature,
            fused_rain,
            fused_precipitation,
            fused_wind
        ]

    })


    st.dataframe(
        comparison_df,
        width="stretch"
    )


    # ========================================================
    # TEMPERATURE FORECAST
    # ========================================================

    st.markdown("## 🌡️ 24-Hour Temperature Forecast")


    fig_temp = go.Figure()

    fig_temp.add_trace(
        go.Scatter(
            x=ifs_df["time"],
            y=ifs_df["temperature"],
            mode="lines+markers",
            name="ECMWF IFS"
        )
    )

    fig_temp.add_trace(
        go.Scatter(
            x=gfs_df["time"],
            y=gfs_df["temperature"],
            mode="lines+markers",
            name="NCEP GFS"
        )
    )


    fused_temperature_series = (
        ifs_df["temperature"] * ifs_weight +
        gfs_df["temperature"] * gfs_weight
    )


    fig_temp.add_trace(
        go.Scatter(
            x=ifs_df["time"],
            y=fused_temperature_series,
            mode="lines+markers",
            name="FUSED"
        )
    )


    fig_temp.update_layout(
        xaxis_title="Time",
        yaxis_title="Temperature (°C)",
        hovermode="x unified"
    )


    st.plotly_chart(
        fig_temp,
        width="stretch"
    )


    # ========================================================
    # RAIN PROBABILITY
    # ========================================================

    st.markdown("## 🌧️ Rain Probability")


    fused_rain_series = (
        ifs_df["rain_probability"] * ifs_weight +
        gfs_df["rain_probability"] * gfs_weight
    )


    fig_rain = go.Figure()


    fig_rain.add_trace(
        go.Scatter(
            x=ifs_df["time"],
            y=ifs_df["rain_probability"],
            mode="lines+markers",
            name="ECMWF IFS"
        )
    )


    fig_rain.add_trace(
        go.Scatter(
            x=gfs_df["time"],
            y=gfs_df["rain_probability"],
            mode="lines+markers",
            name="NCEP GFS"
        )
    )


    fig_rain.add_trace(
        go.Scatter(
            x=ifs_df["time"],
            y=fused_rain_series,
            mode="lines+markers",
            name="FUSED"
        )
    )


    fig_rain.update_layout(
        xaxis_title="Time",
        yaxis_title="Rain Probability (%)",
        hovermode="x unified"
    )


    st.plotly_chart(
        fig_rain,
        width="stretch"
    )


    # ========================================================
    # WIND FORECAST
    # ========================================================

    st.markdown("## 💨 Wind Forecast")


    fused_wind_series = (
        ifs_df["wind"] * ifs_weight +
        gfs_df["wind"] * gfs_weight
    )


    fig_wind = go.Figure()


    fig_wind.add_trace(
        go.Scatter(
            x=ifs_df["time"],
            y=ifs_df["wind"],
            mode="lines+markers",
            name="ECMWF IFS"
        )
    )


    fig_wind.add_trace(
        go.Scatter(
            x=gfs_df["time"],
            y=gfs_df["wind"],
            mode="lines+markers",
            name="NCEP GFS"
        )
    )


    fig_wind.add_trace(
        go.Scatter(
            x=ifs_df["time"],
            y=fused_wind_series,
            mode="lines+markers",
            name="FUSED"
        )
    )


    fig_wind.update_layout(
        xaxis_title="Time",
        yaxis_title="Wind Speed (km/h)",
        hovermode="x unified"
    )


    st.plotly_chart(
        fig_wind,
        width="stretch"
    )


    # ========================================================
    # ADAPTIVE WEIGHTS
    # ========================================================

    st.markdown("## ⚖️ Adaptive Model Weights")


    weight_df = pd.DataFrame({

        "Model": [
            "ECMWF IFS HRES",
            "NCEP GFS GLOBAL"
        ],

        "Historical Weight (%)": [
            base_ifs_weight * 100,
            base_gfs_weight * 100
        ],

        "Current Adaptive Weight (%)": [
            ifs_weight * 100,
            gfs_weight * 100
        ]

    })


    st.dataframe(
        weight_df,
        width="stretch"
    )


    fig_weights = go.Figure()


    fig_weights.add_trace(
        go.Bar(
            x=weight_df["Model"],
            y=weight_df["Current Adaptive Weight (%)"],
            name="Adaptive Weight"
        )
    )


    fig_weights.update_layout(
        yaxis_title="Weight (%)",
        yaxis_range=[0, 100]
    )


    st.plotly_chart(
        fig_weights,
        width="stretch"
    )


    # ========================================================
    # FORECAST STATUS
    # ========================================================

    st.markdown("## 🧠 Fusion Engine Status")


    status1, status2, status3 = st.columns(3)


    status1.success(
        "✓ ECMWF IFS ACTIVE"
    )

    status2.success(
        "✓ NCEP GFS ACTIVE"
    )

    if agreement >= 85:

        status3.success(
            "✓ HIGH MODEL AGREEMENT"
        )

    elif agreement >= 70:

        status3.warning(
            "⚠ MODERATE MODEL AGREEMENT"
        )

    else:

        status3.error(
            "⚠ LOW MODEL AGREEMENT"
        )


    # ========================================================
    # TECHNICAL PIPELINE
    # ========================================================

    st.markdown("---")

    st.markdown("## 🔬 Technical Pipeline")


    st.code(
        """
User enters Indian city
        ↓
India-wide Geocoding
        ↓
Latitude / Longitude
        ↓
ECMWF IFS ─────────┐
                   │
                   ├──→ Model Comparison
                   │
NCEP GFS ──────────┘
        ↓
Historical Skill Weights
        ↓
Current Model Agreement
        ↓
Adaptive Weight Adjustment
        ↓
Weighted Forecast Fusion
        ↓
Fused Weather Forecast
        ↓
24-Hour Visualization
        """,
        language="text"
    )


    # ========================================================
    # FOOTER
    # ========================================================

    st.markdown("---")

    st.caption(
        "WEATHERFUSION-AWX V14 | India-Wide Hybrid AI-NWP Forecast Fusion"
    )

    st.caption(
        "Prototype note: adaptive weighting and agreement scoring "
        "are research/demo heuristics, not calibrated probabilities."
    )