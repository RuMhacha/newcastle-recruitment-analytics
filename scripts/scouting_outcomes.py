from pathlib import Path
import pandas as pd

# ============================================================
# NEWCASTLE UNITED — PHASE 4
# SCOUTING OUTCOMES & FINAL RECRUITMENT RECOMMENDATIONS
# ============================================================

PHASE3_DOSSIERS = Path(
    "frozen/phase3_v1_0/outputs/"
    "scouting_validation_dossiers_v1_0.csv"
)

PHASE3_ACTIONS = Path(
    "frozen/phase3_v1_0/outputs/"
    "scouting_action_queue_v1_0.csv"
)

OUTPUT_DIR = Path("data/outputs/phase4")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


print("=" * 90)
print("NEWCASTLE UNITED — PHASE 4 SCOUTING OUTCOMES")
print("=" * 90)


# ============================================================
# 1. LOAD FROZEN PHASE 3 INPUTS
# ============================================================

dossiers = pd.read_csv(PHASE3_DOSSIERS)
actions = pd.read_csv(PHASE3_ACTIONS)

print("\nPHASE 4.1 — INPUT CHECK")
print("-" * 90)

print(f"Frozen Phase 3 dossiers: {len(dossiers)}")
print(f"Frozen Phase 3 actions:  {len(actions)}")


# ============================================================
# 2. BASIC INPUT VALIDATION
# ============================================================

required_dossier_columns = [
    "Player",
    "Replacement_For",
    "Decision_Tier",
    "Validation_Flag_Count",
    "Validation_Flags",
    "Suggested_Action",
    "Overall_Validation_Status",
]

missing = [
    column
    for column in required_dossier_columns
    if column not in dossiers.columns
]

if missing:
    raise ValueError(
        f"Missing required Phase 3 columns: {missing}"
    )

if len(dossiers) != 9:
    raise ValueError(
        f"Expected 9 Phase 3 dossiers, found {len(dossiers)}"
    )

if len(actions) != 9:
    raise ValueError(
        f"Expected 9 Phase 3 actions, found {len(actions)}"
    )

print("PASS | Frozen Phase 3 dossiers loaded")
print("PASS | Frozen Phase 3 action queue loaded")
print("PASS | Required validation fields present")
print("PASS | 9 candidates entering Phase 4")


# ============================================================
# 3. CREATE PHASE 4 VALIDATION FRAME
# ============================================================

validation = dossiers.copy()

validation["Scouting_Status"] = "NOT STARTED"
validation["Validation_Result"] = "PENDING"
validation["Recommendation_Status"] = "PENDING"

print("\nPHASE 4 VALIDATION FRAME READY")
print("-" * 90)

print(
    validation[
        [
            "Player",
            "Replacement_For",
            "Decision_Tier",
            "Suggested_Action",
            "Scouting_Status",
            "Validation_Result",
            "Recommendation_Status",
        ]
    ].to_string(index=False)
)

print("\nPHASE 4.1 COMPLETE")
print(f"Candidates entering final validation: {len(validation)}")
print("Phase 3 source: FROZEN phase3_v1_0")


# ============================================================
# 4. PHASE 4.2 — SCOUTING EVIDENCE FRAMEWORK
# ============================================================

print("\n" + "=" * 90)
print("PHASE 4.2 — SCOUTING EVIDENCE FRAMEWORK")
print("=" * 90)

# These fields represent evidence that must ultimately come
# from human scouting / validation rather than the model itself.

validation["Role_Fit_Result"] = "PENDING"
validation["Tactical_Fit_Result"] = "PENDING"
validation["Evidence_Review_Result"] = "PENDING"
validation["Development_Review_Result"] = "PENDING"

validation["Scout_Confidence"] = pd.NA
validation["Scout_Notes"] = ""

validation["Validation_Source"] = "HUMAN SCOUTING REQUIRED"


# ============================================================
# 5. DETERMINE REQUIRED VALIDATION WORK
# ============================================================

