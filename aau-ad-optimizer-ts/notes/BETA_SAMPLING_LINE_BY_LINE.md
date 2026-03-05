# Line-by-Line Explanation: betaSample and betaSampleEngine

## Overview

These two functions implement **Cheng's BB Algorithm** for sampling from Beta(a, b) distribution using rejection sampling.

---

## Part 1: betaSample - Setup Function

```metta
(: betaSample (-> Number Number Number))
(= (betaSample $successes $failures) (
    let* (
        ($a $successes)
        ($b $failures)
        ($alpha (+ $a $b))
        ($beta (if (<= (min $a $b) 1) 
                  (max (/ 1 $a) (/ 1 $b)) 
                  (sqrt (/ (- $alpha 2) (- (* 2 (* $a $b)) $alpha)))))
        ($gamma (/ (+ $a 1) $beta))
    ) (betaSampleEngine $alpha $beta $a $b $gamma)
))
```

### Line-by-Line Breakdown:

---

#### Line 1: Type Signature
```metta
(: betaSample (-> Number Number Number))
```

**What it means:**
- Function takes 2 numbers (successes, failures)
- Returns 1 number (the Beta sample)

**Mathematical context:**
- Input: Parameters of Beta(a, b) distribution
- Output: Random sample X ~ Beta(a, b) where X ∈ [0, 1]

---

#### Line 3-4: Store Input Parameters
```metta
($a $successes)
($b $failures)
```

**What it does:**
- Assigns input parameters to local variables
- `$a` = number of successes (α parameter)
- `$b` = number of failures (β parameter)

**Mathematical meaning:**
- Beta(a, b) represents a distribution over probabilities
- `a` = how many times we observed success
- `b` = how many times we observed failure
- Mean of Beta(a, b) = a/(a+b)

**Example:**
- betaSample(8, 2) → Beta(8, 2) with mean = 8/10 = 0.8
- betaSample(3, 7) → Beta(3, 7) with mean = 3/10 = 0.3

---

#### Line 5: Calculate Alpha (Total Count)
```metta
($alpha (+ $a $b))
```

**What it does:**
- Sums the two parameters: α = a + b

**Mathematical meaning:**
- α represents the **total number of observations**
- Higher α → more data → narrower distribution → more certainty

**Example:**
- Beta(8, 2): α = 10 (10 total observations)
- Beta(80, 20): α = 100 (100 total observations, same mean but more certain)

**Why we need this:**
- Used in the acceptance criterion
- Controls the shape of the proposal distribution
- Appears in the log-density calculations

---

#### Line 6-8: Calculate Beta (Scale Parameter)
```metta
($beta (if (<= (min $a $b) 1) 
          (max (/ 1 $a) (/ 1 $b)) 
          (sqrt (/ (- $alpha 2) (- (* 2 (* $a $b)) $alpha)))))
```

**This is the most complex line! Let's break it down:**

**Condition:** `(<= (min $a $b) 1)`
- Check if the smaller of a or b is ≤ 1

**Case 1: If min(a, b) ≤ 1**
```metta
(max (/ 1 $a) (/ 1 $b))
```
- β = max(1/a, 1/b)

**Mathematical reason:**
- When a or b is small (≤ 1), Beta distribution has **heavy tails**
- The distribution might be U-shaped or J-shaped
- Density can go to infinity at boundaries (0 or 1)
- Need larger β to handle these extreme shapes
- max(1/a, 1/b) ensures β is large enough

**Example:**
- Beta(0.5, 3): min = 0.5 ≤ 1
- β = max(1/0.5, 1/3) = max(2, 0.33) = 2

**Case 2: If min(a, b) > 1**
```metta
(sqrt (/ (- $alpha 2) (- (* 2 (* $a $b)) $alpha)))
```
- β = √[(α - 2) / (2ab - α)]

**Mathematical derivation:**
- When both a, b > 1, Beta is bell-shaped (unimodal)
- This formula is derived from optimizing the acceptance rate
- It comes from matching the curvature of Beta PDF with logistic proposal

**Breaking down the formula:**
```
Numerator: (α - 2) = (a + b - 2)
Denominator: (2ab - α) = (2ab - a - b)

β = √[(a + b - 2) / (2ab - a - b)]
```

