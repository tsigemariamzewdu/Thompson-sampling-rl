# AAU Ad Optimizer - Greedy Strategy (Python)

## Overview
This is a **pure greedy (exploitation-only)** implementation for the same AAU ad optimization problem. It serves as a baseline comparison to demonstrate why Thompson Sampling is superior.

## The Greedy Approach
The greedy strategy:
1. Maintains a Beta distribution for each ad's click rate
2. **Always selects the ad with the highest estimated click rate**
3. Never explores other options once it settles on a choice
4. Updates beliefs based on observed clicks

## Problem with Pure Greedy
The greedy approach suffers from the **"early commitment" problem**:
- If an inferior ad gets lucky early on, the algorithm may lock onto it
- It never explores other ads to discover better options
- This leads to **suboptimal long-term performance**

## Ad Configuration
- Ad 1: 5% true click rate
- Ad 2: 10% true click rate
- Ad 3: 3% true click rate
- Ad 4: **20% true click rate (OPTIMAL)**
- Ad 5: 15% true click rate

## How to Run
```bash
cd ad-optimizer-greedy
python3 greedy.py
```

## Expected Behavior
Due to the greedy nature:
- The algorithm may get stuck on a suboptimal ad if it performs well early
- It will rarely explore all ads sufficiently
- Total reward will likely be lower than Thompson Sampling
- The output shows which ad was selected most often and whether it's optimal

## Output
The script produces:
1. Console output showing:
   - Total clicks achieved
   - Selection frequency for each ad
   - Learned vs. true click rates
2. A visualization (`greedy_results.png`) with:
   - Cumulative reward over time
   - Bar chart of ad selection frequency

## Comparison with Thompson Sampling
| Aspect | Greedy | Thompson Sampling |
|--------|--------|-------------------|
| Exploration | None (pure exploitation) | Automatic via sampling |
| Risk | High (can get stuck) | Low (continues exploring) |
| Long-term reward | Suboptimal | Near-optimal |
| Convergence | Fast but wrong | Slower but correct |

## Dependencies
```bash
pip install matplotlib
```

## Why This Matters
This implementation demonstrates that **exploration is essential** in multi-armed bandit problems. Pure exploitation (greedy) can lead to poor long-term outcomes, which is why Thompson Sampling's balanced approach is preferred in real-world applications.
