import pandas as pd
import numpy as np
import os

# ============================================================
# NEWCASTLE UNITED — REPLACEMENT ANALYSIS
# ============================================================

RECRUITMENT_FILE = "data/processed/newcastle_recruitment_2025_26.csv"

STANDARD_FILE = "data/raw/newcastle_standard_2025_26.csv"
SHOOTING_FILE = "data/raw/newcastle_shooting_2025_26.csv"
PLAYING_FILE = "data/raw/newcastle_playing_time_2025_26.csv"
MISC_FILE = "data/raw/newcastle_misc_2025_26.csv"

BENCHMARK_PLAYERS = [
    "Bruno Guimarães",
    "Sandro Tonali",
    "Anthony Gordon",
]

# ------------------------------------------------------------
# LOAD RECRUITMENT DATABASE
# ------------------------------------------------------------

recruit = pd.read_csv(RECRUITMENT_FILE)

print("=" * 80)
print("NEWCASTLE UNITED — REPLACEMENT ANALYSIS")
print("=" * 80)
print(f"Recruitment players loaded: {len(recruit)}")
print(f"Recruitment columns loaded: {len(recruit.columns)}")

# ------------------------------------------------------------
# LOAD NEWCASTLE RAW DATA
# FBref exports use the second row as the real header
# ------------------------------------------------------------

standard = pd.read_csv(STANDARD_FILE, header=1)
shooting = pd.read_csv(SHOOTING_FILE, header=1)
playing = pd.read_csv(PLAYING_FILE, header=1)
misc = pd.read_csv(MISC_FILE, header=1)

print("\nNewcastle files loaded:")
print(f"Standard:     {standard.shape}")
print(f"Shooting:     {shooting.shape}")
print(f"Playing time: {playing.shape}")
print(f"Misc:         {misc.shape}")

# ------------------------------------------------------------
# KEEP BENCHMARK PLAYERS
# ------------------------------------------------------------

def benchmark_rows(df):
    return df[
        df["Player"].astype(str).isin(BENCHMARK_PLAYERS)
    ].copy()

standard_b = benchmark_rows(standard)
shooting_b = benchmark_rows(shooting)
playing_b = benchmark_rows(playing)
misc_b = benchmark_rows(misc)

print("\nBenchmark player check:")

for player in BENCHMARK_PLAYERS:
    found = player in standard_b["Player"].values
    print(f"{player}: {'FOUND' if found else 'NOT FOUND'}")

# ------------------------------------------------------------
# BASIC BENCHMARK TABLE
# ------------------------------------------------------------

benchmark = standard_b[
    ["Player", "Nation", "Pos", "Age", "Min", "90s", "Gls", "Ast"]
].copy()

benchmark = benchmark.merge(
    shooting_b[["Player", "Sh/90", "SoT/90"]],
    on="Player",
    how="left"
)

benchmark = benchmark.merge(
    misc_b[["Player", "Fls", "Fld", "Crs", "Int", "TklW"]],
    on="Player",
    how="left"
)

print("\n" + "=" * 80)
print("NEWCASTLE BENCHMARK PLAYERS — RAW PROFILE")
print("=" * 80)
print(benchmark.to_string(index=False))


# ============================================================
# BUILD COMPARABLE PER-90 BENCHMARKS
# ============================================================

# Convert numeric columns safely
numeric_cols = [
    "90s", "Gls", "Ast", "Sh/90", "SoT/90",
    "Fls", "Fld", "Crs", "Int", "TklW"
]

for col in numeric_cols:
    benchmark[col] = pd.to_numeric(benchmark[col], errors="coerce")

# Newcastle per-90 metrics
benchmark["Gls_per90"] = benchmark["Gls"] / benchmark["90s"]
benchmark["Ast_per90"] = benchmark["Ast"] / benchmark["90s"]
benchmark["GA_per90"] = (
    benchmark["Gls"] + benchmark["Ast"]
) / benchmark["90s"]

benchmark["Shots_per90"] = benchmark["Sh/90"]
benchmark["SoT_per90_calc"] = benchmark["SoT/90"]

