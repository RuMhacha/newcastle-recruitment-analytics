from pathlib import Path
import pandas as pd

# ============================================================
# NEWCASTLE UNITED — PROJECT v1.0 RELEASE QA
# ============================================================

print("=" * 100)
print("NEWCASTLE UNITED — PROJECT v1.0 RELEASE QA")
print("=" * 100)


# ============================================================
# 1. REQUIRED FROZEN PHASES
# ============================================================

print("\n1. FROZEN PHASE STRUCTURE")

required_dirs = [
    Path("frozen/phase2_v1_0"),
    Path("frozen/phase3_v1_0"),
    Path("frozen/phase4_v1_0"),
    Path("frozen/phase5_v1_0"),
]

for path in required_dirs:
    if not path.exists():
        raise AssertionError(
            f"Missing frozen phase directory: {path}"
        )

    print(f"PASS | {path}")


# ============================================================
# 2. REQUIRED RELEASE ARTIFACTS
# ============================================================

print("\n2. REQUIRED ARTIFACTS")

PHASE2_EXECUTIVE = Path(
    "frozen/phase2_v1_0/outputs/"
    "executive_shortlist_v1_0.csv"
)

PHASE3_DOSSIERS = Path(
    "frozen/phase3_v1_0/outputs/"
    "scouting_validation_dossiers_v1_0.csv"
)

PHASE4_GATE = Path(
    "frozen/phase4_v1_0/outputs/"
    "final_decision_gate_v1_0.csv"
)

PHASE5_MASTER = Path(
    "frozen/phase5_v1_0/outputs/"
    "executive_master_summary_v1_0.csv"
)

PHASE5_ALL_BRIEFS = Path(
    "frozen/phase5_v1_0/outputs/"
    "succession_briefs/"
    "all_succession_briefs_v1_0.csv"
)

README = Path("README.md")

required_files = [
    PHASE2_EXECUTIVE,
    PHASE3_DOSSIERS,
    PHASE4_GATE,
    PHASE5_MASTER,
    PHASE5_ALL_BRIEFS,
    README,
]

for path in required_files:
    if not path.exists():
        raise AssertionError(
            f"Missing required release artifact: {path}"
        )

    print(f"PASS | {path}")


# ============================================================
# 3. LOAD FROZEN DATA
# ============================================================

phase2 = pd.read_csv(PHASE2_EXECUTIVE)
phase3 = pd.read_csv(PHASE3_DOSSIERS)
phase4 = pd.read_csv(PHASE4_GATE)
phase5 = pd.read_csv(PHASE5_MASTER)
briefs = pd.read_csv(PHASE5_ALL_BRIEFS)


# ============================================================
# 4. ROW COUNTS
# ============================================================

print("\n3. ROW COUNTS")

expected_rows = 9

for name, df in [
    ("Phase 2 executive shortlist", phase2),
    ("Phase 3 validation dossiers", phase3),
    ("Phase 4 final decision gate", phase4),
    ("Phase 5 executive master", phase5),
    ("Phase 5 combined briefs", briefs),
]:
    if len(df) != expected_rows:
        raise AssertionError(
            f"{name} expected {expected_rows} rows, "
            f"found {len(df)}"
        )

    print(
        f"PASS | {name} contains exactly "
        f"{expected_rows} rows"
    )


# ============================================================
# 5. PLAYER CONTINUITY
# ============================================================

print("\n4. PLAYER CONTINUITY")

player_sets = [
    set(phase2["Player"]),
    set(phase3["Player"]),
    set(phase4["Player"]),
    set(phase5["Player"]),
    set(briefs["Player"]),
]

if not all(
    players == player_sets[0]
    for players in player_sets[1:]
):
    raise AssertionError(
        "Player sets are inconsistent across frozen phases"
    )

print(
    "PASS | Identical 9-player executive population "
    "across Phases 2–5"
)


# ============================================================
# 6. SUCCESSION COVERAGE
# ============================================================

print("\n5. SUCCESSION COVERAGE")

expected_counts = {
    "Anthony Gordon": 2,
    "Bruno Guimaraes": 3,
    "Sandro Tonali": 4,
}

for name, df in [
    ("Phase 2", phase2),
    ("Phase 3", phase3),
    ("Phase 4", phase4),
    ("Phase 5", phase5),
]:
    counts = (
        df["Replacement_For"]
        .value_counts()
        .to_dict()
    )

    if counts != expected_counts:
        raise AssertionError(
            f"{name} succession coverage mismatch: "
            f"{counts}"
        )

    print(
        f"PASS | {name} succession coverage is 2 / 3 / 4"
    )


# ============================================================
# 7. DECISION TIER CONTINUITY
# ============================================================

print("\n6. DECISION TIER CONTINUITY")

p2_tiers = (
    phase2[
        ["Player", "Decision_Tier"]
    ]
    .sort_values("Player")
    .reset_index(drop=True)
)

p5_tiers = (
    phase5[
        ["Player", "Decision_Tier"]
    ]
    .sort_values("Player")
    .reset_index(drop=True)
)

