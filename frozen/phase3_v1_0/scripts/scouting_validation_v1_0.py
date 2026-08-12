from pathlib import Path
import pandas as pd
import sys


# ============================================================
# PHASE 3 — SCOUTING & DECISION VALIDATION
# ============================================================

PHASE2_MASTER = Path(
    "frozen/phase2_v1_0/outputs/recruitment_decision_board_v1_0.csv"
)

PHASE2_EXECUTIVE = Path(
    "frozen/phase2_v1_0/outputs/executive_shortlist_v1_0.csv"
)


print("=" * 100)
print("NEWCASTLE UNITED — PHASE 3 SCOUTING & DECISION VALIDATION")
print("=" * 100)


# ============================================================
# 1. LOAD FROZEN PHASE 2
# ============================================================

if not PHASE2_MASTER.exists():
    sys.exit(f"ERROR | Missing frozen Phase 2 master: {PHASE2_MASTER}")

if not PHASE2_EXECUTIVE.exists():
    sys.exit(
        f"ERROR | Missing frozen Phase 2 executive shortlist: "
        f"{PHASE2_EXECUTIVE}"
    )

master = pd.read_csv(PHASE2_MASTER)
executive = pd.read_csv(PHASE2_EXECUTIVE)

print("\nPHASE 3 INPUT CHECK")
print("-" * 100)

print(f"Frozen Phase 2 master rows:     {len(master)}")
print(f"Frozen executive shortlist:     {len(executive)}")


# ============================================================
# 2. VALIDATE INPUT
# ============================================================

required = [
    "Player",
    "Replacement_For",
    "Succession_Score",
    "Evidence_Band",
    "Development_Profile",
    "Recruitment_Risk",
    "Decision_Score",
    "Risk_Adjusted_Score",
    "Decision_Tier",
]

missing = [c for c in required if c not in executive.columns]

if missing:
    sys.exit(
        "ERROR | Frozen executive shortlist is missing columns: "
        + ", ".join(missing)
    )

if len(executive) != 9:
    sys.exit(
        f"ERROR | Expected 9 executive candidates, found {len(executive)}"
    )

print("PASS | Frozen Phase 2 executive shortlist loaded")
print("PASS | All required decision fields are present")
print("PASS | 9 executive candidates confirmed")


# ============================================================
# 3. PHASE 3 BASE DOSSIER
# ============================================================

