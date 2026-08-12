import pandas as pd

# ============================================================
# NEWCASTLE UNITED RECRUITMENT ANALYTICS
# Shortlist Analysis
# ============================================================

DATA_PATH = "data/processed/newcastle_recruitment_2025_26.csv"

df = pd.read_csv(DATA_PATH)

print("\n" + "=" * 60)
print("NEWCASTLE UNITED — SHORTLIST ANALYSIS")
print("=" * 60)

print(f"\nPlayers loaded: {len(df)}")
print(f"Columns loaded: {len(df.columns)}")

print("\nPosition groups:")
print(df["Position_Group"].value_counts())

print("\nDataset successfully loaded.")

# ============================================================
# REUSABLE SHORTLIST FUNCTION
# ============================================================

def create_shortlist(
    data,
    position_group,
    score_column,
    tier_column,
    max_age=None,
    min_minutes=900,
    tiers=("Priority Target", "Strong Target"),
    top_n=15
):
    shortlist = data.copy()

    # Position filter
    shortlist = shortlist[
        shortlist["Position_Group"] == position_group
    ]

    # Minimum minutes
    shortlist = shortlist[
        shortlist["Min"] >= min_minutes
    ]

    # Optional age filter
    if max_age is not None:
        shortlist = shortlist[
            shortlist["Age"] <= max_age
        ]

    # Recruitment tier filter
    shortlist = shortlist[
        shortlist[tier_column].isin(tiers)
    ]

    # Rank strongest candidates first
    shortlist = shortlist.sort_values(
        score_column,
        ascending=False
    )

    return shortlist.head(top_n)

# ============================================================
# TEST BRIEF — U23 TWO-WAY MIDFIELDERS
# ============================================================

u23_two_way_midfielders = create_shortlist(
    data=df,
    position_group="Midfielder",
    score_column="Midfielder_TwoWay",
    tier_column="Midfielder_TwoWay_Tier",
    max_age=23,
    min_minutes=900,
    top_n=15
)

display_columns = [
    "Player",
    "Squad",
    "League",
    "Age",
    "Min",
    "Goal_Threat",
    "Creation",
    "Ball_Winning",
    "Midfielder_TwoWay",
    "Midfielder_TwoWay_Tier"
]

print("\n" + "=" * 70)
print("NEWCASTLE SHORTLIST — U23 TWO-WAY MIDFIELDERS")
print("=" * 70)

print(
    u23_two_way_midfielders[display_columns]
    .to_string(index=False)
)

# ============================================================
# NEWCASTLE RECRUITMENT ROLE CONFIGURATION
# ============================================================

recruitment_roles = {
    "Goal Threat Forward": {
        "position": "Attacker",
        "score": "Attacker_Scorer",
        "tier": "Attacker_Scorer_Tier"
    },

    "Creative Forward": {
        "position": "Attacker",
        "score": "Attacker_Creator",
        "tier": "Attacker_Creator_Tier"
    },

    "High-Intensity Forward": {
        "position": "Attacker",
        "score": "Attacker_TwoWay",
        "tier": "Attacker_TwoWay_Tier"
    },

    "Creative Midfielder": {
        "position": "Midfielder",
        "score": "Midfielder_Creator",
        "tier": "Midfielder_Creator_Tier"
    },

    "Two-Way Midfielder": {
        "position": "Midfielder",
        "score": "Midfielder_TwoWay",
        "tier": "Midfielder_TwoWay_Tier"
    },

    "Defensive Midfielder": {
        "position": "Midfielder",
        "score": "Midfielder_BallWinner",
        "tier": "Midfielder_BallWinner_Tier"
    },

    "Aggressive Defender": {
        "position": "Defender",
        "score": "Defender_Stopper",
        "tier": "Defender_Stopper_Tier"
    },

    "Two-Way Defender": {
        "position": "Defender",
        "score": "Defender_TwoWay",
        "tier": "Defender_TwoWay_Tier"
    }
}

# ============================================================
# GENERATE ROLE SHORTLISTS
# ============================================================

print("\n" + "=" * 70)
print("NEWCASTLE UNITED — RECRUITMENT SHORTLISTS")
print("=" * 70)

