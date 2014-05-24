An excessively-minimal terminal-UI module.

The most standard way to code a console app like this is with curses,
but curses kind of earns its name. And there are better libraries
now, but I'm not familiar with them yet. (Soon!) Maybe you'll enjoy seeing
how to do without? We use http://en.wikipedia.org/wiki/ANSI_escape_code
and raw or cbreak mode
http://en.wikipedia.org/wiki/Seventh_Edition_Unix_terminal_interface#Input_modes

Thanks to Dave Long for helpful discussion of the key-reading
code.

TODO: example apps to see what's missing
  X Games like tictactoe
  X Why are some examples showing the cursor and others not? Ah, missing flush().
  * pager
  * text editor
  * realtime game 
    * What's the tictactoe of realtime console games? Frogger? Tower defense?
    * Simpler:
      * Type something in while a stopwatch counts, and show your typing speed.
        (The 'realtime' element is the stopwatch display.)
      * A little more fun: solve a puzzle, e.g. SAT, along with a stopwatch.
        Or escape a maze.