def required_checks(row):
    checks = []

    flags = str(row["Validation_Flags"])

    # Every candidate requires basic role validation.
    checks.append("ROLE FIT")

    if row["Suggested_Action"] == "TACTICAL VALIDATION":
        checks.append("TACTICAL FIT")

    if "EVIDENCE_REVIEW" in flags:
        checks.append("EVIDENCE REVIEW")

    if (
        "DEVELOPMENT_PROJECTION" in flags
        or "YOUNG_PROJECTION" in flags
    ):
        checks.append("DEVELOPMENT REVIEW")

    if row["Suggested_Action"] in {
        "LIVE / VIDEO SCOUTING",
        "VIDEO VALIDATION",
    }:
        checks.append("VIDEO / LIVE SCOUTING")

    return " | ".join(dict.fromkeys(checks))


validation["Required_Validation_Work"] = validation.apply(
    required_checks,
    axis=1,
)


# ============================================================
# 6. VALIDATION READINESS
# ============================================================

def validation_readiness(row):
    if row["Overall_Validation_Status"] != "PENDING VALIDATION":
        return "REVIEW STATUS"

    if not row["Required_Validation_Work"]:
        return "NO WORK DEFINED"

    return "READY FOR SCOUTING"


validation["Validation_Readiness"] = validation.apply(
    validation_readiness,
    axis=1,
)


# ============================================================
# 7. DISPLAY PHASE 4.2 QUEUE
# ============================================================

display_columns = [
    "Player",
    "Replacement_For",
    "Decision_Tier",
    "Required_Validation_Work",
    "Validation_Readiness",
]

print(
    validation[display_columns]
    .sort_values(
        ["Replacement_For", "Player"]
    )
    .to_string(index=False)
)

print("\nVALIDATION READINESS COUNTS")
print(
    validation["Validation_Readiness"]
    .value_counts()
    .to_string()
)

print("\nPHASE 4.2 COMPLETE")
print(
    "Human scouting evidence required: "
    f"{(validation['Validation_Readiness'] == 'READY FOR SCOUTING').sum()}"
)


# ============================================================
# 8. PHASE 4.3 — SCOUTING EVIDENCE TEMPLATE
# ============================================================

print("\n" + "=" * 90)
print("PHASE 4.3 — SCOUTING EVIDENCE TEMPLATE")
print("=" * 90)

evidence = validation[
    [
        "Player",
        "Replacement_For",
        "Decision_Tier",
        "Suggested_Action",
        "Required_Validation_Work",
    ]
].copy()


# ============================================================
# 9. HUMAN SCOUTING INPUT FIELDS
# ============================================================

evidence["Role_Fit_Score"] = pd.NA
evidence["Tactical_Fit_Score"] = pd.NA
evidence["Technical_Fit_Score"] = pd.NA
evidence["Physical_Fit_Score"] = pd.NA
evidence["Development_Confidence"] = pd.NA
evidence["Evidence_Confidence"] = pd.NA

evidence["Scout_Recommendation"] = "PENDING"
evidence["Scout_Notes"] = ""
evidence["Validation_Complete"] = False


# ============================================================
# 10. DEFINE SCORING SCALE
# ============================================================

print("\nSCOUTING SCORE SCALE")
print("-" * 90)
print("1 | Major concern")
print("2 | Below required level")
print("3 | Acceptable / neutral")
print("4 | Strong fit")
print("5 | Excellent fit")

print("\nSCOUT RECOMMENDATION OPTIONS")
print("-" * 90)
print("RECOMMEND")
print("CONTINUE SCOUTING")
print("HOLD")
print("REJECT")


# ============================================================
# 11. DISPLAY EVIDENCE QUEUE
# ============================================================

print("\nSCOUTING EVIDENCE QUEUE")
print("-" * 90)

print(
    evidence[
        [
            "Player",
            "Replacement_For",
            "Decision_Tier",
            "Required_Validation_Work",
            "Scout_Recommendation",
            "Validation_Complete",
        ]
    ].to_string(index=False)
)


# ============================================================
# 12. EXPORT BLANK HUMAN-VALIDATION TEMPLATE
# ============================================================

EVIDENCE_TEMPLATE = (
    OUTPUT_DIR /
    "scouting_evidence_template_v1_0.csv"
)

evidence.to_csv(
    EVIDENCE_TEMPLATE,
    index=False,
)

print("\nPHASE 4.3 COMPLETE")
print(f"Evidence template: {EVIDENCE_TEMPLATE}")
print(f"Candidates requiring scouting input: {len(evidence)}")
print(
    "Completed validations: "
    f"{evidence['Validation_Complete'].sum()}"
)


