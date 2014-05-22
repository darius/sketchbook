TODO: example apps to see what's missing
TODO: app that needs timed events, e.g. tetris

An excessively-minimal terminal-UI module.

The most standard way to code a console app like this is with curses,
but curses kind of earns its name. And there are better libraries
now, but I'm not familiar with them yet. (Soon!) Maybe you'll enjoy seeing
how to do without? We use http://en.wikipedia.org/wiki/ANSI_escape_code
and raw or cbreak mode
http://en.wikipedia.org/wiki/Seventh_Edition_Unix_terminal_interface#Input_modes

Thanks to Dave Long for helpful discussion of the key-reading
code.
