"""
Marine Heatwave Dashboard — Great Barrier Reef

Data source: NOAA Coral Reef Watch Daily Global 5km Marine Heatwave Watch
Snapshot: 17–23 September 2026 (7 daily observations)

Place this file next to:
  - marine_heatwave.csv
  - mhw_persistence.png   (persistence map)
  - mhw_week_panels.png   (daily evolution panels)
Run with:  streamlit run app_v2.py
"""

import os

import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(
    page_title="GBR Marine Heatwave Dashboard",
    page_icon="🌊",
    layout="wide",
)


st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Source+Serif+4:wght@600;700&display=swap');

    html, body, [class*="css"], .stMarkdown, .stCaption, p, li {
        font-family: 'Inter', sans-serif;
    }
    .stApp {
        background: linear-gradient(180deg, #eef5fa 0%, #ffffff 35%);
    }
    .block-container {
        padding-top: 2.5rem;
        padding-bottom: 3rem;
        padding-left: 3.5rem !important;
        padding-right: 3.5rem !important;
        max-width: 100% !important;
    }
    #MainMenu, footer {visibility: hidden;}

    /* ---- Bigger, scannable type ---- */
    h1 {
        font-family: 'Source Serif 4', serif !important;
        color: #0b2a4a !important;
        font-weight: 700 !important;
        font-size: 2.9rem !important;
        letter-spacing: -0.5px;
        border-left: 8px solid #0e7490;
        padding-left: 20px !important;
        line-height: 1.15 !important;
    }
    h2 {
        font-family: 'Source Serif 4', serif !important;
        color: #0b2a4a !important;
        font-weight: 700 !important;
        font-size: 2rem !important;
        margin-top: 0.5rem !important;
    }
    h3 {
        color: #0e7490 !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        font-size: 1.25rem !important;
        margin-top: 1.75rem !important;
    }
    p, li {
        color: #334155;
        line-height: 1.7;
        font-size: 1.18rem;
    }
    strong { color: #0b2a4a; }

    /* Captions */
    .stCaption, [data-testid="stCaptionContainer"] {
        color: #64748b !important;
        font-size: 1.02rem !important;
    }

    /* Dividers */
    hr {
        border: none !important;
        height: 1px !important;
        background: linear-gradient(90deg, transparent, #cbd5e1, transparent) !important;
        margin: 2.25rem 0 !important;
    }

    /* Metric cards — big numbers, glanceable */
    [data-testid="stMetric"] {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-top: 6px solid #0e7490;
        border-radius: 14px;
        padding: 1.5rem 1.6rem;
        box-shadow: 0 4px 16px rgba(15, 42, 74, 0.07);
        transition: transform .2s ease, box-shadow .2s ease;
    }
    [data-testid="stMetric"]:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 26px rgba(15, 42, 74, 0.12);
    }
    [data-testid="stMetricLabel"] p {
        color: #64748b !important;
        font-size: 0.95rem !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        letter-spacing: 0.8px;
    }
    [data-testid="stMetricValue"] {
        color: #0b2a4a !important;
        font-weight: 800 !important;
        font-size: 2.8rem !important;
    }
    [data-testid="stMetricDelta"] {
        color: #0e7490 !important;
        font-size: 1rem !important;
    }
    [data-testid="stMetricDelta"] svg { display: none; }

    /* Key insight — the one thing a busy reader must see */
    [data-testid="stAlert"] {
        background: linear-gradient(135deg, #ecfeff 0%, #f0fdf4 100%) !important;
        border: 1px solid #a5f3fc !important;
        border-left: 8px solid #0e7490 !important;
        border-radius: 14px !important;
        padding: 1.4rem 1.6rem !important;
    }
    [data-testid="stAlert"] p {
        color: #0b2a4a !important;
        font-size: 1.3rem !important;
        line-height: 1.6 !important;
    }

    /* Image cards */
    [data-testid="stImage"] {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 0.85rem;
        box-shadow: 0 4px 16px rgba(15, 42, 74, 0.06);
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data
def load_and_clean():
    df = pd.read_csv("marine_heatwave.csv", skiprows=[1])
    df = df.dropna(subset=["heatwave_category"])
    df = df[df["mask"] == 0]
    df = df[df["heatwave_category"].isin([0, 1])]

    # Latitude bands (3° each), defined for this analysis
    bins = [-25, -22, -19, -16, -13, -10]
    labels = ["Z1 (-25 to -22)", "Z2 (-22 to -19)", "Z3 (-19 to -16)",
              "Z4 (-16 to -13)", "Z5 (-13 to -10)"]
    df["zone"] = pd.cut(df["latitude"], bins=bins, labels=labels, right=False)

    return df


df = load_and_clean()

n_days = df["time"].nunique()
latest_time = df["time"].max()

# Latest day, Zone 1 only (the affected zone)
latest_z1 = df[(df["time"] == latest_time) & (df["zone"] == "Z1 (-25 to -22)")]
latest_z1_hw = (latest_z1["heatwave_category"] == 1).sum()
latest_z1_pct = latest_z1_hw / len(latest_z1) * 100 if len(latest_z1) else 0

# Peak day, Zone 1
peak_pct = (
    df[df["zone"] == "Z1 (-25 to -22)"]
      .groupby("time")["heatwave_category"].mean().mul(100).max()
)

# Persistent core (7/7 days)
persistence = (
    df.groupby(["latitude", "longitude"], as_index=False)["heatwave_category"]
      .sum().rename(columns={"heatwave_category": "days_hot"})
)
core7 = persistence[persistence["days_hot"] == n_days]
core7_size = len(core7)
core7_lat = core7["latitude"].mean()
core7_lon = core7["longitude"].mean()


st.title("🌊 Marine Heatwave Dashboard — Great Barrier Reef")
st.caption(
    f"NOAA Coral Reef Watch Daily Global 5km Marine Heatwave Watch  |  "
    f"Snapshot: 17–23 September 2026  |  {n_days} daily observations  |  "
    f"Latest observation: {latest_time[:10]}"
)

st.success(
    f"**As of {latest_time[:10]}, {latest_z1_pct:.2f}% of monitored waters in "
    f"the southern Great Barrier Reef (−25°S to −22°S) remain under active "
    f"marine heat stress — down from a peak of {peak_pct:.2f}% within the "
    f"observation window — with a persistent {core7_size}-pixel core that "
    f"has been heat-stressed on all seven days.**"
)

st.markdown("---")

col1, col2, col3 = st.columns(3, gap="medium")

with col1:
    st.metric(
        label=f"Zone 1 heat stress ({latest_time[:10]})",
        value=f"{latest_z1_pct:.2f}%",
        delta=f"{latest_z1_hw} pixels of {len(latest_z1):,}",
    )

with col2:
    st.metric(
        label="Zone 1 peak heat stress (week)",
        value=f"{peak_pct:.2f}%",
        delta="Peak day within the 7-day window",
    )

with col3:
    st.metric(
        label="Persistent core (7/7 days)",
        value=f"{core7_size} pixels",
        delta=f"Centroid {core7_lat:.2f}°S, {core7_lon:.2f}°E",
    )

#map1
st.markdown("---")
st.header("🗺️ Spatial Distribution")

if os.path.exists("mhw_persistence.png"):
    st.image("mhw_persistence.png", use_container_width=True)
else:
    st.warning("Place `mhw_persistence.png` next to this file to show the map.")

st.caption(
    "Light grey = monitored ocean pixels with no heatwave during the 7-day "
    "window. Red intensity = number of days each pixel was flagged as heatwave. "
    "Black cross = centroid of the persistent 7-day core."
)

#map2
st.markdown("---")
st.header("📅 Daily Evolution")

if os.path.exists("mhw_week_panels.png"):
    st.image("mhw_week_panels.png", use_container_width=True)
else:
    st.warning("Place `mhw_week_panels.png` next to this file to show the panels.")

st.caption(
    "Each panel shows one daily snapshot. Grey = no heatwave, red = heatwave "
    "pixel. The event builds over the southern reef and persists through the "
    "week."
)


st.markdown("---")
st.header("📖 Why this matters")

st.markdown("""
**Marine heatwaves** are prolonged periods of anomalously high sea surface
temperature — typically defined as five or more days above the 90th percentile
for a given location and season. They are a direct consequence of ocean warming
and a primary driver of mass coral bleaching.

The **Great Barrier Reef** has experienced repeated mass bleaching events in
recent years, with thermal stress as the leading cause. Monitoring marine
heatwaves is central to **SDG 13 (Climate Action)** and **SDG 14 (Life Below
Water)**, particularly target 14.2 on protecting marine ecosystems and
strengthening their resilience.

**Data source:** NOAA Coral Reef Watch Daily Global 5km Marine Heatwave Watch,
derived from the CoralTemp satellite sea surface temperature dataset. Heatwave
categories in this file are 0 (no heatwave) and 1 (heatwave present).
""")


st.markdown("---")
st.header("💡 Key Insight")

st.markdown(f"""
**What this means for policy:**

The heatwave is **localized to the southern part of the study domain** and
**persistent** for the full observation window. On the latest day
({latest_time[:10]}), heat stress in the affected band remained above zero but
below its week peak — indicating a still-active event in slow decline.

**Actionable implications:**
- **Targeted monitoring**: The southern band (−25°S to −22°S) is the only
  portion of the domain showing active heat stress; field validation and
  monitoring resources can be focused there.
- **Northern zones unaffected**: Zones north of −22°S recorded no heatwave
  pixels across the entire week, so no additional monitoring is currently
  required there.
- **SDG 13/14 alignment**: This analysis directly supports climate adaptation
  planning (SDG 13.1) and marine ecosystem resilience monitoring (SDG 14.2).

**Limitations:**
- **Single-week snapshot** it cannot distinguish an emerging event from a
  seasonal or multi-week pattern.
- **Satellite-derived heat stress** is a proxy indicator, not a direct
  measurement of coral bleaching.
- **0.05° resolution (~5 km)** may smooth sub-reef variability.
- **Latitude bands (Z1–Z5, 3° each)** are an analytical convention defined for
  this study; they are not official GBR management zones.
""")

st.markdown("---")
st.caption(
    f"Data: NOAA Coral Reef Watch Marine Heatwave Watch (5 km, daily). "
    f"Snapshot: 17–23 September 2026."
)
