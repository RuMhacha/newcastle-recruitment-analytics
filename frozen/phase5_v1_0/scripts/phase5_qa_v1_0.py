from pathlib import Path
import pandas as pd


# ============================================================
# NEWCASTLE UNITED — PHASE 5 FINAL INTEGRATION QA
# ============================================================

MASTER_FILE = Path(
    "data/outputs/phase5/executive_master_summary_v1_0.csv"
)

BRIEF_DIR = Path(
    "data/outputs/phase5/succession_briefs"
)

ALL_BRIEFS_FILE = (
    BRIEF_DIR / "all_succession_briefs_v1_0.csv"
)

INDIVIDUAL_BRIEFS = {
    "Anthony Gordon":
        BRIEF_DIR / "anthony_gordon_succession_brief_v1_0.csv",

    "Bruno Guimaraes":
        BRIEF_DIR / "bruno_guimaraes_succession_brief_v1_0.csv",

    "Sandro Tonali":
        BRIEF_DIR / "sandro_tonali_succession_brief_v1_0.csv",
}

PHASE4_GATE = Path(
    "frozen/phase4_v1_0/outputs/"
    "final_decision_gate_v1_0.csv"
)


def passed(message):
    print(f"PASS | {message}")


def fail(message):
    raise AssertionError(message)


print("=" * 100)
print("NEWCASTLE UNITED — PHASE 5 FINAL INTEGRATION QA")
print("=" * 100)


# ============================================================
# 1. FILE CHECK
# ============================================================

print("\n1. FILES")

required_files = [
    MASTER_FILE,
    ALL_BRIEFS_FILE,
    PHASE4_GATE,
    *INDIVIDUAL_BRIEFS.values(),
]

for path in required_files:
    if not path.exists():
        fail(f"Missing required file: {path}")

    passed(str(path))


# ============================================================
# 2. LOAD DATA
# ============================================================

master = pd.read_csv(MASTER_FILE)
all_briefs = pd.read_csv(ALL_BRIEFS_FILE)
phase4 = pd.read_csv(PHASE4_GATE)

individual = {
    target: pd.read_csv(path)
    for target, path in INDIVIDUAL_BRIEFS.items()
}


# ============================================================
# 3. ROW COUNTS
# ============================================================

print("\n2. ROW COUNTS")

if len(master) != 9:
    fail(f"Executive master expected 9 rows, found {len(master)}")

if len(all_briefs) != 9:
    fail(f"Combined briefs expected 9 rows, found {len(all_briefs)}")

if len(phase4) != 9:
    fail(f"Phase 4 gate expected 9 rows, found {len(phase4)}")

passed("Executive master contains exactly 9 rows")
passed("Combined succession briefs contain exactly 9 rows")
passed("Frozen Phase 4 gate contains exactly 9 rows")


# ============================================================
# 4. SUCCESSION COVERAGE
# ============================================================

print("\n3. SUCCESSION COVERAGE")

expected_counts = {
    "Anthony Gordon": 2,
    "Bruno Guimaraes": 3,
    "Sandro Tonali": 4,
}

actual_counts = (
    master["Replacement_For"]
    .value_counts()
    .to_dict()
)

if actual_counts != expected_counts:
    fail(
        f"Unexpected succession coverage: {actual_counts}"
    )

passed("Succession coverage is exactly 2 / 3 / 4")


# ============================================================
# 5. PLAYER CONSISTENCY
# ============================================================

print("\n4. PLAYER CONSISTENCY")

master_players = set(master["Player"])
brief_players = set(all_briefs["Player"])
phase4_players = set(phase4["Player"])

if not (
    master_players
    == brief_players
    == phase4_players
):
    fail(
        "Player sets differ between Phase 4 and Phase 5 outputs"
    )

passed(
    "Phase 4 gate, executive master, and combined briefs "
    "contain identical players"
)


# ============================================================
# 6. INDIVIDUAL BRIEF CONSISTENCY
# ============================================================

print("\n5. INDIVIDUAL SUCCESSION BRIEFS")

for target, df in individual.items():

    expected = expected_counts[target]

    if len(df) != expected:
        fail(
            f"{target} brief expected {expected} rows, "
            f"found {len(df)}"
        )

    if set(df["Replacement_For"]) != {target}:
        fail(
            f"{target} brief contains incorrect succession target"
        )

    expected_players = set(
        master.loc[
            master["Replacement_For"] == target,
            "Player"
        ]
    )

    if set(df["Player"]) != expected_players:
        fail(
            f"{target} brief players do not match executive master"
        )

    passed(
        f"{target}: {expected} candidates match executive master"
    )


