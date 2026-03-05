;; statistics.metta - Mathematical utilities for Bayesian inference

;; Check if value is between bounds
(: isBetween (-> Number Number Number Bool))
(= (isBetween $val $low $high) (and (>= $val $low) (<= $val $high)))

(: max (-> Number Number Number))
(= (max $x $y) (if (> $x $y) $x $y))

(: min (-> Number Number Number))
(= (min $x $y) (if (> $x $y) $y $x))

(: round (-> Number Number Number))
(= (round $num $sig) ((py-atom round) $num $sig))

(: getRandomInt (-> Number Number Number))
(= (getRandomInt $min $max) (
    (py-atom random.randint) $min $max
))

(: getRandom (-> Number))
(= (getRandom) (
    (py-atom random.random)
))

(: log (-> Number Number))
(= (log $value) (
    (py-atom math.log) $value
))

(: sqrt (-> Number Number))
(= (sqrt $num) (
    (py-atom math.sqrt) $num
))

(: exp (-> Number Number))
(= (exp $num) (
    (py-atom math.exp) $num
))


;; ============================================================================
;; BETA DISTRIBUTION SAMPLING - Cheng's BB Algorithm (1978)
;; ============================================================================
;; Generates random samples from Beta(a, b) distribution using rejection sampling
;; with a logistic proposal distribution. This is the industry-standard algorithm
;; used in NumPy, R, MATLAB, and other statistical software.
;;
;; Algorithm Overview:
;; 1. Transform uniform random to logistic distribution
;; 2. Generate proposal sample W
;; 3. Accept/reject based on Beta PDF ratio
;; 4. Transform accepted W to [0,1] range
;;
;; Efficiency: 60-90% acceptance rate (typically only 1-2 tries needed)
;; Reference: Cheng, R.C.H. (1978). Communications of the ACM, 21(4), 317-322
;; ============================================================================

;; Main entry point: Sample from Beta(a, b) distribution
;; Input: a (successes), b (failures) - parameters of Beta distribution
;; Output: Random sample X ~ Beta(a,b) where X ∈ [0,1]
(: betaSample (-> Number Number Number))
(= (betaSample $successes $failures) (
    let* (
        ;; Store parameters
        ($a $successes)  ; Alpha parameter (number of successes)
        ($b $failures)   ; Beta parameter (number of failures)
        
        ;; Compute derived parameters for Cheng's algorithm
        ($alpha (+ $a $b))  ; Total observations (controls certainty)
        
        ;; Scale parameter β - depends on distribution shape
        ;; Case 1: Heavy tails (U-shape or J-shape) when min(a,b) ≤ 1
        ;; Case 2: Bell-shaped when both a,b > 1 (uses optimized formula)
        ($beta (if (<= (min $a $b) 1) 
                  (max (/ 1 $a) (/ 1 $b))  ; Larger β for heavy tails
                  (sqrt (/ (- $alpha 2) (- (* 2 (* $a $b)) $alpha)))))  ; Optimal β for bell shape
        
        ;; Location parameter γ - centers the proposal distribution
        ($gamma (/ (+ $a 1) $beta))
    ) 
    ;; Call rejection sampling engine with computed parameters
    (betaSampleEngine $alpha $beta $a $b $gamma)
))

;; Rejection sampling engine - the core sampling loop
;; Uses logistic proposal distribution with accept/reject criterion
;; Recursively retries until a sample is accepted
(: betaSampleEngine (-> Number Number Number Number Number Number))
(= (betaSampleEngine $alpha $beta $a $b $gamma) (
    let* (
        ;; Step 1: Generate two independent uniform random numbers
        ($u1 (getRandom))  ; U₁ ~ Uniform(0,1) - for proposal generation
        ($u2 (getRandom))  ; U₂ ~ Uniform(0,1) - for acceptance test
        
        ;; Step 2: Logistic transformation
        ;; V = β × log(U₁/(1-U₁)) transforms Uniform to Logistic distribution
        ;; This maps [0,1] → (-∞,+∞) with tails similar to Beta
        ($v (* $beta (log (/ $u1 (- 1 $u1)))))
        
        ;; Step 3: Generate proposal W
        ;; W = a × e^V maps (-∞,+∞) → (0,+∞)
        ;; The factor 'a' scales toward the Beta distribution's mode
        ($w (* $a (exp $v)))
        
        ;; Step 4: Compute acceptance criterion components
        ;; temp = log(α/(b+W)) - part of Beta distribution's log-density
        ($temp (log (/ $alpha (+ $b $w))))
        
        ;; Left side: log of acceptance ratio
        ;; L = α×log(α/(b+W)) + γ×V - log(4)
        ;; Comes from log[f(X)/(M×g(X))] where f=Beta PDF, g=proposal PDF, M=4
        ($left (+ (* $alpha $temp) (* $gamma $v)))
        
        ;; Right side: log of random threshold
        ;; R = log(4) + log(U₁²×U₂)
        ;; The log(4) is the bounding constant, U₁² accounts for correlation
        ($right (+ (log 4) (log (* (* $u1 $u1) $u2))))
    ) 
    ;; Step 5: Accept or reject
    (if (>= $left $right)
        ;; ACCEPT: Transform W to [0,1] using sigmoid: X = W/(b+W)
        ;; This is our Beta sample! Round to 4 decimal places
        (round (/ $w (+ $b $w)) 4)
        
        ;; REJECT: Try again with new random numbers (tail recursion)
        (betaSampleEngine $alpha $beta $a $b $gamma)
    )
))

