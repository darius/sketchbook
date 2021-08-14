"""
Parsing expressions, with an API meant to resemble Python's re module.
"""

import operator
from grammar import parser_parser
from parsers import Parsing, ParseOutcome, base_semantics, DictSemantics

def match(pe_str, subject_str):
    return compile(pe_str).match(subject_str)

def compile(pe_str, **kwargs):
    unlinked_rules = dict(parser_parser.top(pe_str))
    rules = {}
    for name, rule in unlinked_rules.items():
        rules[name] = rule.link(rules, kwargs)
    return Compiled(rules)

class Compiled(object):         # XXX ugh?
    def __init__(self, rules):
        self.rules = rules
    def match(self, subject_str):
        return Parsing(self.rules, subject_str).parse(None)

## match(r"\x/ \y/* \z/ - foo: bar", 'xyyzz')
#. ParseOutcome<4,4,()>
## match(r"\x/^", 'x').groups()
#. ('x',)
## match(r"x^ x - x: \x/", 'xx').groups()
#. ('x',)

## compile(r"\x/").match('x')
#. ParseOutcome<1,1,()>
## a = compile(r"\a/")
## b = compile(r"\b/")
## axb = compile(r"{a} \x/ {b}", a=a, b=b)
## axb.match('x')
#. ParseOutcome<None,0,()>
## axb.match('axb yay')
#. ParseOutcome<3,3,()>

calc_source = r"""
exp0
- exp0  :  exp1 ( \+/  exp1 :add
                | \-/  exp1 :sub )*
- exp1  :  exp2 ( \*/  exp2 :mul
                | `//` exp2 :div
                | `/`  exp2 :truediv
                | \%/  exp2 :mod )*
- exp2  :  exp3 ( \^/  exp2 :pow )?
- exp3  :  \(/ exp0 \)/
        |  \-/ exp1  :neg
        |  {decimal}
"""

decimal_source = r"""
digit+^ :int
- digit: `\d`
"""

# TODO what a pain
op_semantics = DictSemantics(operator, __builtins__)

## decimal = compile(decimal_source)
## calc = compile(calc_source, decimal=decimal)
## calc.match('1')
#. ParseOutcome<1,1,(('[',), ('[',), ('[',), ('[',), ('[',), (']',), ('lit', '1'), ('do', 'int'), (']',), (']',), (']',), (']',))>
## calc.match('2+3')
#. ParseOutcome<3,3,(('[',), ('[',), ('[',), ('[',), ('[',), (']',), ('lit', '2'), ('do', 'int'), (']',), (']',), (']',), ('[',), ('[',), ('[',), ('[',), (']',), ('lit', '3'), ('do', 'int'), (']',), (']',), (']',), ('do', 'add'), (']',))>
## calc.match('2+3').do(op_semantics)
#. (5,)


aaa = r"""
ha
- ha: \a/
"""
## aaa = compile(aaa)

bbb = r"""
ha
- ha: \b/
"""
## bbb = compile(bbb)

## both = r"""{aaa}{bbb}"""
## both = compile(both, aaa=aaa, bbb=bbb)
## both.match('1')
#. ParseOutcome<None,0,()>
## both.match('ab')
#. ParseOutcome<2,2,(('[',), (']',), ('[',), (']',))>
## both.match('aa')
#. ParseOutcome<None,1,()>

# Could be a regex:
compile(r"`Step (.) must be finished before step (.) can begin[.]`")
compile(r"\Step /.c^\ must be finished before step /.c^\ can begin./")
compile(r"`(.....) => (.)`")

# Could be a regex, I guess? But with the results not grouped as you want?
# Context for these: re.match(r'(?:(.)(.))+', 'xyabcd').groups() --> ('c', 'd')
compile(r"[`(1+)(#{1,5})` :tuple]*")
compile(r"[[`(1+)` :len] [`(#{1,5})` :len] :tuple]*")
compile(r"(.letter+ \!/? | .c)^*")
compile(r"(.letter+^ | .c)*")

# Could not be a regex:
compile(r"([:position .letter+ (`'` .letter+)? :position :tuple] | :skip)*") # TODO :position
compile(r"\#/ .u \ @ / .u \,/ .u \: / .u \x/ .u")
compile(r"\#/.u\ @ /.u\,/.u\: /.u\x/.u")
compile(r".u\, /.u")
compile(r".letter+^ _ .d")
compile(r".u\ players; last marble is worth /.u\ points/ .eol") # TODO '\n' in a \literal/ somehow
compile(r"`(.)` \=/ .d \, / `(.)` \=/ .d \../ .d")
compile(r".c^\=/.d\, /.c^\=/.d\../.d")
compile(r"\depth: /.u .eol \target: / [.u\,/.u :tuple] .eol")
compile(r"[.letter^ .u :tuple] ** \,/")

compile(r"""
- main: clause* :tuple `\n\n` program  # N.B. no .end
- clause: \Before: [/ [.u\, /.u\, /.u\, /.u :tuple] \]/ `\n`
          [.u\ /.u\ /.u\ /.u :tuple] `\n`
          \After:  [/ [.u\, /.u\, /.u\, /.u :tuple] \]/ `\n\n` :tuple

- program: insn* :tuple
- insn:    .u\ /.u\ /.u\ /.u `\n` :tuple
""")

# TODO more
# compile(r"")
