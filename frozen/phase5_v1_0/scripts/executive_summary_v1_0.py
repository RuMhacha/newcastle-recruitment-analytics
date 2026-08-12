from pathlib import Path
import pandas as pd

# ============================================================
# NEWCASTLE UNITED — PHASE 5
# EXECUTIVE MASTER SUMMARY
# ============================================================

PHASE2 = Path(
    "frozen/phase2_v1_0/outputs/"
    "executive_shortlist_v1_0.csv"
)

PHASE3 = Path(
    "frozen/phase3_v1_0/outputs/"
    "scouting_validation_dossiers_v1_0.csv"
)

PHASE4 = Path(
    "frozen/phase4_v1_0/outputs/"
    "final_decision_gate_v1_0.csv"
)

OUTPUT_DIR = Path("data/outputs/phase5")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "executive_master_summary_v1_0.csv"


print("=" * 100)
print("NEWCASTLE UNITED — PHASE 5 EXECUTIVE MASTER SUMMARY")
print("=" * 100)


# ============================================================
# 1. LOAD FROZEN INPUTS
# ============================================================

phase2 = pd.read_csv(PHASE2)
phase3 = pd.read_csv(PHASE3)
phase4 = pd.read_csv(PHASE4)

print("\nPHASE 5.1 — INPUT CHECK")
print("-" * 100)

print(f"Phase 2 executive rows: {len(phase2)}")
print(f"Phase 3 dossier rows:   {len(phase3)}")
print(f"Phase 4 gate rows:      {len(phase4)}")


# ============================================================
# 2. BASIC CONSISTENCY CHECK
# ============================================================

p2_players = set(phase2["Player"])
p3_players = set(phase3["Player"])
p4_players = set(phase4["Player"])

if not (
    p2_players == p3_players == p4_players
):
    raise ValueError(
        "Frozen Phase 2/3/4 player sets do not match."
    )

if len(p2_players) != 9:
    raise ValueError(
        f"Expected 9 executive players, found {len(p2_players)}"
    )

print("PASS | Frozen Phase 2/3/4 player sets match")
print("PASS | 9 executive candidates confirmed")


# ============================================================
# 3. SELECT PHASE-SPECIFIC FIELDS
# ============================================================

phase2_cols = [
    c for c in [
        "Player",
        "Replacement_For",
        "Age",
        "Min",
        "Similarity",
        "Quality",
        "Succession_Score",
        "Evidence_Confidence",
        "Evidence_Band",
        "Development_Profile",
        "Development_Score",
        "Recruitment_Risk",
        "Decision_Score",
        "Risk_Adjusted_Score",
        "Decision_Tier",
    ]
    if c in phase2.columns
]

phase3_cols = [
    c for c in [
        "Player",
        "Validation_Flag_Count",
        "Validation_Flags",
        "Validation_Questions",
        "Suggested_Action",
        "Overall_Validation_Status",
    ]
    if c in phase3.columns
]

phase4_cols = [
    c for c in [
        "Player",
        "Validated_Complete_Record",
        "Final_Recommendation_Eligible",
        "Final_Decision_State",
        "Final_Decision_Approved",
    ]
    if c in phase4.columns
]


# ============================================================
# 4. MERGE INTO EXECUTIVE MASTER
# ============================================================

executive = phase2[phase2_cols].copy()

executive = executive.merge(
    phase3[phase3_cols],
    on="Player",
    how="left",
    validate="one_to_one",
)

executive = executive.merge(
    phase4[phase4_cols],
    on="Player",
    how="left",
    validate="one_to_one",
)


# ============================================================
# 5. EXECUTIVE STATUS
# ============================================================

def executive_status(row):
    if bool(row.get("Final_Decision_Approved", False)):
        return "APPROVED"

    state = str(
        row.get("Final_Decision_State", "")
    ).upper()

    if state == "REJECT":
        return "REJECTED"

    if state == "HOLD":
        return "HOLD"

    if state == "CONTINUE SCOUTING":
        return "CONTINUE SCOUTING"

    return "AWAITING SCOUTING VALIDATION"


executive["Executive_Status"] = executive.apply(
    executive_status,
    axis=1,
)


# ============================================================
# 6. SORT ORDER
# ============================================================

tier_rank = {
    "PRIORITY TARGET": 1,
    "STRONG SHORTLIST": 2,
}

executive["_Tier_Rank"] = (
    executive["Decision_Tier"]
    .map(tier_rank)
    .fillna(99)
)

executive = (
    executive
    .sort_values(
        [
            "Replacement_For",
            "_Tier_Rank",
            "Risk_Adjusted_Score",
        ],
        ascending=[True, True, False],
    )
    .drop(columns="_Tier_Rank")
    .reset_index(drop=True)
)


# ============================================================
# 7. DISPLAY EXECUTIVE VIEW
# ============================================================

print("\n" + "=" * 100)
print("PHASE 5.1 — EXECUTIVE MASTER BOARD")
print("=" * 100)

display_cols = [
    c for c in [
        "Player",
        "Replacement_For",
        "Decision_Tier",
        "Risk_Adjusted_Score",
        "Evidence_Band",
        "Recruitment_Risk",
        "Suggested_Action",
        "Final_Decision_State",
        "Executive_Status",
    ]
    if c in executive.columns
]

print(
    executive[display_cols]
    .to_string(index=False)
)


# ============================================================
# 8. SUMMARY COUNTS
# ============================================================

print("\nEXECUTIVE STATUS COUNTS")
print(
    executive["Executive_Status"]
    .value_counts()
    .to_string()
)

print("\nSUCCESSION COVERAGE")
print(
    executive["Replacement_For"]
    .value_counts()
    .to_string()
)


# ============================================================
# 9. EXPORT
# ============================================================

executive.to_csv(
    OUTPUT_FILE,
    index=False,
)

print("\nPHASE 5.1 COMPLETE")
print(f"Executive master summary: {OUTPUT_FILE}")
print(f"Rows exported: {len(executive)}")
print(
    "Succession problems: "
    f"{executive['Replacement_For'].nunique()}"
)


