program
S0
   call rule
   win_loop S0
   read_eof
   win_or_die
W1
   return
rule
   read_id
   if_lose L2
   write_it
   write_nl
   read '='
   win_or_die
   call choice
   win_or_die
   read ';'
   win_or_die
   write '   return'
   write_nl
L2
W3
   return
choice
   call chain
   if_lose L4
   do_gensym
S5
   read '|'
   if_lose L6
   write '   if_win W'
   write_top
   write_nl
   call chain
   win_or_die
L6
W7
   win_loop S5
   write 'W'
   write_pop
   write_nl
L4
W8
   return
chain
   call surely
   if_lose L9
   call tail
   win_or_die
L9
   if_win W10
   call maybe
   if_lose L11
   write '   if_lose '
   do_gensym
   write 'L'
   write_top
   write_nl
   call tail
   win_or_die
   write 'L'
   write_pop
   write_nl
L11
W10
   return
tail
S12
   call surely
   if_lose L13
L13
   if_win W14
   call maybe
   if_lose L15
   write '   win_or_die'
   write_nl
L15
W14
   win_loop S12
W16
   return
surely
   read '.'
   if_lose L17
   read_qstring
   if_lose L18
   write '   write '
   write_it
   write_nl
L18
   if_win W19
   read_id
   if_lose L20
   write '   write_'
   write_it
   write_nl
L20
W19
   win_or_die
L17
   if_win W21
   read '%'
   if_lose L22
   read_id
   win_or_die
   write '   do_'
   write_it
   write_nl
L22
   if_win W21
   read '*'
   if_lose L23
   do_gensym
   write 'S'
   write_top
   write_nl
   call maybe
   win_or_die
   write '   win_loop S'
   write_pop
   write_nl
L23
W21
   return
maybe
   read_qstring
   if_lose L24
   write '   read '
   write_it
   write_nl
L24
   if_win W25
   read '?'
   if_lose L26
   read_id
   win_or_die
   write '   read_'
   write_it
   write_nl
L26
   if_win W25
   read_id
   if_lose L27
   write '   call '
   write_it
   write_nl
L27
   if_win W25
   read '('
   if_lose L28
   call choice
   win_or_die
   read ')'
   win_or_die
L28
W25
   return
