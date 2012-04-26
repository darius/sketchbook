;; Compiling stream networks by partial evaluation.

;; Things to investigate:
;; How much bigger can the generated code be than the network given
;; to the generator?  Exponentially bigger?

(define (make-literal-feeder string eater)
  (_loop (lambda (again i)
           (_if (_< i (string-length string))
                (eater (_string-ref string i)
                       (lambda () (again (_+ i 1))))))
         0))

(define (make-constant-feeder ch eater)
  (lambda ()
    (_loop (lambda (again)
             (eater ch again)))))

(define (echo c feeder)
  (_begin (_write-char c)
          feeder))

(define (upperize eater)
  (lambda (c feeder)
    (eater (_char-upcase c) feeder)))

(define (duplicate eater1 eater2)
  (lambda (c feeder)
    (eater1 c (lambda ()
                (eater2 c feeder)))))

(define (_if test then)
  `(if ,test ,then))

(define (_begin x y)
  `(begin ,x ,(y)))

(define (_loop f . inits)
  (define vars (map (lambda (x y) y) inits '(v0 v1 v2 v3))) ;FIXME hygiene
  `(let ()
     (define (looping ,@vars)
       ,(apply f (lambda args `(looping ,@args)) vars))
     (looping ,@inits)))

(define (_ name)
  (lambda args
    (cons name args)))

(define _write-char (_ 'write-char))
(define _char-upcase (_ 'char-upcase))
(define _< (_ '<))
(define _+ (_ '+))
(define _string-ref (_ 'string-ref))

(define a (make-constant-feeder #\X echo))

(define p (make-literal-feeder "Hello" (duplicate (upperize echo) echo)))
