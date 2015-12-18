(defun barchart-make-bar (length fraction)
  "Return a string of the given length that looks like a
horizontal bar representing a real number between 0 and 1 (the
fraction)."
  (assert (<= 0 fraction 1))
  (apply 'string
         (let ((f (* fraction length)))
           (loop for i from 0 below length
                 collect (let* ((cf (max 0 (min 1 (- f i)))) ; fraction of a character space
                                (ci (round (* 8 cf))))       ; index of the char filling that amount of space
                           (aref barchart--bar-chars ci))))))

;; Character codes from https://en.wikipedia.org/wiki/Block_Elements
(defconst barchart--bar-chars
  [32 #x258f #x258e #x258d #x258c #x258b #x258a #x2589 #x2588])

;; E.g. (barchart-make-bar 10 0.333)
