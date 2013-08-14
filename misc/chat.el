;; Let's make something like Unix talk.

(defun chat (you me)
  (interactive "sChat with: \nsAs: \n")
  (let ((you-buf (concat "from " you))
        (you-fifo (concat "/tmp/" you)))
    (call-process "mkfifo" nil nil nil you-fifo)
    (call-process "chmod" nil nil nil "a+w" you-fifo)
    (start-process "tail-f" you-buf "tail" "-f" you-fifo)
    (switch-to-buffer you-buf))
  (let ((me-buf (get-buffer-create (concat "to " you)))
        (me-fifo (concat "/tmp/" me)))
    (call-process "mkfifo" nil nil nil me-fifo)
    (call-process "chmod" nil nil nil "a+r" me-fifo)
    (switch-to-buffer-other-window me-buf)
    (make-local-hook 'after-change-functions)
    (add-hook 'after-change-functions
              `(lambda (begin end length)
                 (chat-send ,me-fifo begin end length))
              nil
              t)))

(defun chat-send (fifo begin end length)
  (write-region begin end fifo))

;; TO DO:
;; only seeing comms one way?!
;; permission problems depending on who creates the files?
;; rm fifos when done with them
