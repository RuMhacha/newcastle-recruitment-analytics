import pandas as pd
from pathlib import Path

# --------------------------------------------------
# Load player master
# --------------------------------------------------

MASTER_FILE = Path("data/processed/player_master_2025_26.csv")

df = pd.read_csv(MASTER_FILE)

print("=" * 50)
print("RECRUITMENT METRICS")
print("=" * 50)

print(f"Players loaded: {len(df)}")
print(f"Columns loaded: {len(df.columns)}")

# --------------------------------------------------
# Create position groups
# --------------------------------------------------

def position_group(pos):
    if pd.isna(pos):
        return "Unknown"

    pos = str(pos)

    if pos == "GK":
        return "Goalkeeper"

    if pos in ["DF", "DFMF", "MFDF"]:
        return "Defender"

    if pos == "MF":
        return "Midfielder"

    if pos in ["FW", "MFFW", "FWMF", "DFFW"]:
        return "Attacker"

    return "Unknown"

df["Position_Group"] = df["Pos"].apply(position_group)

# --------------------------------------------------
# Remove goalkeepers
# --------------------------------------------------

outfield = df[df["Position_Group"] != "Goalkeeper"].copy()

print(f"\nOutfield players: {len(outfield)}")

# --------------------------------------------------
# Check minutes
# --------------------------------------------------

print("\nMinutes summary:")
print(outfield["Min"].describe())

print(f"\nOutfield players: {len(outfield)}")

# --------------------------------------------------
# Check minutes
# --------------------------------------------------

print("\nMinutes summary:")
print(outfield["Min"].describe())


# --------------------------------------------------
# Minimum minutes filter
# --------------------------------------------------

MIN_MINUTES = 900

eligible = outfield[
    outfield["Min"] >= MIN_MINUTES
].copy()

print("\n" + "=" * 50)
print("ELIGIBLE RECRUITMENT POOL")
print("=" * 50)

print(f"Minimum minutes: {MIN_MINUTES}")
print(f"Eligible players: {len(eligible)}")

print("\nEligible players by position group:")
print(
    eligible["Position_Group"]
    .value_counts()
)

# --------------------------------------------------
# Create per-90 recruitment metrics
# --------------------------------------------------

PER90_METRICS = {
    "Gls": "Gls_per90",
    "Ast": "Ast_per90",
    "G+A": "GA_per90",
    "G-PK": "NonPKGls_per90",
    "Sh": "Shots_per90",
    "SoT": "SoT_per90_calc",
    "Int": "Int_per90",
    "TklW": "TklW_per90",
    "Crs": "Crs_per90",
    "Fls": "Fls_per90",
    "Fld": "Fld_per90",
}

for source_col, new_col in PER90_METRICS.items():
    eligible[new_col] = (
        eligible[source_col] * 90 / eligible["Min"]
    )

print("\n" + "=" * 50)
print("PER-90 METRICS CREATED")
print("=" * 50)

print(
    eligible[
        [
            "Player",
            "Squad",
            "League",
            "Position_Group",
            "Min",
            "Gls_per90",
            "Ast_per90",
            "Shots_per90",
            "Int_per90",
            "TklW_per90",
        ]
    ].head(10)
)

print("\n" + "=" * 50)
print("PER-90 SANITY CHECK")
print("=" * 50)

eligible["Shots_per90_difference"] = (
    eligible["Shots_per90"] - eligible["Sh/90"]
).abs()

print(
    "Largest difference between calculated Shots/90 "
    "and FBref Sh/90:"
)
print(eligible["Shots_per90_difference"].max())

print("\nCorrected eligible position groups:")
print(eligible["Position_Group"].value_counts())

# ============================================================
# POSITION-SPECIFIC PERCENTILES
# ============================================================

print("\n" + "=" * 50)
print("POSITION-SPECIFIC PERCENTILES")
print("=" * 50)

# Metrics currently available and useful across our three
# outfield recruitment groups.
percentile_metrics = [
    "Gls_per90",
    "Ast_per90",
    "Shots_per90",
    "Int_per90",
    "TklW_per90",
]

# Calculate percentiles WITHIN each position group.
# This prevents attackers being compared directly with
# midfielders or defenders.
for metric in percentile_metrics:
    percentile_col = metric.replace("_per90", "_pct")

    eligible[percentile_col] = (
        eligible
        .groupby("Position_Group")[metric]
        .rank(pct=True) * 100
    )

