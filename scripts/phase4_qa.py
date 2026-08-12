from pathlib import Path
import pandas as pd
import sys

TEMPLATE_FILE = Path(
    "data/outputs/phase4/scouting_evidence_template_v1_0.csv"
)

VALIDATED_FILE = Path(
    "data/outputs/phase4/validated_scouting_evidence_v1_0.csv"
)

FINAL_GATE_FILE = Path(
    "data/outputs/phase4/final_decision_gate_v1_0.csv"
)

errors = []

print("=" * 90)
print("NEWCASTLE UNITED — PHASE 4 FINAL QA")
print("=" * 90)


# ============================================================
# 1. FILE CHECKS
# ============================================================

print("\n1. FILES")

for path in [
    TEMPLATE_FILE,
    VALIDATED_FILE,
    FINAL_GATE_FILE,
]:
    if path.exists():
        print(f"PASS | {path}")
    else:
        print(f"FAIL | Missing file: {path}")
        errors.append(f"Missing file: {path}")

if errors:
    sys.exit(1)

template = pd.read_csv(TEMPLATE_FILE)
validated = pd.read_csv(VALIDATED_FILE)
final_gate = pd.read_csv(FINAL_GATE_FILE)


# ============================================================
# 2. ROW COUNTS
# ============================================================

print("\n2. ROW COUNTS")

for name, df in [
    ("Evidence template", template),
    ("Validated evidence", validated),
    ("Final decision gate", final_gate),
]:
    if len(df) == 9:
        print(f"PASS | {name} contains exactly 9 rows")
    else:
        print(f"FAIL | {name} contains {len(df)} rows")
        errors.append(f"{name} row count")


# ============================================================
# 3. PLAYER CONSISTENCY
# ============================================================

print("\n3. PLAYER CONSISTENCY")

template_players = set(template["Player"])
validated_players = set(validated["Player"])
final_players = set(final_gate["Player"])

if (
    template_players
    == validated_players
    == final_players
):
    print("PASS | All Phase 4 files contain the same players")
else:
    print("FAIL | Player sets differ between Phase 4 files")
    errors.append("Player consistency")


# ============================================================
# 4. SUCCESSION COVERAGE
# ============================================================

print("\n4. SUCCESSION COVERAGE")

expected_targets = {
    "Anthony Gordon",
    "Bruno Guimaraes",
    "Sandro Tonali",
}

actual_targets = set(
    final_gate["Replacement_For"]
    .dropna()
    .unique()
)

if actual_targets == expected_targets:
    print("PASS | All three succession problems are present")
else:
    print(f"FAIL | Found targets: {sorted(actual_targets)}")
    errors.append("Succession coverage")


# ============================================================
# 5. REQUIRED COLUMNS
# ============================================================

print("\n5. REQUIRED COLUMNS")

required_template = [
    "Player",
    "Replacement_For",
    "Role_Fit_Score",
    "Tactical_Fit_Score",
    "Technical_Fit_Score",
    "Physical_Fit_Score",
    "Development_Confidence",
    "Evidence_Confidence",
    "Scout_Recommendation",
    "Validation_Complete",
]

missing_template = [
    c for c in required_template
    if c not in template.columns
]

if not missing_template:
    print("PASS | Evidence template contains required fields")
else:
    print(f"FAIL | Missing template fields: {missing_template}")
    errors.append("Template fields")


required_final = [
    "Validated_Complete_Record",
    "Final_Recommendation_Eligible",
    "Final_Decision_State",
    "Final_Decision_Approved",
]

missing_final = [
    c for c in required_final
    if c not in final_gate.columns
]

if not missing_final:
    print("PASS | Final decision gate contains required fields")
else:
    print(f"FAIL | Missing final-gate fields: {missing_final}")
    errors.append("Final gate fields")


# ============================================================
# 6. SCOUTING SCORE RANGE
# ============================================================

print("\n6. SCOUTING SCORE RANGE")

