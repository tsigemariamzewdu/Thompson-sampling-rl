# Why performAction is Fair and Correct

## Your Question

In `performAction`, we simulate clicks randomly:
```metta
(= (performAction $ruleId $space) (
    let* (
        ($sample (getRandom))              ; Random number [0, 1]
        ($clickProb (if (== $ruleId 1) 0.3
                    (if (== $ruleId 2) 0.5
                    (if (== $ruleId 3) 0.8  ; Ad 3 has 80% click rate
                    (if (== $ruleId 4) 0.4
                    0.6)))))
    ) (if (< $sample $clickProb) 1 0)      ; Click if sample < clickProb
))
```

**Is it fair to expect Ad 3 to have greater STV than others?**

**Answer: YES, absolutely!** Here's why:

---

## How It Works

### The Simulation

For each ad, when selected:
1. Generate random number: `sample ~ Uniform(0, 1)`
2. Compare to true click probability
3. Return 1 (click) if `sample < clickProb`, else 0 (no click)

### Example for Ad 3 (80% click rate):

**Over 100 selections:**
```
Selection 1: sample = 0.23 < 0.8 → Click ✓
Selection 2: sample = 0.91 > 0.8 → No click ✗
Selection 3: sample = 0.45 < 0.8 → Click ✓
Selection 4: sample = 0.67 < 0.8 → Click ✓
Selection 5: sample = 0.88 > 0.8 → No click ✗
...
Selection 100: sample = 0.12 < 0.8 → Click ✓

Expected clicks: ~80 out of 100
```

### Example for Ad 1 (30% click rate):

**Over 100 selections:**
```
Selection 1: sample = 0.23 < 0.3 → Click ✓
Selection 2: sample = 0.45 > 0.3 → No click ✗
Selection 3: sample = 0.67 > 0.3 → No click ✗
Selection 4: sample = 0.88 > 0.3 → No click ✗
Selection 5: sample = 0.12 < 0.3 → Click ✓
...
Selection 100: sample = 0.29 < 0.3 → Click ✓

Expected clicks: ~30 out of 100
```

---

## Why This is Fair

### 1. Law of Large Numbers

As the number of trials increases, the observed click rate converges to the true probability:

```
Observed click rate = (Number of clicks) / (Number of selections)
                    → True click probability (as n → ∞)
```

**For Ad 3:**
- After 10 selections: might see 7-9 clicks (70-90%)
- After 100 selections: will see ~75-85 clicks (75-85%)
- After 1000 selections: will see ~795-805 clicks (79.5-80.5%)

**For Ad 1:**
- After 10 selections: might see 2-4 clicks (20-40%)
- After 100 selections: will see ~27-33 clicks (27-33%)
- After 1000 selections: will see ~295-305 clicks (29.5-30.5%)

### 2. Bayesian Learning Captures This

Thompson Sampling learns from these observations:

**Ad 3 (80% true rate):**
```
Initial:  STV(0.5, 0.002)  → Beta(0.8, 0.8)
After 5:  STV(0.8, 0.006)  → Beta(4, 1)      [4 clicks, 1 no-click]
After 20: STV(0.81, 0.024) → Beta(16, 4)     [16 clicks, 4 no-clicks]
After 50: STV(0.80, 0.059) → Beta(40, 10)    [40 clicks, 10 no-clicks]
```

**Ad 1 (30% true rate):**
```
Initial:  STV(0.5, 0.002)  → Beta(0.8, 0.8)
After 5:  STV(0.2, 0.006)  → Beta(1, 4)      [1 click, 4 no-clicks]
After 20: STV(0.29, 0.024) → Beta(6, 14)     [6 clicks, 14 no-clicks]
After 50: STV(0.30, 0.059) → Beta(15, 35)    [15 clicks, 35 no-clicks]
```

**The STV strength converges to the true click rate!**

---

## Mathematical Proof

### Bernoulli Process

Each ad selection is a **Bernoulli trial**:
```
X ~ Bernoulli(p)

P(X = 1) = p        (click)
P(X = 0) = 1 - p    (no click)
```

Your code implements this exactly:
```metta
(if (< $sample $clickProb) 1 0)
```

Since `sample ~ Uniform(0,1)`:
```
P(sample < p) = p
P(sample ≥ p) = 1 - p
```

**This is the standard way to simulate Bernoulli trials!**

### Expected Value

After n selections of Ad i with true click rate p_i:
```
E[clicks] = n × p_i
E[STV strength] → p_i   (as n → ∞)
```

