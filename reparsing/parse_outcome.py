"""
What to do with the result of a parse.
"""

class ParseOutcome(object):
    def __init__(self, parsing, rule, memo):
        self.memo = memo
        # We remember the parsing and rule for the sake of debugging support, TBD
        self.parsing, self.rule = parsing, rule

    def __nonzero__(self):   # N.B. in py3 this'd be __bool__
        "Did the parse succeed and reach the end?"
        return self.is_full()

    def is_full(self):          # TODO naming
        return self.prefix() == len(self.parsing.subject)

    def prefix(self):           # TODO maybe make these properties instead of methods
        return self.memo[0]

    def inspected(self):
        return self.memo[1]

    def surely_full(self):
        if not self.is_full():
            hop, peek, ops = self.memo
            if hop is None:
                raise Exception("Unparsable", peek, self.parsing.subject)
            else:
                raise Exception("Incomplete parse", hop, peek, self.parsing.subject)
    
    def interpret(self, semantics):
        self.surely_full()      # TODO but it's legitimate to interpret a prefix parse...
        frames = []
        values = []
        ops = self.memo[2]
        for insn in ops:
            op = insn[0]
            if op == '[':
                frames.append(values)
                values = []
            elif op == ']':
                parent = frames.pop()
                parent.extend(values)
                values = parent
            elif op == 'do':
                fn = semantics[insn[1]]
                values[:] = [fn(*values)]
            elif op == 'lit':
                values.append(insn[1])
            else:
                assert 0
        assert not frames
        return tuple(values)

    def __repr__(self):
        return '%s<%r,%r,%r>' % ((self.rule,) + self.memo)