**Example:**
- Beta(8, 2): α = 10, a = 8, b = 2
- Numerator: 10 - 2 = 8
- Denominator: 2×8×2 - 10 = 32 - 10 = 22
- β = √(8/22) = √0.364 ≈ 0.603

**Why this formula?**
- Derived by Cheng to minimize rejection rate
- Balances between proposal spread and target spread
- Optimal for bell-shaped Beta distributions

---

#### Line 9: Calculate Gamma (Location Parameter)
```metta
($gamma (/ (+ $a 1) $beta))
```

**What it does:**
- γ = (a + 1) / β

**Mathematical meaning:**
- γ is a **location shift parameter**
- Adjusts where the proposal distribution is centered
- The "+1" comes from the mode of Beta(a, b) being at (a-1)/(a+b-2)

**Example:**
- Beta(8, 2): a = 8, β ≈ 0.603
- γ = (8 + 1) / 0.603 = 9 / 0.603 ≈ 14.93

**Why we need this:**
- Used in the acceptance criterion
- Shifts the proposal to match the target better
- Improves acceptance rate

---

#### Line 10: Call the Sampling Engine
```metta
(betaSampleEngine $alpha $beta $a $b $gamma)
```

**What it does:**
- Passes all computed parameters to the rejection sampling loop
- Returns the final Beta sample

**Parameters passed:**
- α = a + b (total count)
- β = scale parameter (computed above)
- a = successes (original parameter)
- b = failures (original parameter)
- γ = location parameter

---

## Part 2: betaSampleEngine - Rejection Sampling Loop

```metta
(: betaSampleEngine (-> Number Number Number Number Number Number))
(= (betaSampleEngine $alpha $beta $a $b $gamma) (
    let* (
        ($u1 (getRandom))
        ($u2 (getRandom))
        ($v (* $beta (log (/ $u1 (- 1 $u1)))))
        ($w (* $a (exp $v)))
        ($temp (log (/ $alpha (+ $b $w))))
        ($left (+ (* $alpha $temp) (* $gamma $v)))
        ($right (+ (log 4) (log (* (* $u1 $u1) $u2))))
    ) (if (>= $left $right)
        (round (/ $w (+ $b $w)) 4)
        (betaSampleEngine $alpha $beta $a $b $gamma)
    )
))
```

### Line-by-Line Breakdown:

---

#### Line 4: Generate First Uniform Random Number
```metta
($u1 (getRandom))
```

**What it does:**
- Generates U₁ ~ Uniform(0, 1)
- Random number between 0 and 1

**Mathematical purpose:**
- Used to generate the proposal sample (via logistic transform)
- Also used in the acceptance test

**Example:**
- U₁ = 0.7

---

#### Line 5: Generate Second Uniform Random Number
```metta
($u2 (getRandom))
```

**What it does:**
- Generates U₂ ~ Uniform(0, 1)
- Independent from U₁

**Mathematical purpose:**
- Used only in the acceptance test
- Provides the stochastic threshold for rejection sampling

**Example:**
- U₂ = 0.4

---

#### Line 6: Logistic Transformation
```metta
($v (* $beta (log (/ $u1 (- 1 $u1)))))
```

**Breaking it down:**
```
Step 1: (- 1 $u1)           → 1 - U₁
Step 2: (/ $u1 (- 1 $u1))   → U₁ / (1 - U₁)
Step 3: (log ...)           → log(U₁ / (1 - U₁))
Step 4: (* $beta ...)       → β × log(U₁ / (1 - U₁))
```

**Mathematical formula:**
```
V = β × log(U₁ / (1 - U₁))
```

**What this does:**
- Transforms Uniform(0,1) to Logistic distribution
- log(U/(1-U)) is called the **logit function**
- Maps [0, 1] → (-∞, +∞)

**Why logistic?**
- The logistic distribution has tails similar to Beta
- Easy to sample from (just transform uniform)
- Good proposal for rejection sampling

**Mathematical properties:**
- If U ~ Uniform(0,1), then log(U/(1-U)) ~ Logistic(0, 1)
- Multiplying by β scales the distribution: V ~ Logistic(0, β)

