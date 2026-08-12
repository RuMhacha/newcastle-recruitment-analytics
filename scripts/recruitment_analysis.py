import pandas as pd
from pathlib import Path

# --------------------------------------------------
# Load player master
# --------------------------------------------------

DATA_PATH = Path("data/processed/player_master_2025_26.csv")

players = pd.read_csv(DATA_PATH)

print("=" * 50)
print("RECRUITMENT DATABASE")
print("=" * 50)

print(f"Players: {len(players)}")
print(f"Columns: {len(players.columns)}")

print("\nPlayers by league:")
print(
    players.groupby("League")
    .size()
    .sort_values(ascending=False)
)

print("\nPosition values:")
print(players["Pos"].value_counts(dropna=False))

# --------------------------------------------------
# Create broad recruitment position groups
# --------------------------------------------------

def assign_position_group(pos):
    if pd.isna(pos):
        return "Unknown"

    pos = str(pos)

    if pos == "GK":
        return "Goalkeeper"

    if pos in ["DF", "DFMF", "MFDF"]:
        return "Defender"

    if pos in ["MF"]:
        return "Midfielder"

    if pos in ["FW", "MFFW", "FWMF", "DFFW"]:
        return "Attacker"

    return "Unknown"


players["Position_Group"] = players["Pos"].apply(assign_position_group)

print("\nRecruitment position groups:")
print(players["Position_Group"].value_counts())

# --------------------------------------------------
# Inspect available recruitment metrics
# --------------------------------------------------

print("\n" + "=" * 50)
print("AVAILABLE COLUMNS")
print("=" * 50)

for i, column in enumerate(players.columns, start=1):
    print(f"{i:>2}. {column}")


# --------------------------------------------------
# Inspect column data types
# --------------------------------------------------

print("\n" + "=" * 50)
print("COLUMN DATA TYPES")
print("=" * 50)

print(players.dtypes.to_string())

