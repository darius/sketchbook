;;; instructions: 
;;; fetch store unsmash smash    XXX rename smashes
;;; set add
;;; jump trap
;;; ifeq ifne

;;; display format for next-gen instructions:
;;;   aa load r r aa
;;; (address: mnemonic reg reg/char address)
;;; 14 columns, or 15 counting another space after
;;; so you could have 5 columns of these instructions in 74-char display
;;; * 20 lines for 100 addresses total
;;; the runtime is about 40 instructions, so 2 columns
;;; one more each for compiled code, CLIST, NLIST?
        
;;; r1: current character from input
;;; r2: call address from a CLIST instruction
;;; r4: call address from a CODE instruction
;;; r6: (local) index into CLIST
;;; r7: (local) CLIST or NLIST size
;;; r3, r5: (local) scratch
        
; During execution of the code produced by the compiler, two lists
; (named CLIST and NLIST) are maintained by the subroutines CNODE and
; NNODE.  CLIST contains a list of TSX **,2 instructions terminated by
; a TRA XCHG.  Each TSX represents a partial match of the regular
; expression and the TRA XCHG represents the end of the list of
; possible matches.

; A call to CNODE from location x moves the TRA XCHG instruction down
; one location in CLIST and inserts in its place a TSX x+l,2
; instruction.  Control is then returned to x+2.  This effectively
; branches the current search path.  The path at x+1 is deferred until
; later while the branch at x+2 is searched immediately.

cnode   set     r7              ; CLIST count
                                ; r7 = clist_count (filled in with smash)
        fetch   r3,r7,clist     ; r3 = clist[r7]
        store   r3,r7,clist+1   ; clist[1+r7] = r3
        set     r3,r4           ; r3 = r4

        fetch   r5,,callcmd
        add     r3,r5           ; r3 += callcmd[0]

        store   r3,r7,clist     ; insert new CALL r2,** instruction
                                ; clist[r7] = r3
        add     r7,r7,1         ; r7++
        smash   r7,,cnode       ; increment CLIST count
                                ; cnode->datum = r7
        jump    ,r4,2           ; return
                                ; goto *(r4+2)

callcmd jump    r2,,0           ; (constant, not executed)
                                ; r2 = PC; goto **

; The subroutine NNODE is called after a successful match of the
; current character.  This routine, when called from location x,
; places a JUMP r2,,x+l in NLIST.  It then returns to the next
; instruction in CLIST.  This sets up the place in CODE to be executed
; with the next character.

nnode   set     r7,,0           ; NLIST count
        set     r3,r4           ; r3 = r4
        fetch   r5,,callcmd
        add     r3,r5           ; r3 += callcmd[0]
        store   r3,r7,nlist     ; place new TSX **,2 instruction
                                ; nlist[r7] = r3
        add     r7,r7,1         ; r7++
        smash   r7,,nnode       ; increment NLIST count
                                ; nnode->literal = r7
        jump    ,r2,1           ; goto *(r2+1)

; FAIL simply returns to the next entry in the current list CLIST.

fail    jump    ,r2,1

; XCHG is transferred to when the current list is exhausted.  This
; routine copies NLIST onto CLIST, appends a TRA XCHG instruction,
; gets a new character in index register one, and transfers to CLIST.
; The instruction TSX CODE,2 is also executed to start a new search of
; the entire regular expression with each character.  Thus the regular
; expression will be found anywhere in the text to be searched.
; Variations can be easily incorporated.

xchg    fetch   r7,,nnode       ; pick up NLIST count
                                ; r7 = nnode[0]
        set     r6              ; pick up CLIST count
                                ; r6 = 0
x1      ifeq    r7              ; if x7 == 0 goto x2
        jump    ,,x2
        add     r7,r7,-1        ; r7--
        fetch   r3,r7,nlist     ; r3 = nlist[r7]
        store   r3,r6,clist     ; copy NLIST onto CLIST
                                ; clist[r6] = r3
        add     r6,r6,1         ; r6++
        jump    ,,x1
        
x2      fetch   r3,,jumpcmd     ; r3 = jumpcmd[0]
        store   r3,r6,clist     ; put JUMP XCHG at bottom
                                ; clist[r6] = r3
        smash   r7,,cnode       ; initialize CNODE count
                                ; cnode->literal = r7
        smash   ,,nnode         ; initialize NNODE count
                                ; nnode->literal = 0
        getch                   ; r1 = get_next_character()
        jump    r2,,code        ; start search
                                ; r2 = PC; goto code
        jump    ,,clist         ; finish search

jumpcmd jump    ,,xchg          ; (constant, not executed)

; Initialization is required to set up the initial lists and start the
; first character.

init    smash   ,,nnode        ; nnode->literal = 0
        jump    ,,xchg

; The routine FOUND is transferred to for each successful match of the
; entire regular expression.  There is a one character delay between
; the end of a successful match and the transfer to FOUND.

; The integer procedure GETCHA (called from XCHG) obtains the next
; character from the text to be searched.  This character is right
; adjusted in r1.  GETCHA must also recognize the end of
; the text and terminate the search.

code
        noop
        ifne    r1,'A',fail
        jump    r4,,nnode
        noop
        ifne    r1,'B',fail
        jump    r4,,nnode
        found

        zeroes  60-__here__     ; put clist at address 60, visually nice
clist   zeroes  20
nlist   zeroes  20
