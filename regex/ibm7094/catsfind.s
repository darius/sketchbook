;;; A Thompson-like runtime.
;;; Our patterns are represented as machine code. The states are addresses
;;; in the pattern's code (Thompson's states were jump instructions into
;;; the pattern's code).
;;; Another difference: Thompson mostly didn't allocate registers
;;; globally (using self-modifying code to hold some of the pointers)
;;; and copied the next-states array istead of swapping pointers.

; r1    ch       current character
; r2    scratch

; r4    cur_lo   start of current states array
; r5    cur_hi   end of current states array (points to terminator)
; r6    next_lo  start of next states array
; r7    next_hi  end of next states array
; r8    state    pointer into current states
; r9             return address into code

; Point to the states arrays.
start   set     r4,,states1
        set     r5,r4
        set     r6,,states2
        set     r7,r6
                
; Advance to the next character of input, swapping the state-arrays.
advance set     r2,,advance
        store   r2,r7           ; terminate the old next-states array
        set     r5,r7           ; 
        set     r7,r4           ; empty the new next-states
        set     r4,r6           ; new current = old next states
        set     r6,r7           ; new next = old current states
        getch   r1
        set     r8,r4           ; next current state = the first one
        jump    ,,code     ; but start at `code`, an implicit current state
        
        zeroes  20-__here__
	
; Append r9 to the next-states array, and continue to the next current state.
next    store   r9,r7
        set     r7,r7,1
        
; Continue to the next current state.
fail    fetch   r2,r8
        set     r8,r8,1
        jump    ,r2

; Append r9 to the current states, and return to the instruction
; following code_cont.
fork    store   r9,r5
        set     r5,r5,1
        set     r2,,advance
        store   r2,r5
        jump    ,r9,1

; A states array will have addresses of instructions in `code`,
; terminated by the address `advance`. The two arrays serve for the current
; and next states-sets, with the roles getting swapped each time around.
        zeroes  40-__here__
states1 zeroes  20             ; or properly maxnstates+1
states2 zeroes  20

; The compiled code

code    jump    r9,,fork
        jump    ,,dog
        ifne    r1,'C',fail
        jump    r9,,next
        ifne    r1,'A',fail
        jump    r9,,next
        ifne    r1,'T',fail
        found
dog     ifne    r1,'D',fail
        jump    r9,,next
        ifne    r1,'O',fail
        jump    r9,,next
        ifne    r1,'G',fail
        found