for role_name, config in recruitment_roles.items():

    shortlist = create_shortlist(
        data=df,
        position_group=config["position"],
        score_column=config["score"],
        tier_column=config["tier"],
        max_age=25,
        min_minutes=900,
        top_n=10
    )

    print("\n" + "-" * 70)
    print(role_name.upper())
    print("-" * 70)

    role_columns = [
        "Player",
        "Squad",
        "League",
        "Age",
        "Min",
        config["score"],
        config["tier"]
    ]

    print(
        shortlist[role_columns]
        .to_string(index=False)
    )


# ============================================================
# MULTI-ROLE ELITE CANDIDATES
# ============================================================

elite_tiers = ["Priority Target", "Strong Target"]

multi_role_results = []

for role_name, config in recruitment_roles.items():

    role_candidates = df[
        (df["Position_Group"] == config["position"]) &
        (df["Min"] >= 900) &
        (df["Age"] <= 25) &
        (df[config["tier"]].isin(elite_tiers))
    ].copy()

    for _, player in role_candidates.iterrows():
        multi_role_results.append({
            "Player": player["Player"],
            "Squad": player["Squad"],
            "League": player["League"],
            "Age": player["Age"],
            "Role": role_name,
            "Role_Score": player[config["score"]],
            "Tier": player[config["tier"]]
        })

multi_role_df = pd.DataFrame(multi_role_results)

# Count how many elite recruitment roles each player qualifies for
role_counts = (
    multi_role_df
    .groupby(["Player", "Squad", "League", "Age"])
    .agg(
        Elite_Roles=("Role", "nunique"),
        Roles=("Role", lambda x: " | ".join(sorted(set(x)))),
        Average_Role_Score=("Role_Score", "mean"),
        Best_Role_Score=("Role_Score", "max")
    )
    .reset_index()
)

multi_role_candidates = (
    role_counts[
        role_counts["Elite_Roles"] >= 2
    ]
    .sort_values(
        ["Elite_Roles", "Average_Role_Score"],
        ascending=[False, False]
    )
)

print("\n" + "=" * 70)
print("MULTI-ROLE ELITE RECRUITMENT CANDIDATES")
print("=" * 70)

print(
    multi_role_candidates.head(25)
    .to_string(index=False)
)


# ============================================================
# EXPORT RECRUITMENT SHORTLISTS
# ============================================================

import os

output_dir = "data/outputs"
os.makedirs(output_dir, exist_ok=True)

# Save multi-role candidates
role_counts.to_csv(
    f"{output_dir}/multi_role_candidates.csv",
    index=False
)

# Save individual role shortlists
role_definitions = [
    ("Goal Threat Forward", "Attacker_Scorer", "Attacker_Scorer_Tier"),
    ("Creative Forward", "Attacker_Creator", "Attacker_Creator_Tier"),
    ("High-Intensity Forward", "Attacker_TwoWay", "Attacker_TwoWay_Tier"),
    ("Creative Midfielder", "Midfielder_Creator", "Midfielder_Creator_Tier"),
    ("Two-Way Midfielder", "Midfielder_TwoWay", "Midfielder_TwoWay_Tier"),
    ("Defensive Midfielder", "Midfielder_BallWinner", "Midfielder_BallWinner_Tier"),
    ("Aggressive Defender", "Defender_Stopper", "Defender_Stopper_Tier"),
    ("Two-Way Defender", "Defender_TwoWay", "Defender_TwoWay_Tier"),

]

for role_name, score_col, tier_col in role_definitions:
    shortlist = df[
        df[tier_col].isin(["Priority Target", "Strong Target"])
    ].copy()

    shortlist = shortlist.sort_values(
        score_col,
        ascending=False
    )

    safe_name = (
        role_name
        .lower()
        .replace(" ", "_")
        .replace("-", "_")
    )

    shortlist.to_csv(
        f"{output_dir}/{safe_name}_shortlist.csv",
        index=False
    )

print("\n" + "=" * 70)
print("SHORTLIST FILES EXPORTED")
print("=" * 70)
print(f"Output directory: {output_dir}")
print(f"Multi-role candidates: {len(role_counts)}")
print("Individual role shortlists exported:", len(role_definitions))