dossier_columns = [
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

available_columns = [
    c for c in dossier_columns
    if c in executive.columns
]

dossiers = executive[available_columns].copy()

dossiers = dossiers.sort_values(
    ["Replacement_For", "Risk_Adjusted_Score"],
    ascending=[True, False],
).reset_index(drop=True)




# ============================================================
# 4. DISPLAY BASE DOSSIERS
# ============================================================

print("\n" + "=" * 100)
print("PHASE 3.1 — EXECUTIVE CANDIDATE DOSSIERS")
print("=" * 100)

for replacement_for, group in dossiers.groupby(
    "Replacement_For",
    sort=False,
):
    print(f"\nREPLACEMENT FOR: {replacement_for.upper()}")
    print("-" * 100)

    display_cols = [
        c for c in [
            "Player",
            "Age",
            "Succession_Score",
            "Evidence_Band",
            "Development_Profile",
            "Recruitment_Risk",
            "Risk_Adjusted_Score",
            "Decision_Tier",
        ]
        if c in group.columns
    ]

    print(
        group[display_cols]
        .to_string(index=False)
    )


# ============================================================
# 5. PHASE 3.1 STATUS
# ============================================================

print("\n" + "=" * 100)
print("PHASE 3.1 COMPLETE")
print("=" * 100)

print(f"Candidates entering validation: {len(dossiers)}")
print(
    "Succession problems:            "
    f"{dossiers['Replacement_For'].nunique()}"
)
print(
    "Phase 2 source:                 "
    "FROZEN phase2_v1_0"
)
print("=" * 100)


# ============================================================
# 6. PHASE 3.2 — VALIDATION DIAGNOSTICS
# ============================================================

def build_validation_diagnostics(row):
    questions = []
    flags = []

    evidence_band = str(row.get("Evidence_Band", "")).upper()
    development = str(row.get("Development_Profile", "")).upper()
    risk = str(row.get("Recruitment_Risk", "")).upper()

    succession_score = row.get("Succession_Score", 0)
    risk_adjusted = row.get("Risk_Adjusted_Score", 0)
    minutes = row.get("Min", 0)
    age = row.get("Age", 0)

    # --------------------------------------------------------
    # Universal validation
    # --------------------------------------------------------

    questions.append(
        "Confirm role and tactical responsibilities translate "
        "to Newcastle's intended use."
    )

    questions.append(
        "Validate similarity through video rather than relying "
        "on statistical profile alone."
    )

    # --------------------------------------------------------
    # Evidence strength
    # --------------------------------------------------------

    if evidence_band == "HIGH":
        questions.append(
            "Confirm strong statistical evidence remains stable "
            "across opponents and match states."
        )

    elif evidence_band == "GOOD":
        flags.append("EVIDENCE_REVIEW")

        questions.append(
            "Review whether the evidence sample is sufficiently "
            "robust for recruitment progression."
        )

    elif evidence_band in {"MODERATE", "LIMITED"}:
        flags.append("EVIDENCE_GAP")

        questions.append(
            "Increase evidence base before making a recruitment "
            "decision."
        )

    # --------------------------------------------------------
    # Development profile
    # --------------------------------------------------------

    if development == "HIGH UPSIDE":
        flags.append("DEVELOPMENT_PROJECTION")

        questions.append(
            "Validate projected upside against current technical "
            "and tactical limitations."
        )

    elif development == "DEVELOPMENT":
        questions.append(
            "Assess development runway and likely adaptation "
            "timeline."
        )

    elif development in {"PRIME", "PRIME ENTRY"}:
        questions.append(
            "Confirm current performance level is immediately "
            "transferable."
        )

    # --------------------------------------------------------
    # Recruitment risk
    # --------------------------------------------------------

    if risk == "HIGH":
        flags.append("HIGH_RECRUITMENT_RISK")

        questions.append(
            "Resolve major recruitment uncertainty before "
            "progressing."
        )

    elif risk == "MEDIUM":
        flags.append("RECRUITMENT_RISK")

        questions.append(
            "Investigate the factors creating moderate "
            "recruitment uncertainty."
        )

    # --------------------------------------------------------
    # Minutes / sample size
    # --------------------------------------------------------

    if pd.notna(minutes) and minutes < 1500:
        flags.append("LOW_MINUTES")

        questions.append(
            "Determine whether limited senior minutes distort "
            "the player's statistical profile."
        )

    # --------------------------------------------------------
    # Young-player projection
    # --------------------------------------------------------

    if pd.notna(age) and age <= 20:
        flags.append("YOUNG_PROJECTION")

        questions.append(
            "Separate current first-team ability from long-term "
            "development projection."
        )

    # --------------------------------------------------------
    # Score relationship
    # --------------------------------------------------------

    if (
        pd.notna(succession_score)
        and pd.notna(risk_adjusted)
        and risk_adjusted >= succession_score + 8
    ):
        flags.append("DECISION_UPLIFT")

        questions.append(
            "Validate why contextual decision factors materially "
            "raise the player above the raw succession score."
        )

    # Remove duplicates while preserving order
    questions = list(dict.fromkeys(questions))
    flags = list(dict.fromkeys(flags))

    return pd.Series({
        "Validation_Flags":
            " | ".join(flags) if flags else "NONE",
        "Validation_Questions":
            " || ".join(questions),
        "Validation_Flag_Count":
            len(flags),
    })


diagnostics = dossiers.apply(
    build_validation_diagnostics,
    axis=1,
)

dossiers = pd.concat(
    [dossiers, diagnostics],
    axis=1,
)


# ============================================================
# 7. DISPLAY VALIDATION DIAGNOSTICS
# ============================================================

print("\n" + "=" * 100)
print("PHASE 3.2 — VALIDATION DIAGNOSTICS")
print("=" * 100)

for _, row in dossiers.iterrows():

    print(
        f"\n{row['Player']} "
        f"— replacement for {row['Replacement_For']}"
    )

    print(
        f"Decision tier: {row['Decision_Tier']} | "
        f"Risk-adjusted score: {row['Risk_Adjusted_Score']}"
    )

    print(
        f"Validation flags: {row['Validation_Flags']}"
    )

    questions = row["Validation_Questions"].split(" || ")

    for i, question in enumerate(questions, start=1):
        print(f"  {i}. {question}")


# ============================================================
# 8. DIAGNOSTIC SUMMARY
# ============================================================

print("\n" + "=" * 100)
print("PHASE 3.2 — DIAGNOSTIC SUMMARY")
print("=" * 100)

print(
    dossiers[
        [
            "Player",
            "Replacement_For",
            "Decision_Tier",
            "Validation_Flag_Count",
            "Validation_Flags",
        ]
    ]
    .sort_values(
    [
        "Validation_Flag_Count",
        "Player",
    ],
    ascending=[False, True],
)
    .to_string(index=False)
)

print("\nPHASE 3.2 COMPLETE")
print(
    f"Candidates diagnosed: "
    f"{len(dossiers)}"
)
print(
    f"Candidates with validation flags: "
    f"{(dossiers['Validation_Flag_Count'] > 0).sum()}"
)


# ============================================================
# 9. PHASE 3.3 — SCOUTING VALIDATION OUTCOMES
# ============================================================

# These fields are deliberately separate from the model.
# They represent human scouting outcomes, not statistical scores.

dossiers["Role_Validation"] = "UNRESOLVED"
dossiers["Evidence_Validation"] = "UNRESOLVED"
dossiers["Development_Validation"] = "UNRESOLVED"
dossiers["Overall_Validation_Status"] = "PENDING VALIDATION"


# ============================================================
# 10. SUGGESTED VALIDATION ACTION
# ============================================================

def suggested_action(row):
    flags = str(row["Validation_Flags"])

    if "HIGH_RECRUITMENT_RISK" in flags:
        return "HOLD — RESOLVE RISK"

    if "EVIDENCE_GAP" in flags or "LOW_MINUTES" in flags:
        return "DATA + VIDEO REVIEW"

    if (
        "DEVELOPMENT_PROJECTION" in flags
        or "YOUNG_PROJECTION" in flags
    ):
        return "LIVE / VIDEO SCOUTING"

    if "RECRUITMENT_RISK" in flags:
        return "VIDEO VALIDATION"

    if "DECISION_UPLIFT" in flags:
        return "TACTICAL VALIDATION"

    return "PROGRESS TO SCOUTING"


dossiers["Suggested_Action"] = dossiers.apply(
    suggested_action,
    axis=1,
)


# ============================================================
# 11. DISPLAY PHASE 3.3
# ============================================================

print("\n" + "=" * 100)
print("PHASE 3.3 — SCOUTING VALIDATION OUTCOMES")
print("=" * 100)

print(
    dossiers
    .sort_values(
        [
            "Replacement_For",
            "Risk_Adjusted_Score",
        ],
        ascending=[True, False],
    )[
        [
            "Player",
            "Replacement_For",
            "Decision_Tier",
            "Validation_Flag_Count",
            "Suggested_Action",
            "Overall_Validation_Status",
        ]
    ]
    .to_string(index=False)
)


print("\nSUGGESTED ACTION COUNTS")

print(
    dossiers["Suggested_Action"]
    .value_counts()
    .to_string()
)


print("\nPHASE 3.3 COMPLETE")
print(
    f"Candidates awaiting validation: "
    f"{(dossiers['Overall_Validation_Status'] == 'PENDING VALIDATION').sum()}"
)


# ============================================================
# 12. PHASE 3.4 — EXPORT VALIDATION DOSSIERS
# ============================================================

PHASE3_DIR = Path("data/outputs/phase3")
PHASE3_DIR.mkdir(parents=True, exist_ok=True)

DOSSIER_FILE = PHASE3_DIR / "scouting_validation_dossiers_v1_0.csv"
ACTION_FILE = PHASE3_DIR / "scouting_action_queue_v1_0.csv"


# Full validation dossier
dossiers.to_csv(
    DOSSIER_FILE,
    index=False,
)


# Operational scouting queue
action_columns = [
    "Player",
    "Replacement_For",
    "Decision_Tier",
    "Risk_Adjusted_Score",
    "Validation_Flag_Count",
    "Validation_Flags",
    "Suggested_Action",
    "Role_Validation",
    "Evidence_Validation",
    "Development_Validation",
    "Overall_Validation_Status",
]

action_columns = [
    c for c in action_columns
    if c in dossiers.columns
]

action_queue = (
    dossiers[action_columns]
    .sort_values(
        [
            "Suggested_Action",
            "Player",
        ],
        ascending=[True, True],
    )
)

action_queue.to_csv(
    ACTION_FILE,
    index=False,
)


print("\n" + "=" * 100)
print("PHASE 3.4 — VALIDATION EXPORT COMPLETE")
print("=" * 100)

print(f"Full dossiers:        {DOSSIER_FILE}")
print(f"Scouting action queue:{ACTION_FILE}")
print(f"Dossier rows:         {len(dossiers)}")
print(f"Action queue rows:    {len(action_queue)}")


