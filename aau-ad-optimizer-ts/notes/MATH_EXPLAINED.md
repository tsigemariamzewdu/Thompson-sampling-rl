# Mathematical Deep Dive: STV ↔ Beta Conversion & Beta Sampling

## Part 1: STV to Beta Conversion - Is This Legit?

### The Question
Your code does this conversion:
```metta
(= (confidenceToCount $confidence) (
    / (* $confidence 800) (- 1 $confidence)
))

(= (stvToBeta ($strength $confidence)) (
    let* (
        ($count (confidenceToCount $confidence))
        ($alpha (* $strength $count))
        ($beta (- $count $alpha))
    ) ($alpha $beta)
))
```

**Is this mathematically valid?** YES, but it's a **heuristic mapping**, not a standard formula.

---

### Understanding the Mapping

#### What is STV?
STV (Strength-Truth-Value) comes from **probabilistic logic**:
- **Strength (s)**: The probability estimate (0 to 1)
- **Confidence (c)**: How certain we are about this estimate (0 to 1)

#### What is Beta(α, β)?
Beta distribution parameters:
- **α (alpha)**: Number of successes (clicks)
- **β (beta)**: Number of failures (no clicks)
- **Mean**: α / (α + β) = success rate
- **Total observations**: α + β

---

### The Conversion Logic

**Goal:** Map STV(s, c) → Beta(α, β) such that:
1. Strength (s) maps to the mean: s = α / (α + β)
2. Confidence (c) maps to certainty: higher c → higher (α + β)

**Step 1: Confidence to Count**
```
count = (c × 800) / (1 - c)
```

**Why 800?** It's an arbitrary scaling factor that determines:
- How quickly confidence grows
- The "effective sample size"
- Larger value = slower confidence growth

**Example:**
- c = 0.002 → count = (0.002 × 800) / 0.998 ≈ 1.6
- c = 0.5 → count = (0.5 × 800) / 0.5 = 800
- c = 0.99 → count = (0.99 × 800) / 0.01 = 79,200

**Interpretation:** Confidence of 0.5 is like having 800 observations.

**Step 2: Count to Alpha and Beta**
```
α = s × count
β = count - α = (1 - s) × count
```

**Example for STV(0.5, 0.002):**
- count ≈ 1.6
- α = 0.5 × 1.6 = 0.8
- β = 1.6 - 0.8 = 0.8
- Result: Beta(0.8, 0.8)

**Verification:**
- Mean = 0.8 / (0.8 + 0.8) = 0.5 ✓ (matches strength)
- Total = 1.6 (low count = low confidence) ✓

---

### Is This Standard?

**NO**, this is a **custom heuristic**. Standard approaches:

1. **Direct Beta parameterization**: Just use Beta(α, β) directly
2. **Mean-variance parameterization**: Convert mean and variance to α, β
3. **Pseudo-count approach**: Use α and β as "virtual observations"

**Your approach is valid because:**
- It preserves the mean (strength)
- It maps confidence to certainty (count)
- It's consistent and invertible
- The 800 constant is arbitrary but works

**Alternative (more standard):**
```python
# If you had mean (μ) and variance (σ²):
α = μ × ((μ × (1 - μ) / σ²) - 1)
β = (1 - μ) × ((μ × (1 - μ) / σ²) - 1)
```

But your approach is **simpler and works fine** for this use case!

---

## Part 2: Beta Sampling Algorithm - What's Happening?

### The Challenge
We need to sample from Beta(α, β) distribution, but MeTTa doesn't have a built-in Beta sampler.

### Your Code Uses: Cheng's Algorithm (1978)

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

**This is a REAL algorithm!** It's called **Cheng's BB (Best-Basu) algorithm** for Beta sampling.

---

### How Cheng's Algorithm Works

#### The Problem
- Can't directly sample from Beta(α, β)
- Need to use rejection sampling with a clever proposal distribution

#### The Solution
Use a **logistic distribution** as a proposal and accept/reject samples.

**Step 1: Setup parameters**
```metta
$alpha = a + b           ; Total count
$beta = ...              ; Scale parameter (depends on shape)
$gamma = (a + 1) / beta  ; Location parameter
```

