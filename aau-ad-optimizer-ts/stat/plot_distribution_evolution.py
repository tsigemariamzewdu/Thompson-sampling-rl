#!/usr/bin/env python3
"""
Visualize Beta Distribution Evolution for Thompson Sampling

Shows 10 snapshots of all 5 ads' Beta distributions at different iterations.
"""

import re
import subprocess
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
from math import gamma


def beta_pdf(x, alpha, beta_param):
    """Compute Beta distribution PDF without scipy."""
    if alpha <= 0 or beta_param <= 0:
        return np.zeros_like(x)
    
    try:
        beta_func = gamma(alpha) * gamma(beta_param) / gamma(alpha + beta_param)
        pdf = np.power(x, alpha - 1) * np.power(1 - x, beta_param - 1) / beta_func
        pdf = np.nan_to_num(pdf, nan=0.0, posinf=0.0, neginf=0.0)
        return pdf
    except (ValueError, OverflowError):
        return np.zeros_like(x)


def stv_to_beta(strength, confidence):
    """Convert STV values to Beta distribution parameters."""
    count = (confidence * 800) / (1 - confidence)
    alpha = strength * count
    beta_param = count - alpha
    return alpha, beta_param


def run_simulation():
    """Run the MeTTa simulation and capture output."""
    repo_root = Path(__file__).resolve().parent.parent.parent
    process = subprocess.run(
        ["metta", "aau-ad-optimizer-ts/ad-selector.metta"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=True,
    )
    return process.stdout


def parse_iteration_states(output):
    """Parse STV values for each iteration."""
    # Pattern: (ITERATION_STATE 10 1 0.5 0.002)
    pattern = re.compile(r'\(ITERATION_STATE (\d+) (\d+) ([\d.]+) ([\d.]+)\)')
    
    iterations = {}
    
    for line in output.splitlines():
        match = pattern.search(line)
        if match:
            iter_num = int(match.group(1))
            ad_id = int(match.group(2))
            strength = float(match.group(3))
            confidence = float(match.group(4))
            
            if iter_num not in iterations:
                iterations[iter_num] = {}
            iterations[iter_num][ad_id] = (strength, confidence)
    
    return iterations


def plot_iteration_snapshots(iterations, save_path=None):
    """Plot 10 snapshots showing all 5 ads at different iterations."""
    # Get sorted iteration numbers
    iter_nums = sorted(iterations.keys(), reverse=True)  # Reverse because countdown
    
    # Select 10 evenly spaced iterations
    if len(iter_nums) > 10:
        step = len(iter_nums) // 10
        selected_iters = [iter_nums[i * step] for i in range(10)]
    else:
        selected_iters = iter_nums
    
    # True click probabilities
    true_probs = {1: 0.3, 2: 0.5, 3: 0.8, 4: 0.4, 5: 0.6}
    colors = {1: '#1f77b4', 2: '#ff7f0e', 3: '#2ca02c', 4: '#d62728', 5: '#9467bd'}
    
    fig, axes = plt.subplots(2, 5, figsize=(20, 8))
    axes = axes.flatten()
    
    x = np.linspace(0.001, 0.999, 200)
    
    for idx, iter_num in enumerate(selected_iters[:10]):
        ax = axes[idx]
        state = iterations[iter_num]
        
        # Plot all 5 ads
        for ad_id in range(1, 6):
            if ad_id in state:
                s, c = state[ad_id]
                alpha, beta_param = stv_to_beta(s, c)
                if alpha > 0 and beta_param > 0:
                    y = beta_pdf(x, alpha, beta_param)
                    ax.plot(x, y, label=f'Ad {ad_id}', 
                           color=colors[ad_id], linewidth=2)
                    
                    # Mark true probability
                    true_prob = true_probs[ad_id]
                    ax.axvline(true_prob, color=colors[ad_id], 
                              linestyle=':', linewidth=1, alpha=0.5)
        
        ax.set_title(f'After Iteration {iter_num}', fontsize=10, fontweight='bold')
        ax.set_xlabel('Click Probability', fontsize=8)
        ax.set_ylabel('Density', fontsize=8)
        ax.legend(fontsize=7, loc='upper right')
        ax.grid(True, alpha=0.3)
        ax.set_xlim(0, 1)
    
    plt.suptitle('Beta Distribution Evolution: All 5 Ads Across 10 Iterations', 
                fontsize=14, fontweight='bold')
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Saved distribution evolution plot to: {save_path}")
    
    plt.show()


def main():
    print("Running Thompson Sampling simulation...")
    output = run_simulation()
    
    print("Parsing iteration states...")
    iterations = parse_iteration_states(output)
    
    if not iterations:
        print("No iteration states found in output. Check simulation logging.")
        return
    
    print(f"Found {len(iterations)} iterations")
    print("Generating distribution evolution plot...")
    
    save_path = Path(__file__).parent / "distribution_evolution.png"
    plot_iteration_snapshots(iterations, save_path)


if __name__ == "__main__":
    main()
