import pandas as pd
from pathlib import Path

BOARD = Path("data/outputs/succession_recruitment_board_v1_0.csv")
MULTI = Path("data/outputs/multi_player_successors_v1_0.csv")

print("=" * 80)
print("NEWCASTLE RECRUITMENT MODEL — QA CHECKS")
print("=" * 80)

board = pd.read_csv(BOARD)
multi = pd.read_csv(MULTI)

errors = []
warnings = []


def check(condition, message):
    if condition:
        print(f"PASS  | {message}")
    else:
        print(f"FAIL  | {message}")
        errors.append(message)


# ------------------------------------------------------------
# 1. FILE / STRUCTURE CHECKS
# ------------------------------------------------------------

print("\n1. STRUCTURE")

required = [
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

check(
    all(c in board.columns for c in required),
    "All required recruitment-board columns exist"
)

check(len(board) > 0, "Recruitment board is not empty")
check(len(multi) > 0, "Multi-player successor table is not empty")


# ------------------------------------------------------------
# 2. MISSING DATA
# ------------------------------------------------------------

print("\n2. MISSING DATA")

check(
    board["Player"].notna().all(),
    "No missing player names"
)

check(
    board["Succession_Score"].notna().all(),
    "No missing succession scores"
)

check(
    board["Recruitment_Verdict"].notna().all(),
    "No missing recruitment verdicts"
)


# ------------------------------------------------------------
# 3. RANGE CHECKS
# ------------------------------------------------------------

print("\n3. VALUE RANGES")

check(
    board["Age"].between(15, 40).all(),
    "All player ages are plausible"
)

check(
    (board["Min"] >= 0).all(),
    "No negative minutes"
)

check(
    board["Similarity"].between(0, 100).all(),
    "Similarity scores are between 0 and 100"
)

check(
    board["Quality"].between(0, 100).all(),
    "Quality scores are between 0 and 100"
)

check(
    board["Succession_Score"].between(0, 100).all(),
    "Succession scores are between 0 and 100"
)


# ------------------------------------------------------------
# 4. SUCCESSION BOARD CHECKS
# ------------------------------------------------------------

print("\n4. SUCCESSION BOARDS")

expected_targets = {
    "Bruno Guimaraes",
    "Sandro Tonali",
    "Anthony Gordon",
}

actual_targets = set(board["Replacement_For"].dropna())

check(
    expected_targets == actual_targets,
    "All three Newcastle succession problems are present"
)

counts = board.groupby("Replacement_For").size()

for player in sorted(expected_targets):
    count = counts.get(player, 0)

    check(
        count == 10,
        f"{player} has exactly 10 shortlisted candidates"
    )


# ------------------------------------------------------------
# 5. DUPLICATES
# ------------------------------------------------------------

print("\n5. DUPLICATES")

duplicate_rows = board.duplicated(
    subset=["Player", "Replacement_For"]
).sum()

check(
    duplicate_rows == 0,
    "No duplicate player/replacement combinations"
)


# ------------------------------------------------------------
# 6. VERDICT CHECKS
# ------------------------------------------------------------

print("\n6. RECRUITMENT VERDICTS")

allowed_verdicts = {
    "PRIORITY TARGET",
    "STRONG OPTION",
    "SCOUT FURTHER",
    "MONITOR",
    "LOW PRIORITY",
}

unexpected = set(
    board["Recruitment_Verdict"].dropna()
) - allowed_verdicts

check(
    len(unexpected) == 0,
    "All recruitment verdicts use approved categories"
)


# ------------------------------------------------------------
# FINAL RESULT
# ------------------------------------------------------------

print("\n" + "=" * 80)

if errors:
    print(f"QA RESULT: FAILED — {len(errors)} check(s) need attention")
    for error in errors:
        print(f"  - {error}")
else:
    print("QA RESULT: PASSED")
    print("Succession Model v1.0 passed all automated checks.")

print("=" * 80)


