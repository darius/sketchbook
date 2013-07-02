;;;  The compiled code jumps to FOUND on match.
found   found
        
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

; Initialization is required to set up the initial lists and start the
; first character.

        zeroes  20-__here__     ; put code at address 20, visually nice
init    smash   ,,nnode        ; nnode->literal = 0

; XCHG is transferred to when the current list is exhausted.  This
; routine copies NLIST onto CLIST, appends a JUMP ,,XCHG instruction,
; gets a new character in r1, and transfers to CLIST.
; The instruction JUMP r2,,CODE is also executed to start a new search of
; the entire regular expression with each character.  Thus the regular
; expression will be found anywhere in the text to be searched.

xchg    aload   r7,,nnode       ; pick up NLIST count
                                ; r7 = nnode[0]
        set     r6              ; pick up CLIST count
                                ; r6 = 0
x1      ifeq    r7,0,x2         ; if x7 == 0 goto x2
        set     r7,r7,-1        ; r7--
        fetch   r3,r7,nlist     ; r3 = nlist[r7]
        store   r3,r6,clist     ; copy NLIST onto CLIST
                                ; clist[r6] = r3
        set     r6,r6,1         ; r6++
        jump    ,,x1
        
x2      fetch   r3,,jumpcmd     ; r3 = jumpcmd[0]
        store   r3,r6,clist     ; put JUMP XCHG at bottom
                                ; clist[r6] = r3
        smash   r6,,cnode       ; initialize CNODE count
                                ; cnode->literal = r7
        smash   ,,nnode         ; initialize NNODE count
                                ; nnode->literal = 0
        getch   r1              ; r1 = get_next_character()
        jump    r2,,code        ; start search
                                ; r2 = PC; goto code
        jump    ,,clist         ; finish search

jumpcmd jump    ,,xchg          ; (constant, not executed)

        zeroes  40-__here__     ; put code at address 40, visually nice
        
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
        set     r7,r7,1         ; r7++
        smash   r7,,nnode       ; increment NLIST count
                                ; nnode->literal = r7
fail    jump    ,r2             ; goto *r2

; FAIL simply returns to the next entry in the current list CLIST.

; A call to CNODE from location x moves the JUMP ,,XCHG instruction down
; one location in CLIST and inserts in its place a JUMP r2,,x+l
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

        store   r3,r7,clist     ; insert new JUMP r2,** instruction
                                ; clist[r7] = r3
        set     r7,r7,1         ; r7++
        smash   r7,,cnode       ; increment CLIST count
                                ; cnode->datum = r7
        jump    ,r4,1           ; return
                                ; goto *(r4+2)

callcmd jump    r2,,0           ; (constant, not executed)
                                ; r2 = PC; goto **

; The routine FOUND is transferred to for each successful match of the
; entire regular expression.  There is a one character delay between
; the end of a successful match and the transfer to FOUND.

; The integer procedure GETCHA (called from XCHG) obtains the next
; character from the text to be searched.  This character is right
; adjusted in r1.  GETCHA must also recognize the end of
; the text and terminate the search.

        zeroes  60-__here__     ; put clist at address 60, visually nice
clist   zeroes  20
nlist   zeroes  20
