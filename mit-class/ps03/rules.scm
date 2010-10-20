(define (symbol<? x y)
  (string<? (symbol->string x)
            (symbol->string y)))

(define (list<? x y)
  (let ((nx (length x))
        (ny (length y)))
    (or (< nx ny)
        (and (= nx ny)
             (let comparing ((x x) (y y))
               (cond ((null? x) #f) ; same
                     ((expr<? (car x) (car y)) #t)
                     ((expr<? (car y) (car x)) #f)
                     (else (comparing (cdr x) (cdr y)))))))))

(define (expr<? x y)
  (cond ((null? x)
         (if (null? y) #f #t))
        ((null? y) #f)
        ((number? x)
         (if (number? y) (< x y) #t))
        ((number? y) #f)
        ((symbol? x)
         (if (symbol? y) (symbol<? x y) #t))
        ((symbol? y) #f)
        ((list? x)
         (if (list? y) (list<? x y) #t))
        ((list? y) #f)
        (else
         (error "Unknown expression type -- expr<?" x y))))

(define algebra-1
  (let ((a (match.compile '(? a)))
        (b (match.compile '(? b)))
        (c (match.compile '(? c))))
    `(
      ; Associative law of addition
      ((+ ,a (+ ,b ,c))
       none
       (+ (+ a b) c))
       
      ; Commutative law of multiplication
      ((* ,b ,a)
       (,expr<? a b)
       (* a b))
       
      ; Distributive law of multiplication over addition
      ((* ,a (+ ,b ,c))
       none
       (+ (* a b) (* a c)))
     )))