# ============================================================
# 13. PHASE 4.4 — SCOUTING EVIDENCE INGESTION
# ============================================================

print("\n" + "=" * 90)
print("PHASE 4.4 — SCOUTING EVIDENCE INGESTION")
print("=" * 90)

EVIDENCE_INPUT = (
    OUTPUT_DIR /
    "scouting_evidence_template_v1_0.csv"
)

if not EVIDENCE_INPUT.exists():
    raise FileNotFoundError(
        f"Missing scouting evidence file: {EVIDENCE_INPUT}"
    )

scouting_input = pd.read_csv(EVIDENCE_INPUT)

print(f"Evidence rows loaded: {len(scouting_input)}")


# ============================================================
# 14. STRUCTURE CHECKS
# ============================================================

required_evidence_columns = [
    "Player",
    "Replacement_For",
    "Role_Fit_Score",
    "Tactical_Fit_Score",
    "Technical_Fit_Score",
    "Physical_Fit_Score",
    "Development_Confidence",
    "Evidence_Confidence",
    "Scout_Recommendation",
    "Scout_Notes",
    "Validation_Complete",
]

missing_evidence_columns = [
    c
    for c in required_evidence_columns
    if c not in scouting_input.columns
]

if missing_evidence_columns:
    raise ValueError(
        "Missing scouting evidence columns: "
        f"{missing_evidence_columns}"
    )

if len(scouting_input) != 9:
    raise ValueError(
        f"Expected 9 scouting rows, found {len(scouting_input)}"
    )

print("PASS | Required scouting evidence columns present")
print("PASS | 9 scouting evidence rows present")


# ============================================================
# 15. SCORE VALIDATION
# ============================================================

score_columns = [
    "Role_Fit_Score",
    "Tactical_Fit_Score",
    "Technical_Fit_Score",
    "Physical_Fit_Score",
    "Development_Confidence",
    "Evidence_Confidence",
]

for col in score_columns:
    scouting_input[col] = pd.to_numeric(
        scouting_input[col],
        errors="coerce",
    )

invalid_score_rows = pd.Series(
    False,
    index=scouting_input.index,
)

for col in score_columns:
    invalid_score_rows = (
        invalid_score_rows
        | (
            scouting_input[col].notna()
            & ~scouting_input[col].between(1, 5)
        )
    )

if invalid_score_rows.any():
    bad = scouting_input.loc[
        invalid_score_rows,
        ["Player"] + score_columns,
    ]

    print("\nINVALID SCOUTING SCORES")
    print(bad.to_string(index=False))

    raise ValueError(
        "Scouting scores must be between 1 and 5."
    )

print("PASS | All entered scouting scores are within 1–5")


# ============================================================
# 16. RECOMMENDATION VALIDATION
# ============================================================

allowed_recommendations = {
    "PENDING",
    "RECOMMEND",
    "CONTINUE SCOUTING",
    "HOLD",
    "REJECT",
}

unexpected_recommendations = (
    set(
        scouting_input[
            "Scout_Recommendation"
        ]
        .dropna()
        .astype(str)
        .str.strip()
        .str.upper()
    )
    - allowed_recommendations
)

if unexpected_recommendations:
    raise ValueError(
        "Unexpected scout recommendations: "
        f"{sorted(unexpected_recommendations)}"
    )

print("PASS | Scout recommendations use approved categories")


# ============================================================
# 17. NORMALISE COMPLETION FIELD
# ============================================================

def normalise_bool(value):
    if isinstance(value, bool):
        return value

    text = str(value).strip().lower()

    if text in {"true", "1", "yes", "y"}:
        return True

    if text in {"false", "0", "no", "n", "", "nan"}:
        return False

    raise ValueError(
        f"Invalid Validation_Complete value: {value}"
    )


scouting_input["Validation_Complete"] = (
    scouting_input["Validation_Complete"]
    .apply(normalise_bool)
)


# ============================================================
# 18. COMPLETENESS CHECK
# ============================================================

def row_is_complete(row):
    if not row["Validation_Complete"]:
        return False

    if row["Scout_Recommendation"] == "PENDING":
        return False

    required_scores = [
        row["Role_Fit_Score"],
        row["Tactical_Fit_Score"],
        row["Technical_Fit_Score"],
        row["Physical_Fit_Score"],
        row["Development_Confidence"],
        row["Evidence_Confidence"],
    ]

    return all(pd.notna(x) for x in required_scores)


