;;; The simplest nontrivial Thompson-like runtime.
;;; There's no `fork`, so we can only find a single literal string.
;;; But we find it without backtracking, and our patterns are
;;; represented as machine code. The states are addresses in the
;;; pattern's code (Thompson's states were jump instructions into
;;; the pattern's code).
;;; Another difference: Thompson mostly didn't allocate registers
;;; globally (using self-modifying code to hold some of the pointers)
;;; and copied the next-states array istead of swapping pointers.

; r1    current character
; r2    scratch

; r4    start of current states array

; r6    start of next states array
; r7    end of next states array
; r8    pointer into current states
; r9    return into code

; Set up the initial states arrays.
start   set     r4,,states1
        set     r6,,states2
        set     r7,,states2
                
; Advance to the next character of input, swapping the state-array
; pointers. The next-states first needs its terminator added.
advance set     r2,,advance
        store   r2,r7           ; terminate the next-states array
        set     r7,r4           ; empty the new next-states
        set     r4,r6           ; new current = old next states
        set     r6,r7           ; new next = old current states
        getch   r1
        set     r8,r4           ; next current state = the first one
        jump    ,,code     ; but start at `code`, an implicit current state
        
; Append r9 to the next-states array, and continue to the next current state.
next    store   r9,r7
        set     r7,r7,1
        
; Continue to the next current state.
fail    fetch   r2,r8
        set     r8,r8,1
        jump    ,r2

; A states array will have addresses of instructions in `code`,
; terminated by the address `advance`. The two arrays serve for the current
; and next states-sets, with the roles getting swapped each time around.
        zeroes  20-__here__
states1 zeroes  20             ; or properly maxnstates+1
states2 zeroes  20

; The compiled code

code    ifne    r1,'C',fail
        jump    r9,,next
        ifne    r1,'A',fail
        jump    r9,,next
        ifne    r1,'T',fail
        found

;; Instructions used: 8 of 'em
;; found, getch
;; != 
;; jump/call
;; =
;; from, to
