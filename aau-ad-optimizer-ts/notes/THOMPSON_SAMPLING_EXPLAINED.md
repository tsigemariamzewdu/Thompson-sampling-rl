# Thompson Sampling Deep Dive - How It Works

## Overview
Thompson Sampling is a **Bayesian approach** to the multi-armed bandit problem. It naturally balances exploration and exploitation by maintaining probability distributions over each ad's click rate and sampling from them.

---

## The Core Idea

Instead of just tracking "Ad 3 has 80% click rate", Thompson Sampling maintains **uncertainty** about each ad's performance:
- "I'm 90% confident Ad 3's click rate is between 75-85%"
- "I'm only 20% confident Ad 1's click rate is between 20-40%"

This uncertainty drives exploration: uncertain ads get more chances to prove themselves.

---

## Step-by-Step Walkthrough

### 1. INITIALIZATION (rules.metta)

```metta
(: Ad 1
    (STV 0.5 0.002)  
    (Action (DISPLAY AD_ONE))
)
```

**What this means:**
- `STV 0.5 0.002` = Strength-Truth-Value with:
  - **Strength (0.5)**: Our best guess of click rate = 50%
  - **Confidence (0.002)**: How sure we are = very uncertain (close to 0)

**Why start at 0.5?**
- It's the "I have no idea" prior - could be anywhere from 0% to 100%
- Low confidence (0.002) means "I'm very uncertain, please explore!"

---

### 2. SELECTION PHASE (thompsonSampling function)

**For each iteration, Thompson Sampling does this:**

```metta
(= (thompsonSampling $ruleIds $space) (
    let* (
        (($strength $confidence) (getSTV $ruleId $space))
        (($alpha $beta) (stvToBeta ($strength $confidence)))
        ($sample (betaSample $alpha $beta))
    ) ...
))
```

**Step 2a: Convert STV to Beta parameters**

```metta
(= (stvToBeta ($strength $confidence)) (
    let* (
        ($count (confidenceToCount $confidence))  ; Convert confidence to "sample size"
        ($alpha (* $strength $count))              ; Successes
        ($beta (- $count $alpha))                  ; Failures
    ) ($alpha $beta)
))
```

**Example for Ad 1 initially:**
- Strength = 0.5, Confidence = 0.002
- Count = (0.002 × 800) / (1 - 0.002) ≈ 1.6
- Alpha = 0.5 × 1.6 = 0.8 (like 0.8 clicks)
- Beta = 1.6 - 0.8 = 0.8 (like 0.8 non-clicks)

**What is Beta(α, β)?**
- A probability distribution over [0, 1]
- Beta(0.8, 0.8) = very wide, flat distribution (high uncertainty)
- Beta(80, 20) = narrow peak around 0.8 (low uncertainty)

**Step 2b: Sample from Beta distribution**

```metta
($sample (betaSample $alpha $beta))
```

This draws a **random number** from the Beta distribution:
- Ad 1 with Beta(0.8, 0.8) might sample: 0.23
- Ad 2 with Beta(0.8, 0.8) might sample: 0.67
- Ad 3 with Beta(0.8, 0.8) might sample: 0.91  ← HIGHEST!
- Ad 4 with Beta(0.8, 0.8) might sample: 0.45
- Ad 5 with Beta(0.8, 0.8) might sample: 0.52

**Step 2c: Pick the ad with highest sample**

```metta
(if (>= $sample $chosenSample) 
    ($ruleId $sample) 
    ($chosenId $chosenSample)
)
```

Ad 3 sampled 0.91 → **Ad 3 is selected!**

**Why this works:**
- Ads with higher true click rates will tend to sample higher values
- But uncertain ads can still "get lucky" and sample high → exploration!
- As we learn, distributions narrow → less randomness → more exploitation

---

### 3. EXECUTION PHASE (performAction function)

```metta
(= (performAction $ruleId $space) (
    let* (
        ($sample (getRandom))
        ($clickProb (if (== $ruleId 1) 0.3
                    (if (== $ruleId 2) 0.5
                    (if (== $ruleId 3) 0.8  ; TRUE click rate
                    ...))))
    ) (if (< $sample $clickProb) 1 0)
))
```

**What happens:**
- We selected Ad 3
- Ad 3's TRUE click rate is 80% (unknown to algorithm)
- Generate random number: 0.65
- 0.65 < 0.8? YES → Return 1 (click!)

**Result: Ad 3 got clicked**

---