benchmark["Int_per90"] = benchmark["Int"] / benchmark["90s"]
benchmark["TklW_per90"] = benchmark["TklW"] / benchmark["90s"]
benchmark["Crs_per90"] = benchmark["Crs"] / benchmark["90s"]
benchmark["Fls_per90"] = benchmark["Fls"] / benchmark["90s"]
benchmark["Fld_per90"] = benchmark["Fld"] / benchmark["90s"]

comparison_metrics = [
    "Gls_per90",
    "Ast_per90",
    "GA_per90",
    "Shots_per90",
    "SoT_per90_calc",
    "Int_per90",
    "TklW_per90",
    "Crs_per90",
    "Fls_per90",
    "Fld_per90",
]

print("\n" + "=" * 100)
print("NEWCASTLE BENCHMARK PLAYERS — PER 90 PROFILE")
print("=" * 100)

display_cols = ["Player", "Pos", "Age", "Min"] + comparison_metrics

print(
    benchmark[display_cols]
    .round(2)
    .to_string(index=False)
)

# ------------------------------------------------------------
# CHECK RECRUITMENT DATABASE HAS SAME METRICS
# ------------------------------------------------------------

available_metrics = [
    col for col in comparison_metrics
    if col in recruit.columns
]

missing_metrics = [
    col for col in comparison_metrics
    if col not in recruit.columns
]

print("\nComparable recruitment metrics:")
print(available_metrics)

print("\nMissing recruitment metrics:")
print(missing_metrics)


# ============================================================
# STANDARDISED PLAYER SIMILARITY
# ============================================================

SIMILARITY_METRICS = [
    "Gls_per90",
    "Ast_per90",
    "Shots_per90",
    "SoT_per90_calc",
    "Int_per90",
    "TklW_per90",
    "Crs_per90",
    "Fls_per90",
    "Fld_per90",
]

# Convert recruitment metrics to numeric
for col in SIMILARITY_METRICS:
    recruit[col] = pd.to_numeric(recruit[col], errors="coerce")

# Population mean/std used to put every metric onto same scale
metric_means = recruit[SIMILARITY_METRICS].mean()
metric_stds = recruit[SIMILARITY_METRICS].std()

# Avoid division problems if any metric has zero variance
metric_stds = metric_stds.replace(0, np.nan)


def find_similar_players(
    benchmark_player,
    position_group,
    role_score,
    tier_column,
    max_age=27,
    min_minutes=900,
    top_n=15
):
    # --------------------------------------------------------
    # Benchmark profile
    # --------------------------------------------------------

    target = benchmark[
        benchmark["Player"] == benchmark_player
    ].iloc[0]

    target_values = pd.to_numeric(
        target[SIMILARITY_METRICS],
        errors="coerce"
    )

    target_z = (
        target_values - metric_means
    ) / metric_stds

    # --------------------------------------------------------
    # Candidate pool
    # --------------------------------------------------------

    candidates = recruit[
        (recruit["Position_Group"] == position_group)
        & (recruit["Min"] >= min_minutes)
        & (recruit["Age"].notna())
        & (recruit["Age"] <= max_age)
    ].copy()

    # Only compare complete profiles
    candidates = candidates.dropna(
        subset=SIMILARITY_METRICS
    )

    candidate_z = (
        candidates[SIMILARITY_METRICS] - metric_means
    ) / metric_stds

    # --------------------------------------------------------
    # Standardised Euclidean distance
    # Root mean squared difference across metrics
    # --------------------------------------------------------

    squared_diff = (
        candidate_z - target_z.values
    ) ** 2

    candidates["Profile_Distance"] = np.sqrt(
        squared_diff.mean(axis=1)
    )

    # Convert distance to an intuitive 0–100 similarity score.
    # Identical profile = 100.
    candidates["Similarity"] = (
        100 / (1 + candidates["Profile_Distance"])
    )

    candidates = candidates.sort_values(
        "Similarity",
        ascending=False
    )

    display = [
        "Player",
        "Squad",
        "League",
        "Age",
        "Min",
        "Similarity",
        role_score,
        tier_column,
    ]

    print("\n" + "=" * 100)
    print(f"{benchmark_player.upper()} — REPLACEMENT PROFILE")
    print("=" * 100)

    print(
        candidates[display]
        .head(top_n)
        .round(2)
        .to_string(index=False)
    )

    return candidates

