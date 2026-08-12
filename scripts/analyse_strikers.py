import pandas as pd

# Load datasets
ered = pd.read_csv("data/processed/eredivisie_player_master.csv")
newcastle = pd.read_csv("data/processed/newcastle_player_master.csv")

print("Eredivisie dataset:", ered.shape)
print("Newcastle dataset:", newcastle.shape)

# Keep Eredivisie forwards
ered_forwards = ered[ered["Pos"].astype(str).str.contains("FW", na=False)].copy()

print("\nEredivisie forwards:", ered_forwards.shape)

print(
    ered_forwards[
        ["Player", "Squad", "Age", "Min", "Gls", "Sh/90", "SoT/90"]
    ].head(20)
)
# Apply basic recruitment filters
candidates = ered_forwards[
    (ered_forwards["Age"] <= 25) &
    (ered_forwards["Min"] >= 500)
].copy()

print("\nCandidates after age/minutes filter:", candidates.shape)

# Newcastle striker benchmark
benchmark = newcastle[
    newcastle["Player"].isin(
        ["Nick Woltemade", "William Osula", "Yoane Wissa"]
    )
]

benchmark_cols = ["Age", "Gls", "Sh/90", "SoT/90"]

benchmark_profile = benchmark[benchmark_cols].mean(numeric_only=True)

print("\nNewcastle striker benchmark:")
print(benchmark_profile)

# Score Eredivisie striker candidates

# Convert scoring columns to numeric
score_cols = ["Gls", "Sh/90", "SoT/90"]

for col in score_cols:
    candidates[col] = pd.to_numeric(candidates[col], errors="coerce")

# Goals per 90
candidates["Gls/90"] = (
    candidates["Gls"] / candidates["Min"] * 90
)

# Simple recruitment score
candidates["RecruitmentScore"] = (
    candidates["Gls/90"] * 0.40 +
    candidates["Sh/90"] * 0.30 +
    candidates["SoT/90"] * 0.30
)

ranked = candidates.sort_values(
    "RecruitmentScore",
    ascending=False
)

print("\nTop Eredivisie striker candidates:")

print(
    ranked[
        [
            "Player",
            "Squad",
            "Age",
            "Min",
            "Gls",
            "Gls/90",
            "Sh/90",
            "SoT/90",
            "RecruitmentScore"
        ]
    ].head(20)
)

# Compare candidates with Newcastle striker benchmark

benchmark = benchmark.copy()

for col in ["Gls", "Min", "Sh/90", "SoT/90"]:
    benchmark[col] = pd.to_numeric(benchmark[col], errors="coerce")

benchmark["Gls/90"] = (
    benchmark["Gls"] / benchmark["Min"] * 90
)

similarity_cols = ["Gls/90", "Sh/90", "SoT/90"]

benchmark_target = benchmark[similarity_cols].mean()

print("\nNewcastle per-90 striker target:")
print(benchmark_target)

# Standardise metrics using the Eredivisie candidate pool
metric_means = candidates[similarity_cols].mean()
metric_stds = candidates[similarity_cols].std().replace(0, 1)

for col in similarity_cols:
    candidates[col + "_z"] = (
        candidates[col] - metric_means[col]
    ) / metric_stds[col]

benchmark_z = (
    benchmark_target - metric_means
) / metric_stds

candidates["BenchmarkDistance"] = (
    (
        (candidates["Gls/90_z"] - benchmark_z["Gls/90"]) ** 2
        + (candidates["Sh/90_z"] - benchmark_z["Sh/90"]) ** 2
        + (candidates["SoT/90_z"] - benchmark_z["SoT/90"]) ** 2
    ) ** 0.5
)

candidates["BenchmarkSimilarity"] = (
    1 / (1 + candidates["BenchmarkDistance"])
)

similarity_ranked = candidates.sort_values(
    "BenchmarkSimilarity",
    ascending=False
)

print("\nClosest matches to Newcastle striker profile:")

print(
    similarity_ranked[
        [
            "Player",
            "Squad",
            "Age",
            "Min",
            "Gls",
            "Gls/90",
            "Sh/90",
            "SoT/90",
            "BenchmarkSimilarity"
        ]
    ].head(20)
)

# Save striker rankings
ranked.to_csv(
    "data/processed/eredivisie_striker_recruitment_rankings.csv",
    index=False
)

similarity_ranked.to_csv(
    "data/processed/eredivisie_striker_similarity_rankings.csv",
    index=False
)

print("\nSaved striker recruitment and similarity rankings.")

