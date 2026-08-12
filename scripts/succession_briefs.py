from pathlib import Path
import pandas as pd


# ============================================================
# NEWCASTLE UNITED — PHASE 5.2
# SUCCESSION BRIEFS
# ============================================================

MASTER_FILE = Path(
    "data/outputs/phase5/executive_master_summary_v1_0.csv"
)

OUTPUT_DIR = Path(
    "data/outputs/phase5/succession_briefs"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


print("=" * 100)
print("NEWCASTLE UNITED — PHASE 5.2 SUCCESSION BRIEFS")
print("=" * 100)


# ============================================================
# 1. LOAD EXECUTIVE MASTER
# ============================================================

master = pd.read_csv(MASTER_FILE)

print("\nPHASE 5.2 — INPUT CHECK")
print("-" * 100)

print(f"Executive candidates loaded: {len(master)}")

if len(master) != 9:
    raise ValueError(
        f"Expected 9 executive candidates, found {len(master)}"
    )

expected_targets = {
    "Anthony Gordon",
    "Bruno Guimaraes",
    "Sandro Tonali",
}

actual_targets = set(
    master["Replacement_For"]
    .dropna()
    .unique()
)

if actual_targets != expected_targets:
    raise ValueError(
        f"Unexpected succession targets: {sorted(actual_targets)}"
    )

print("PASS | 9 executive candidates loaded")
print("PASS | All three succession problems confirmed")


# ============================================================
# 2. RANK CANDIDATES WITHIN EACH SUCCESSION PROBLEM
# ============================================================

tier_rank = {
    "PRIORITY TARGET": 1,
    "STRONG SHORTLIST": 2,
}

master["_Tier_Rank"] = (
    master["Decision_Tier"]
    .map(tier_rank)
    .fillna(99)
)

master = master.sort_values(
    [
        "Replacement_For",
        "_Tier_Rank",
        "Risk_Adjusted_Score",
    ],
    ascending=[True, True, False],
).reset_index(drop=True)

master["Succession_Rank"] = (
    master
    .groupby("Replacement_For")
    .cumcount()
    + 1
)


# ============================================================
# 3. BUILD ONE-LINE EXECUTIVE RATIONALE
# ============================================================

def build_rationale(row):
    parts = []

    evidence = str(
        row.get("Evidence_Band", "")
    ).upper()

    risk = str(
        row.get("Recruitment_Risk", "")
    ).upper()

    development = str(
        row.get("Development_Profile", "")
    ).upper()

    if evidence:
        parts.append(
            f"{evidence.lower()} evidence"
        )

    if risk:
        parts.append(
            f"{risk.lower()} recruitment risk"
        )

    if development:
        parts.append(
            development.lower()
        )

    action = str(
        row.get("Suggested_Action", "")
    ).strip()

    if action:
        parts.append(
            f"next step: {action.lower()}"
        )

    return "; ".join(parts)


master["Executive_Rationale"] = master.apply(
    build_rationale,
    axis=1,
)


# ============================================================
# 4. DISPLAY SUCCESSION BRIEFS
# ============================================================

print("\n" + "=" * 100)
print("PHASE 5.2 — SUCCESSION BRIEFS")
print("=" * 100)

for replacement_for, group in master.groupby(
    "Replacement_For",
    sort=False,
):

    print(
        f"\nREPLACEMENT FOR: "
        f"{replacement_for.upper()}"
    )

    print("-" * 100)

    for _, row in group.iterrows():

        print(
            f"{int(row['Succession_Rank'])}. "
            f"{row['Player']} "
            f"| {row['Decision_Tier']} "
            f"| Score {row['Risk_Adjusted_Score']:.1f}"
        )

        print(
            f"   {row['Executive_Rationale']}"
        )

        print(
            f"   Status: "
            f"{row['Executive_Status']}"
        )


# ============================================================
# 5. EXPORT INDIVIDUAL CSV BRIEFS
# ============================================================

brief_columns = [
    c for c in [
        "Succession_Rank",
        "Player",
        "Replacement_For",
        "Age",
        "Decision_Tier",
        "Risk_Adjusted_Score",
        "Succession_Score",
        "Evidence_Band",
        "Recruitment_Risk",
        "Development_Profile",
        "Validation_Flag_Count",
        "Validation_Flags",
        "Suggested_Action",
        "Final_Decision_State",
        "Executive_Status",
        "Executive_Rationale",
    ]
    if c in master.columns
]

exported_files = []

for replacement_for, group in master.groupby(
    "Replacement_For",
    sort=False,
):

    slug = (
        replacement_for
        .lower()
        .replace(" ", "_")
    )

    output_file = (
        OUTPUT_DIR /
        f"{slug}_succession_brief_v1_0.csv"
    )

    group[
        brief_columns
    ].to_csv(
        output_file,
        index=False,
    )

    exported_files.append(
        output_file
    )


# ============================================================
# 6. EXPORT ALL-BRIEFS MASTER
# ============================================================

ALL_BRIEFS_FILE = (
    OUTPUT_DIR /
    "all_succession_briefs_v1_0.csv"
)

master[
    brief_columns
].to_csv(
    ALL_BRIEFS_FILE,
    index=False,
)


# ============================================================
# 7. COMPLETE
# ============================================================

print("\n" + "=" * 100)
print("PHASE 5.2 COMPLETE")
print("=" * 100)

print(
    f"Succession briefs exported: "
    f"{len(exported_files)}"
)

for path in exported_files:
    print(f" - {path}")

print(
    f"Combined succession brief: "
    f"{ALL_BRIEFS_FILE}"
)


