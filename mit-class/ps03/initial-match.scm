;; Pattern matching with segment variables.
;; A rewrite of the sample code from problem set 3.


;; Facade

; Return a procedure matching a single item against PATTERN and returning
; the environment of the first match, or #f if none.
(define (matcher pattern)
  (match.maybe (match.compile pattern)))

(define (match.maybe matcher)
  (let ((item-matcher (match.only matcher)))
    ; Return the environment from the first match of MATCHER against ITEM,
    ; or #f if none.
    (lambda (item)
      (item-matcher (list item) '() (lambda (ls r) r)))))

; Return MATCHER restricted to eating the whole input list.
(define (match.only matcher)
  (match.compose matcher match.end))


;; Matcher constructors
;;
;; A matcher is a procedure taking
;;   LS: A list of items; we are to eat some head of this list.
;;   R: An environment (r is short for 'rho').
;;   SUCCEED: A procedure taking the uneaten remainder of LS and an
;;     extension of R, and returning a final value or #f.
;; The matcher returns a final value or #f. It calls SUCCEED for each 
;; way of matching a head of LS in R until SUCCEED returns non-#f.
;;
;; Generally, matching a variable must respect previous bindings; if it
;; can't, the matcher should fail (return #f). Also generally, when a
;; matcher calls on other matchers, the environments compose.
;;
;; N.B. matchers work on lists -- there's no combinator for taking
;; apart a dotted pair. It's an error to use the same name for a segment
;; variable and an element variable, unless you know what you're doing.

; Return a matcher that eats a single item that satisfies OK?.
(define (match.restrict ok?)
  (lambda (ls r succeed)
    (and (pair? ls)
         (ok? (car ls))
         (succeed (cdr ls) r))))

; Return a matcher that eats a single item eqv? to CONSTANT.
(define (match.eqv constant)
  (match.restrict (lambda (item) (eqv? item constant))))

; Return a matcher of an element-variable with the given NAME.
; This eats and binds any single item.
(define (match.element name)
  (lambda (ls r succeed)
    (and (pair? ls)
         (match.fetch r name
           (lambda (value)
             (and (equal? (car ls) value)
                  (succeed (cdr ls) r)))
           (lambda ()
             (succeed (cdr ls)
                      (match.bind r name (car ls))))))))

; Return a matcher of a segment-variable with the given NAME.
; This eats and binds any sequence of initial items.
(define (match.segment name)
  (lambda (ls r succeed)
    (match.fetch r name
      (lambda (value)
        (let comparing ((ls ls) (v value))
          (cond ((null? v) (succeed ls r))
                ((and (pair? ls)
                      (equal? (car ls) (car v)))
                 (comparing (cdr ls) (cdr v)))
                (else #f))))
      (lambda ()
        (let matching ((reversed-head '()) (tail ls))
          (or (succeed tail (match.bind r name (reverse reversed-head)))
              (and (pair? tail)
                   (matching (cons (car tail) reversed-head)
                             (cdr tail)))))))))

; Return a matcher eating a single item, which must be a list matched
; by each of MATCHERS in sequence, with nothing left over.
(define (match.list . matchers)
  (match.nest (foldr match.compose match.end matchers)))

; Return a matcher eating a single item, which must be a list matched
; initially by MATCHER.
(define (match.nest matcher)
  (lambda (ls r succeed)
    (and (pair? ls)
         (matcher (car ls) r
                  (lambda (match-remainder match-r)
                    (succeed (cdr ls) match-r))))))

; Return a matcher eating an initial sequence MATCHER-1 eats, followed
; by a sequence MATCHER-2 eats.
(define (match.compose matcher-1 matcher-2)
  (lambda (ls r succeed)
    (matcher-1 ls r
               (lambda (ls1 r1)
                 (matcher-2 ls1 r1 succeed)))))

; A matcher for the end of a list.
(define match.end
  (lambda (ls r succeed)
    (and (null? ls)
         (succeed ls r))))


;; Environments
;; Using a-lists for visibility.

; Return (SUCCEED value-of-NAME-in-R) or (FAIL).
(define (match.fetch r name succeed fail)
  (cond ((assq name r)
         => (lambda (pair) (succeed (cadr pair))))
        (else (fail))))

; Return R extended with NAME bound to VALUE.
(define (match.bind r name value)
  (cons (list name value) r))


;; Helpers

(define (foldr f id ls)
  (if (null? ls)
      id
      (f (car ls)
         (foldr f id (cdr ls)))))

(define (any f ls)
  (and (pair? ls)
       (or (f (car ls))
           (any f (cdr ls)))))


;; Pattern syntax

(define (match.make-compile make-matcher head-matcher . tail-matchers)
  (let ((tagged? (match.maybe (match.nest head-matcher)))
        (valid? (match.maybe (apply match.list head-matcher tail-matchers))))
    ; Return the matcher PATTERN denotes, or #f if it doesn't have a
    ; list-head matching HEAD-MATCHER.
    (lambda (pattern)
      (and (tagged? pattern)
           (if (valid? pattern)
               (apply make-matcher (cdr pattern))  ; XXX ugh
               (error "Bad pattern syntax" pattern))))))

(define (match.make-compiler . compilers)
  ; Return the matcher PATTERN denotes.
  (define (compile pattern)
    (or (any (lambda (compiler) (compiler pattern))
             compilers)
        (cond ((list? pattern) (apply match.list (map compile pattern)))
              ((pair? pattern) (error "Non-list in pattern" pattern))
              (else (match.eqv pattern)))))
  compile)

(define match.compile
  (match.make-compiler
   (match.make-compile match.element
                       (match.eqv '?) (match.restrict symbol?))
   (match.make-compile match.segment
                       (match.eqv '??) (match.restrict symbol?))
   (match.make-compile match.restrict
                       (match.eqv '?:restrict) (match.restrict symbol?))))


;; Examples

(define (print x)
  (write x)
  (newline))

(print ((matcher '(a ((? b) 2 3) (? b) c))
        '(a (1 2 3) 1 c)))