# ============================================================
# NEWCASTLE SUCCESSION SEARCHES
# ============================================================

bruno_matches = find_similar_players(
    benchmark_player="Bruno Guimarães",
    position_group="Midfielder",
    role_score="Midfielder_TwoWay",
    tier_column="Midfielder_TwoWay_Tier",
    max_age=25
)

tonali_matches = find_similar_players(
    benchmark_player="Sandro Tonali",
    position_group="Midfielder",
    role_score="Midfielder_TwoWay",
    tier_column="Midfielder_TwoWay_Tier",
    max_age=25
)

gordon_matches = find_similar_players(
    benchmark_player="Anthony Gordon",
    position_group="Attacker",
    role_score="Attacker_TwoWay",
    tier_column="Attacker_TwoWay_Tier",
    max_age=25
)


# ============================================================
# WEIGHTED BRUNO GUIMARAES REPLACEMENT MODEL
# ============================================================

BRUNO_WEIGHTS = {
    "Gls_per90": 0.10,
    "Ast_per90": 0.15,
    "Shots_per90": 0.05,
    "SoT_per90_calc": 0.05,
    "Int_per90": 0.15,
    "TklW_per90": 0.20,
    "Crs_per90": 0.10,
    "Fls_per90": 0.05,
    "Fld_per90": 0.15,
}

print("\n" + "=" * 100)
print("BRUNO GUIMARAES — WEIGHTED SUCCESSION MODEL")
print("=" * 100)

def weighted_similarity(
    benchmark_player,
    position_group,
    weights,
    max_age=25,
    min_minutes=900,
):
    metrics = list(weights.keys())

    target = benchmark[
        benchmark["Player"] == benchmark_player
    ].iloc[0]

    target_values = pd.to_numeric(
        target[metrics],
        errors="coerce"
    )

    candidates = recruit[
        (recruit["Position_Group"] == position_group)
        & (recruit["Min"] >= min_minutes)
        & (recruit["Age"].notna())
        & (recruit["Age"] <= max_age)
    ].copy()

    candidates = candidates.dropna(subset=metrics)

    means = recruit[metrics].mean()
    stds = recruit[metrics].std().replace(0, np.nan)

    target_z = (target_values - means) / stds
    candidate_z = (candidates[metrics] - means) / stds

    weighted_sq_diff = pd.DataFrame(index=candidates.index)

    for metric, weight in weights.items():
        weighted_sq_diff[metric] = (
            (candidate_z[metric] - target_z[metric]) ** 2
        ) * weight

    candidates["Profile_Distance"] = np.sqrt(
        weighted_sq_diff.sum(axis=1)
    )

    candidates["Similarity"] = (
        100 / (1 + candidates["Profile_Distance"])
    )

    return candidates   


bruno_weighted = weighted_similarity(
    benchmark_player="Bruno Guimarães",
    position_group="Midfielder",
    weights=BRUNO_WEIGHTS,
    max_age=25,
    min_minutes=900,
)

# Add quality/context columns
bruno_weighted["Bruno_Quality"] = (
    0.50 * bruno_weighted["Midfielder_TwoWay"] +
    0.30 * bruno_weighted["Midfielder_Creator"] +
    0.20 * bruno_weighted["Midfielder_BallWinner"]
)

# Succession score:
# 60% stylistic fit, 40% demonstrated quality
bruno_weighted["Bruno_Succession_Score"] = (
    0.60 * bruno_weighted["Similarity"] +
    0.40 * bruno_weighted["Bruno_Quality"]
)


bruno_weighted = bruno_weighted.sort_values(
    "Bruno_Succession_Score",
    ascending=False
)

bruno_display = [
    "Player",
    "Squad",
    "League",
    "Age",
    "Min",
    "Similarity",
    "Midfielder_Creator",
    "Midfielder_BallWinner",
    "Midfielder_TwoWay",
    "Bruno_Quality",
    "Bruno_Succession_Score",
    "Midfielder_TwoWay_Tier",
]

