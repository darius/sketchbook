;; Pattern matching with segment variables.


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

; A matcher that always fails.
(define match.fail
  (lambda (ls r succeed)
    #f))

; A matcher that always succeeds, eating nothing.
(define match.succeed
  (lambda (ls r succeed)
    (succeed ls r)))

; Return a matcher that eats a single item that satisfies OK?.
(define (match.restrict ok?)
  (lambda (ls r succeed)
    (and (pair? ls)
         (ok? (car ls))
         (succeed (cdr ls) r))))

; Return a matcher that eats a single item eqv? to CONSTANT.
(define (match.eqv constant)
  (match.restrict (lambda (item) (eqv? item constant))))

; Return a matcher that eats nothing, but checks that NAME is bound to
; a value satisfying OK?.
(define (match.restrict-variable name ok?)
  (lambda (ls r succeed)
    (match.fetch r name
      (lambda (value)
        (and (ok? value)
             (succeed ls r)))
      (lambda ()
        (error "Unbound name in match.restrict-variable" name)))))

; Return an element-matcher with a restriction.
(define (match.restrict-element name ok?)
  (match.compose (match.element name)
                 (match.restrict-variable name ok?)))

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
    (and (list? ls)
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
                                  (cdr tail))))))))))

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

; Return a matcher that succeeds for each way one of MATCHERS can succeed.
(define (match.choice . matchers)
  (foldr match.binary-choice match.fail matchers))

; Return a matcher that tries MATCHER-1 and then backtracks to MATCHER-2.
(define (match.binary-choice matcher-1 matcher-2)
  (if (eq? matcher-2 match.fail)   ; an optimization
      matcher-1
      (lambda (ls r succeed)
        (or (matcher-1 ls r succeed)
            (matcher-2 ls r succeed)))))


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

(define (some f ls)
  (and (pair? ls)
       (or (f (car ls))
           (some f (cdr ls)))))


;; Pattern syntax

(define (match.make-compiler compilers)
  ; Return the matcher PATTERN denotes.
  (lambda (pattern)
    (or (some (lambda (compiler) (compiler pattern))
              compilers)
        (error "Bad pattern syntax" pattern))))

(define (match.make-ruleoid patternoid actionoid)
  (define (parse patternoid)
    (cond ((procedure? patternoid) patternoid)
          ((pair? patternoid) (apply match.list (map parse patternoid)))
          (else (match.eqv patternoid))))
  (match.make-rule (parse patternoid) (car actionoid) (cdr actionoid)))

(define (match.make-rule matcher procedure template)
  (let ((match (match.maybe matcher)))
    (lambda (subject)
      (cond ((match subject)
             => (lambda (r)
                  (apply procedure (match.instantiate r template))))
            (else #f)))))

(define (match.instantiate r x)
  (cond ((pair? x) (cons (match.instantiate r (car x))
                         (match.instantiate r (cdr x))))
        ((symbol? x) (match.fetch r x
                       (lambda (value) value)
                       (lambda () x)))
        (else x)))

(define (match.ill-formed . expression)
  (error "Ill formed pattern" expression))

(define match.compile
  (match.make-compiler
   (let ((name      (match.restrict-element 'name symbol?))
         (procedure (match.restrict-element 'procedure procedure?))
         (??items   (match.segment '??items))
         (atom      (match.restrict-element 'atom (lambda (x) (not (pair? x))))))
     (define (recurse-for constructor)
       (lambda (patterns)
         (apply constructor (map match.compile patterns))))
     (map (lambda (r) (match.make-ruleoid (car r) (cadr r)))
          `(((? ,name)             (,match.element name))
            ((? ,procedure)        (,match.restrict procedure))
            ((? ,name ,procedure)  (,match.restrict-element name procedure))
            ((? ,??items)          (,match.ill-formed ? ??items))
            ((?? ,name)            (,match.segment name))
            ((?? ,??items)         (,match.ill-formed ?? ??items))
            ((?:choice ,??items)   (,(recurse-for match.choice) ??items))
            ; A procedure is taken as a literal matcher object:
            (,procedure            (,(lambda (x) x) procedure))
            (,atom                 (,match.eqv atom))
            (,(match.list ??items) (,(recurse-for match.list) ??items)))))))


;; Examples

(define (print x)
  (write x)
  (newline))

(print ((matcher '(a ((? b) 2 3) (? b) c))
        '(a (1 2 3) 1 c)))

(print ((matcher '(a (?? x) (?? x) z))
        '(a b c d b c d z)))

(print ((matcher `(? ,number?))
        42))

(print ((matcher `(? ,number?))
        'forty-two))

(print ((matcher `(1 2 (? a ,symbol?) 4))
        '(1 2 3 4)))

(print ((matcher `(1 2 (? a ,symbol?) 4))
        '(1 2 three 4)))

(print ((matcher `(1 2 (?:choice (? ,symbol?) (?? x)) 4))
        '(1 2 3 4 5 4)))

; The main way this is more awkward than that ?:pletrec syntax is the
; need to eta-expand the recursive refs. I'd introduce a macro or two
; if a need for this comes up much. (One for eta-expand and one for
; pattern-letrec.)
(define match-odd-even
  (let ()
    (define odd-even-etc
      (match.compile `(?:choice () (1 ,(lambda (ls r succeed)
                                         (even-odd-etc ls r succeed))))))
    (define even-odd-etc
      (match.compile `(?:choice () (2 ,(lambda (ls r succeed)
                                         (odd-even-etc ls r succeed))))))
    odd-even-etc))

(print ((match.maybe match-odd-even)
        '(1 (2 (1 ())))))
