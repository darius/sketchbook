;; A Schemier version of push-driven streams.
;; http://cap-lore.com/code/Streams/

;; Things to investigate:

;; Do dags or cyclic graphs make any sense?  Would a nonreentrant,
;; static-allocating version of DUPLICATE or LITERAL-FEEDER ever be a
;; problem?

;; Under what most general circumstances can we static-allocate the
;; continuations?

;; Can you do the equivalent of MERGE in a purely functional way?

;; Corresponding design for demand-driven dataflow.  Is that just
;; SICP streams?  No, I think the difference is the network being
;; 'wired up' statically before processing starts.

;; Look up how Synthesis did I/O.


(define (sample-run)
  ((make-literal-feeder "Hi, my name is Darius."
                        (upperize (stutter echo)))))

;; Exponential slowdown in the 'obvious' version of DUPLICATE?
;; Yup, try it:
(define (bug)
  (define (duplicate eater1 eater2)
    (lambda (c feeder)
      (eater1 c feeder)
      (eater2 c feeder)))
  ((make-literal-feeder "abcd" (duplicate echo echo))))


;; Feeder builders
;; A feeder takes no arguments, and calls an eater with something to
;; eat.

(define (make-constant-feeder ch eater)
  (define (constant-feeder)
    (eater ch constant-feeder))
  constant-feeder)

(define (make-literal-feeder string eater)
  (let loop ((i 0))
    (lambda ()
      (if (< i (string-length string))
          (eater (string-ref string i) (loop (+ i 1)))))))


;; Eaters
;; An eater takes a character and a feeder (which normally represents
;; the rest of the stream), and does something with them.

(define (echo c feeder)
  (write-char c)
  (feeder))

(define (upperize eater)
  (lambda (c feeder)
    (eater (char-upcase c) feeder)))

(define (discard c feeder)
  (feeder))

(define (stutter eater)
  (duplicate eater eater))

(define (discard-xs eater)
  (lambda (c feeder)
    (if (char=? c #\x)
        (feeder)
        (eater c feeder))))

(define (duplicate eater1 eater2)
  (lambda (c feeder)
    (eater1 c (lambda ()
                (eater2 c feeder)))))

(define (merge other-feeder eater)
  (lambda (c feeder)
    (let ((f other-feeder))
      (set! other-feeder feeder)
      (eater c f))))
