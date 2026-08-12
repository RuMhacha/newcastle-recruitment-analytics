from pathlib import Path
import pandas as pd
import sys

DOSSIER_FILE = Path(
    "data/outputs/phase3/scouting_validation_dossiers_v1_0.csv"
)

ACTION_FILE = Path(
    "data/outputs/phase3/scouting_action_queue_v1_0.csv"
)

errors = []

print("=" * 90)
print("NEWCASTLE UNITED — PHASE 3 FINAL QA")
print("=" * 90)


# ============================================================
# 1. FILE CHECKS
# ============================================================

print("\n1. FILES")

for path in [DOSSIER_FILE, ACTION_FILE]:
    if path.exists():
        print(f"PASS | {path}")
    else:
        print(f"FAIL | Missing file: {path}")
        errors.append(f"Missing file: {path}")

if errors:
    sys.exit(1)

dossiers = pd.read_csv(DOSSIER_FILE)
actions = pd.read_csv(ACTION_FILE)


# ============================================================
# 2. ROW COUNTS
# ============================================================

print("\n2. ROW COUNTS")

if len(dossiers) == 9:
    print("PASS | Validation dossier contains exactly 9 rows")
else:
    print(f"FAIL | Dossier contains {len(dossiers)} rows")
    errors.append("Dossier row count")

if len(actions) == 9:
    print("PASS | Action queue contains exactly 9 rows")
else:
    print(f"FAIL | Action queue contains {len(actions)} rows")
    errors.append("Action queue row count")


# ============================================================
# 3. SUCCESSION COVERAGE
# ============================================================

print("\n3. SUCCESSION COVERAGE")

expected_targets = {
    "Anthony Gordon",
    "Bruno Guimaraes",
    "Sandro Tonali",
}

actual_targets = set(
    dossiers["Replacement_For"].dropna().unique()
)

if actual_targets == expected_targets:
    print("PASS | All three succession problems are present")
else:
    print(f"FAIL | Found targets: {sorted(actual_targets)}")
    errors.append("Succession coverage")


# ============================================================
# 4. REQUIRED VALIDATION FIELDS
# ============================================================

print("\n4. VALIDATION FIELDS")

required = [
    "Player",
    "Replacement_For",
    "Decision_Tier",
    "Validation_Flag_Count",
    "Validation_Flags",
    "Suggested_Action",
    "Role_Validation",
    "Evidence_Validation",
    "Development_Validation",
    "Overall_Validation_Status",
]

missing = [
    c for c in required
    if c not in dossiers.columns
]

if not missing:
    print("PASS | All required Phase 3 fields exist")
else:
    print(f"FAIL | Missing fields: {missing}")
    errors.append("Required fields")


# ============================================================
# 5. VALIDATION STATUS
# ============================================================

print("\n5. VALIDATION STATUS")

if (
    dossiers["Overall_Validation_Status"]
    .eq("PENDING VALIDATION")
    .all()
):
    print("PASS | All 9 candidates are pending validation")
else:
    print("FAIL | Unexpected validation status found")
    errors.append("Validation status")


# ============================================================
# 6. ACTION CHECKS
# ============================================================

print("\n6. SUGGESTED ACTIONS")

allowed_actions = {
    "TACTICAL VALIDATION",
    "LIVE / VIDEO SCOUTING",
    "PROGRESS TO SCOUTING",
    "VIDEO VALIDATION",
    "DATA + VIDEO REVIEW",
    "HOLD — RESOLVE RISK",
}

unexpected = set(
    dossiers["Suggested_Action"].dropna()
) - allowed_actions

if not unexpected:
    print("PASS | All suggested actions use approved categories")
else:
    print(f"FAIL | Unexpected actions: {unexpected}")
    errors.append("Suggested actions")


# ============================================================
# 7. FLAG CONSISTENCY
# ============================================================

print("\n7. VALIDATION FLAGS")

flag_counts = pd.to_numeric(
    dossiers["Validation_Flag_Count"],
    errors="coerce"
)

if flag_counts.notna().all():
    print("PASS | All validation flag counts are numeric")
else:
    print("FAIL | Invalid validation flag count")
    errors.append("Validation flag counts")

if (flag_counts >= 0).all():
    print("PASS | No negative validation flag counts")
else:
    print("FAIL | Negative validation flag count found")
    errors.append("Negative flag counts")


# ============================================================
# 8. ACTION QUEUE CONSISTENCY
# ============================================================

print("\n8. ACTION QUEUE")

dossier_players = set(dossiers["Player"])
action_players = set(actions["Player"])

if dossier_players == action_players:
    print("PASS | Action queue contains the same 9 players")
else:
    print("FAIL | Player mismatch between dossier and action queue")
    errors.append("Action queue player mismatch")


# ============================================================
# FINAL RESULT
# ============================================================

print("\n" + "=" * 90)

if errors:
    print(
        f"PHASE 3 QA RESULT: FAILED — "
        f"{len(errors)} issue(s)"
    )

    for error in errors:
        print(f" - {error}")

    sys.exit(1)

print("PHASE 3 QA RESULT: PASSED")
print("Phase 3 scouting validation system is ready to freeze.")
print("=" * 90)