scouting_input["Validated_Complete_Record"] = (
    scouting_input.apply(
        row_is_complete,
        axis=1,
    )
)

completed_count = int(
    scouting_input[
        "Validated_Complete_Record"
    ].sum()
)

print("\nSCOUTING COMPLETION CHECK")
print("-" * 90)

print(f"Validated complete records: {completed_count}")
print(
    "Incomplete / pending records: "
    f"{len(scouting_input) - completed_count}"
)


# ============================================================
# 19. PREVENT FALSE FINAL RECOMMENDATIONS
# ============================================================

scouting_input["Final_Recommendation_Eligible"] = (
    scouting_input["Validated_Complete_Record"]
)

if completed_count == 0:
    print(
        "PASS | No final recruitment recommendations "
        "can be produced yet."
    )
else:
    print(
        "INFO | Completed scouting evidence exists for "
        f"{completed_count} candidate(s)."
    )


# ============================================================
# 20. EXPORT VALIDATED INGESTION STATE
# ============================================================

INGESTION_OUTPUT = (
    OUTPUT_DIR /
    "validated_scouting_evidence_v1_0.csv"
)

scouting_input.to_csv(
    INGESTION_OUTPUT,
    index=False,
)

print("\nPHASE 4.4 COMPLETE")
print(f"Validated evidence file: {INGESTION_OUTPUT}")
print(f"Rows checked: {len(scouting_input)}")
print(
    "Final-recommendation eligible: "
    f"{scouting_input['Final_Recommendation_Eligible'].sum()}"
)


# ============================================================
# 21. PHASE 4.5 — FINAL DECISION GATE
# ============================================================

print("\n" + "=" * 90)
print("PHASE 4.5 — FINAL DECISION GATE")
print("=" * 90)


def final_decision_state(row):
    if not row["Validated_Complete_Record"]:
        return "SCOUTING REQUIRED"

    recommendation = str(
        row["Scout_Recommendation"]
    ).strip().upper()

    if recommendation == "RECOMMEND":
        return "FINAL RECOMMENDATION"

    if recommendation == "CONTINUE SCOUTING":
        return "CONTINUE SCOUTING"

    if recommendation == "HOLD":
        return "HOLD"

    if recommendation == "REJECT":
        return "REJECT"

    return "SCOUTING REQUIRED"


scouting_input["Final_Decision_State"] = (
    scouting_input.apply(
        final_decision_state,
        axis=1,
    )
)


# ============================================================
# 22. FINAL DECISION ELIGIBILITY
# ============================================================

scouting_input["Final_Decision_Approved"] = (
    scouting_input["Final_Decision_State"]
    .eq("FINAL RECOMMENDATION")
)


# ============================================================
# 23. DISPLAY DECISION GATE
# ============================================================

print(
    scouting_input[
        [
            "Player",
            "Replacement_For",
            "Scout_Recommendation",
            "Validated_Complete_Record",
            "Final_Decision_State",
            "Final_Decision_Approved",
        ]
    ]
    .sort_values(
        [
            "Replacement_For",
            "Player",
        ]
    )
    .to_string(index=False)
)


print("\nFINAL DECISION STATE COUNTS")

print(
    scouting_input[
        "Final_Decision_State"
    ]
    .value_counts()
    .to_string()
)


# ============================================================
# 24. SAFETY / HUMAN-EVIDENCE GATE
# ============================================================

eligible_count = int(
    scouting_input[
        "Final_Decision_Approved"
    ].sum()
)

if eligible_count == 0:
    print(
        "\nPASS | No candidate has crossed the final "
        "recruitment decision gate without validated "
        "human scouting evidence."
    )
else:
    print(
        "\nINFO | Final recommendations approved: "
        f"{eligible_count}"
    )


# ============================================================
# 25. EXPORT FINAL DECISION STATE
# ============================================================

FINAL_GATE_FILE = (
    OUTPUT_DIR /
    "final_decision_gate_v1_0.csv"
)

scouting_input.to_csv(
    FINAL_GATE_FILE,
    index=False,
)

print("\nPHASE 4.5 COMPLETE")
print(f"Final decision gate file: {FINAL_GATE_FILE}")
print(f"Candidates checked: {len(scouting_input)}")
print(f"Final recommendations approved: {eligible_count}")


