"""
# Example:
not:10          # Table definition, arity 1.
1=not 0         # Assertion (as documentation/check)
0=not 1
and:0001        # Table definition, arity 2.
0=and 0 0
0=and 0 1
0=and 1 0
1=and 1 1
or:0111
0=or 0 0
1=or 0 1
1=or 1 0
1=or 1 1
mux:00110101    # Table definition, arity 3.
t<and 0 0       # Assignment, arity 0.
1=not t         # Use of an assigned variable (in an assertion).
t<and 1 1       # It can be reassigned. (The last assignment to a variable persists into the next cycle.)
0=not t
mem 0 t<or t 1  # Assignment, arity 2. Use for addressable memories.
1=mem 0 t
0=mem 1 1       # Unassigned variables are 0 (unless set by the simulator, e.g. an input device).
"""

def eval_hdl(text, env):
    """`text` is a machine description following the grammar above.
    `env` is a dict, for two purposes:
       * sequential-circuit state (and RAM)
       * I/O devices
    To use this for a particular machine, call eval_hdl() in a loop,
    once for each most-basic machine cycle, reading/writing the data
    of any special devices from/to env."""
    XXX
