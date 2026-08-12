import pandas as pd
from pathlib import Path


# ============================================================
# NEWCASTLE UNITED RECRUITMENT ANALYTICS
# PHASE 2 — RECRUITMENT DECISION BOARD
# ============================================================

INPUT_FILE = Path(
    "data/outputs/succession_recruitment_board_v1_0.csv"
)

OUTPUT_DIR = Path("data/outputs/phase2")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# 1. LOAD FROZEN V1.0 SUCCESSION MODEL
# ============================================================

board = pd.read_csv(INPUT_FILE)

print("=" * 80)
print("NEWCASTLE UNITED — PHASE 2 RECRUITMENT DECISION BOARD")
print("=" * 80)

print(f"\nLoaded frozen v1.0 board: {len(board)} rows")


# ============================================================
# 2. VALIDATE INPUT
# ============================================================

required_columns = [
    "Player",
    "Squad",
    "League",
    "Age",
    "Min",
    "Similarity",
    "Quality",
    "Succession_Score",
    "Replacement_For",
    "Recruitment_Verdict",
]

missing_columns = [
    col for col in required_columns
    if col not in board.columns
]

if missing_columns:
    raise KeyError(
        f"Missing required columns: {missing_columns}"
    )

if len(board) != 30:
    raise ValueError(
        f"Expected 30 frozen v1.0 candidates, found {len(board)}"
    )

print("PASS | Frozen v1.0 recruitment board loaded correctly")
print("PASS | All required columns are present")
print("PASS | 30 succession candidates confirmed")


# ============================================================
# 3. CREATE PHASE 2 MASTER BOARD
# ============================================================

master = board[required_columns].copy()

master["Age"] = pd.to_numeric(
    master["Age"], errors="coerce"
)

master["Min"] = pd.to_numeric(
    master["Min"], errors="coerce"
)

master["Similarity"] = pd.to_numeric(
    master["Similarity"], errors="coerce"
)

master["Quality"] = pd.to_numeric(
    master["Quality"], errors="coerce"
)

master["Succession_Score"] = pd.to_numeric(
    master["Succession_Score"], errors="coerce"
)


# ============================================================
# 4. BASIC PHASE 2 CHECK
# ============================================================

print("\nCANDIDATES BY SUCCESSION PROBLEM")
print("-" * 80)

print(
    master["Replacement_For"]
    .value_counts()
    .to_string()
)

print("\nPHASE 2 MASTER BOARD READY")
print(f"Rows: {len(master)}")
print(f"Unique players: {master['Player'].nunique()}")
print(f"Leagues represented: {master['League'].nunique()}")


# ============================================================
# 5. EVIDENCE CONFIDENCE
# ============================================================

# Minutes are converted into an evidence-confidence score.
#
# 900 minutes  -> 30
# 1800 minutes -> 60
# 3000+ minutes -> 100
#
# This does NOT measure player quality.
# It measures how much playing-time evidence supports the profile.

master["Evidence_Confidence"] = (
    master["Min"] / 3000 * 100
).clip(lower=0, upper=100)


def evidence_band(score):
    if score >= 80:
        return "HIGH"
    elif score >= 60:
        return "GOOD"
    elif score >= 40:
        return "MODERATE"
    else:
        return "LIMITED"


master["Evidence_Band"] = (
    master["Evidence_Confidence"]
    .apply(evidence_band)
)


# ============================================================
# 6. EVIDENCE CHECK
# ============================================================

print("\n" + "=" * 80)
print("PHASE 2 — EVIDENCE CONFIDENCE")
print("=" * 80)

evidence_view = (
    master[
        [
            "Player",
            "Replacement_For",
            "Min",
            "Evidence_Confidence",
            "Evidence_Band",
        ]
    ]
    .sort_values(
        "Evidence_Confidence",
        ascending=False
    )
)

print(
    evidence_view
    .head(15)
    .round(1)
    .to_string(index=False)
)

print("\nEVIDENCE BAND COUNTS")

print(
    master["Evidence_Band"]
    .value_counts()
    .to_string()
)


# ============================================================
# 7. DEVELOPMENT PROFILE
# ============================================================

