;; Scheme subset with LETREC restricted to LAMBDAs only, plus a
;; primitive %UNLESS for IF to expand into.

;; Core syntax:
;; e = v
;;   | (QUOTE constant)
;;   | (LAMBDA (v ...) e)
;;   | (LETREC ((v e) ...) e)
;;   | (e e ...)

(define (interpret e)
  (evaluate (elaborate e) the-global-env '(halt)))

(define (elaborate e) e)                ;XXX

(define (continue k value)
;  (pp (list value k))
  (apply
   (case (car k)
     ((halt)
      (lambda ()
        value))
     ((start-eval-rands)
      (lambda (rands r k)
        (eval-rands rands r '() (list value k))))
     ((eval-rands)
      (lambda (rands r rev-args fk)
        (eval-rands rands r (cons value rev-args) fk)))
     (else (error "Unknown frame type" k)))
   (cdr k)))

(define (eval-rands rands r rev-args fk)
  (if (null? rands)
      (let ((f (car fk))
            (k (cadr fk)))
        (f (reverse rev-args) k))
      (evaluate (car rands) r
                `(eval-rands ,(cdr rands) ,r ,rev-args ,fk))))

(define (evaluate e r k)
  (if (symbol? e)
      (continue k (env-lookup r e))
      (case (car e)
        ((quote)
         (continue k (cadr e)))
        ((lambda)
         (continue k
                   (lambda (arguments k)
                     (evaluate (caddr e)
                               (env-extend r (cadr e) arguments)
                               k))))
        ((letrec)
         (let ((new-r (env-extend-promises r (map car (cadr e)))))
           (for-each (lambda (defn)
                       (env-resolve! new-r
                                     (car defn)
                                     (evaluate (cadr defn) new-r '(halt))))
                     (cadr e))
           (evaluate (caddr e) new-r k)))
        (else
         (evaluate (car e) r `(start-eval-rands ,(cdr e) ,r ,k))))))

(define (env-lookup r v)
  (cond ((assv v r) => cadr)
        (else (error '"Unbound variable" v))))

(define (env-extend r vs values)
  (append (map list vs values) r))

(define (env-extend-promises r vs)
  (env-extend r vs (map (lambda (_) '*uninitialized*) vs)))

(define (env-resolve! r v value)
  (cond ((assv v r) => (lambda (pair)
;;                         (assert (eqv? (cadr pair) '*uninitialized*)
;;                                 "Redefinition" pair)
                         (set-car! (cdr pair) value)))
        (else (error '"Can't happen" v))))

(define (%unless arguments k)
  (let ((test (car arguments))
        (if-no (cadr arguments))
        (if-yes (caddr arguments)))
    ((if test if-yes if-no) '() k)))

(define (true arguments k)  ((car arguments) '() k))
(define (false arguments k) ((cadr arguments) '() k))

(define (make-predicate f)
  (lambda arguments
    (if (apply f arguments) true false)))

(define (make-primitive f)
  (lambda (arguments k)
    (continue k (apply f arguments))))

(define the-global-env
  (cons `(%unless     ,%unless)
        (map (lambda (pair)
               `(,(car pair) ,(make-primitive (cadr pair))))
             `(
               (boolean?    ,(make-predicate boolean?))
               (number?     ,(make-predicate number?))
               (pair?       ,(make-predicate pair?))
               (symbol?     ,(make-predicate symbol?))
               (eqv?        ,(make-predicate eqv?))
               (+           ,+)
               (-           ,-)
               (*           ,*)
               (<           ,(make-predicate <))
               (cons        ,cons)
               (car         ,car)
               (cdr         ,cdr)
               (make-vector ,make-vector)          ;XXX should distinguish procs
               (vector-ref  ,vector-ref)
               (vector-set! ,vector-set!)
               ;; For now:
               (error       ,error)
               (gensym      ,gensym)
               (read        ,read)
               (write       ,write)
               (newline     ,newline)
               ;;    (snarf       ,snarf)
               (pp          ,pp)
                ))))
