#!/usr/bin/env python3
import argparse
import re
import subprocess
from collections import Counter
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


def parse_selected_ads(output: str) -> Counter:
    pattern = re.compile(r"#\s+(\d+)\s+was chosen and executed")
    counts = Counter()
    for line in output.splitlines():
        match = pattern.search(line)
        if match:
            counts[int(match.group(1))] += 1
    return counts


def _autopct_with_count(values: list[int]):
    total = sum(values)

    def formatter(pct: float) -> str:
        count = int(round((pct / 100.0) * total))
        return f"{pct:.1f}%\n(n={count})"

    return formatter


def plot_selection_pie(counts: Counter, save_path: Path | None, show_plot: bool) -> None:
    try:
        import matplotlib.pyplot as plt
    except Exception as error:
        raise RuntimeError(
            "matplotlib is required. Install it with: pip install matplotlib"
        ) from error

    ad_ids = sorted(counts.keys())
    labels = [f"Ad {ad_id}" for ad_id in ad_ids]
    values = [counts[ad_id] for ad_id in ad_ids]

    top_ad_id, top_count = max(counts.items(), key=lambda item: item[1])
    explode = [0.08 if ad_id == top_ad_id else 0 for ad_id in ad_ids]

    plt.figure(figsize=(7, 7))
    wedges, texts, autotexts = plt.pie(
        values,
        labels=labels,
        autopct=_autopct_with_count(values),
        startangle=90,
        explode=explode,
        wedgeprops={"edgecolor": "white", "linewidth": 1},
    )
    for autotext in autotexts:
        autotext.set_fontsize(9)

    plt.title(f"Thompson Sampling Selections (Most selected: Ad {top_ad_id}, n={top_count})")
    plt.axis("equal")
    plt.tight_layout()

    if save_path is not None:
        save_path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(save_path, dpi=150)
        print(f"Saved pie chart to: {save_path}")

    if show_plot:
        plt.show()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Plot a pie chart of ad selections made by Thompson Sampling."
    )
    parser.add_argument(
        "--save",
        type=Path,
        default=None,
        help="Optional file path to save the chart image (e.g., aau-ad-optimizer/ad_selection_pie.png)",
    )
    parser.add_argument(
        "--no-show",
        action="store_true",
        help="Do not open a plot window.",
    )
    args = parser.parse_args()

    output = run_simulation()
    counts = parse_selected_ads(output)

    if not counts:
        print("No ad-selection lines found in output. Check ad-selector.metta logging.")
        print(output)
        return

    top_ad_id, top_count = max(counts.items(), key=lambda item: item[1])
    total = sum(counts.values())
    print(f"Total selections parsed: {total}")
    print(f"Most selected ad: Ad {top_ad_id} (selected {top_count} times)")

    plot_selection_pie(counts, args.save, show_plot=not args.no_show)


if __name__ == "__main__":
    main()