def development_profile(age):
    if age <= 20:
        return "HIGH UPSIDE"
    elif age <= 22:
        return "DEVELOPMENT"
    elif age <= 24:
        return "PRIME ENTRY"
    else:
        return "PRIME"


master["Development_Profile"] = (
    master["Age"]
    .apply(development_profile)
)


# Numerical development score
#
# This is deliberately modest.
# It represents development runway, NOT current ability.

def development_score(age):
    if age <= 20:
        return 100
    elif age == 21:
        return 90
    elif age == 22:
        return 80
    elif age == 23:
        return 70
    elif age == 24:
        return 60
    else:
        return 50


master["Development_Score"] = (
    master["Age"]
    .apply(development_score)
)


# ============================================================
# 8. DEVELOPMENT PROFILE CHECK
# ============================================================

print("\n" + "=" * 80)
print("PHASE 2 — DEVELOPMENT PROFILE")
print("=" * 80)

development_view = (
    master[
        [
            "Player",
            "Replacement_For",
            "Age",
            "Min",
            "Development_Profile",
            "Development_Score",
            "Evidence_Band",
        ]
    ]
    .sort_values(
        ["Development_Score", "Min"],
        ascending=[False, False]
    )
)

print(
    development_view
    .head(20)
    .to_string(index=False)
)

print("\nDEVELOPMENT PROFILE COUNTS")

print(
    master["Development_Profile"]
    .value_counts()
    .to_string()
)


# ============================================================
# 9. RECRUITMENT RISK
# ============================================================

# Evidence risk converts evidence confidence into a simple
# penalty. Higher number = greater uncertainty.

evidence_risk_map = {
    "HIGH": 0,
    "GOOD": 10,
    "MODERATE": 20,
    "LIMITED": 30,
}

master["Evidence_Risk"] = (
    master["Evidence_Band"]
    .map(evidence_risk_map)
)


def recruitment_risk(row):
    """
    Risk here means uncertainty in making a recruitment decision,
    not lack of player quality.
    """

    evidence = row["Evidence_Band"]
    score = row["Succession_Score"]

    if evidence == "LIMITED":
        return "HIGH"

    if evidence == "MODERATE" and score < 65:
        return "HIGH"

    if evidence in ["MODERATE", "GOOD"]:
        return "MEDIUM"

    return "LOW"


master["Recruitment_Risk"] = master.apply(
    recruitment_risk,
    axis=1
)


# ============================================================
# 10. RECRUITMENT RISK CHECK
# ============================================================

print("\n" + "=" * 80)
print("PHASE 2 — RECRUITMENT RISK")
print("=" * 80)

risk_view = (
    master[
        [
            "Player",
            "Replacement_For",
            "Age",
            "Succession_Score",
            "Evidence_Confidence",
            "Evidence_Band",
            "Evidence_Risk",
            "Recruitment_Risk",
        ]
    ]
    .sort_values(
        ["Evidence_Risk", "Succession_Score"],
        ascending=[False, False]
    )
)

print(
    risk_view
    .head(20)
    .round(1)
    .to_string(index=False)
)

print("\nRECRUITMENT RISK COUNTS")

print(
    master["Recruitment_Risk"]
    .value_counts()
    .to_string()
)


# ============================================================
# 11. RECRUITMENT DECISION SCORE
# ============================================================

# Final decision score combines:
#   60% succession suitability
#   20% evidence confidence
#   20% development runway
#
# Succession suitability remains the dominant component.

master["Decision_Score"] = (
    master["Succession_Score"] * 0.60
    + master["Evidence_Confidence"] * 0.20
    + master["Development_Score"] * 0.20
).round(1)


# Risk-adjusted score
#
# Apply a modest uncertainty penalty AFTER calculating
# the transparent decision score.

risk_penalty = {
    "LOW": 0,
    "MEDIUM": 3,
    "HIGH": 7,
}

master["Risk_Penalty"] = (
    master["Recruitment_Risk"]
    .map(risk_penalty)
)

master["Risk_Adjusted_Score"] = (
    master["Decision_Score"]
    - master["Risk_Penalty"]
).round(1)


# ============================================================
# 12. DECISION SCORE CHECK
# ============================================================

print("\n" + "=" * 80)
print("PHASE 2 — RECRUITMENT DECISION SCORE")
print("=" * 80)