**For Ad 3 (p = 0.8):**
```
After 100 selections: E[clicks] = 100 × 0.8 = 80
After 100 selections: E[strength] → 0.8
```

**For Ad 1 (p = 0.3):**
```
After 100 selections: E[clicks] = 100 × 0.3 = 30
After 100 selections: E[strength] → 0.3
```

---

## Why Ad 3 Will Have Higher STV

### Scenario: 10 iterations, each ad selected twice

**Ad 1 (30% true rate):**
```
Selection 1: 0.23 < 0.3 → Click
Selection 2: 0.67 > 0.3 → No click
Result: 1 click, 1 no-click
New STV: Beta(1.8, 1.8) → strength ≈ 0.5
```

**Ad 3 (80% true rate):**
```
Selection 1: 0.23 < 0.8 → Click
Selection 2: 0.67 < 0.8 → Click
Result: 2 clicks, 0 no-clicks
New STV: Beta(2.8, 0.8) → strength ≈ 0.78
```

**Ad 3's strength (0.78) > Ad 1's strength (0.5)** ✓

### Over Many Iterations

As Thompson Sampling runs:
1. All ads get explored initially (high uncertainty)
2. Ad 3 clicks more often → strength increases faster
3. Ad 3's Beta distribution peaks around 0.8
4. Ad 3 gets selected more often (exploitation)
5. But other ads still get tried occasionally (exploration)

**Final result:**
- Ad 3: STV(~0.80, high confidence)
- Ad 5: STV(~0.60, high confidence)
- Ad 2: STV(~0.50, high confidence)
- Ad 4: STV(~0.40, high confidence)
- Ad 1: STV(~0.30, high confidence)

**Ad 3 has the highest STV because it truly has the highest click rate!**

---

## Is This Realistic?

**YES!** This is exactly how real-world A/B testing works:

### Real AAU Website Scenario:

**Ad 3 (Research Center):**
- Well-designed, relevant to students
- True click rate: 80%
- When shown, 80% of visitors click

**Ad 1 (Cafeteria Menu):**
- Less interesting to most visitors
- True click rate: 30%
- When shown, only 30% of visitors click

**Your simulation:**
```metta
($clickProb (if (== $ruleId 3) 0.8 ...))
(if (< $sample $clickProb) 1 0)
```

**This models the real behavior!**

---

## Common Misconception

**Wrong thinking:**
"Since we're using random numbers, all ads should have equal STV."

**Correct thinking:**
"We use random numbers to simulate the stochastic nature of user behavior, but each ad has a different underlying click probability. Over time, the algorithm learns these true probabilities."

### Analogy: Coin Flipping

**Fair coin (50%):**
- Flip 100 times → expect ~50 heads
- Observed rate → 50%

**Biased coin (80%):**
- Flip 100 times → expect ~80 heads
- Observed rate → 80%

**Both use randomness, but different probabilities!**

---

## Verification

You can verify this works by running your simulation:

```bash
metta aau-ad-optimizer-ts/ad-selector.metta
```

**Expected output after 10 iterations:**
```
Ad 1: Learned STV ≈ (0.3-0.4, low confidence)
Ad 2: Learned STV ≈ (0.4-0.6, low confidence)
Ad 3: Learned STV ≈ (0.7-0.9, low confidence)  ← Highest!
Ad 4: Learned STV ≈ (0.3-0.5, low confidence)
Ad 5: Learned STV ≈ (0.5-0.7, low confidence)
```

**After 1000 iterations:**
```
Ad 1: Learned STV ≈ (0.29-0.31, high confidence)
Ad 2: Learned STV ≈ (0.49-0.51, high confidence)
Ad 3: Learned STV ≈ (0.79-0.81, high confidence)  ← Highest!
Ad 4: Learned STV ≈ (0.39-0.41, high confidence)
Ad 5: Learned STV ≈ (0.59-0.61, high confidence)
```

**Ad 3 consistently has the highest STV!**

---

## Summary

**Q: Is it fair to expect Ad 3 to have greater STV than others?**

**A: YES, because:**

1. ✅ Ad 3 has the highest true click rate (80%)
2. ✅ Random sampling correctly simulates Bernoulli trials
3. ✅ Law of Large Numbers ensures convergence to true rate
4. ✅ Thompson Sampling learns from observations
5. ✅ Bayesian updates capture the true probabilities
6. ✅ This is how real A/B testing works

**Your implementation is correct and realistic!** 🎯

The randomness doesn't make all ads equal—it simulates the stochastic nature of user behavior while preserving the underlying true click rates.
