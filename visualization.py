import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Load & clean (same as before) 
df = pd.read_csv("marine_heatwave.csv", skiprows=[1])
df = df.dropna(subset=["heatwave_category"])
df = df[df["mask"] == 0]
df = df[df["heatwave_category"].isin([0, 1])]

# build persistence
persistence = (
    df.groupby(["latitude", "longitude"], as_index=False)["heatwave_category"]
      .sum()
      .rename(columns={"heatwave_category": "days_hot"})
)

# How many days in the dataset overall (should be 7)
n_days = df["time"].nunique()
print(f"Days in dataset: {n_days}")
print(f"Pixels ever hot: {(persistence.days_hot > 0).sum():,}")
print(persistence.days_hot.value_counts().sort_index())

# plot
fig, ax = plt.subplots(figsize=(12, 9), dpi=150)

# background = all analyzed pixels in light grey
ax.scatter(df["longitude"], df["latitude"],
           s=1, c="#e0e0e0", marker="s", linewidths=0, zorder=1)

# overlay colored by persistence (only pixels hot at least once)
hot = persistence[persistence.days_hot > 0]
sc = ax.scatter(hot["longitude"], hot["latitude"],
                c=hot["days_hot"], cmap="Reds",
                s=8, marker="s", linewidths=0,
                vmin=0, vmax=n_days, zorder=2)

cbar = plt.colorbar(sc, ax=ax, ticks=range(0, n_days + 1))
cbar.set_label("Days flagged as heatwave (out of 7)", fontsize=11)

ax.set_xlabel("Longitude (°E)", fontsize=12)
ax.set_ylabel("Latitude (°N)", fontsize=12)
ax.set_title(
    "Marine Heatwave Persistence — Great Barrier Reef\n"
    "2026-09-17 → 2026-09-23 (7 daily snapshots)",
    fontsize=14, fontweight="bold"
)
ax.set_aspect("equal")
ax.grid(True, linestyle=":", alpha=0.4)

plt.tight_layout()
plt.savefig("mhw_persistence.png", dpi=300, bbox_inches="tight")
plt.show()

times = sorted(df["time"].unique())
fig, axes = plt.subplots(2, 4, figsize=(20, 10), dpi=120)
axes = axes.flatten()

for i, t in enumerate(times):
    day = df[df["time"] == t]
    ax = axes[i]

    ax.scatter(day.loc[day.heatwave_category == 0, "longitude"],
               day.loc[day.heatwave_category == 0, "latitude"],
               s=1, c="#e0e0e0", marker="s", linewidths=0)
    ax.scatter(day.loc[day.heatwave_category == 1, "longitude"],
               day.loc[day.heatwave_category == 1, "latitude"],
               s=4, c="#d62728", marker="s", linewidths=0)

    n_hw = (day.heatwave_category == 1).sum()
    ax.set_title(f"{t[:10]}\nHW pixels: {n_hw:,}", fontsize=10)
    ax.set_aspect("equal")
    ax.tick_params(labelsize=7)

# turn off the 8th empty subplot
for j in range(len(times), len(axes)):
    axes[j].axis("off")

fig.suptitle("Daily Marine Heatwave Evolution — GBR, 2026-09-17 → 2026-09-23",
             fontsize=15, fontweight="bold")
plt.tight_layout()
plt.savefig("mhw_week_panels.png", dpi=300, bbox_inches="tight")
plt.show()

print(persistence.days_hot.value_counts().sort_index())
print(df[df.heatwave_category == 1].groupby("time").size())


core = persistence[persistence.days_hot >= 5]

print("Persistent core (>=5 days hot)")
print(f"Pixels:    {len(core)}")
print(f"Lat range: {core.latitude.min():.3f}  to  {core.latitude.max():.3f}")
print(f"Lon range: {core.longitude.min():.3f}  to  {core.longitude.max():.3f}")
print(f"Centroid:  ({core.latitude.mean():.3f}, {core.longitude.mean():.3f})")

print("\n Full-week core (7/7 days)")
core7 = persistence[persistence.days_hot == 7]
print(f"Pixels:    {len(core7)}")
print(f"Lat range: {core7.latitude.min():.3f}  to  {core7.latitude.max():.3f}")
print(f"Lon range: {core7.longitude.min():.3f}  to  {core7.longitude.max():.3f}")
print(f"Centroid:  ({core7.latitude.mean():.3f}, {core7.longitude.mean():.3f})")


# centroid of HW pixels per day
for t in sorted(df["time"].unique()):
    day = df[(df["time"] == t) & (df["heatwave_category"] == 1)]
    if len(day) == 0:
        continue
    print(f"{t[:10]}  n={len(day):4d}  "
          f"lat={day.latitude.mean():7.3f}  "
          f"lon={day.longitude.mean():7.3f}")


# block 2
bins = [-25, -22, -19, -16, -13, -10]
labels = ["Z1 (-25 to -22)", "Z2 (-22 to -19)", "Z3 (-19 to -16)",
          "Z4 (-16 to -13)", "Z5 (-13 to -10)"]
df["zone"] = pd.cut(df["latitude"], bins=bins, labels=labels, right=False)

pivot = (df.groupby(["zone", "time"], observed=True)["heatwave_category"]
           .mean().mul(100).round(2).unstack("time"))
pivot.columns = [c[:10] for c in pivot.columns]
print(pivot)

# block 3
counts = (df[df.heatwave_category == 1]
            .groupby(["zone", "time"], observed=True).size()
            .unstack("time"))
counts.columns = [c[:10] for c in counts.columns]
print(counts.fillna(0).astype(int))

# block 4
print(df.groupby("zone", observed=True).size())