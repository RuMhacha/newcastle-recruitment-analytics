import pandas as pd
import numpy as np

# ============================================================
# LOAD ENRICHED RECRUITMENT DATABASE
# ============================================================

FILE = "data/processed/recruitment_metrics_enriched_2025_26.csv"

df = pd.read_csv(FILE)

print("=" * 60)
print("NEWCASTLE UNITED RECRUITMENT ANALYSIS")
print("=" * 60)

print(f"\nPlayers loaded: {len(df)}")
print(f"Columns loaded: {len(df.columns)}")

print("\nPosition groups:")
print(df["Position_Group"].value_counts())

print("\nCareer stages:")
print(df["Career_Stage"].value_counts())

# ============================================================
# NEWCASTLE RECRUITMENT BRIEFS
# ============================================================

RECRUITMENT_BRIEFS = {

    "Goal Threat Forward": {
        "position": "Attacker",
        "score": "Attacker_Scorer",
        "max_age": 27,
    },

    "Creative Forward": {
        "position": "Attacker",
        "score": "Attacker_Creator",
        "max_age": 27,
    },

    "High-Intensity Forward": {
        "position": "Attacker",
        "score": "Attacker_TwoWay",
        "max_age": 27,
    },

    "Creative Midfielder": {
        "position": "Midfielder",
        "score": "Midfielder_Creator",
        "max_age": 27,
    },

    "Two-Way Midfielder": {
        "position": "Midfielder",
        "score": "Midfielder_TwoWay",
        "max_age": 27,
    },

    "Defensive Midfielder": {
        "position": "Midfielder",
        "score": "Midfielder_BallWinner",
        "max_age": 27,
    },

    "Aggressive Defender": {
        "position": "Defender",
        "score": "Defender_Stopper",
        "max_age": 27,
    },

    "Two-Way Defender": {
        "position": "Defender",
        "score": "Defender_TwoWay",
        "max_age": 27,
    },
}

# ============================================================
# GENERATE NEWCASTLE SHORTLISTS
# ============================================================

display_cols = [
    "Player",
    "Squad",
    "League",
    "Age",
    "Min",
    "Goal_Threat",
    "Creation",
    "Ball_Winning",
]

for brief_name, brief in RECRUITMENT_BRIEFS.items():

    pool = df[
        (df["Position_Group"] == brief["position"])
        & (df["Age"].notna())
        & (df["Age"] <= brief["max_age"])
    ].copy()

    pool = pool.sort_values(
        brief["score"],
        ascending=False
    )

    print("\n" + "=" * 70)
    print(f"NEWCASTLE BRIEF: {brief_name.upper()}")
    print("=" * 70)

    print(
        pool[
            display_cols + [brief["score"]]
        ]
        .head(15)
        .round(2)
        .to_string(index=False)
    )


# ============================================================
# LEAGUE CONTEXT
# ============================================================

print("\n" + "=" * 70)
print("LEAGUE CONTEXT")
print("=" * 70)

ROLE_COLUMNS = {
    "Attacker_Scorer": "Attacker",
    "Attacker_Creator": "Attacker",
    "Attacker_TwoWay": "Attacker",
    "Midfielder_Creator": "Midfielder",
    "Midfielder_BallWinner": "Midfielder",
    "Midfielder_TwoWay": "Midfielder",
    "Defender_Stopper": "Defender",
    "Defender_TwoWay": "Defender",
}

for role, position in ROLE_COLUMNS.items():

    position_mask = df["Position_Group"] == position

    # Cross-league percentile:
    # ranked against every eligible player in the same position group
    df.loc[position_mask, f"{role}_PoolPct"] = (
        df.loc[position_mask, role]
        .rank(pct=True) * 100
    )

    # Within-league percentile:
    # ranked only against same-position players from the same league
    df.loc[position_mask, f"{role}_LeaguePct"] = (
        df.loc[position_mask]
        .groupby("League")[role]
        .rank(pct=True) * 100
    )

# ============================================================
# CONTEXT LABEL
# ============================================================

def context_label(pool_pct, league_pct):
    if pd.isna(pool_pct) or pd.isna(league_pct):
        return "Insufficient Data"

    if pool_pct >= 90:
        return "Elite Across Pool"

    if pool_pct >= 75 and league_pct >= 90:
        return "League Standout"

    if pool_pct >= 75:
        return "Strong Cross-League"

    if league_pct >= 90:
        return "Domestic Standout"

    return "Monitor"

# ============================================================
# NEWCASTLE SHORTLISTS WITH LEAGUE CONTEXT
# ============================================================

for brief_name, brief in RECRUITMENT_BRIEFS.items():

    role = brief["score"]

    pool_pct_col = f"{role}_PoolPct"
    league_pct_col = f"{role}_LeaguePct"

    pool = df[
        (df["Position_Group"] == brief["position"])
        & (df["Age"].notna())
        & (df["Age"] <= brief["max_age"])
    ].copy()

    pool["Context"] = pool.apply(
        lambda row: context_label(
            row[pool_pct_col],
            row[league_pct_col]
        ),
        axis=1
    )

    pool = pool.sort_values(
        pool_pct_col,
        ascending=False
    )

    print("\n" + "=" * 70)
    print(f"LEAGUE-CONTEXT BRIEF: {brief_name.upper()}")
    print("=" * 70)

    columns = [
        "Player",
        "Squad",
        "League",
        "Age",
        "Min",
        role,
        pool_pct_col,
        league_pct_col,
        "Context",
    ]

    print(
        pool[columns]
        .head(15)
        .round(2)
        .to_string(index=False)
    )


