# 🌊 Marine Heatwave Dashboard — Great Barrier Reef

**Monitoring active heat stress in the southern Great Barrier Reef using NOAA satellite data (17–23 September 2026).**

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://gbr-mhw-dashboard.streamlit.app)

---

## Climate & SDG Context

Oceans absorb over 90% of excess heat from climate change, and marine heatwaves are prolonged periods of anomalously warm water that drive mass coral bleaching. The Great Barrier Reef has experienced repeated mass bleaching events in recent years, with a **mass bleaching event confirmed in September 2026** — the seventh since 1998 [citation:13]. Some areas of the Marine Park recorded water temperatures **2–4°C above average** [citation:6].

This dashboard supports:
- **SDG 13 (Climate Action)** — monitoring climate-related hazards and building adaptive capacity [citation:17]
- **SDG 14 (Life Below Water)** — tracking threats to marine ecosystems and informing conservation priorities, particularly target 14.2 on protecting marine ecosystems and strengthening their resilience [citation:17]

---

## What This Dashboard Shows

A **single-week snapshot** (17–23 September 2026) of NOAA Coral Reef Watch's Daily Global 5km Marine Heatwave Watch product for the Great Barrier Reef region.

**Key finding:** As of 23 September 2026, **3.75% of monitored waters in the southern GBR (−25°S to −22°S)** remain under active marine heat stress — down from a peak of 5.86% within the observation window — with a **persistent 103-pixel core** heat-stressed on all seven days.

---

## Data Source

**NOAA Coral Reef Watch** — Daily Global 5km Satellite Monitoring Marine Heatwave Watch [citation:5][citation:12]

- **Product**: Marine heatwave categories derived from CoralTemp satellite SST
- **Resolution**: 5 km global, daily
- **Method**: Hobday et al. (2018) marine heatwave algorithm applied to CRW's CoralTemp SST product 
- **Categories**: 0 (none), 1 (Moderate), 2 (Strong), 3 (Severe), 4 (Extreme), 5 (beyond Extreme)

**Snapshot date:** 2026-09-17 → 2026-09-23 (7 daily observations)
**Region:** 145°E–155°E, 10°S–25°S (Great Barrier Reef)

---

## Methodology

1. **Cleaning**: Filtered to analyzed ocean pixels (`mask = 0`), dropped NaNs, retained only valid heatwave categories (0 or 1).
2. **Zone binning**: Latitude bands of 3° each: Z1 (−25 to −22), Z2 (−22 to −19), Z3 (−19 to −16), Z4 (−16 to −13), Z5 (−13 to −10).
3. **Persistence calculation**: For each (lat, lon) pixel, summed heatwave flags across all 7 days.
4. **Metrics**: Heatwave percentage = (heatwave pixels / total analyzed pixels) × 100.

---

## How to Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py