decision_view = (
    master[
        [
            "Player",
            "Replacement_For",
            "Age",
            "Succession_Score",
            "Evidence_Confidence",
            "Development_Score",
            "Recruitment_Risk",
            "Decision_Score",
            "Risk_Penalty",
            "Risk_Adjusted_Score",
        ]
    ]
    .sort_values(
        "Risk_Adjusted_Score",
        ascending=False
    )
)

print(
    decision_view
    .head(20)
    .to_string(index=False)
)

print("\nTOP 3 PER SUCCESSION PROBLEM")

top3 = (
    master
    .sort_values(
        ["Replacement_For", "Risk_Adjusted_Score"],
        ascending=[True, False]
    )
    .groupby("Replacement_For")
    .head(3)
)

print(
    top3[
        [
            "Player",
            "Replacement_For",
            "Age",
            "Succession_Score",
            "Decision_Score",
            "Recruitment_Risk",
            "Risk_Adjusted_Score",
        ]
    ]
    .to_string(index=False)
)


# ============================================================
# 13. RECRUITMENT DECISION TIERS
# ============================================================

def decision_tier(score):
    if score >= 72:
        return "PRIORITY TARGET"
    elif score >= 67:
        return "STRONG SHORTLIST"
    elif score >= 62:
        return "SCOUT / VALIDATE"
    else:
        return "WATCHLIST"


master["Decision_Tier"] = (
    master["Risk_Adjusted_Score"]
    .apply(decision_tier)
)


# ============================================================
# 14. FINAL SHORTLIST CHECK
# ============================================================

print("\n" + "=" * 90)
print("PHASE 2 — RECRUITMENT SHORTLIST TIERS")
print("=" * 90)

final_view = (
    master[
        [
            "Player",
            "Replacement_For",
            "Age",
            "Succession_Score",
            "Evidence_Band",
            "Development_Profile",
            "Recruitment_Risk",
            "Decision_Score",
            "Risk_Adjusted_Score",
            "Decision_Tier",
        ]
    ]
    .sort_values(
        ["Replacement_For", "Risk_Adjusted_Score"],
        ascending=[True, False]
    )
)

for replacement, group in final_view.groupby(
    "Replacement_For",
    sort=True
):
    print(f"\nREPLACEMENT FOR: {replacement.upper()}")
    print("-" * 90)

    print(
        group
        .head(10)
        .to_string(index=False)
    )


print("\n" + "=" * 90)
print("DECISION TIER COUNTS")
print("=" * 90)

print(
    master["Decision_Tier"]
    .value_counts()
    .to_string()
)


# ============================================================
# 15. MULTI-SUCCESSOR / STRATEGIC COVERAGE
# ============================================================

coverage = (
    master
    .groupby("Player")
    .agg(
        Succession_Coverage=("Replacement_For", "nunique"),
        Average_Risk_Adjusted_Score=("Risk_Adjusted_Score", "mean"),
        Best_Risk_Adjusted_Score=("Risk_Adjusted_Score", "max"),
        Average_Succession_Score=("Succession_Score", "mean"),
    )
    .reset_index()
)

coverage["Average_Risk_Adjusted_Score"] = (
    coverage["Average_Risk_Adjusted_Score"].round(1)
)

coverage["Best_Risk_Adjusted_Score"] = (
    coverage["Best_Risk_Adjusted_Score"].round(1)
)

coverage["Average_Succession_Score"] = (
    coverage["Average_Succession_Score"].round(1)
)


replacement_lists = (
    master
    .groupby("Player")["Replacement_For"]
    .apply(lambda x: " | ".join(sorted(set(x))))
    .reset_index(name="Can_Replace")
)

coverage = coverage.merge(
    replacement_lists,
    on="Player",
    how="left"
)


def strategic_value(row):
    if (
        row["Succession_Coverage"] >= 2
        and row["Average_Risk_Adjusted_Score"] >= 62
    ):
        return "HIGH"
    elif row["Succession_Coverage"] >= 2:
        return "VERSATILE"
    else:
        return "SINGLE ROLE"


coverage["Strategic_Value"] = coverage.apply(
    strategic_value,
    axis=1
)


# Attach coverage information back to master board

