!(register-module! ../../tsrl)
!(import! &self tsrl:aau-ad-optimizer-ts:rules)
!(import! &self tsrl:aau-ad-optimizer-ts:bandit-algo)
!(import! &self tsrl:aau-ad-optimizer-ts:math-helpers)
(= (rand-random) (py-call (random.random)))
!(py-call (random.seed 42))

;;Thompson Sampling for ad selection

!(bind! &rules (new-space))
!(addAdRules &rules)

(: run (-> Number Number Expression))
(= (run $iter $cumReward) (
    if (== $iter 0)
    ()
    (let* (
        ($_ (println! (--- Iteration  $iter ---)))
        ($reward (AdLoop  &rules))
        ($newCumReward (+ $cumReward $reward))
        ($_ (println! (METRIC reward $reward cumulative $newCumReward)))
        ($_ (println! (--- After iteration $iter ---)))
    ) (run (- $iter 1) $newCumReward)
)
))

(= (AdLoop $ruleSpace) (
    let* (
        ($allRules (getAllRules $ruleSpace))
        ($_ (println! ("Available actions: " $allRules)))
        (($chosenActionId $score) (thompsonSampling $allRules $ruleSpace))
        ($result (performAction $chosenActionId $ruleSpace))
        ($_ (println! (# $chosenActionId was chosen  and resulted in $result)))
        ($updatedRule (updateRule $chosenActionId $result $ruleSpace))
    ) $result
))
;; Run iterations of the Ad loop 
!(run 10 0)

;;  print final learned STV values
(= (printAdSummary $adId $space) (
    let* (
        (($s $c) (getSTV $adId $space))
        ($trueProb (if (== $adId 1) 0.3
                   (if (== $adId 2) 0.5
                   (if (== $adId 3) 0.8
                   (if (== $adId 4) 0.4
                   0.6)))))
        ($_ (println! ("Ad " $adId ": True Click Rate = " $trueProb ", Learned STV = (" $s ", " $c ")")))
    ) ()
))

!(println! ("\n=== FINAL RESULTS ==="))
!(printAdSummary 1 &rules)
!(printAdSummary 2 &rules)
!(printAdSummary 3 &rules)
!(printAdSummary 4 &rules)
!(printAdSummary 5 &rules)

