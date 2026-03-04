# AAU Ad Optimization - Multi-Armed Bandit Solutions

Two implementations solving the same problem: optimizing ad selection on Addis Ababa University's website.

## Problem

AAU displays ads from five organizations. Each has an unknown click-through rate. Goal: maximize total clicks while learning which ads perform best.

## Implementations

### Thompson Sampling (MeTTa) - `aau-ad-optimizer-ts/`
Bayesian approach that balances exploration and exploitation.

```bash
metta aau-ad-optimizer-ts/ad-selector.metta
```

[Details →](aau-ad-optimizer-ts/README.md)

### Greedy Strategy (Python) - `ad-optimizer-greedy/`
Pure exploitation baseline for comparison.

```bash
python3 ad-optimizer-greedy/greedy.py
```

[Details →](ad-optimizer-greedy/README.md)

## Comparison

| Feature | Thompson Sampling | Greedy |
|---------|------------------|--------|
| **Exploration** | ✅ Automatic | ❌ None |
| **Long-term reward** | Near-optimal | Suboptimal |
| **Risk** | Low | High (gets stuck) |

## Dependencies

```bash
pip install matplotlib
```

Thompson Sampling also requires MeTTa runtime.

## Why This Matters

Thompson Sampling achieves higher cumulative reward by balancing exploration and exploitation. The greedy approach demonstrates why pure exploitation fails in uncertain environments.