**Example:**
- U₁ = 0.7, β = 0.603
- 1 - U₁ = 0.3
- U₁/(1-U₁) = 0.7/0.3 = 2.333
- log(2.333) = 0.847
- V = 0.603 × 0.847 = 0.511

**Intuition:**
- U₁ = 0.5 → V = 0 (center)
- U₁ > 0.5 → V > 0 (right tail)
- U₁ < 0.5 → V < 0 (left tail)
- U₁ → 1 → V → +∞
- U₁ → 0 → V → -∞

---

#### Line 7: Generate Proposal W
```metta
($w (* $a (exp $v)))
```

**Mathematical formula:**
```
W = a × e^V
```

**What this does:**
- Transforms V from (-∞, +∞) to (0, +∞)
- Exponential ensures W is always positive
- Multiplying by 'a' scales appropriately

**Example:**
- a = 8, V = 0.511
- e^V = e^0.511 = 1.667
- W = 8 × 1.667 = 13.336

**Why this transformation?**
- We need a value in (0, +∞) to eventually map to [0, 1]
- The exponential of logistic gives a good proposal
- The factor 'a' shifts the distribution toward the Beta's mode

---

#### Line 8: Calculate Temporary Log Term
```metta
($temp (log (/ $alpha (+ $b $w))))
```

**Mathematical formula:**
```
temp = log(α / (b + W))
```

**Breaking it down:**
```
Step 1: (+ $b $w)      → b + W
Step 2: (/ $alpha ...) → α / (b + W)
Step 3: (log ...)      → log(α / (b + W))
```

**Example:**
- α = 10, b = 2, W = 13.336
- b + W = 2 + 13.336 = 15.336
- α/(b+W) = 10/15.336 = 0.652
- temp = log(0.652) = -0.428

**Mathematical meaning:**
- This term comes from the Beta distribution's log-density
- Part of the acceptance criterion
- Relates to the normalizing constant of Beta

---

#### Line 9: Calculate Left Side (Log Acceptance Ratio)
```metta
($left (+ (* $alpha $temp) (* $gamma $v)))
```

**Mathematical formula:**
```
L = α × temp + γ × V
  = α × log(α/(b+W)) + γ × V
```

**Breaking it down:**
```
Term 1: (* $alpha $temp)  → α × log(α/(b+W))
Term 2: (* $gamma $v)     → γ × V
Sum: (+ ...)              → α × log(α/(b+W)) + γ × V
```

**Example:**
- α = 10, temp = -0.428, γ = 14.93, V = 0.511
- Term 1: 10 × (-0.428) = -4.28
- Term 2: 14.93 × 0.511 = 7.629
- L = -4.28 + 7.629 = 3.349

**Mathematical meaning:**
- This is the **log of the acceptance ratio**
- Comes from: log[f(X) / (M × g(X))]
- Where f = Beta PDF, g = proposal PDF, M = bounding constant
- If L ≥ R (right side), we accept the sample

**Why these terms?**
- α × log(α/(b+W)): From Beta distribution's normalizing constant
- γ × V: Adjustment for the logistic proposal distribution

---

#### Line 10: Calculate Right Side (Log Threshold)
```metta
($right (+ (log 4) (log (* (* $u1 $u1) $u2))))
```

**Mathematical formula:**
```
R = log(4) + log(U₁² × U₂)
  = log(4) + 2×log(U₁) + log(U₂)
  = log(4 × U₁² × U₂)
```

**Breaking it down:**
```
Step 1: (* $u1 $u1)       → U₁²
Step 2: (* ... $u2)       → U₁² × U₂
Step 3: (log ...)         → log(U₁² × U₂)
Step 4: (+ (log 4) ...)   → log(4) + log(U₁² × U₂)
```

**Example:**
- U₁ = 0.7, U₂ = 0.4
- U₁² = 0.49
- U₁² × U₂ = 0.49 × 0.4 = 0.196
- log(0.196) = -1.629
- log(4) = 1.386
- R = 1.386 + (-1.629) = -0.243

**Mathematical meaning:**
- This is the **log of the random threshold**
- In standard rejection sampling: accept if U ≤ f(X)/(M×g(X))
- Taking logs: accept if log(U) ≤ log(f(X)) - log(M×g(X))
- The log(4) is part of the bounding constant M
- U₁² × U₂ provides the randomness