if not p2_tiers.equals(p5_tiers):
    raise AssertionError(
        "Phase 5 decision tiers differ from frozen Phase 2"
    )

print(
    "PASS | Phase 5 preserves frozen Phase 2 decision tiers"
)


# ============================================================
# 8. RISK-ADJUSTED SCORE CONTINUITY
# ============================================================

print("\n7. RISK-ADJUSTED SCORE CONTINUITY")

p2_scores = (
    phase2[
        ["Player", "Risk_Adjusted_Score"]
    ]
    .sort_values("Player")
    .reset_index(drop=True)
)

p5_scores = (
    phase5[
        ["Player", "Risk_Adjusted_Score"]
    ]
    .sort_values("Player")
    .reset_index(drop=True)
)

merged_scores = p2_scores.merge(
    p5_scores,
    on="Player",
    suffixes=("_p2", "_p5"),
)

score_diff = (
    merged_scores["Risk_Adjusted_Score_p2"]
    - merged_scores["Risk_Adjusted_Score_p5"]
).abs()

if (score_diff > 1e-9).any():
    raise AssertionError(
        "Phase 5 risk-adjusted scores differ from Phase 2"
    )

print(
    "PASS | Phase 5 preserves frozen Phase 2 "
    "risk-adjusted scores"
)


# ============================================================
# 9. VALIDATION ACTION CONTINUITY
# ============================================================

print("\n8. VALIDATION ACTION CONTINUITY")

p3_actions = (
    phase3[
        ["Player", "Suggested_Action"]
    ]
    .sort_values("Player")
    .reset_index(drop=True)
)

p5_actions = (
    phase5[
        ["Player", "Suggested_Action"]
    ]
    .sort_values("Player")
    .reset_index(drop=True)
)

if not p3_actions.equals(p5_actions):
    raise AssertionError(
        "Phase 5 suggested actions differ from Phase 3"
    )

print(
    "PASS | Phase 5 preserves frozen Phase 3 scouting actions"
)


# ============================================================
# 10. HUMAN-SCOUTING SAFEGUARD
# ============================================================

print("\n9. HUMAN-SCOUTING SAFEGUARD")

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

if (approved & ~completed).any():
    bad = phase4.loc[
        approved & ~completed,
        "Player"
    ].tolist()

    raise AssertionError(
        "Approval exists without completed scouting: "
        f"{bad}"
    )

print(
    "PASS | No final approval exists without "
    "completed human scouting"
)


# ============================================================
# 11. CURRENT RELEASE STATE
# ============================================================

print("\n10. CURRENT RELEASE STATE")

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
    statuses = set(
        phase5["Executive_Status"]
    )

    if statuses != {
        "AWAITING SCOUTING VALIDATION"
    }:
        raise AssertionError(
            "Blank scouting state should leave all "
            "executive candidates awaiting validation"
        )

    print(
        "PASS | Blank scouting state remains safely blocked"
    )


# ============================================================
# 12. SUCCESSION BRIEF RANKINGS
# ============================================================

print("\n11. SUCCESSION BRIEF RANKINGS")

for target, group in briefs.groupby(
    "Replacement_For"
):
    ordered = group.sort_values(
        "Succession_Rank"
    )

    expected_ranks = list(
        range(1, len(ordered) + 1)
    )

    actual_ranks = (
        ordered["Succession_Rank"]
        .astype(int)
        .tolist()
    )

    if actual_ranks != expected_ranks:
        raise AssertionError(
            f"{target} succession ranks are invalid: "
            f"{actual_ranks}"
        )

    print(
        f"PASS | {target} succession ranks are sequential"
    )


# ============================================================
# 13. README CHECK
# ============================================================

print("\n12. README")

readme_text = README.read_text(
    encoding="utf-8"
)

required_readme_sections = [
    "## 1. Project Objective",
    "## 2. Analytical Architecture",
    "## 3. Core Design Principle",
    "## 13. Quality Assurance",
    "## 14. Reproducibility",
    "## 16. Limitations",
    "## 17. Project Status",
]

for section in required_readme_sections:
    if section not in readme_text:
        raise AssertionError(
            f"README missing section: {section}"
        )

print(
    "PASS | README contains required methodology "
    "and reproducibility sections"
)


# ============================================================
# 14. FROZEN FILE PERMISSIONS
# ============================================================

print("\n13. FROZEN FILE PERMISSIONS")

frozen_files = []

for phase_dir in required_dirs:
    frozen_files.extend(
        [
            path
            for path in phase_dir.rglob("*")
            if path.is_file()
        ]
    )

writable_files = [
    path
    for path in frozen_files
    if path.stat().st_mode & 0o222
]

if writable_files:
    raise AssertionError(
        "Writable files found inside frozen releases: "
        f"{writable_files}"
    )

print(
    f"PASS | {len(frozen_files)} frozen release files "
    "are write-protected"
)


# ============================================================
# FINAL RESULT
# ============================================================

print("\n" + "=" * 100)
print("RELEASE QA RESULT: PASSED")
print(
    "Newcastle recruitment analytics v1.0 "
    "is ready for release."
)
print("=" * 100)