### 4. UPDATE PHASE (updateRule function)

```metta
(= (updateRule $ruleId $result $space) (
    let* (
        (($strength $confidence) (getSTV $ruleId $space))
        (($alpha $beta) (stvToBeta ($strength $confidence)))
        ($newAlpha (if (== $result 1) (+ $alpha 1) $alpha))      ; Add 1 if clicked
        ($newBeta (if (== $result 1) $beta (+ $beta 1)))         ; Add 1 if NOT clicked
        (($newStrength $newConfidence) (betaToSTV ($newAlpha $newBeta)))
    ) ...
))
```

**Bayesian Update:**
- Ad 3 was clicked (result = 1)
- Old: Beta(0.8, 0.8)
- New: Beta(0.8 + 1, 0.8) = Beta(1.8, 0.8)

**Convert back to STV:**
```metta
(= (betaToSTV ($alpha $beta)) (
    let* (
        ($count (+ $alpha $beta))              ; Total observations
        ($strength (/ $alpha $count))          ; Success rate
        ($confidence (countToConfindence $count))
    ) ($strength $confidence)
))
```

- Count = 1.8 + 0.8 = 2.6
- Strength = 1.8 / 2.6 ≈ 0.69 (69% estimated click rate)
- Confidence = 2.6 / (800 + 2.6) ≈ 0.0032 (slightly more confident)

**Ad 3's new belief: STV(0.69, 0.0032)**

---

## How Learning Happens Over Time

### Iteration 1:
- All ads: Beta(0.8, 0.8) - very uncertain
- Random sampling picks different ads
- Each gets updated based on clicks

### Iteration 5:
- Ad 3 (80% true): Beta(4, 1) - starting to look good
- Ad 1 (30% true): Beta(1, 3) - starting to look bad
- Distributions are narrowing

### Iteration 50:
- Ad 3: Beta(40, 10) - narrow peak around 0.8 ✓
- Ad 1: Beta(9, 21) - narrow peak around 0.3 ✓
- Algorithm has learned the true rates!

### Iteration 100:
- Ad 3 selected 70% of the time (exploitation)
- Other ads selected 30% of the time (exploration)
- Still exploring in case environment changes

---

## Why Thompson Sampling is Brilliant

### 1. **Automatic Exploration-Exploitation Balance**
- No need to manually tune ε (like ε-greedy)
- Uncertainty naturally drives exploration
- As confidence grows, exploitation increases

### 2. **Bayesian Reasoning**
- Maintains full probability distributions
- Updates beliefs using Bayes' theorem
- Handles uncertainty mathematically

### 3. **Optimistic in Face of Uncertainty**
- Uncertain ads can sample high values
- Gives them a chance to prove themselves
- But bad ads quickly get low confidence

### 4. **Converges to Optimal**
- Eventually learns true click rates
- Selects best ad most often
- But never stops exploring completely

---

## Key Mathematical Concepts

### Beta Distribution
- **Beta(α, β)** where α = successes, β = failures
- Mean = α / (α + β)
- Variance decreases as α + β increases (more data = more confidence)
- Perfect for modeling probabilities!

### Conjugate Prior
- Beta is the "conjugate prior" for Bernoulli (click/no-click)
- Makes Bayesian updates simple: just add 1 to α or β
- No complex integration needed

### Thompson Sampling = Probability Matching
- Selects each ad proportional to probability it's optimal
- If Ad 3 has 80% chance of being best → selected 80% of time
- Mathematically optimal strategy!

---

## Comparison with Greedy

### Greedy:
```
Iteration 1: Ad 2 gets lucky, clicks
Iteration 2-100: Always pick Ad 2 (stuck!)
Result: Suboptimal
```

### Thompson Sampling:
```
Iteration 1: Ad 2 gets lucky, clicks
Iteration 2: Ad 2 has high belief, but Ad 3 samples higher → try Ad 3
Iteration 3: Ad 3 clicks! Now both look good
Iteration 4-10: Explore all ads
Iteration 11-100: Mostly Ad 3 (best), but still try others
Result: Near-optimal!
```

---

## Summary

Thompson Sampling works by:
1. **Maintaining beliefs** (Beta distributions) about each ad's click rate
2. **Sampling** from these distributions to pick an ad
3. **Observing** the result (click or no click)
4. **Updating** beliefs using Bayesian inference
5. **Repeating** until convergence

The beauty is that **uncertainty drives exploration automatically** - no manual tuning needed!
