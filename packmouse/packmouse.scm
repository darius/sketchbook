;; Conventions:
;;   p - a PE
;;   ls - a list of items to parse (typically characters)

; Return true iff P eats all of STRING.
(define (peg.eats? p string)
  (not (not ((peg.only p) (string->list string)))))


; The basic PEG combinators
; When a PEG is applied to some input, it either fails (returning #f), 
; or succeeds and eats some head of the input (returning the remainder).
; Below, when we say that a PEG is to eat something, it's implicit that
; it may fail. Each PEG can succeed on a particular input at most once;
; there's no deeper backtracking as in Prolog or Icon.

; Eat one item, provided it satisfies OK?.
(define (peg.eat ok?)
  (lambda (ls)
    (and (pair? ls)
         (ok? (car ls))
         (cdr ls))))

; Have P2 eat P1's leftovers.
(define (peg.compose p1 p2)
  (lambda (ls)
    (cond ((p1 ls) => p2)
          (else #f))))

; Eat what P1 eats, unless it fails; then eat as P2 instead.
(define (peg.either p1 p2)
  (lambda (ls)
    (or (p1 ls) (p2 ls))))

; Eat the empty string if P fails.
(define (peg.not p)
  (lambda (ls)
    (if (p ls) #f ls)))

; (THUNK), but delayed (for recursive grammars).
(define (peg.delay thunk)
  (lambda (ls) ((thunk) ls)))


; Convenience PEG combinators

(define peg.any (peg.eat (lambda (char) #t)))

; Eat nothing, but only at the end of input.
(define peg.end (peg.not peg.any))

; Always fail.
(define peg.fail (peg.eat (lambda (c) #f)))

; Always succeed, eating nothing.
(define peg.empty (peg.not peg.fail))

(define (peg.lookahead p)
  (peg.not (peg.not p)))

(define (peg.only p)
  (peg.compose p peg.end))

(define (peg.sequence ps)
  (foldr peg.compose peg.empty ps))

(define (peg.choice ps)
  (foldr peg.either peg.fail ps))

(define (peg.optional p)
  (peg.either p peg.empty))

; Compose P zero or more times, as many as possible.
; XXX loops if P matches empty
(define (peg.zero-or-more p)
  (define p*
    (peg.optional (peg.compose p (peg.delay (lambda () p*)))))
  p*)

(define (peg.one-or-more p)
  (peg.compose p (peg.zero-or-more p)))

(define (peg.char char)
  (peg.eat (lambda (char1) (char=? char char1))))

(define (peg.string string)
  (peg.sequence (map peg.char (string->list string))))

(define (peg.char-class string)
  (peg.choice (map peg.char (string->list string))))

(define (peg.char-range lo hi)
  (peg.eat (lambda (char)
             (and (char<=? lo char) (char<=? char hi)))))


;; Helpers

(define (foldr f id ls)
  (if (null? ls)
      id
      (f (car ls)
         (foldr f id (cdr ls)))))


;; A conventional syntax

(define peg.grammar
  (let ()

    (define c peg.char)
    (define s peg.string)
    
    (define * peg.zero-or-more)
    (define + peg.one-or-more)
    (define ? peg.optional)
    (define ! peg.not)
    
    (define (seq . ps) (peg.sequence ps))
    (define (/ . ps)   (peg.choice ps))
    
    (define <peg> '*promise*)
    (define peg (peg.delay (lambda () <peg>)))
    
    (let*
        ((comment         (seq (c #\#)
                               (* (seq (! (c #\newline)) peg.any))))
         (white-char      (peg.char-class " \t\r\n\f"))
         (whitespace      (* (/ white-char comment)))

         (t (lambda (string)
              (peg.compose (peg.string string) whitespace)))

         (alpha           (/ (peg.char-range #\A #\Z)
                             (peg.char-range #\a #\z)
                             (c #\_)))
         (alphanum        (/ alpha (peg.char-range #\0 #\9)))

         (name            (seq alpha
                               (* alphanum)
                               whitespace))

         (lit-char-class  (/ (seq (c #\\) peg.any)
                             (seq (! (c #\])) peg.any)))
         (quoted-char     (/ (seq (c #\\) peg.any)
                             (seq (! (c #\')) peg.any)))
         (dquoted-char    (/ (seq (c #\\) peg.any)
                             (seq (! (c #\")) peg.any)))  ;"
         (char-class      (seq lit-char-class
                               (? (seq (c #\-) lit-char-class))))

         (primary         (/ (seq (t "(") peg (t ")"))
                             (seq (c #\[) (* char-class) (t "]"))
                             (seq (c #\") (* dquoted-char) (t "\""))
                             (seq (c #\') (* quoted-char) (t "'"))
                             name
                             (t "$")))

         (factor          (/ (seq (t "&") primary)
                             (seq (t "!") primary)
                             (seq primary (t "*"))
                             (seq primary (t "+"))
                             (seq primary (t "?"))
                             primary))

         (term            (+ factor))

         (rule            (seq name (t "=") peg (t ".")))

         (grammar         (seq whitespace (+ rule))))
    
      (set! <peg>         (seq term (* (seq (t "/") term))))

      grammar)))


; Test it

(define (snarf-to-string filename)
  (list->string (snarf-chars filename)))

(define (snarf-chars filename)
  (call-with-input-file filename
    (lambda (in)
      (let reading ()
        (let ((c (read-char in)))
          (if (eof-object? c)
              '()
              (cons c (reading))))))))

(define unparsed-grammar (snarf-to-string "peg.peg"))

(define (try)
  (peg.eats? peg.grammar unparsed-grammar))
