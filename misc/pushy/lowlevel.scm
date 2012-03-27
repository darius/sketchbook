;; Low-level Pushy streams.
;; http://cap-lore.com/code/Streams/Pushy.html

(define memory (make-vector 12 0))

(define (fetch x offset)
  (vector-ref memory (+ x offset)))

(define (store x offset value)
  (vector-set! memory (+ x offset) value))

(define start '*)
(define (build . slot-values)
  (let loop ((sv slot-values))
    (cond ((not (null? sv))
           (loop (cdr sv))
           (set! start (- start 1))
           (store start 0 (car sv)))))
  start)

(define (sample)
  (set! start (vector-length memory))
  (build-literal-stream
   "Hi there, my name is Darius." 
   (build-upperize 
    (build-stutter
     (build-echo))))
  (dispatch 'ignore 'ignore start))

(define (print x) (write x) (newline))

(define counter 0)
(define (exhausted?)
  (set! counter (+ counter 1))
  (= counter 40))

(define (downstream a b x)
  (dispatch a b (fetch x 1)))

(define (dispatch a b x)
;  (or (exhausted?)
;      (begin
;       (print `(,(fetch x 0) ,a ,b ,x))
       ((fetch x 0) a b x))
;       ))

(define (build-literal-stream string downstream-node)
  (build do-literal downstream-node 0 string))

(define (do-literal a b x)
  (cond ((< (fetch x 2) (string-length (fetch x 3)))
         (set! a (string-ref (fetch x 3) (fetch x 2)))
         (store x 2 (+ (fetch x 2) 1))
         (downstream a x x))))

(define (build-stream-of-as downstream-node)
  (build do-stream-of-as downstream-node))

(define (do-stream-of-as a b x)
  (downstream #\a x x))

(define (build-upperize downstream-node)
  (build do-upperize downstream-node))

(define (do-upperize a b x)
  (if (char-lower-case? a)
      (set! a (char-upcase a)))
  (downstream a b x))

(define (build-echo)
  (build do-echo))

(define (do-echo a b x)
  (write-char a)
  (dispatch a b b))

(define (build-discard)
  (build do-discard))

(define (do-discard a b x)
  (dispatch a x x))

(define (build-stutter downstream-node)
  (build do-stutter1
         downstream-node
         '-char-to-repeat-slot-
         '-promise-for-remainder-slot-
         do-stutter2))

(define (do-stutter1 a b x)
  (store x 3 b)
  (set! b (+ x 4))
  (store x 2 a)
  (downstream a b x))

(define (do-stutter2 a b x)
  (set! x (- x 4))
  (downstream (fetch x 2) (fetch x 3) x))

(define (build-duplicate downstream1-node downstream2-node)
  (build do-duplicate1
         downstream1-node
         downstream2-node
         '-char-to-dup-slot-
         '-promise-for-remainder-slot-
         do-duplicate2))

(define (do-duplicate1 a b x)
  (store x 4 b)
  (set! b (+ x 5))
  (store x 3 a)
  (downstream a b x))

(define (do-duplicate2 a b x)
  (set! x (- x 5))
  (dispatch (fetch x 3) (fetch x 4) (fetch x 2)))

(define (build-discard-xs downstream-node)
  (build do-discard-xs downstream-node))

(define (do-discard-xs a b x)
  (if (eqv? a #\x)
      (dispatch a b b)
      (downstream a b x)))

(define (build-merge pull-node downstream-node)
  (build do-merge downstream-node pull-node))

(define (do-merge a b x)
  (let ((new-b (fetch x 2)))
    (store x 2 b)
    (downstream a new-b x)))
