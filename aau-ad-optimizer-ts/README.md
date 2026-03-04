# AAU Ad Optimizer (Thompson Sampling in MeTTa)

## Problem Statement

### Context
Addis Ababa University (AAU) wants to optimize ad placement on their website to maximize visitor engagement. The university has partnered with five different organizations (academic programs, research centers, student services, etc.) who want to advertise on the main university portal. Each ad has an unknown click-through rate (CTR) that depends on visitor preferences, ad design, and relevance.

### The Challenge
The university faces a classic exploration-exploitation dilemma:
- **Exploitation**: Show the ad that currently appears to have the highest CTR to maximize immediate clicks
- **Exploration**: Try different ads to discover if there are better options we haven't fully evaluated yet

If we always show the currently best-known ad (pure exploitation), we might miss discovering that another ad actually performs better. If we explore too much by randomly trying different ads, we lose valuable clicks in the short term.

### Problem Formulation as Multi-Armed Bandit
This scenario is formulated as a **multi-armed bandit problem**:
- **Arms**: Each of the 5 ads represents an arm of the bandit
- **Action**: At each visitor impression, select one ad to display
- **Reward**: Binary feedback (1 if clicked, 0 if not clicked)
- **Unknown**: The true click probability for each ad
- **Goal**: Maximize cumulative clicks over time while learning which ads perform best

### True Click Probabilities (Unknown to Algorithm)
In our simulation, each ad has a different true CTR:
- Ad 1: 30% click rate
- Ad 2: 50% click rate  
- Ad 3: 80% click rate (optimal choice)
- Ad 4: 40% click rate
- Ad 5: 60% click rate

The Thompson Sampling algorithm must discover through trial and error that Ad 3 is the best choice, while still occasionally exploring other ads to ensure it hasn't missed anything.

## Approach
The optimizer uses **Thompson Sampling** with Beta-distributed uncertainty per ad.

- Every ad starts with an initial `STV` belief in `rules.metta`.
- `bandit-algo.metta` converts STV values to Beta parameters (`alpha`, `beta`).
- A random sample is drawn from each ad's posterior.
- The ad with the largest sample is selected.
- After observing reward, the selected ad’s posterior is updated.

This naturally balances exploration and exploitation:
- uncertain ads can still be tried,
- consistently good ads are selected more often over time.

## Project Structure
- `ad-selector.metta` — main simulation loop and logging (`METRIC` lines).
- `rules.metta` — ad definitions and initial STV values.
- `bandit-algo.metta` — Thompson sampling and belief update logic.
- `math-helpers.metta` — random/math helpers and Beta sampling routine.
- `stat/plot_cumulative_reward.py` — plots cumulative reward vs iteration.
- `stat/plot_ad_selection_pie.py` — plots ad-selection frequency as a pie chart.

## How to Run
From the repository root:

```bash
metta aau-ad-optimizer-ts/ad-selector.metta
```

This runs the simulation and prints:
- selected ad IDs,
- rewards per iteration,
- cumulative reward metrics,
- final learned STV values compared to true click rates.

## Generate Visualizations
### 1) Cumulative reward chart (PNG)
```bash
python3 aau-ad-optimizer-ts/stat/plot_cumulative_reward.py \
  --no-show \
  --save aau-ad-optimizer-ts/stat/cumulative_reward.png
```

### 2) Ad-selection pie chart (PNG)
```bash
python3 aau-ad-optimizer-ts/stat/plot_ad_selection_pie.py \
  --no-show \
  --save aau-ad-optimizer-ts/stat/ad_selection_pie.png
```

The pie chart highlights the most-selected ad by Thompson Sampling.

## Dependencies
- MeTTa runtime (`metta` command available).
- Python 3.10+.
- `matplotlib` for plotting:

```bash
pip install matplotlib
```

## Notes
- Each ad has a different true click probability in `performAction` (Ad 1: 30%, Ad 2: 50%, Ad 3: 80%, Ad 4: 40%, Ad 5: 60%).
- Ad 3 has the highest click rate, so Thompson Sampling should converge to selecting it most often.
- Random seed is set in `ad-selector.metta` for reproducible runs.
- To stress-test policy behavior, increase simulation iterations in `run` inside `ad-selector.metta`.