print("\nPercentile columns created:")
for metric in percentile_metrics:
    print(metric.replace("_per90", "_pct"))

print("\nPercentile ranges:")
percentile_cols = [
    metric.replace("_per90", "_pct")
    for metric in percentile_metrics
]

print(eligible[percentile_cols].describe())

# ============================================================
# VALIDATE PERCENTILES WITH REAL PLAYERS
# ============================================================

print("\n" + "=" * 60)
print("VALIDATING PERCENTILES WITH REAL PLAYERS")
print("=" * 60)

display_cols = [
    "Player",
    "Squad",
    "League",
    "Position_Group",
    "Min",
    "Gls_per90",
    "Gls_pct",
    "Ast_per90",
    "Ast_pct",
    "Shots_per90",
    "Shots_pct",
    "Int_per90",
    "Int_pct",
    "TklW_per90",
    "TklW_pct",
]

# Top scorers among attackers
print("\nTOP 10 ATTACKERS — GOALS/90")
attackers = eligible[
    eligible["Position_Group"] == "Attacker"
]

print(
    attackers
    .sort_values("Gls_pct", ascending=False)
    [display_cols]
    .head(10)
    .to_string(index=False)
)

# Top creators among midfielders
print("\nTOP 10 MIDFIELDERS — ASSISTS/90")
midfielders = eligible[
    eligible["Position_Group"] == "Midfielder"
]

print(
    midfielders
    .sort_values("Ast_pct", ascending=False)
    [display_cols]
    .head(10)
    .to_string(index=False)
)

# Top interceptors among defenders
print("\nTOP 10 DEFENDERS — INTERCEPTIONS/90")
defenders = eligible[
    eligible["Position_Group"] == "Defender"
]

print(
    defenders
    .sort_values("Int_pct", ascending=False)
    [display_cols]
    .head(10)
    .to_string(index=False)
)


# ============================================================
# SAVE RECRUITMENT METRICS DATASET
# ============================================================

output_path = "data/processed/recruitment_metrics_2025_26.csv"

eligible.to_csv(output_path, index=False)

print("\n" + "=" * 60)
print("RECRUITMENT METRICS DATASET SAVED")
print("=" * 60)
print(f"Saved to: {output_path}")
print(f"Players: {len(eligible)}")
print(f"Columns: {len(eligible.columns)}")

# ============================================================
# RECRUITMENT ATTRIBUTE SCORES
# ============================================================

print("\n" + "=" * 60)
print("RECRUITMENT ATTRIBUTE SCORES")
print("=" * 60)

# Goal threat:
# combines actual scoring output with shot volume
eligible["Goal_Threat"] = (
    eligible["Gls_pct"] * 0.60
    + eligible["Shots_pct"] * 0.40
)

# Creation:
# currently based on assists because detailed passing
# and chance-creation data are not yet in the dataset
eligible["Creation"] = eligible["Ast_pct"]

# Ball winning:
# combines interceptions with tackles won
eligible["Ball_Winning"] = (
    eligible["Int_pct"] * 0.50
    + eligible["TklW_pct"] * 0.50
)

attribute_cols = [
    "Goal_Threat",
    "Creation",
    "Ball_Winning",
]

print("\nAttribute score summary:")
print(eligible[attribute_cols].describe().round(2))

# ============================================================
# POSITION-SPECIFIC RECRUITMENT SCORES
# ============================================================

eligible["Recruitment_Score"] = 0.0

# Attackers:
# primarily goal threat, with creation and defensive work
attacker_mask = eligible["Position_Group"] == "Attacker"

eligible.loc[attacker_mask, "Recruitment_Score"] = (
    eligible.loc[attacker_mask, "Goal_Threat"] * 0.60
    + eligible.loc[attacker_mask, "Creation"] * 0.25
    + eligible.loc[attacker_mask, "Ball_Winning"] * 0.15
)

# Midfielders:
# more balanced between creation, goal threat and ball winning
midfielder_mask = eligible["Position_Group"] == "Midfielder"