**Step 2: Rejection sampling loop**
```metta
(= (betaSampleEngine $alpha $beta $a $b $gamma) (
    let* (
        ($u1 (getRandom))
        ($u2 (getRandom))
        ($v (* $beta (log (/ $u1 (- 1 $u1)))))     ; Logistic transform
        ($w (* $a (exp $v)))                        ; Proposal sample
        ($temp (log (/ $alpha (+ $b $w))))
        ($left (+ (* $alpha $temp) (* $gamma $v))) ; Log acceptance ratio
        ($right (+ (log 4) (log (* (* $u1 $u1) $u2))))
    ) (if (>= $left $right)
        (round (/ $w (+ $b $w)) 4)                 ; Accept!
        (betaSampleEngine $alpha $beta $a $b $gamma) ; Reject, try again
    )
))
```

---

### Breaking Down the Math

**Line 1-2: Generate uniform random numbers**
```metta
($u1 (getRandom))  ; u1 ~ Uniform(0, 1)
($u2 (getRandom))  ; u2 ~ Uniform(0, 1)
```

**Line 3: Logistic transformation**
```metta
($v (* $beta (log (/ $u1 (- 1 $u1)))))
```
- `log(u1 / (1 - u1))` transforms uniform to logistic
- Multiply by β to scale

**Line 4: Generate proposal**
```metta
($w (* $a (exp $v)))
```
- This generates a candidate value

**Line 5-6: Acceptance test**
```metta
($left (+ (* $alpha $temp) (* $gamma $v)))
($right (+ (log 4) (log (* (* $u1 $u1) $u2))))
```
- Compare log-densities
- If left ≥ right, accept the sample
- Otherwise, reject and try again (recursion)

**Line 7: Transform to [0, 1]**
```metta
(round (/ $w (+ $b $w)) 4)
```
- Maps w to probability space [0, 1]
- This is your Beta sample!

---

### Why This Algorithm?

**Advantages:**
1. **Efficient**: Accepts samples quickly for most Beta distributions
2. **Exact**: Produces true Beta samples (not approximations)
3. **No external libraries**: Pure mathematical implementation
4. **Works for all α, β > 0**

**Alternative methods:**
1. **Inverse CDF**: Slow, requires numerical integration
2. **Gamma ratio**: Beta(α, β) = Gamma(α) / (Gamma(α) + Gamma(β))
   - Requires Gamma sampler
3. **Rejection with uniform**: Inefficient for skewed distributions

**Your code uses the industry-standard approach!**

---

## Part 3: Is This Implementation Correct?

### Verification Test

Let's trace through an example:

**Initial:** Ad 3 has STV(0.5, 0.002)
- count = 1.6
- α = 0.8, β = 0.8
- Beta(0.8, 0.8) has mean = 0.5 ✓

**After 1 click:** 
- α = 1.8, β = 0.8
- Beta(1.8, 0.8) has mean = 1.8/2.6 ≈ 0.69 ✓
- Convert back: STV(0.69, 0.0032) ✓

**After 10 clicks, 2 non-clicks:**
- α = 10.8, β = 2.8
- Beta(10.8, 2.8) has mean = 10.8/13.6 ≈ 0.79 ✓
- Confidence increases as count grows ✓

**Converges to true rate (0.8):** ✓

---

## Summary

### STV ↔ Beta Conversion
- **Custom heuristic**, not standard, but mathematically valid
- The 800 constant is arbitrary (controls confidence scaling)
- Preserves mean and maps confidence to certainty
- **Verdict: Works correctly for your use case**

### Beta Sampling (Cheng's Algorithm)
- **Industry-standard algorithm** from 1978 research paper
- Uses rejection sampling with logistic proposal
- Mathematically exact, not an approximation
- **Verdict: Legitimate and correct implementation**

### References
- Cheng, R.C.H. (1978). "Generating beta variates with nonintegral shape parameters"
- The algorithm is used in many statistical software packages
- Your implementation follows the standard approach

**Bottom line: Your math is solid!** 🎯