# ============================================================
# 7. RANKING CONSISTENCY
# ============================================================

print("\n6. RANKING CONSISTENCY")

for target, df in individual.items():

    ordered = df.sort_values(
        "Succession_Rank"
    ).reset_index(drop=True)

    expected_ranks = list(
        range(1, len(ordered) + 1)
    )

    actual_ranks = (
        ordered["Succession_Rank"]
        .astype(int)
        .tolist()
    )

    if actual_ranks != expected_ranks:
        fail(
            f"{target} has invalid succession ranks: "
            f"{actual_ranks}"
        )

    scores = (
        ordered["Risk_Adjusted_Score"]
        .astype(float)
        .tolist()
    )

    # Ranking is tier-first, then risk-adjusted score.
    tiers = ordered["Decision_Tier"].tolist()

    tier_rank = {
        "PRIORITY TARGET": 1,
        "STRONG SHORTLIST": 2,
    }

    ordering_keys = [
        (
            tier_rank.get(tier, 99),
            -score,
        )
        for tier, score in zip(tiers, scores)
    ]

    if ordering_keys != sorted(ordering_keys):
        fail(
            f"{target} ranking is inconsistent with "
            f"tier/score ordering"
        )

    passed(
        f"{target} succession ranking is internally consistent"
    )


# ============================================================
# 8. EXECUTIVE STATUS SAFEGUARD
# ============================================================

print("\n7. EXECUTIVE STATUS SAFEGUARD")

allowed_statuses = {
    "AWAITING SCOUTING VALIDATION",
    "CONTINUE SCOUTING",
    "HOLD",
    "REJECTED",
    "APPROVED",
}

actual_statuses = set(
    master["Executive_Status"]
    .dropna()
)

if not actual_statuses.issubset(allowed_statuses):
    fail(
        f"Unexpected executive statuses: {actual_statuses}"
    )

passed("Executive statuses use approved categories")


# ============================================================
# 9. HUMAN SCOUTING GATE
# ============================================================

print("\n8. HUMAN SCOUTING GATE")

completed = (
    phase4["Validated_Complete_Record"]
    .fillna(False)
    .astype(bool)
)

approved = (
    phase4["Final_Decision_Approved"]
    .fillna(False)
    .astype(bool)
)

invalid_approval = approved & ~completed

if invalid_approval.any():
    bad_players = phase4.loc[
        invalid_approval,
        "Player"
    ].tolist()

    fail(
        "Candidate approved without completed scouting: "
        f"{bad_players}"
    )

passed(
    "No candidate is approved without completed "
    "human scouting evidence"
)


# ============================================================
# 10. CURRENT BLANK-TEMPLATE STATE
# ============================================================

print("\n9. CURRENT VALIDATION STATE")

completed_count = int(completed.sum())
approved_count = int(approved.sum())

print(
    f"INFO | Completed human scouting records: "
    f"{completed_count}"
)

print(
    f"INFO | Final recruitment approvals: "
    f"{approved_count}"
)

if completed_count == 0:

    expected_status = {
        "AWAITING SCOUTING VALIDATION"
    }

    actual = set(
        master["Executive_Status"]
    )

    if actual != expected_status:
        fail(
            "Blank scouting state should leave all candidates "
            "awaiting scouting validation"
        )

    passed(
        "Blank human-scouting state remains safely blocked"
    )


# ============================================================
# 11. REQUIRED EXECUTIVE FIELDS
# ============================================================

print("\n10. REQUIRED EXECUTIVE FIELDS")

required_columns = {
    "Player",
    "Replacement_For",
    "Decision_Tier",
    "Risk_Adjusted_Score",
    "Evidence_Band",
    "Recruitment_Risk",
    "Suggested_Action",
    "Final_Decision_State",
    "Executive_Status",
}

missing = (
    required_columns
    - set(master.columns)
)

if missing:
    fail(
        f"Executive master missing fields: {sorted(missing)}"
    )

passed("Executive master contains all required fields")


# ============================================================
# FINAL RESULT
# ============================================================

print("\n" + "=" * 100)
print("PHASE 5 QA RESULT: PASSED")
print(
    "Executive reporting layer is internally consistent "
    "and preserves the human-scouting decision gate."
)
print("=" * 100)