eligible.loc[midfielder_mask, "Recruitment_Score"] = (
    eligible.loc[midfielder_mask, "Creation"] * 0.40
    + eligible.loc[midfielder_mask, "Ball_Winning"] * 0.35
    + eligible.loc[midfielder_mask, "Goal_Threat"] * 0.25
)

# Defenders:
# ball winning receives the greatest weighting
defender_mask = eligible["Position_Group"] == "Defender"

eligible.loc[defender_mask, "Recruitment_Score"] = (
    eligible.loc[defender_mask, "Ball_Winning"] * 0.65
    + eligible.loc[defender_mask, "Creation"] * 0.20
    + eligible.loc[defender_mask, "Goal_Threat"] * 0.15
)

print("\nRecruitment score summary by position:")
print(
    eligible
    .groupby("Position_Group")["Recruitment_Score"]
    .describe()
    .round(2)
)


# ============================================================
# INITIAL RECRUITMENT SHORTLISTS
# ============================================================

print("\n" + "=" * 60)
print("INITIAL RECRUITMENT SHORTLISTS")
print("=" * 60)

display_cols = [
    "Player",
    "Squad",
    "League",
    "Age",
    "Min",
    "Goal_Threat",
    "Creation",
    "Ball_Winning",
    "Recruitment_Score",
]

for position in ["Attacker", "Midfielder", "Defender"]:

    print(f"\nTOP 15 {position.upper()}S")
    print("-" * 60)

    shortlist = (
        eligible[eligible["Position_Group"] == position]
        .sort_values("Recruitment_Score", ascending=False)
        .head(15)
    )

    print(
        shortlist[display_cols]
        .round(2)
        .to_string(index=False)
    )

# ============================================================
# HIGH-POTENTIAL AGE FILTER
# ============================================================

print("\n" + "=" * 60)
print("U23 RECRUITMENT SHORTLISTS")
print("=" * 60)

young_pool = eligible[
    eligible["Age"].notna()
    & (eligible["Age"] <= 23)
].copy()

print(f"\nU23 eligible players: {len(young_pool)}")

for position in ["Attacker", "Midfielder", "Defender"]:

    print(f"\nTOP 10 U23 {position.upper()}S")
    print("-" * 60)

    shortlist = (
        young_pool[young_pool["Position_Group"] == position]
        .sort_values("Recruitment_Score", ascending=False)
        .head(10)
    )

    print(
        shortlist[display_cols]
        .round(2)
        .to_string(index=False)
    )

# ============================================================
# ROLE-SPECIFIC RECRUITMENT SCORES
# ============================================================

print("\n" + "=" * 60)
print("ROLE-SPECIFIC RECRUITMENT SCORES")
print("=" * 60)

# ------------------------------------------------------------
# ATTACKERS
# ------------------------------------------------------------

# Scoring-forward profile:
# heavily rewards goal threat
eligible["Attacker_Scorer"] = (
    eligible["Goal_Threat"] * 0.70
    + eligible["Creation"] * 0.20
    + eligible["Ball_Winning"] * 0.10
)

# Creative-forward / winger profile:
# places much greater value on creation
eligible["Attacker_Creator"] = (
    eligible["Goal_Threat"] * 0.40
    + eligible["Creation"] * 0.50
    + eligible["Ball_Winning"] * 0.10
)

# High-intensity attacker:
# balances output with defensive work
eligible["Attacker_TwoWay"] = (
    eligible["Goal_Threat"] * 0.45
    + eligible["Creation"] * 0.25
    + eligible["Ball_Winning"] * 0.30
)


# ------------------------------------------------------------
# MIDFIELDERS
# ------------------------------------------------------------

# Creative midfielder
eligible["Midfielder_Creator"] = (
    eligible["Goal_Threat"] * 0.20
    + eligible["Creation"] * 0.55
    + eligible["Ball_Winning"] * 0.25
)

# Ball-winning midfielder
eligible["Midfielder_BallWinner"] = (
    eligible["Goal_Threat"] * 0.10
    + eligible["Creation"] * 0.20
    + eligible["Ball_Winning"] * 0.70
)

# Balanced / two-way midfielder
eligible["Midfielder_TwoWay"] = (
    eligible["Goal_Threat"] * 0.25
    + eligible["Creation"] * 0.35
    + eligible["Ball_Winning"] * 0.40
)


# ------------------------------------------------------------
# DEFENDERS
# ------------------------------------------------------------

