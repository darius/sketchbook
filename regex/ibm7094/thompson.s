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

nnode   axc     **, 7           NLIST count
        pca     ,4
        acl     tsxcmd
        slw     nlist, 7        place new TSX **,2 instruction
        txi     *+1, 7, -1
        sca     nnode, 7        increment NLIST count
        tra     1, 2

fail    tra     1, 2

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

init    sca     nnode, 0
        tra     xchg
