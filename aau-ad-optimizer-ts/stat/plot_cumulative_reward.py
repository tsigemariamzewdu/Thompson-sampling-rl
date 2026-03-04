#!/usr/bin/env python3
import argparse
import re
import subprocess
from pathlib import Path


def run_simulation() -> str:
    repo_root = Path(__file__).resolve().parent.parent.parent
    process = subprocess.run(
        ["metta", "aau-ad-optimizer-ts/ad-selector.metta"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=True,
    )
    return process.stdout


def parse_cumulative_rewards(output: str) -> list[float]:
    pattern = re.compile(r"METRIC\s+reward\s+([-+]?\d*\.?\d+)\s+cumulative\s+([-+]?\d*\.?\d+)")
    cumulative = []
    for line in output.splitlines():
        match = pattern.search(line)
        if match:
            cumulative.append(float(match.group(2)))
    return cumulative


def plot(cumulative: list[float], save_path: Path | None, show_plot: bool) -> None:
    try:
        import matplotlib.pyplot as plt
    except Exception as error:
        raise RuntimeError(
            "matplotlib is required. Install it with: pip install matplotlib"
        ) from error

    iterations = list(range(1, len(cumulative) + 1))

    plt.figure(figsize=(8, 5))
    plt.plot(iterations, cumulative, marker="o")
    plt.title("Cumulative Reward over Iterations")
    plt.xlabel("Iteration")
    plt.ylabel("Cumulative Reward")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()

    if save_path is not None:
        save_path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(save_path, dpi=150)
        print(f"Saved cumulative reward chart to: {save_path}")

    if show_plot:
        plt.show()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Plot cumulative reward over iterations from the Metta ad selector output."
    )
    parser.add_argument(
        "--save",
        type=Path,
        default=None,
        help="Optional file path to save the chart image (e.g., aau-ad-optimizer/cumulative_reward.png)",
    )
    parser.add_argument(
        "--no-show",
        action="store_true",
        help="Do not open a plot window.",
    )
    args = parser.parse_args()

    output = run_simulation()
    cumulative = parse_cumulative_rewards(output)

    if not cumulative:
        print("No METRIC lines found in output. Check ad-selector.metta logging.")
        print(output)
        return

    print(f"Parsed {len(cumulative)} iterations.")
    print(f"Final cumulative reward: {cumulative[-1]}")
    plot(cumulative, args.save, show_plot=not args.no_show)


if __name__ == "__main__":
    main()