print(
    bruno_weighted[bruno_display]
    .head(20)
    .round(2)
    .to_string(index=False)
)


# ============================================================
# TONALI + GORDON WEIGHTED SUCCESSION MODELS
# ============================================================

TONALI_WEIGHTS = {
    "Gls_per90": 0.05,
    "Ast_per90": 0.10,
    "Shots_per90": 0.05,
    "SoT_per90_calc": 0.05,
    "Int_per90": 0.20,
    "TklW_per90": 0.25,
    "Crs_per90": 0.05,
    "Fls_per90": 0.15,
    "Fld_per90": 0.10,
}

GORDON_WEIGHTS = {
    "Gls_per90": 0.20,
    "Ast_per90": 0.15,
    "Shots_per90": 0.20,
    "SoT_per90_calc": 0.15,
    "Int_per90": 0.05,
    "TklW_per90": 0.05,
    "Crs_per90": 0.10,
    "Fls_per90": 0.025,
    "Fld_per90": 0.075,
}


tonali_weighted = weighted_similarity(
    benchmark_player="Sandro Tonali",
    position_group="Midfielder",
    weights=TONALI_WEIGHTS,
    max_age=25,
    min_minutes=900,
)

tonali_weighted["Tonali_Quality"] = (
    0.25 * tonali_weighted["Midfielder_Creator"] +
    0.40 * tonali_weighted["Midfielder_BallWinner"] +
    0.35 * tonali_weighted["Midfielder_TwoWay"]
)

tonali_weighted["Tonali_Succession_Score"] = (
    0.60 * tonali_weighted["Similarity"] +
    0.40 * tonali_weighted["Tonali_Quality"]
)

tonali_weighted = tonali_weighted.sort_values(
    "Tonali_Succession_Score",
    ascending=False
)

tonali_display = [
    "Player",
    "Squad",
    "League",
    "Age",
    "Min",
    "Similarity",
    "Midfielder_Creator",
    "Midfielder_BallWinner",
    "Midfielder_TwoWay",
    "Tonali_Quality",
    "Tonali_Succession_Score",
    "Midfielder_TwoWay_Tier",
]

print("\n" + "=" * 100)
print("SANDRO TONALI — WEIGHTED SUCCESSION MODEL")
print("=" * 100)

print(
    tonali_weighted[tonali_display]
    .head(20)
    .round(2)
    .to_string(index=False)
)

gordon_weighted = weighted_similarity(
    benchmark_player="Anthony Gordon",
    position_group="Attacker",
    weights=GORDON_WEIGHTS,
    max_age=25,
    min_minutes=900,
)

gordon_weighted["Gordon_Quality"] = (
    0.45 * gordon_weighted["Attacker_Scorer"] +
    0.20 * gordon_weighted["Attacker_Creator"] +
    0.35 * gordon_weighted["Attacker_TwoWay"]
)

gordon_weighted["Gordon_Succession_Score"] = (
    0.60 * gordon_weighted["Similarity"] +
    0.40 * gordon_weighted["Gordon_Quality"]
)

gordon_weighted = gordon_weighted.sort_values(
    "Gordon_Succession_Score",
    ascending=False
)

gordon_display = [
    "Player",
    "Squad",
    "League",
    "Age",
    "Min",
    "Similarity",
    "Attacker_Scorer",
    "Attacker_Creator",
    "Attacker_TwoWay",
    "Gordon_Quality",
    "Gordon_Succession_Score",
    "Attacker_TwoWay_Tier",
]

print("\n" + "=" * 100)
print("ANTHONY GORDON — WEIGHTED SUCCESSION MODEL")
print("=" * 100)

print(
    gordon_weighted[gordon_display]
    .head(20)
    .round(2)
    .to_string(index=False)
)


# ============================================================
# SUCCESSION VERDICT CALIBRATION
# ============================================================