score_columns = [
    "Role_Fit_Score",
    "Tactical_Fit_Score",
    "Technical_Fit_Score",
    "Physical_Fit_Score",
    "Development_Confidence",
    "Evidence_Confidence",
]

score_error = False

for col in score_columns:
    values = pd.to_numeric(
        validated[col],
        errors="coerce",
    )

    invalid = (
        values.notna()
        & ~values.between(1, 5)
    )

    if invalid.any():
        print(f"FAIL | Invalid values found in {col}")
        score_error = True

if not score_error:
    print("PASS | All entered scouting scores are within 1–5")
else:
    errors.append("Scouting score range")


# ============================================================
# 7. SCOUT RECOMMENDATIONS
# ============================================================

print("\n7. SCOUT RECOMMENDATIONS")

allowed_recommendations = {
    "PENDING",
    "RECOMMEND",
    "CONTINUE SCOUTING",
    "HOLD",
    "REJECT",
}

actual_recommendations = set(
    validated["Scout_Recommendation"]
    .dropna()
    .astype(str)
    .str.strip()
    .str.upper()
)

unexpected = (
    actual_recommendations
    - allowed_recommendations
)

if not unexpected:
    print("PASS | Scout recommendations use approved categories")
else:
    print(f"FAIL | Unexpected recommendations: {unexpected}")
    errors.append("Scout recommendations")


# ============================================================
# 8. COMPLETION CONSISTENCY
# ============================================================

print("\n8. COMPLETION CONSISTENCY")

completed = final_gate[
    "Validated_Complete_Record"
].astype(str).str.lower().eq("true")

eligible = final_gate[
    "Final_Recommendation_Eligible"
].astype(str).str.lower().eq("true")

approved = final_gate[
    "Final_Decision_Approved"
].astype(str).str.lower().eq("true")

if (eligible & ~completed).any():
    print(
        "FAIL | Candidate marked eligible without "
        "validated complete record"
    )
    errors.append("Eligibility gate")
else:
    print(
        "PASS | No candidate is eligible without "
        "validated human evidence"
    )

if (approved & ~completed).any():
    print(
        "FAIL | Candidate approved without "
        "validated complete record"
    )
    errors.append("Approval gate")
else:
    print(
        "PASS | No candidate is approved without "
        "validated human evidence"
    )


# ============================================================
# 9. CURRENT BLANK-TEMPLATE STATE
# ============================================================

print("\n9. CURRENT VALIDATION STATE")

complete_count = int(completed.sum())
approved_count = int(approved.sum())

print(f"INFO | Completed scouting records: {complete_count}")
print(f"INFO | Final recommendations approved: {approved_count}")

if complete_count == 0 and approved_count == 0:
    print(
        "PASS | Blank Phase 4 template remains safely blocked"
    )
else:
    print(
        "INFO | Human scouting evidence has been entered"
    )


# ============================================================
# 10. FINAL DECISION STATE
# ============================================================

print("\n10. FINAL DECISION STATE")

allowed_states = {
    "SCOUTING REQUIRED",
    "FINAL RECOMMENDATION",
    "CONTINUE SCOUTING",
    "HOLD",
    "REJECT",
}

actual_states = set(
    final_gate["Final_Decision_State"]
    .dropna()
)

unexpected_states = actual_states - allowed_states

if not unexpected_states:
    print("PASS | Final decision states use approved categories")
else:
    print(f"FAIL | Unexpected states: {unexpected_states}")
    errors.append("Final decision states")


# ============================================================
# FINAL RESULT
# ============================================================

print("\n" + "=" * 90)

if errors:
    print(
        f"PHASE 4 QA RESULT: FAILED — "
        f"{len(errors)} issue(s)"
    )

    for error in errors:
        print(f" - {error}")

    sys.exit(1)

print("PHASE 4 QA RESULT: PASSED")
print("Phase 4 human-scouting decision gate is ready to freeze.")
print("=" * 90)


