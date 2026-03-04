;; Ad definitions for Addis Ababa University website
;; Each ad starts with uniform prior: STV(strength=0.5, confidence=0.002)
;; This represents high uncertainty about click rates initially

;(: initializeAd (-> hyperon::space::DynSpace Expression))
(= (initializeAd $space) (
    add-reduct $space 
        (superpose (
            ;; Ad 1: True click rate 30%
            (: Ad 1
                (STV 0.5 0.002)
                (Action (DISPLAY AD_ONE))
            )

            ;; Ad 2: True click rate 50%
            (: Ad 2
                (STV 0.5 0.002)
                (Action (DISPLAY AD_TWO))
            )

            ;; Ad 3: True click rate 80% (BEST)
            (: Ad 3
                (STV 0.5 0.002)
                (Action (DISPLAY AD_THREE))
            )

            ;; Ad 4: True click rate 40%
            (: Ad 4
                (STV 0.5 0.002)
                (Action (DISPLAY AD_FOUR))
            )

            ;; Ad 5: True click rate 60%
            (: Ad 5
                (STV 0.5 0.002)
                (Action (DISPLAY AD_FIVE))
            )
        ))
))

;(: addAdRules (-> hyperon::space::DynSpace Expression))
(= (addAdRules $space) (
    initializeAd $space
))