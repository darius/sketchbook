program
L1
   call st
   win_loop L1
   read_eof
   win_or_die
L2
   return
st
   read_id
   if_lose L3
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
L3
L4
   return
choice
   call chain
   if_lose L5
L6
   read '|'
   if_lose L7
   write '   if_win '
   write_label1
   write_nl
   call chain
   win_or_die
L7
L8
   win_loop L6
   write_label1
   write_nl
L5
L9
   return
chain
   call surely
   if_lose L10
   call tail
   win_or_die
L10
   if_win L11
   call maybe
   if_lose L12
   write '   if_lose '
   write_label1
   write_nl
   call tail
   win_or_die
   write_label1
   write_nl
L12
L11
   return
tail
L13
   call surely
   if_lose L14
L14
   if_win L15
   call maybe
   if_lose L16
   write '   win_or_die'
   write_nl
L16
L15
   win_loop L13
L17
   return
surely
   read ':'
   if_lose L18
   read_qstring
   if_lose L19
   write '   write '
   write_it
   write_nl
L19
   if_win L20
   read_id
   if_lose L21
   write '   write_'
   write_it
   write_nl
L21
L20
   win_or_die
L18
   if_win L22
   read '*'
   if_lose L23
   write_label1
   write_nl
   call maybe
   win_or_die
   write '   win_loop '
   write_label1
   write_nl
L23
L22
   return
maybe
   read_qstring
   if_lose L24
   write '   read '
   write_it
   write_nl
L24
   if_win L25
   read '?'
   if_lose L26
   read_id
   win_or_die
   write '   read_'
   write_it
   write_nl
L26
   if_win L25
   read_id
   if_lose L27
   write '   call '
   write_it
   write_nl
L27
   if_win L25
   read '('
   if_lose L28
   call choice
   win_or_die
   read ')'
   win_or_die
L28
L25
   return
