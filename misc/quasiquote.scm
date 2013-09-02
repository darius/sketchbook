;; Expand quasiquote forms. Based on quasi-q from
;; http://norvig.com/paip/compile3.lisp

;; This handles nested quasiquotes like Alan Bawden 1999,
;; "Quasiquotation in Lisp", and unlike the Scheme standard and actual
;; Scheme systems I've tried. This behavior here seems better.
;; N.B. the expansion is not hygienic: it references LIST, etc.,
;; without regard to scope.

(define (qq-expand x)
  (cond ((or (null? x) (symbol? x))
         (list 'quote x))
        ((not (pair? x))
         x)
        ((starts-with? x 'unquote)
         (second x))
        ((starts-with? x 'unquote-splicing)
         (error "Bad syntax in quasiquote" x))
        ((starts-with? x 'quasiquote)
         (qq-expand (qq-expand (second x))))
        ((starts-with? (car x) 'unquote-splicing)
         (qq-append (second (car x))
                    (qq-expand (cdr x))))
        (else (qq-cons (qq-expand (car x))
                       (qq-expand (cdr x))
                       x))))

(define (qq-append spliceme expansion)
  (if (equal? expansion ''())
      spliceme
      (list 'append spliceme expansion)))

(define (qq-cons left right x)
  (cond ((and (constant? left) (constant? right))
         (list 'quote (reuse-cons (qq-eval left) (qq-eval right) x)))
        ((equal? right ''())
         (list 'list left))
        ((starts-with? right 'list)
         (cons 'list (cons left (cdr right))))
        (else
         (list 'cons left right))))

(define (reuse-cons new-car new-cdr pair)
  (if (and (eqv? new-car (car pair))
           (eqv? new-cdr (cdr pair)))
      pair
      (cons new-car new-cdr)))

(define (constant? exp)
  (if (pair? exp)
      (eq? (car exp) 'quote)
      (not (symbol? exp))))

(define (qq-eval constant)
  (if (pair? constant)       ;; must be quoted constant
      (second constant)
      constant))

(define (starts-with? x tag)
  (and (pair? x) (eq? (car x) tag)))

(define second cadr)
