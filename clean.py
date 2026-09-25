import pandas as pd

# cleaning the dataset

df = pd.read_csv("marine_heatwave.csv", skiprows=[1])  
df = df.dropna(subset=["heatwave_category"])                 
df = df[df["mask"] == 0]                                           
df = df[df["heatwave_category"].isin([0, 1])]                       
print(f"Clean rows: {len(df):,}")
print(df["heatwave_category"].value_counts())

# binning into 5 zones

import numpy as np

bins = [-25, -22, -19, -16, -13, -10]
labels = ["Z1 (-25 to -22)", "Z2 (-22 to -19)", "Z3 (-19 to -16)",
          "Z4 (-16 to -13)", "Z5 (-13 to -10)"]

df["zone"] = pd.cut(df["latitude"], bins=bins, labels=labels, right=False)

# computing percentage heatwave

risk = df.groupby("zone", observed=True).agg(
    total_pixels=("heatwave_category", "size"),
    hw_pixels=("heatwave_category", lambda x: (x == 1).sum())
)
risk["pct_hw"] = (risk["hw_pixels"] / risk["total_pixels"] * 100).round(2)
risk = risk.sort_values("pct_hw", ascending=False)

print(risk)