def calibrate_succession_verdicts(df):
    df = df.copy()

    score_candidates = [
        "Succession_Score",
        "Bruno_Succession_Score",
        "Tonali_Succession_Score",
        "Gordon_Succession_Score",
    ]

    score_col = next(
        (c for c in score_candidates if c in df.columns),
        None
    )

    if score_col is None:
        raise KeyError(
            "No succession score column found. "
            f"Available columns: {list(df.columns)}"
        )

    df["Succession_Percentile"] = (
        df[score_col]
        .rank(pct=True, method="average")
        * 100
    )

    def verdict(percentile):
        if percentile >= 95:
            return "PRIORITY TARGET"
        elif percentile >= 85:
            return "STRONG OPTION"
        elif percentile >= 65:
            return "SCOUT FURTHER"
        elif percentile >= 40:
            return "MONITOR"
        else:
            return "LOW PRIORITY"

    df["Recruitment_Verdict"] = (
        df["Succession_Percentile"].apply(verdict)
    )

    return df




    

# ------------------------------------------------------------
# Apply independently to each Newcastle succession problem
# ------------------------------------------------------------

bruno_weighted = calibrate_succession_verdicts(bruno_weighted)
tonali_weighted = calibrate_succession_verdicts(tonali_weighted)
gordon_weighted = calibrate_succession_verdicts(gordon_weighted)

# ============================================================
# CALIBRATION CHECK
# ============================================================

print("\n" + "=" * 100)
print("SUCCESSION VERDICT CALIBRATION CHECK")
print("=" * 100)

for player_name, df in [
    ("Bruno Guimarães", bruno_weighted),
    ("Sandro Tonali", tonali_weighted),
    ("Anthony Gordon", gordon_weighted),
]:
    print(f"\n{player_name.upper()}")

    score_candidates = [
    "Succession_Score",
    "Bruno_Succession_Score",
    "Tonali_Succession_Score",
    "Gordon_Succession_Score",
]

score_col = next(
    (c for c in score_candidates if c in df.columns),
    None
)

cols = [
    "Player",
    score_col,
    "Succession_Percentile",
    "Recruitment_Verdict",
]

print(
    df[cols]
    .sort_values(score_col, ascending=False)
    .head(15)
    .round(1)
    .to_string(index=False)
)



# ============================================================
# FINAL SUCCESSION RECRUITMENT BOARD
# ============================================================

def build_succession_board(
    df,
    replacement_for,
    quality_col,
    succession_col,
    role_score_col,
    role_tier_col,
    top_n=10,
):
    """
    Produce executive shortlist for one departing player.
    """

    board = df.copy()

    # Only keep columns that actually exist
    wanted = [
        "Player",
        "Squad",
        "League",
        "Age",
        "Min",
        "Similarity",
        quality_col,
        succession_col,
        role_score_col,
        role_tier_col,
    ]

    wanted = [c for c in wanted if c in board.columns]

    board = board[wanted].copy()

    board["Replacement_For"] = replacement_for

    # Standardise names for final combined board
    board = board.rename(
        columns={
            quality_col: "Quality",
            succession_col: "Succession_Score",
            role_score_col: "Role_Score",
            role_tier_col: "Role_Tier",
        }
    )

    board = board.sort_values(
        "Succession_Score",
        ascending=False
    ).head(top_n)

    # Recruitment verdict
    def verdict(row):
        succession = row["Succession_Score"]
        similarity = row["Similarity"]

        if succession >= 70 and similarity >= 60:
            return "PRIORITY REPLACEMENT"
        elif succession >= 65:
            return "STRONG OPTION"
        elif succession >= 58:
            return "SCOUT FURTHER"
        else:
            return "MONITOR"

    board["Recruitment_Verdict"] = board.apply(
        verdict,
        axis=1
    )

    return board


# ------------------------------------------------------------
# Build individual succession boards
# ------------------------------------------------------------

bruno_board = build_succession_board(
    bruno_weighted,
    replacement_for="Bruno Guimaraes",
    quality_col="Bruno_Quality",
    succession_col="Bruno_Succession_Score",
    role_score_col="Midfielder_Twoway",
    role_tier_col="Midfielder_Twoway_Tier",
    top_n=10,
)