**Why U₁²?**
- U₁ is used twice: once for generating V, once for threshold
- Squaring accounts for this correlation
- Ensures the acceptance probability is correct

**Why log(4)?**
- Comes from the bounding constant M = 4
- Cheng proved M = 4 is sufficient for all Beta(a,b) with a,b > 0
- Ensures f(x) ≤ M × g(x) everywhere

---

#### Line 11-13: Accept or Reject
```metta
(if (>= $left $right)
    (round (/ $w (+ $b $w)) 4)
    (betaSampleEngine $alpha $beta $a $b $gamma)
)
```

**Acceptance Test:**
```
If L ≥ R: ACCEPT
Else: REJECT and try again
```

**Case 1: Accept (L ≥ R)**
```metta
(round (/ $w (+ $b $w)) 4)
```

**Mathematical formula:**
```
X = W / (b + W)
```

**Breaking it down:**
```
Step 1: (+ $b $w)    → b + W
Step 2: (/ $w ...)   → W / (b + W)
Step 3: (round ... 4) → Round to 4 decimal places
```

**Example:**
- W = 13.336, b = 2
- b + W = 15.336
- X = 13.336 / 15.336 = 0.8696
- Rounded: 0.8696

**Mathematical meaning:**
- This transforms W from (0, +∞) to [0, 1]
- It's a **logistic sigmoid** transformation
- Maps our proposal to a valid probability

**Properties:**
- W = 0 → X = 0
- W → ∞ → X → 1
- W = b → X = 0.5
- Monotonic: larger W → larger X

**This is our Beta sample!** X ~ Beta(a, b)

**Case 2: Reject (L < R)**
```metta
(betaSampleEngine $alpha $beta $a $b $gamma)
```

**What it does:**
- Recursive call: try again with new random numbers
- Keep trying until we get an accepted sample

**Example:**
- L = 3.349, R = -0.243
- 3.349 ≥ -0.243? YES → Accept!
- Return X = 0.8696

---

## Complete Example Walkthrough

**Goal:** Sample from Beta(8, 2)

### Setup (betaSample):
```
a = 8, b = 2
α = 8 + 2 = 10
min(8, 2) = 2 > 1 → Use formula
β = √[(10-2)/(2×8×2-10)] = √[8/22] = 0.603
γ = (8+1)/0.603 = 14.93
```

### Iteration 1 (betaSampleEngine):
```
U₁ = 0.7, U₂ = 0.4

V = 0.603 × log(0.7/0.3) = 0.603 × 0.847 = 0.511

W = 8 × e^0.511 = 8 × 1.667 = 13.336

temp = log(10/15.336) = log(0.652) = -0.428

L = 10×(-0.428) + 14.93×0.511 = -4.28 + 7.629 = 3.349

R = log(4) + log(0.7² × 0.4) = 1.386 + (-1.629) = -0.243

L ≥ R? → 3.349 ≥ -0.243? → YES! ✓

X = 13.336 / 15.336 = 0.8696
```

**Return: 0.8696** (a valid Beta(8,2) sample!)

**Verification:**
- Beta(8, 2) has mean = 8/10 = 0.8
- Our sample 0.8696 is close to the mean ✓
- It's in [0, 1] ✓
- If we sample many times, they'll follow Beta(8, 2) distribution ✓

---

## Summary

**betaSample:**
1. Computes α = a + b (total observations)
2. Computes β (scale parameter, depends on shape)
3. Computes γ = (a+1)/β (location parameter)
4. Calls betaSampleEngine with these parameters

**betaSampleEngine:**
1. Generate U₁, U₂ ~ Uniform(0,1)
2. Transform U₁ to logistic: V = β × log(U₁/(1-U₁))
3. Generate proposal: W = a × e^V
4. Compute acceptance ratio: L = α×log(α/(b+W)) + γ×V
5. Compute threshold: R = log(4) + log(U₁²×U₂)
6. If L ≥ R: Accept X = W/(b+W)
7. Else: Reject and try again (recursion)

**The result is a true sample from Beta(a, b)!** 🎯
