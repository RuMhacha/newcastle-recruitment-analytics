import pandas as pd
from pathlib import Path

# Project folders
RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")

# Leagues included in the recruitment database
LEAGUES = {
    "eredivisie": {
        "name": "Eredivisie",
        "prefix": "eredivisie",
    },
    "belgian_pro_league": {
        "name": "Belgian Pro League",
        "prefix": "belgian_pro_league",
    },
   "german_bundesliga": {
        "name": "German Bundesliga",
        "prefix": "german_bundesliga",
    },
    "austrian_bundesliga": {
        "name": "Austrian Bundesliga",
        "prefix": "austrian_bundesliga",
    },
    "portuguese_primeira_liga": {
        "name": "Portuguese Primeira Liga",
        "prefix": "portuguese_primeira_liga",
    },
    "danish_superliga": {
        "name": "Danish Superliga",
        "prefix": "danish_superliga",
    },
}

TABLES = ["standard", "shooting", "playing_time", "misc"]


def load_league_tables(league_key):
    """Load the four FBref tables for one league."""

    config = LEAGUES[league_key]
    prefix = config["prefix"]

    tables = {}

    for table in TABLES:
        path = RAW_DIR / f"{prefix}_{table}_2025_26.csv"

        print(f"Loading: {path}")

        tables[table] = pd.read_csv(path, header=1)

    return tables


# Clean FBref tables
# --------------------------------------------------

def clean_fbref_table(df):
    df = df.copy()

    if "Player" in df.columns:
        df = df[
            ~df["Player"].isin(
                ["Player", "Squad Total", "Opponent Total"]
            )
        ].copy()

    return df
# Load and clean every league
all_leagues = {}

for league_key, config in LEAGUES.items():
    print(f"\n{'=' * 50}")
    print(f"Processing {config['name']}")
    print("=" * 50)

    raw_tables = load_league_tables(league_key)

    clean_tables = {}
    for table_name, df in raw_tables.items():
        clean_tables[table_name] = clean_fbref_table(df)

    all_leagues[league_key] = clean_tables

    print(f"\n{config['name']} cleaned tables:")
    for table_name, df in clean_tables.items():
        print(table_name, df.shape)


# Validate columns across leagues
print("\n" + "=" * 50)
print("VALIDATING COLUMN STRUCTURE")
print("=" * 50)

for table_name in TABLES:
    reference_cols = list(all_leagues["eredivisie"][table_name].columns)

    print(f"\n{table_name}:")

    for league_key, tables in all_leagues.items():
        cols = list(tables[table_name].columns)

        if cols == reference_cols:
            print(f"  {league_key}: OK")
        else:
            print(f"  {league_key}: COLUMN MISMATCH")


# Merge all leagues into master tables
master_tables = {}

for table_name in TABLES:
    league_frames = []

    for league_key, config in LEAGUES.items():
        df = all_leagues[league_key][table_name].copy()

        # Keep league identity after combining datasets
        df["League"] = config["name"]

        league_frames.append(df)

    master_tables[table_name] = pd.concat(
        league_frames,
        ignore_index=True
    )

print("\n" + "=" * 50)
print("MASTER TABLES")
print("=" * 50)

for table_name, df in master_tables.items():
    print(table_name, df.shape)

print("\n" + "=" * 50)
print("CHECKING PLAYER IDENTIFIERS")
print("=" * 50)

for table_name, df in master_tables.items():
    print(f"\n{table_name}:")
    print(df.columns.tolist())

print("\n" + "=" * 50)
print("CHECKING DUPLICATE PLAYER KEYS")
print("=" * 50)

key_cols = ["Player", "Squad", "League"]

for table_name, df in master_tables.items():
    duplicate_count = df.duplicated(subset=key_cols).sum()
    unique_count = df.drop_duplicates(subset=key_cols).shape[0]

    print(f"\n{table_name}:")
    print(f"  rows: {len(df)}")
    print(f"  unique player keys: {unique_count}")
    print(f"  duplicate keys: {duplicate_count}")

print("\n" + "=" * 50)
print("DUPLICATE PLAYER KEYS")
print("=" * 50)

key_cols = ["Player", "Squad", "League"]

for table_name, df in master_tables.items():
    dupes = df[df.duplicated(subset=key_cols, keep=False)]

    if not dupes.empty:
        print(f"\n{table_name}:")
        print(
            dupes[
                ["Player", "Squad", "League", "Pos", "Age"]
            ].sort_values(key_cols)
        )

print("\n" + "=" * 50)
print("CHECKING EXTENDED PLAYER KEY")
print("=" * 50)

key_cols = ["Player", "Squad", "League", "Born"]

for table_name, df in master_tables.items():
    duplicate_count = df.duplicated(subset=key_cols).sum()

    print(f"{table_name}: {duplicate_count} duplicate keys")

print("\n" + "=" * 50)
print("BUILDING PLAYER MASTER")
print("=" * 50)

merge_keys = ["Player", "Squad", "League", "Born"]

player_master = master_tables["standard"].copy()

for table_name in ["shooting", "playing_time", "misc"]:
    other = master_tables[table_name].copy()

    # Remove columns already supplied by the standard table,
    # except for our merge keys.
    duplicate_cols = [
        col for col in other.columns
        if col in player_master.columns and col not in merge_keys
    ]

    other = other.drop(columns=duplicate_cols)

    player_master = player_master.merge(
        other,
        on=merge_keys,
        how="left",
        validate="one_to_one"
    )

    print(f"After {table_name}: {player_master.shape}")

print("\nFinal player master:")
print(player_master.shape)
print(f"Unique players: {player_master[merge_keys].drop_duplicates().shape[0]}")


print("\n" + "=" * 50)
print("FINAL MASTER QUALITY CHECK")
print("=" * 50)

print(f"Rows: {len(player_master)}")
print(f"Columns: {len(player_master.columns)}")

print("\nMissing values by column:")
missing = player_master.isna().sum()
print(missing[missing > 0].sort_values(ascending=False))


# Save final multi-league player database
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

output_path = PROCESSED_DIR / "player_master_2025_26.csv"

player_master.to_csv(output_path, index=False)

print("\n" + "=" * 50)
print("PLAYER MASTER SAVED")
print("=" * 50)
print(f"Saved to: {output_path}")
print(f"Players: {len(player_master)}")
print(f"Columns: {len(player_master.columns)}")