tonali_board = build_succession_board(
    tonali_weighted,
    replacement_for="Sandro Tonali",
    quality_col="Tonali_Quality",
    succession_col="Tonali_Succession_Score",
    role_score_col="Midfielder_Twoway",
    role_tier_col="Midfielder_Twoway_Tier",
    top_n=10,
)

gordon_board = build_succession_board(
    gordon_weighted,
    replacement_for="Anthony Gordon",
    quality_col="Gordon_Quality",
    succession_col="Gordon_Succession_Score",
    role_score_col="Attacker_Twoway",
    role_tier_col="Attacker_Twoway_Tier",
    top_n=10,
)


# ------------------------------------------------------------
# Combine boards
# ------------------------------------------------------------

succession_board = pd.concat(
    [
        bruno_board,
        tonali_board,
        gordon_board,
    ],
    ignore_index=True,
)

# Round numbers for terminal/export
for col in [
    "Age",
    "Min",
    "Similarity",
    "Quality",
    "Succession_Score",
    "Role_Score",
]:
    if col in succession_board.columns:
        succession_board[col] = pd.to_numeric(
            succession_board[col],
            errors="coerce"
        ).round(1)


# ------------------------------------------------------------
# Print executive boards
# ------------------------------------------------------------

print("\n" + "=" * 120)
print("NEWCASTLE UNITED — SUCCESSION RECRUITMENT BOARD")
print("=" * 120)

for replacement_for in [
    "Bruno Guimaraes",
    "Sandro Tonali",
    "Anthony Gordon",
]:

    section = succession_board[
        succession_board["Replacement_For"]
        == replacement_for
    ]

    print("\n" + "-" * 120)
    print(f"REPLACEMENT FOR: {replacement_for.upper()}")
    print("-" * 120)

    print(
        section.to_string(
            index=False
        )
    )


# ============================================================
# MULTI-PLAYER SUCCESSION ANALYSIS
# ============================================================

overlap_source = succession_board[
    [
        "Player",
        "Replacement_For",
        "Similarity",
        "Succession_Score",
    ]
].copy()

coverage = (
    overlap_source
    .groupby("Player")
    .agg(
        Succession_Coverage=(
            "Replacement_For",
            "nunique"
        ),
        Average_Succession_Score=(
            "Succession_Score",
            "mean"
        ),
        Best_Succession_Score=(
            "Succession_Score",
            "max"
        ),
        Average_Similarity=(
            "Similarity",
            "mean"
        ),
    )
    .reset_index()
)

roles_covered = (
    overlap_source
    .groupby("Player")["Replacement_For"]
    .apply(lambda x: " | ".join(sorted(set(x))))
    .reset_index(name="Can_Replace")
)

coverage = coverage.merge(
    roles_covered,
    on="Player",
    how="left"
)

# Only players appearing on more than one succession shortlist
multi_successors = coverage[
    coverage["Succession_Coverage"] >= 2
].copy()

multi_successors = multi_successors.sort_values(
    [
        "Succession_Coverage",
        "Average_Succession_Score",
    ],
    ascending=[False, False],
)

for col in [
    "Average_Succession_Score",
    "Best_Succession_Score",
    "Average_Similarity",
]:
    multi_successors[col] = (
        multi_successors[col].round(1)
    )


print("\n" + "=" * 120)
print("MULTI-PLAYER SUCCESSION CANDIDATES")
print("=" * 120)

if len(multi_successors) == 0:
    print(
        "No players currently appear in the top 10 "
        "for more than one succession profile."
    )
else:
    print(
        multi_successors.to_string(
            index=False
        )
    )


# ============================================================
# EXPORT
# ============================================================

output_dir = "data/outputs"
os.makedirs(output_dir, exist_ok=True)

succession_board.to_csv(
    f"{output_dir}/succession_recruitment_board.csv",
    index=False,
)

multi_successors.to_csv(
    f"{output_dir}/multi_player_successors.csv",
    index=False,
)

print("\n" + "=" * 120)
print("SUCCESSION FILES EXPORTED")
print("=" * 120)

print(
    "data/outputs/succession_recruitment_board.csv"
)
print(
    "data/outputs/multi_player_successors.csv"
)