master = master.merge(
    coverage[
        [
            "Player",
            "Succession_Coverage",
            "Can_Replace",
            "Strategic_Value",
        ]
    ],
    on="Player",
    how="left"
)


# ============================================================
# 16. STRATEGIC COVERAGE CHECK
# ============================================================

print("\n" + "=" * 90)
print("PHASE 2 — MULTI-SUCCESSOR VALUE")
print("=" * 90)

multi = (
    coverage[
        coverage["Succession_Coverage"] > 1
    ]
    .sort_values(
        [
            "Succession_Coverage",
            "Average_Risk_Adjusted_Score",
        ],
        ascending=[False, False]
    )
)

if multi.empty:
    print("No multi-successor candidates identified.")
else:
    print(
        multi.to_string(index=False)
    )

print("\nSTRATEGIC VALUE COUNTS")

print(
    coverage["Strategic_Value"]
    .value_counts()
    .to_string()
)


# ============================================================
# 17. EXPLAINABLE RECRUITMENT RECOMMENDATIONS
# ============================================================

def build_recommendation(row):
    reasons = []

    # Core succession assessment
    if row["Succession_Score"] >= 66:
        reasons.append("strong succession fit")
    elif row["Succession_Score"] >= 62:
        reasons.append("credible succession fit")
    else:
        reasons.append("moderate succession fit")

    # Evidence
    if row["Evidence_Band"] == "HIGH":
        reasons.append("high evidence confidence")
    elif row["Evidence_Band"] == "GOOD":
        reasons.append("good evidence base")
    elif row["Evidence_Band"] == "MODERATE":
        reasons.append("further evidence required")
    else:
        reasons.append("limited evidence")

    # Development
    if row["Development_Profile"] == "HIGH UPSIDE":
        reasons.append("high development upside")
    elif row["Development_Profile"] == "DEVELOPMENT":
        reasons.append("development runway")
    elif row["Development_Profile"] == "PRIME ENTRY":
        reasons.append("entering prime years")
    else:
        reasons.append("prime-age profile")

    # Risk
    if row["Recruitment_Risk"] == "LOW":
        reasons.append("low decision uncertainty")
    elif row["Recruitment_Risk"] == "MEDIUM":
        reasons.append("moderate decision uncertainty")
    else:
        reasons.append("high decision uncertainty")

    # Multi-successor coverage
    if row["Succession_Coverage"] > 1:
        reasons.append("multi-successor versatility")

    return "; ".join(reasons)


master["Recommendation_Rationale"] = master.apply(
    build_recommendation,
    axis=1
)


# ============================================================
# 18. EXECUTIVE SHORTLIST
# ============================================================

executive = (
    master[
        master["Decision_Tier"].isin(
            ["PRIORITY TARGET", "STRONG SHORTLIST"]
        )
    ]
    .sort_values(
        ["Replacement_For", "Risk_Adjusted_Score"],
        ascending=[True, False]
    )
)


print("\n" + "=" * 100)
print("PHASE 2 — EXECUTIVE RECRUITMENT SHORTLIST")
print("=" * 100)

for replacement, group in executive.groupby(
    "Replacement_For",
    sort=True
):
    print(f"\nREPLACEMENT FOR: {replacement.upper()}")
    print("-" * 100)

    for _, row in group.iterrows():
        print(
            f"{row['Player']} | "
            f"{row['Decision_Tier']} | "
            f"Score {row['Risk_Adjusted_Score']:.1f}"
        )
        print(f"  {row['Recommendation_Rationale']}")


# ============================================================
# 19. PHASE 2 EXPORTS
# ============================================================

from pathlib import Path

phase2_dir = Path("data/outputs/phase2")
phase2_dir.mkdir(parents=True, exist_ok=True)

master_file = phase2_dir / "recruitment_decision_board_v1_0.csv"
executive_file = phase2_dir / "executive_shortlist_v1_0.csv"

master.to_csv(master_file, index=False)
executive.to_csv(executive_file, index=False)

print("\n" + "=" * 100)
print("PHASE 2 EXPORT COMPLETE")
print("=" * 100)
print(f"Master decision board: {master_file}")
print(f"Executive shortlist:   {executive_file}")
print(f"Master rows:            {len(master)}")
print(f"Executive rows:         {len(executive)}")


