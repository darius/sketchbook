"""
What to do with the result of a parse.
"""

class ParseOutcome(object):
    def __init__(self, parsing, rule, memo):
        # We remember the rule for the sake of debugging support, TBD
        self.parsing, self.rule, self.memo = parsing, rule, memo
        self.subject = self.parsing.subject

    def is_full(self):          # TODO naming
        return self.prefix() == len(self.parsing.subject)

    def prefix(self):           # TODO maybe make these properties instead of methods
        return self.memo[0]

    def inspected(self):
        return self.memo[1]

    def surely_full(self):
        di, far, ops = self.memo
        if di is None:
            raise Exception("Unparsable", far, self.parsing.subject)
        if di != len(self.parsing.subject):
            raise Exception("Incomplete parse", di, far, self.parsing.subject)
    
    def interpret(self, semantics):
        self.surely_full()      # TODO but it's legitimate to interpret a prefix parse...
        assert self.subject == self.parsing.subject
        stack = []
        frame = []
        ops = self.memo[2]
        for insn in ops:
            op = insn[0]
            if op == '[':
                stack.append(frame)
                frame = []
            elif op == ']':
                parent = stack.pop()
                parent.extend(frame)
                frame = parent
            elif op == 'do':
                fn = semantics[insn[1]]
                frame[:] = [fn(*frame)]
            elif op == 'lit':
                frame.append(insn[1])
            else:
                assert 0
        assert not stack
        return tuple(frame)

    def __repr__(self):
        return '%s<%r,%r,%r>' % ((self.rule,) + self.memo)
