program
L1
   call st
   win_loop L1
   read_eof
   win_or_die
L2
L3
   return
st
   read_id
   if_lose L4
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
L4
L5
   return
choice
   call chain
   if_lose L6
L7
   read '|'
   if_lose L8
   write '   if_win '
   write_label1
   write_nl
   call chain
   win_or_die
L8
L9
   win_loop L7
   write_label1
   write_nl
L6
L10
   return
chain
   call maybe
   if_lose L11
   write '   if_lose '
   write_label1
   write_nl
L11
   if_win L12
   call surely
   if_lose L13
L13
L12
   if_lose L14
L15
   call maybe
   if_lose L16
   write '   win_or_die'
   write_nl
L16
   if_win L17
   call surely
   if_lose L18
L18
L17
   win_loop L15
   write_label1
   write_nl
L14
L19
   return
maybe
   read_id
   if_lose L20
   write '   call '
   write_it
   write_nl
L20
   if_win L21
   read_qstring
   if_lose L22
   write '   read '
   write_it
   write_nl
L22
   if_win L21
   read '?'
   if_lose L23
   read_id
   win_or_die
   write '   read_'
   write_it
   write_nl
L23
   if_win L21
   read '('
   if_lose L24
   call choice
   win_or_die
   read ')'
   win_or_die
L24
L21
   return
surely
   read '*'
   if_lose L25
   write_label1
   write_nl
   call maybe
   win_or_die
   write '   win_loop '
   write_label1
   write_nl
L25
   if_win L26
   read ':'
   if_lose L27
   read_id
   if_lose L28
   write '   write_'
   write_it
   write_nl
L28
   if_win L29
   read_qstring
   if_lose L30
   write '   write '
   write_it
   write_nl
L30
L29
   win_or_die
L27
L26
   return
