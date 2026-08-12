

import os
import pandas as pd

RAW_DIR = "data/raw"
PROCESSED_DIR = "data/processed"

os.makedirs(PROCESSED_DIR, exist_ok=True)

def load_fbref_csv(filename):
    path = os.path.join(RAW_DIR, filename)
    return pd.read_csv(path, header=1)

standard = load_fbref_csv("newcastle_standard_2025_26.csv")
shooting = load_fbref_csv("newcastle_shooting_2025_26.csv")
playing_time = load_fbref_csv("newcastle_playing_time_2025_26.csv")
misc = load_fbref_csv("newcastle_misc_2025_26.csv")

# Remove FBref summary rows
for df in [standard, shooting, playing_time, misc]:
    df.drop(
        df[df["Player"].isin(["Squad Total", "Opponent Total"])].index,
        inplace=True
    )

print("Standard:", standard.shape)
print("Shooting:", shooting.shape)
print("Playing time:", playing_time.shape)
print("Misc:", misc.shape)

print("\nStandard columns:")
print(standard.columns.tolist())

standard.to_csv("data/processed/newcastle_standard_clean.csv", index=False)
shooting.to_csv("data/processed/newcastle_shooting_clean.csv", index=False)
playing_time.to_csv("data/processed/newcastle_playing_time_clean.csv", index=False)
misc.to_csv("data/processed/newcastle_misc_clean.csv", index=False)

print("\nClean files saved to data/processed/")

# Merge player tables
merged = standard.merge(
    shooting[["Player", "Sh", "SoT", "SoT%", "Sh/90", "SoT/90", "G/Sh", "G/SoT"]],
    on="Player",
    how="left"
)

merged = merged.merge(
    playing_time[["Player", "Mn/MP", "Min%", "Mn/Start", "Compl", "Subs", "Mn/Sub", "unSub"]],
    on="Player",
    how="left"
)

merged = merged.merge(
    misc[["Player", "Fls", "Fld", "Off", "Crs", "Int", "TklW"]],
    on="Player",
    how="left"
)

merged.to_csv("data/processed/newcastle_player_master.csv", index=False)

print("\nMaster player dataset:", merged.shape)
print("Saved: data/processed/newcastle_player_master.csv")

strikers = merged[
    merged["Player"].isin(["Nick Woltemade", "Yoane Wissa", "William Osula"])
].copy()

strikers.to_csv(
    "data/processed/newcastle_striker_benchmarks.csv",
    index=False
)

print("\nStriker benchmarks:")
print(strikers[["Player", "Age", "Min", "90s", "Gls", "Ast", "Sh/90", "SoT/90"]])

print("\nSaved: data/processed/newcastle_striker_benchmarks.csv")

benchmark_cols = ["Age", "Min", "90s", "Gls", "Ast", "Sh/90", "SoT/90"]

benchmark_profile = strikers[benchmark_cols].mean(numeric_only=True)

print("\nAverage striker benchmark:")
print(benchmark_profile)

benchmark_profile.to_csv(
    "data/processed/newcastle_striker_benchmark_profile.csv",
    header=["Benchmark"]
)

print("\nSaved: data/processed/newcastle_striker_benchmark_profile.csv")


# -----------------------------
# Eredivisie player dataset
# -----------------------------

ered_standard = pd.read_csv(
    "data/raw/eredivisie_standard_2025_26.csv",
    header=1
)

ered_shooting = pd.read_csv(
    "data/raw/eredivisie_shooting_2025_26.csv",
    header=1
)

ered_playing = pd.read_csv(
    "data/raw/eredivisie_playing_time_2025_26.csv",
    header=1
)

ered_misc = pd.read_csv(
    "data/raw/eredivisie_misc_2025_26.csv",
    header=1
)

# Remove repeated FBref header/summary rows
for df in [ered_standard, ered_shooting, ered_playing, ered_misc]:
    df.drop(
        df[df["Player"].isin(["Player", "Squad Total", "Opponent Total"])].index,
        inplace=True
    )

print("\nEredivisie cleaned shapes:")
print("Standard:", ered_standard.shape)
print("Shooting:", ered_shooting.shape)
print("Playing time:", ered_playing.shape)
print("Misc:", ered_misc.shape)

# Merge Eredivisie player tables
ered_merged = ered_standard.merge(
    ered_shooting[
        ["Player", "Squad", "Sh", "SoT", "SoT%", "Sh/90", "SoT/90", "G/Sh", "G/SoT"]
    ],
    on=["Player", "Squad"],
    how="left"
)

ered_merged = ered_merged.merge(
    ered_playing[
        ["Player", "Squad", "Mn/MP", "Min%", "Mn/Start", "Compl", "Subs", "Mn/Sub", "unSub"]
    ],
    on=["Player", "Squad"],
    how="left"
)

ered_merged = ered_merged.merge(
    ered_misc[
        ["Player", "Squad", "Fls", "Fld", "Off", "Crs", "Int", "TklW"]
    ],
    on=["Player", "Squad"],
    how="left"
)

print("\nEredivisie master shape:", ered_merged.shape)
print(ered_merged[["Player", "Squad", "Pos", "Age", "Min", "Gls", "Sh/90", "SoT/90"]].head(10))

ered_merged.to_csv(
    "data/processed/eredivisie_player_master.csv",
    index=False
)

print("\nSaved: data/processed/eredivisie_player_master.csv")
