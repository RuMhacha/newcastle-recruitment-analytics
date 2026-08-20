"""Create the Tonali succession vs decision comparison visual."""

from pathlib import Path

import pandas as pd

import matplotlib.pyplot as plt


# Repository paths
ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    ROOT
    / "data"
    / "outputs"
    / "phase2"
    / "recruitment_decision_board_v1_0.csv"
)

def load_tonali_candidates() -> pd.DataFrame:
    """Load the Phase 2 decision board and return Tonali candidates."""

    board = pd.read_csv(INPUT_FILE)

    tonali = board[
        board["Replacement_For"] == "Sandro Tonali"
    ].copy()

    print(
        tonali[
            [
                "Player",
                "Succession_Score",
                "Evidence_Confidence",
                "Development_Score",
                "Recruitment_Risk",
                "Risk_Adjusted_Score",
                "Decision_Tier",
            ]
        ].sort_values(
            "Risk_Adjusted_Score",
            ascending=False,
        )
    )

    return tonali
  
def create_chart(tonali: pd.DataFrame) -> None:
    """Compare initial succession scores with final risk-adjusted scores."""

    chart_data = tonali.sort_values(
        "Risk_Adjusted_Score",
        ascending=True,
    )

    # Portfolio colour palette
    positive_colour = "#173F5F"   # dark blue
    negative_colour = "#C65D2E"   # burnt orange

    fig, ax = plt.subplots(figsize=(11, 7))

    for _, row in chart_data.iterrows():

        succession = row["Succession_Score"]
        adjusted = row["Risk_Adjusted_Score"]
        player = row["Player"]
        

        if adjusted >= succession:
            colour = positive_colour
        else:
            colour = negative_colour

        # Connect initial and final scores
        ax.plot(
            [succession, adjusted],
            [row["Player"], row["Player"]],
            color=colour,
            linewidth=2.5,
            alpha=0.8,
        )

        # Initial succession score
        ax.scatter(
            succession,
            row["Player"],
            color=colour,
            s=80,
            marker="o",
            zorder=3,
        )

        # Final risk-adjusted score
        ax.scatter(
            adjusted,
            row["Player"],
            color=colour,
            s=90,
            marker="D",
            zorder=3,
        )

                    # Label every candidate
        label = f"{succession:.1f} → {adjusted:.1f}"

        # Place labels outside the score movement so that
        # the connecting line never runs through the numbers.
        if adjusted >= succession:
            ax.annotate(
                label,
                xy=(adjusted, player),
                xytext=(8, 0),
                textcoords="offset points",
                va="center",
                ha="left",
                fontsize=9,
                fontweight="bold",
                color=colour,
                zorder=5,
            )
        else:
            midpoint = (succession + adjusted) / 2

            ax.annotate(
                label,
                xy=(midpoint, player),
                xytext=(0, 8),
                textcoords="offset points",
                va="bottom",
                ha="center",
                fontsize=9,
                fontweight="bold",
                color=colour,
                zorder=5,
            )

        


    ax.set_title(
        "Decision modelling reshapes the Sandro Tonali succession shortlist",
        fontsize=16,
        fontweight="bold",
        pad=18,
    )

    ax.text(
        0.5,
        1.01,
        "Evidence strength, development potential and recruitment risk "
        "alter the initial succession assessment",
        transform=ax.transAxes,
        ha="center",
        fontsize=10,
    )

    ax.set_xlabel("Score", fontsize=11)
    ax.set_ylabel("")

    ax.grid(
        axis="x",
        alpha=0.2,
    )

    # Remove unnecessary chart borders
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)

    # Explain marker meaning
    ax.scatter(
        [],
        [],
        color="black",
        marker="o",
        s=70,
        label="Initial succession score",
    )

    ax.scatter(
        [],
        [],
        color="black",
        marker="D",
        s=70,
        label="Final risk-adjusted score",
    )

    ax.legend(
        frameon=False,
        loc="lower right",
    )

    plt.tight_layout()

    output_dir = ROOT / "portfolio" / "figures"
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / "tonali_decision_comparison.png"

    plt.savefig(
        output_file,
        dpi=200,
        bbox_inches="tight",
    )

    print(f"\nChart saved to: {output_file}")

    plt.close(fig)


if __name__ == "__main__":
    tonali = load_tonali_candidates()
    create_chart(tonali)
