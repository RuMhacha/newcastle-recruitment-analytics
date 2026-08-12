import pandas as pd
import sys
from pathlib import Path

MASTER = Path("data/outputs/phase2/recruitment_decision_board_v1_0.csv")
EXECUTIVE = Path("data/outputs/phase2/executive_shortlist_v1_0.csv")

errors = []

print("=" * 80)
print("NEWCASTLE UNITED — PHASE 2 FINAL QA")
print("=" * 80)

# ------------------------------------------------------------
# 1. FILES
# ------------------------------------------------------------

print("\n1. FILES")

for path in [MASTER, EXECUTIVE]:
    if path.exists():
        print(f"PASS | {path}")
    else:
        print(f"FAIL | Missing: {path}")
        errors.append(f"Missing file: {path}")

if errors:
    sys.exit(1)

master = pd.read_csv(MASTER)
executive = pd.read_csv(EXECUTIVE)

# ------------------------------------------------------------
# 2. ROW COUNTS
# ------------------------------------------------------------

print("\n2. ROW COUNTS")

if len(master) == 30:
    print("PASS | Master board contains exactly 30 rows")
else:
    print(f"FAIL | Master board contains {len(master)} rows")
    errors.append("Master row count")

if len(executive) == 9:
    print("PASS | Executive shortlist contains exactly 9 rows")
else:
    print(f"FAIL | Executive shortlist contains {len(executive)} rows")
    errors.append("Executive row count")

# ------------------------------------------------------------
# 3. SUCCESSION PROBLEMS
# ------------------------------------------------------------

print("\n3. SUCCESSION PROBLEMS")

expected = {
    "Anthony Gordon",
    "Bruno Guimaraes",
    "Sandro Tonali",
}

actual = set(master["Replacement_For"].dropna().unique())

if actual == expected:
    print("PASS | All three succession problems are present")
else:
    print(f"FAIL | Found: {sorted(actual)}")
    errors.append("Succession problems")

counts = master["Replacement_For"].value_counts()

for player in sorted(expected):
    count = counts.get(player, 0)

    if count == 10:
        print(f"PASS | {player}: exactly 10 candidates")
    else:
        print(f"FAIL | {player}: {count} candidates")
        errors.append(f"{player} candidate count")

# ------------------------------------------------------------
# 4. DECISION DATA
# ------------------------------------------------------------

print("\n4. DECISION DATA")

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

missing = [c for c in required if c not in master.columns]

if not missing:
    print("PASS | All required Phase 2 decision columns exist")
else:
    print(f"FAIL | Missing columns: {missing}")
    errors.append("Required columns")

if master["Player"].notna().all():
    print("PASS | No missing player names")
else:
    print("FAIL | Missing player names")
    errors.append("Missing players")

if master["Risk_Adjusted_Score"].notna().all():
    print("PASS | No missing risk-adjusted scores")
else:
    print("FAIL | Missing risk-adjusted scores")
    errors.append("Missing scores")

# ------------------------------------------------------------
# 5. EXECUTIVE SHORTLIST
# ------------------------------------------------------------

print("\n5. EXECUTIVE SHORTLIST")

allowed = {"PRIORITY TARGET", "STRONG SHORTLIST"}

bad_tiers = set(executive["Decision_Tier"].dropna()) - allowed

if not bad_tiers:
    print("PASS | Executive shortlist contains only approved tiers")
else:
    print(f"FAIL | Unexpected tiers: {bad_tiers}")
    errors.append("Executive tiers")

exec_counts = executive["Decision_Tier"].value_counts()

print(
    f"INFO | PRIORITY TARGET: "
    f"{exec_counts.get('PRIORITY TARGET', 0)}"
)
print(
    f"INFO | STRONG SHORTLIST: "
    f"{exec_counts.get('STRONG SHORTLIST', 0)}"
)

# ------------------------------------------------------------
# FINAL RESULT
# ------------------------------------------------------------

print("\n" + "=" * 80)

if errors:
    print(f"PHASE 2 QA RESULT: FAILED — {len(errors)} issue(s)")
    for error in errors:
        print(f" - {error}")
    sys.exit(1)

print("PHASE 2 QA RESULT: PASSED")
print("Phase 2 recruitment decision model is ready to freeze.")
print("=" * 80)