# Defensive stopper:
# overwhelmingly driven by ball-winning output
eligible["Defender_Stopper"] = (
    eligible["Goal_Threat"] * 0.05
    + eligible["Creation"] * 0.10
    + eligible["Ball_Winning"] * 0.85
)

# More rounded defender:
# allows attacking contribution to matter slightly more
eligible["Defender_TwoWay"] = (
    eligible["Goal_Threat"] * 0.15
    + eligible["Creation"] * 0.20
    + eligible["Ball_Winning"] * 0.65
)

# ============================================================
# VALIDATE ROLE LEADERS
# ============================================================

role_tests = {
    "Attacker_Scorer": "Attacker",
    "Attacker_Creator": "Attacker",
    "Attacker_TwoWay": "Attacker",
    "Midfielder_Creator": "Midfielder",
    "Midfielder_BallWinner": "Midfielder",
    "Midfielder_TwoWay": "Midfielder",
    "Defender_Stopper": "Defender",
    "Defender_TwoWay": "Defender",
}

role_display = [
    "Player",
    "Squad",
    "League",
    "Age",
    "Min",
    "Goal_Threat",
    "Creation",
    "Ball_Winning",
]

for role, position in role_tests.items():

    print(f"\nTOP 10 — {role}")
    print("-" * 60)

    role_pool = eligible[
        eligible["Position_Group"] == position
    ]

    top_role = (
        role_pool
        .sort_values(role, ascending=False)
        .head(10)
    )

    print(
        top_role[
            role_display + [role]
        ]
        .round(2)
        .to_string(index=False)
    )


# ============================================================
# AGE / CAREER-STAGE SEGMENTATION
# ============================================================

print("\n" + "=" * 60)
print("AGE / CAREER-STAGE SEGMENTATION")
print("=" * 60)

def career_stage(age):
    if pd.isna(age):
        return "Unknown"
    elif age <= 21:
        return "U21 Development"
    elif age <= 24:
        return "22-24 Emerging"
    elif age <= 27:
        return "25-27 Prime"
    else:
        return "28+ Experienced"

eligible["Career_Stage"] = eligible["Age"].apply(career_stage)

print("\nEligible players by career stage:")
print(
    eligible["Career_Stage"]
    .value_counts()
)

print("\nPlayers by position and career stage:")
print(
    pd.crosstab(
        eligible["Position_Group"],
        eligible["Career_Stage"]
    )
)

# ============================================================
# EMERGING-TARGET SHORTLISTS
# ============================================================

print("\n" + "=" * 60)
print("EMERGING TARGETS — AGE 24 OR UNDER")
print("=" * 60)

emerging = eligible[
    eligible["Age"].notna()
    & (eligible["Age"] <= 24)
].copy()

print(f"\nEligible emerging players: {len(emerging)}")

role_shortlists = {
    "Attacker_Scorer": "Attacker",
    "Attacker_Creator": "Attacker",
    "Attacker_TwoWay": "Attacker",
    "Midfielder_Creator": "Midfielder",
    "Midfielder_BallWinner": "Midfielder",
    "Midfielder_TwoWay": "Midfielder",
    "Defender_Stopper": "Defender",
    "Defender_TwoWay": "Defender",
}

shortlist_cols = [
    "Player",
    "Squad",
    "League",
    "Age",
    "Min",
    "Goal_Threat",
    "Creation",
    "Ball_Winning",
]

for role, position in role_shortlists.items():

    print(f"\nTOP 10 U25 — {role}")
    print("-" * 60)

    role_pool = emerging[
        emerging["Position_Group"] == position
    ]

    top_players = (
        role_pool
        .sort_values(role, ascending=False)
        .head(10)
    )

    print(
        top_players[
            shortlist_cols + [role]
        ]
        .round(2)
        .to_string(index=False)
    )

# ============================================================
# SAVE ENRICHED RECRUITMENT DATASET
# ============================================================

final_output = "data/processed/recruitment_metrics_enriched_2025_26.csv"

eligible.to_csv(final_output, index=False)

print("\n" + "=" * 60)
print("ENRICHED RECRUITMENT DATASET SAVED")
print("=" * 60)
print(f"Saved to: {final_output}")
print(f"Players: {len(eligible)}")
print(f"Columns: {len(eligible.columns)}")

