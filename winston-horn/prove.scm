; Resolution theorem prover for propositional logic

; Example inputs
(define premise 
  '(and (or q (not p))
        (or r (not q))
        (or s (not r))
        (or (not u) (not s))))
(define negation
  '(and (or p) (or u)))

; Try to prove that PREMISE implies (NOT NEGATION).
; Pre: the arguments are in conjunctive normal form.
(define (prove premise negation)
  (resolving (append (cdr premise) (cdr negation))))

; Repeatedly find and add resolvents to the clauses; return true iff
; we find an empty resolvent.
(define (resolving clauses)
  (let trying ((remainder clauses))
    (and (not (null? remainder))
         (cond ((some (lambda (clause) (resolve (car remainder) clause))
                      (cdr remainder))
                => (lambda (resolvent)
                     (print resolvent)
                     (or (null? (cdr resolvent))
                         (resolving (cons resolvent clauses)))))
               (else (trying (cdr remainder)))))))

; Return a resolution of the clauses, or #f if there is none.
; They resolve if a variable appears in the positive sense in one
; clause and negated in the other; the resolution combines all the
; other variables from both clauses.
(define (resolve clause1 clause2)
  (let ((xs (cdr clause1))
        (ys (cdr clause2)))
    (some (lambda (x)
            (let ((-x (invert x)))
              (and (member -x ys)
                   (combine (delete x xs) (delete -x ys)))))
          xs)))

; Simplify `(not ,x).
(define (invert x)
  (cond ((symbol? x) `(not ,x))
        ((starts-with? 'not x) (cadr x))
        (else (error "Bad x" x))))

; Simplify `(or ,@xs ,@ys).
(define (combine xs ys)
  `(or ,@(foldr adjoin ys xs)))


; Helpers

(define (print x)
  (write x)
  (newline))

(define (starts-with? tag sexpr)
  (and (pair? sexpr)
       (eq? tag (car sexpr))))

(define (delete x xs)
  (cond ((null? xs) '())
        ((equal? x (car xs)) (cdr xs))
        (else (cons (car xs) (delete x (cdr xs))))))

(define (adjoin x xs)
  (if (member x xs) xs (cons x xs)))

(define (some f ls)
  (and (not (null? ls))
       (or (f (car ls))
           (some f (cdr ls)))))

(define (foldr f id ls)
  (if (null? ls)
      id
      (f (car ls)
         (foldr f id (cdr ls)))))

(define (dedup L)
  (cond ((null? L) '())
        ((member (car L) (cdr L)) (dedup (cdr L)))
        (else (cons (car L) (dedup (cdr L))))))

(define (filter ok? L)
  (cond ((null? L) '())
        ((ok? (car L))
         (cons (car L)
               (filter ok? (cdr L))))
        (else
         (filter ok? (cdr L)))))
