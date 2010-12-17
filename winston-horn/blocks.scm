;; Helpers

(define (delq x xs)
  (cond ((null? xs) '())
        ((eq? x (car xs))
         (cdr xs))
        (else (cons (car xs) 
                    (delq x (cdr xs))))))


;; Plan collection

(define *plan* '())

(define (try planning)
  (set! *plan* '())
  (planning)
  (reverse *plan*))

(define (did proc-name . args)
  (set! *plan* (cons (make-step proc-name args) *plan*))
  'ok)

(define (make-step proc-name args)
  (cons proc-name (map (lambda (arg) (arg 'name)) args)))


;; Objects

(define (make-object name a-list)
  (lambda (msg . args)
    (case msg
      ((name) name)
      ((show) (cons name a-list))
      ((get)
       (let ((key (car args)))
         (cond ((assq key a-list) => cadr)
               (else #f))))
      ((set)
       (let ((key (car args))
             (val (cadr args)))
         (cond ((assq key a-list)
                => (lambda (pair)
                     (set-car! (cdr pair) val)))
               (else 
                (set! a-list (cons (list key val) a-list)))))
       'ok)
      (else (error "Unknown message" msg)))))

(define hand (make-object 'hand '()))
(define table (make-object 'table '()))


;; Plan makers

(define (put-on object support)
  (cond ((make-space support object)
         => (lambda (place) (put-at object place)))
        (else #f)))

(define (put-at object place)
  (grasp object)
  (move-object object place)
  (ungrasp object))

(define (grasp object)
  (if (eq? object (hand 'get 'grasping))
      'ok
      (begin
        (if (object 'get 'directly-supports)
            (clear-top object))
        (cond ((hand 'get 'grasping) => get-rid-of))
        (move-hand (top-center object))
        (hand 'set 'grasping object)
        (did 'grasp object))))

(define (move-object object place)
  (remove-support object)
  (move-hand (new-top-center object place))
  (object 'set 'position place)
  (add-support object place)
  (did 'move-object object place))

(define (move-hand position)
  (hand 'set 'position position))

(define (ungrasp object)
  (if (not (object 'get 'supported-by))
      (error "Tried to ungrasp an unsupported object"))
  (hand 'set 'grasping #f)
  (did 'ungrasp object))

(define (get-rid-of object)
  (put-at object (find-space table object)))

(define (clear-top object)
  (for-each get-rid-of
            (or (object 'get 'directly-supports) '())))

(define (remove-support object)
  (let ((support (object 'get 'supported-by)))
    (support 'set 'directly-supports
             (delq object (support 'get 'directly-supports))))
  (object 'set 'supported-by #f))

(define (add-support object place)
  (let ((support (get-object-under place)))
    (if (not (can-support-things? support))
        (error "Can't support things" support))
    (support 'set 'directly-supports
             (cons object (or (support 'get 'directly-supports) '())))
    (object 'set 'supported-by support)))

(define (can-support-things? object)
  (or (eq? object table)
      (memq (object 'get 'type) '(box brick))))

(define (make-space support object)
  (or (find-space support object)
      (begin 
        (get-rid-of (car (support 'get 'directly-supports)))
        (make-space support object))))


;; Fake geometry functions

(define (find-space support object)
  (or (eq? support table)
      ;; XXX should also be able to fail and return #f
      `(space above ,support for ,object)))

(define (get-object-under place)
  (caddr place))

(define (top-center object)
  (list 'top-center object))

; Return the position for OBJECT for its bottom center to be just above
; (TOP-CENTER PLACE).
(define (new-top-center object place)
  (list 'new-top-center object place))