# ============================================================
# NEWCASTLE CANDIDATE TIERS
# ============================================================

print("\n" + "=" * 70)
print("NEWCASTLE CANDIDATE TIERS")
print("=" * 70)

def candidate_tier(age, minutes, pool_pct, league_pct):
    if pd.isna(age) or pd.isna(pool_pct) or pd.isna(league_pct):
        return "Insufficient Data"

    if (
        pool_pct >= 95
        and league_pct >= 90
        and minutes >= 1200
        and age <= 23
    ):
        return "Priority Target"

    if (
        pool_pct >= 90
        and league_pct >= 85
        and minutes >= 1000
        and age <= 25
    ):
        return "Strong Target"

    if (
        pool_pct >= 80
        and minutes >= 900
        and age <= 27
    ):
        return "Scout Further"

    return "Monitor"

# ============================================================
# APPLY TIERS TO EACH RECRUITMENT BRIEF
# ============================================================

for brief_name, brief in RECRUITMENT_BRIEFS.items():

    role = brief["score"]

    pool_pct_col = f"{role}_PoolPct"
    league_pct_col = f"{role}_LeaguePct"

    pool = df[
        (df["Position_Group"] == brief["position"])
        & (df["Age"].notna())
        & (df["Age"] <= brief["max_age"])
    ].copy()

    pool["Candidate_Tier"] = pool.apply(
        lambda row: candidate_tier(
            row["Age"],
            row["Min"],
            row[pool_pct_col],
            row[league_pct_col],
        ),
        axis=1
    )

    tier_order = {
        "Priority Target": 1,
        "Strong Target": 2,
        "Scout Further": 3,
        "Monitor": 4,
    }

    pool["Tier_Order"] = pool["Candidate_Tier"].map(tier_order)

    pool = pool.sort_values(
        ["Tier_Order", pool_pct_col],
        ascending=[True, False]
    )

    print("\n" + "=" * 70)
    print(f"CANDIDATE TIERS: {brief_name.upper()}")
    print("=" * 70)

    print(
        pool[
            [
                "Player",
                "Squad",
                "League",
                "Age",
                "Min",
                role,
                pool_pct_col,
                league_pct_col,
                "Candidate_Tier",
            ]
        ]
        .head(20)
        .round(2)
        .to_string(index=False)

)

# ============================================================
# CANDIDATE TIER SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("NEWCASTLE RECRUITMENT FUNNEL SUMMARY")
print("=" * 70)

for brief_name, brief in RECRUITMENT_BRIEFS.items():

    role = brief["score"]

    pool_pct_col = f"{role}_PoolPct"
    league_pct_col = f"{role}_LeaguePct"

    pool = df[
        (df["Position_Group"] == brief["position"])
        & (df["Age"].notna())
        & (df["Age"] <= brief["max_age"])
    ].copy()

    pool["Candidate_Tier"] = pool.apply(
        lambda row: candidate_tier(
            row["Age"],
            row["Min"],
            row[pool_pct_col],
            row[league_pct_col],
        ),
        axis=1
    )

    counts = pool["Candidate_Tier"].value_counts()

    print(f"\n{brief_name}")
    print("-" * len(brief_name))

    for tier in [
        "Priority Target",
        "Strong Target",
        "Scout Further",
        "Monitor"
    ]:
        print(f"{tier:<18}: {counts.get(tier, 0)}")


# ============================================================
# BUILD FINAL TIERED RECRUITMENT DATASET
# ============================================================

print("\n" + "=" * 70)
print("BUILDING FINAL TIERED RECRUITMENT DATASET")
print("=" * 70)

final_df = df.copy()

for brief_name, brief in RECRUITMENT_BRIEFS.items():

    role = brief["score"]

    pool_pct_col = f"{role}_PoolPct"
    league_pct_col = f"{role}_LeaguePct"
    tier_col = f"{role}_Tier"

    # Default value
    final_df[tier_col] = "Not Eligible"

    mask = (
        (final_df["Position_Group"] == brief["position"])
        & (final_df["Age"].notna())
        & (final_df["Age"] <= brief["max_age"])
    )

    final_df.loc[mask, tier_col] = final_df.loc[mask].apply(
        lambda row: candidate_tier(
            row["Age"],
            row["Min"],
            row[pool_pct_col],
            row[league_pct_col],
        ),
        axis=1
    )

# ============================================================
# SAVE FINAL NEWCASTLE RECRUITMENT DATABASE
# ============================================================

output_file = "data/processed/newcastle_recruitment_2025_26.csv"

final_df.to_csv(output_file, index=False)

print("\n" + "=" * 70)
print("NEWCASTLE RECRUITMENT DATABASE SAVED")
print("=" * 70)

print(f"Saved to: {output_file}")
print(f"Players: {len(final_df)}")
print(f"Columns: {len(final_df.columns)}")


