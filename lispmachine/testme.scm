(interpret
 '(letrec ((fact (lambda (n)
                   ((eqv? n '0)
                    (lambda () '1)
                    (lambda () (* n (fact (- n '1))))))))
    (fact '5)))
