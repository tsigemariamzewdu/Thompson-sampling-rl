#!/usr/bin/env python3
"""
Greedy Ad Selection for AAU Website

This implements a pure greedy (exploitation-only) strategy for the same
AAU ad optimization problem. Unlike Thompson Sampling, this approach always
selects the ad with the highest estimated click rate, never exploring.
"""

import random
import matplotlib.pyplot as plt
from collections import Counter

# True click probabilities for each ad (unknown to algorithm)
# Ad 1: 5%, Ad 2: 10%, Ad 3: 3%, Ad 4: 20% (BEST), Ad 5: 15%
true_probs = [0.05, 0.10, 0.03, 0.20, 0.15]

K = len(true_probs)
rounds = 10000

# Set seed for reproducibility
random.seed(42)

# Initialize Beta distribution parameters (uniform prior)
alpha = [1] * K
beta = [1] * K

total_reward = 0
cumulative_rewards = []
selections = Counter()

print("Starting Greedy Ad Selection Simulation...")
print(f"True click probabilities: {true_probs}")
print(f"Optimal ad: Ad {true_probs.index(max(true_probs)) + 1} ({max(true_probs)*100}%)\n")

for t in range(rounds):
    # Step 1: Calculate estimated click rate (mean of Beta distribution)
    theta_hat = [alpha[k] / (alpha[k] + beta[k]) for k in range(K)]
    
    # Step 2: Select greedy arm (always choose highest estimate)
    chosen_arm = theta_hat.index(max(theta_hat))
    selections[chosen_arm] += 1
    
    # Step 3: Simulate reward based on true click probability
    reward = 1 if random.random() < true_probs[chosen_arm] else 0
    
    # Step 4: Update Beta distribution parameters
    alpha[chosen_arm] += reward
    beta[chosen_arm] += (1 - reward)
    
    total_reward += reward
    cumulative_rewards.append(total_reward)

print("=== FINAL RESULTS ===")
print(f"Total clicks: {total_reward} out of {rounds} impressions")
print(f"Overall CTR: {total_reward/rounds:.2%}\n")

print("Ad Selection Frequency:")
for ad_id in range(K):
    count = selections[ad_id]
    pct = (count / rounds) * 100
    print(f"  Ad {ad_id + 1}: {count:5d} times ({pct:5.2f}%) - True CTR: {true_probs[ad_id]:.2%}, Learned: {alpha[ad_id]/(alpha[ad_id]+beta[ad_id]):.2%}")

print(f"\nOptimal ad (Ad {true_probs.index(max(true_probs)) + 1}) selected: {selections[true_probs.index(max(true_probs))]} times ({selections[true_probs.index(max(true_probs))]/rounds*100:.2f}%)")

# Plotting
plt.figure(figsize=(12, 5))

# Plot 1: Cumulative Reward
plt.subplot(1, 2, 1)
plt.plot(range(rounds), cumulative_rewards, linewidth=1.5)
plt.xlabel("Round")
plt.ylabel("Cumulative Clicks")
plt.title("Cumulative Reward Over Time (Greedy Strategy)")
plt.grid(True, alpha=0.3)

# Plot 2: Selection Distribution
plt.subplot(1, 2, 2)
ad_labels = [f"Ad {i+1}\n({true_probs[i]:.0%})" for i in range(K)]
selection_counts = [selections[i] for i in range(K)]
colors = ['#ff6b6b' if i != true_probs.index(max(true_probs)) else '#51cf66' for i in range(K)]
plt.bar(ad_labels, selection_counts, color=colors, edgecolor='black', linewidth=1.2)
plt.xlabel("Ad (True CTR)")
plt.ylabel("Times Selected")
plt.title("Ad Selection Frequency")
plt.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('greedy_results.png', dpi=150, bbox_inches='tight')
print("\nPlot saved as 'greedy_results.png'")
plt.show()
