# During execution of the code produced by the compiler, two lists
# (named CLIST and NLIST) are maintained by the subroutines CNODE and
# NNODE.  CLIST contains a list of TSX **,2 instructions terminated by
# a TRA XCHG.  Each TSX represents a partial match of the regular
# expression and the TRA XCHG represents the end of the list of
# possible matches.

# A call to CNODE from location x moves the TRA XCHG instruction down
# one location in CLIST and inserts in its place a TSX x+l,2
# instruction.  Control is then returned to x+2.  This effectively
# branches the current search path.  The path at x+1 is deferred until
# later while the branch at x+2 is searched immediately.

cnode   axc     **, 7           CLIST count
        cal     clist, 7
        slw     clist+1, 7      move TRA XCHG instruction
        pca     ,4
        acl     tsxcmd
        slw     clist, 7        insert new TSX **,2 instruction
        txi     *+1, 7, -1
        sca     cnode, 7        increment CLIST count
        tra     2, 4            return
*
tsxcmd  tsx     1, 2            constant, not executed

# The subroutine NNODE is called after a successful match of the
# current character.  This routine, when called from location x,
# places a TSX x+l,2 in NLIST.  It then returns to the next
# instruction in CLIST.  This sets up the place in CODE to be executed
# with the next character.

nnode   axc     **, 7           NLIST count
        pca     ,4
        acl     tsxcmd
        slw     nlist, 7        place new TSX **,2 instruction
        txi     *+1, 7, -1
        sca     nnode, 7        increment NLIST count
        tra     1, 2

# FAIL simply returns to the next entry in the current list CLIST.

fail    tra     1, 2

# XCHG is transferred to when the current list is exhausted.  This
# routine copies NLIST onto CLIST, appends a TRA XCHG instruction,
# gets a new character in index register one, and transfers to CLIST.
# The instruction TSX CODE,2 is also executed to start a new search of
# the entire regular expression with each character.  Thus the regular
# expression will be found anywhere in the text to be searched.
# Variations can be easily incorporated.

xchg    lac     nnode, 7        pick up NLIST count
        axc     0, 6            pick up CLIST count
x1      txl     x2, 7, 0
        txi     *+1, 7, 1
        cal     nlist, 7
        slw     clist, 6        copy NLIST onto CLIST
        txi     x1, 6, -1
x2      cla     tracmd
        slw     clist, 6        put TRA XCHG at bottom
        sca     cnode, 6        initialize CNODE count
        sca     nnode, 0        initialize NNODE count
        tsx     getcha, 4
        pac     ,1              get next character
        tsx     code, 2         start search
        tra     clist           finish search
*
tracmd  tra     xchg            constant, not executed

# Initialization is required to set up the initial lists and start the
# first character.

init    sca     nnode, 0
        tra     xchg

# The routine FOUND is transferred to for each successful match of the
# entire regular expression.  There is a one character delay between
# the end of a successful match and the transfer to FOUND.

# The integer procedure GETCHA (called from XCHG) obtains the next
# character from the text to be searched.  This character is right
# adjusted in the accumulator.  GETCHA must also recognize the end of
# the text and terminate the search.
