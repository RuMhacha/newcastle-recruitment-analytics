"""Create the Gordon succession vs decision comparison visual."""

from pathlib import Path

import pandas as pd


# Repository paths
ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    ROOT
    / "data"
    / "outputs"
    / "phase2"
    / "recruitment_decision_board_v1_0.csv"
)


def load_gordon_candidates() -> pd.DataFrame:
    """Load the Phase 2 decision board."""

    board = pd.read_csv(INPUT_FILE)

    # Inspect the dataset before filtering or plotting
    print("Columns:")
    print(board.columns.tolist())

    print("\nFirst five rows:")
    print(board.head())

    return board


if __name__ == "__main__":
    gordon = load_gordon_candidates()
