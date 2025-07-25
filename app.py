# -*- coding: utf-8 -*-
"""app

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/113L1QzGyfkDEx2eGmbAKDf6FVRvgPTz6
"""

pip install streamlit

import streamlit as st
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_style("whitegrid")

st.title("💧 WaterGuard Prototype: Water Usage Anomaly Detection")

st.write("""
Upload your water usage data CSV file. The CSV must contain:
- `timestamp`: datetime values
- `usage_liters`: numeric water usage per hour

If no file is uploaded, simulated data will be used.
""")

uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

def simulate_data():
    np.random.seed(42)
    hours = 90 * 24
    base_usage = np.random.normal(loc=12, scale=3, size=hours)
    base_usage = np.clip(base_usage, 5, 25)
    anomalies = np.random.choice(range(hours), size=15, replace=False)
    for i in anomalies:
        base_usage[i] *= np.random.uniform(2, 4)
    dates = pd.date_range("2025-05-01", periods=hours, freq="H")
    df = pd.DataFrame({"timestamp": dates, "usage_liters": base_usage})
    return df

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file, parse_dates=["timestamp"])
    st.success("File loaded successfully!")
else:
    st.info("Using simulated data")
    df = simulate_data()

df["timestamp"] = pd.to_datetime(df["timestamp"])

model = IsolationForest(contamination=0.02, random_state=42)
df["anomaly"] = model.fit_predict(df[["usage_liters"]])
df["anomaly"] = df["anomaly"].map({1: "Normal", -1: "Anomaly"})

anomaly_count = df["anomaly"].value_counts().get("Anomaly", 0)
st.write(f"Detected anomalies (possible leaks/spikes): **{anomaly_count}**")

st.subheader("Anomaly Details")
st.dataframe(df[df["anomaly"] == "Anomaly"][["timestamp", "usage_liters"]])

# Select day for hourly plot
df["date"] = df["timestamp"].dt.date
unique_dates = sorted(df["date"].unique())
selected_day = st.selectbox("Select a date to view hourly usage", unique_dates)

df_hourly = df[df["date"] == selected_day]

fig1, ax1 = plt.subplots(figsize=(14,6))
sns.lineplot(data=df_hourly, x="timestamp", y="usage_liters", ax=ax1, label="Usage")
sns.scatterplot(
    data=df_hourly[df_hourly["anomaly"] == "Anomaly"],
    x="timestamp",
    y="usage_liters",
    color="red",
    marker="X",
    s=60,
    label="Anomaly",
    ax=ax1
)
ax1.set_title(f"Hourly Water Usage for {selected_day}")
ax1.set_xlabel("Hour")
ax1.set_ylabel("Liters per Hour")
ax1.tick_params(axis="x", rotation=45)
ax1.legend()
st.pyplot(fig1)

# Daily plot
df_daily = df.set_index("timestamp").resample("D")["usage_liters"].sum().reset_index()

fig2, ax2 = plt.subplots(figsize=(14,5))
sns.lineplot(data=df_daily, x="timestamp", y="usage_liters", ax=ax2)
ax2.set_title("Daily Water Usage (Total per Day)")
ax2.set_xlabel("Date")
ax2.set_ylabel("Liters per Day")
ax2.tick_params(axis="x", rotation=45)
st.pyplot(fig2)

# Monthly plot
df_monthly = df.set_index("timestamp").resample("M")["usage_liters"].sum().reset_index()

fig3, ax3 = plt.subplots(figsize=(12,5))
sns.lineplot(data=df_monthly, x="timestamp", y="usage_liters", ax=ax3)
ax3.set_title("Monthly Water Usage (Total per Month)")
ax3.set_xlabel("Month")
ax3.set_ylabel("Liters per Month")
ax3.tick_params(axis="x", rotation=45)
st.pyplot(fig3)