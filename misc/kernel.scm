;; Working out what Shutt's Kernel might be like, from the vague
;; general idea. Unfinished and not compared to his yet.

'($call $define 'define                        ;XXX quote
  ($ env (name expr)
     ($call $define name (env expr))))

(($ _ignore (def)
    ($call $define def ($ env (name expr)
                          ($call $define name (env expr)))))
 define)

(define quote ($ env (x) x))

(define cons  ($ env (x xs) ($call $cons (env x) (env xs))))

'(define wrap
  (lambda (ff)
    (lambda params
      ($call $apply ff params))))

(define wrap
  ($ env (ff)
     ($call ($ _ignore (p) ($call p (env ff)))
            ($ _ignore (fff)
               ($ env2 params
                  ($call $apply fff (env2 params)))))))

(define lambda
  ($ env (params body)
     (wrap (env (cons $ (cons '_ignore (cons params (cons body '()))))))))


(define if
  ($ env (test if-true if-false)
     (env ((as-boolean test) if-true if-false))))

(define as-boolean (wrap $as-boolean))


(define zero? (wrap $zero?))
(define *     (wrap $*))
(define -     (wrap $-))

;; $call
;; $define
;; <environment>
;; $apply  XXX needed?
;; $
;; _ignore

;; <pair>
;; <nil>
;; $cons $car $cdr

;; <boolean>
;; $as-boolean

;; <number>
;; $zero? $* $-


; example program
(define factorial
  (lambda (n)
    (if (zero? n)
        1
        (* n (factorial (- n 1))))))
