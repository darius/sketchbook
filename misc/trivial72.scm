;; A (very slightly) Smalltalk-72-like open interpreter.
;; I think the key thing still to do is this:
;; In an expression like (1 + (t length)) I have to parenthesize
;; the (t length), where Smalltalk-72 would have (1 + t length).
;; Here's how I think that's supposed to work:
;; The object bound to t looks for a message in "... length",
;; and eats it if it finds it, but if it doesn't find a message
;; it understands, it leaves the tail alone and returns itself.
;; So:
;; 1. Don't raise an error if you see no message you understand.
;;    (Expect debugging troubles from this.)
;; 2. Make the message frames mutable?
;;    *Probably* easier to implement that way.


;; Example programs in the language:

(define (a0) (run '(#t >> 42 137)))
(define (a1) (run '(#f >> 42 137)))
(define (a2) (run '(2 + 3)))

(define (b0) (run '((: $) 42)))
(define (b1) (run '((: ($)) 42)))

(define (c0) (run '((: 5 + $) 67)))
(define (c1) (run '((: $ + $) 5 67)))

(define (d0) (run '((: % length) length)))
(define (d1) (run '((: % length) not-length)))
(define (d2) (run '((: % length >> 0) length)))

(define (t4) (run '((: $ length) (: % length >> 42))))

(define eg-empty
  '(
    let empty (: % length >> 10)
    empty length + 1
    ))
(define eg-pair-0
  '(
    let empty (: % length >> 0)
    let pair
       (: let t $
          : % length >> (1 + (t length)))
    (pair empty) length
    ))
;; Here's the only 'real' example:
;; Define constructors equivalent to Lisp's NIL and CONS,
;; plus CAR, CDR, LENGTH methods. (Actually HD and TL.)
(define eg-pair-1
  '(
    let empty (: % length >> 10)
    let pair
       (: let h $
          let t $
          : % hd     >> h
            % tl     >> t
            % length >> (t length + 1))
    (pair 1 (pair 2 empty)) length
    ))

(define (e0) (run eg-empty))
(define (e1) (run eg-pair-0))
(define (e2) (run eg-pair-1))

(define (run e)
  (terp e '() '(halt)))

(define (print x)
  (write x)
  (newline))

(define (trace x) 'ok)


;; OK, now to implement it.

(define (terp e r k)
  (trace `(terp ,e ,r ,k))
  (cond ((pair? e)
         (case (car e)
           ((%) (terp-% (cadr e) (nest (cddr e) r k)))
           ((:) (terp-: (cdr e) r k))
           ((let) (terp-let (cadr e) (caddr e) (cdddr e) r k))
           (else (terp (car e) r
                       (nest (cdr e) r k)))))
        ((eq? e '$) (prim-$ k))
        ((symbol? e) (return k (lookup r e)))
        ((null? e) (error))
        (else (return k e))))

(define (terp-let variable val-e e r k)
  (terp val-e r (list 'let variable e r k)))

(define (nest e r k)
  (if (null? e) k (list 'nest e r k)))

(define (make-message e r k)
  ;; XXX null message probably should be kept instead
  ;; e.g. so you'd get an error on too many $'s
  (if (null? e) k (list 'message e r k)))

(define (return k value)
  (case (car k)
    ((nest message)
     (send value k))
    ((let)
     (unpack k (lambda (variable e2 r2 k2)
                 (terp e2 (cons (list variable value) r2) k2))))
    ((number-+)
     (unpack k (lambda (self k2)
                 (return k2 (+ self value)))))
    ((halt)
     value)
    (else (error))))

(define (send object k)
  (let ((k (to-message k)))
    (trace `(send ,object ,k))
    (cond ((number? object)  (send-number object k))
          ((boolean? object) (send-boolean object k))
          ((definition? object)
           (terp (cadr object) (caddr object) k))
          (else (error)))))

(define (to-message k)
  (case (car k)
    ((nest) (cons 'message (cdr k)))
    ((message) k)                       ;I guess?
    (else (error))))

(define (terp-: e r k)
  (return k (make-definition e r)))

(define (prim-$ k)
  (extract-message k (lambda (replace e2 r2 k2)
                       (terp (car e2) r2
                             (replace (make-message (cdr e2) r2 k2))))))

(define (terp-% pattern k)
  (trace `(terp-% (pattern: ,pattern) (k: ,k)))
  (extract-message k (lambda (replace e2 r2 k2)
                       (if (equal? pattern (car e2))
                           (answer #t (replace (make-message (cdr e2) r2 k2)))
                           (answer #f k)))))

(define (extract-message k take-message)
  (let walk ((k k)
             (replace (lambda (k-prime) k-prime)))
    (case (car k)
      ((message)
       (unpack k (lambda (e2 r2 k2)
                   (take-message replace e2 r2 k2))))
      (else
       (walk (last k) (lambda (k-prime)
                        (append (butlast k) (list k-prime))))))))

(define (last xs) (car (last-pair xs)))
(define (butlast xs)
  (if (null? (cdr xs))
      '()
      (cons (car xs) (butlast (cdr xs)))))

(define (answer value k) (return k value))

(define (send-number self k)
  (case (car k)
    ((message)
     (unpack k (lambda (e2 r2 k2)
                 (case (car e2)
                   ((+)
                    (terp (cadr e2) r2 
                          (list 'number-+ self (nest (cddr e2) r2 k2))))
                   (else (error))))))
    (else (error))))
  
(define (send-boolean self k)
  (case (car k)
    ((message)
     (unpack k (lambda (e2 r2 k2)
                 (case (car e2)
                   ((>>) (terp ((if self cadr cddr) e2) r2 k2))
                   (else (error))))))
    (else (error))))
  
(define (make-definition e r)
  (list tag-definition e r))
  
(define (definition? object)
  (and (pair? object) (eq? (car object) tag-definition)))

(define tag-definition (list 'definition))

(define (lookup r name)
  (cond ((assq name r) => cadr)
        (else (error))))

(define (unpack k cont)
  (apply cont (cdr k)))
