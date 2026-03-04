;; Utility functions for Thompson Sampling based action planner
(= (thompsonSampling $ruleIds $space) (
    if (== $ruleIds ())
        (-1 0) 
    (let* (
        (($ruleId $rest) (decons-atom $ruleIds))
        ($_ (println! ("Considering rule: " $ruleId)))
        (($strength $confidence) (getSTV $ruleId $space))
        (($alpha $beta) (stvToBeta ($strength $confidence)))
        ($sample (betaSample $alpha $beta))
        ($_ (println! ("Rule " $ruleId " gave sample: " $sample)))
        (($chosenId $chosenSample) (thompsonSampling $rest $space))
    ) (if (>= $sample $chosenSample) 
        ($ruleId $sample) 
        ($chosenId $chosenSample)
    ))
))

;; Perform the action associated with the rule and return result (1 for click, 0 for no click)
;; Each ad has a different true click probability

(= (performAction $ruleId $space) (
    let* (
        ($action (getAction $ruleId $space))
        ($sample (getRandom))
        ($_ (println!("here is the random sample: " $sample)))
        ($_ (println! ("Performing action: " $action)))
        ($clickProb (if (== $ruleId 1) 0.3
                    (if (== $ruleId 2) 0.5
                    (if (== $ruleId 3) 0.8
                    (if (== $ruleId 4) 0.4
                    0.6)))))
    ) (if (< $sample $clickProb) 1 0)
))

;; Convert confidence to count
;(: confidenceToCount (-> Number Number))

(= (confidenceToCount $confidence) (
    / (* $confidence 800) (- 1 $confidence)
))

;; Convert count to confidence
;(: countToConfindence (-> Number Number))
(= (countToConfindence $count) (
    / $count (+ 800 $count)
))

;; Convert strength and confidence to alpha and beta parameters of Beta distribution
;(: stvToBeta (-> (Number Number) (Number Number)))
(= (stvToBeta ($strength $confidence)) (
    let* (
        ($count (confidenceToCount $confidence))
        ($alpha (* $strength $count))
        ($beta (- $count $alpha))
    ) ($alpha $beta)
))

;; Convert alpha and beta parameters of Beta distribution to strength and confidence
;(: betaToSTV (-> (Number Number) (Number Number)))
(= (betaToSTV ($alpha $beta)) (
    let* (
        ($count (+ $alpha $beta))
        ($strength (round (/ $alpha $count) 2))
        ($confidence (countToConfindence $count))
    ) ($strength $confidence)
))

;; Get all rule IDs in the rule space
;(: getAllRules (-> hyperon::space::DynSpace Expression))
(= (getAllRules $space) (
    collapse (match $space (: Ad $id $stv $action) $id)
))

;; Get rule details by rule ID
;(: getRule (-> Number hyperon::space::DynSpace Expression))
(= (getRule $ruleId $space) (
    match $space (: Ad $ruleId $stv $action) (: Ad $ruleId $stv $action)
))

;; Get specific attributes (STV) of a rule by rule ID
;(: getSTV (-> Number hyperon::space::DynSpace (Number Number)))
(= (getSTV $ruleId $space) (
    match $space (: Ad $ruleId (STV $s $c) $action) ($s $c)
))

;; Get specific attributes (Action) of a rule by rule ID
;(: getAction (-> Number hyperon::space::DynSpace Expression))
(= (getAction $ruleId $space) (
    match $space (: Ad $ruleId $stv (Action $action)) $action
))

;; Thompson Sampling to select a rule based on its STV values
;(: thompsonSampling (-> Expression hyperon::space::DynSpace (Number Number)))

;; Update Atoms in a space
;(: updateAtom (-> Grounded Atom Atom (->)))
(= (updateAtom $space $oatom $natom) (let $_ (remove-atom $space $oatom) (add-atom $space $natom)))

;; Update STV of a rule by rule ID
;(: updateSTV (-> Number (Number Number) hyperon::space::DynSpace (->)))
(= (updateSTV $ruleId ($s $c) $space) (
    let* (
        ($rule (getRule $ruleId $space))
        ($_ (println! ("Old rule: " $rule)))
        ((: Ad $ruleId (STV $os $oc) $action) $rule)
        ($newRule (: Ad $ruleId (STV $s $c) $action))
        ($_ (updateAtom $space $rule $newRule))
        ($_ (println! ("New rule: " $newRule)))
    ) ()
))

;; Update rule after action execution based on result (1 for success, 0 for failure)
;(: updateRule (-> Number Number hyperon::space::DynSpace (->)))
(= (updateRule $ruleId $result $space) (
    let* (
        (($strength $confidence) (getSTV $ruleId $space))
        (($alpha $beta) (stvToBeta ($strength $confidence)))
        ($newAlpha (if (== $result 1) (+ $alpha 1) $alpha))
        ($newBeta (if (== $result 1) $beta (+ $beta 1)))
        (($newStrength $newConfidence) (betaToSTV ($newAlpha $newBeta)))
        ($_ (updateSTV $ruleId ($newStrength $newConfidence) $space))
    ) ()
))