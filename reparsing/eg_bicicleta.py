"""
Ported from the Parson example
"""

import grammars
from semantics import ast_semantics

grammar_source = r"""
start       : expr _.

expr        : factor (infix_op factor       :mk_infix)*.
factor      : primary suffix*.

primary     : name                          :VarRef
            | _ {/\d/* '.' /\d/+}    :float :Literal
            | _ {/\d/+}              :int   :Literal
            | _ '"' {/[^"\\]/*} '"'         :Literal
            | _ '(' expr _ ')'
            | :empty extend.

suffix      = _'.' name                     :Call
            | extend
            | _'(' :'()' bindings _')'      :mk_funcall
            | _'[' :'[]' bindings _']'      :mk_funcall.

extend      = _'{' name _':' bindings _'}'  :Extend
            | _'{'   :None   bindings _'}'  :SelflessExtend.
bindings    : binding ** bindsep            :name_positions.
bindsep     : newline | _','.
binding     : (name _'=' | :None) expr      :hug.

infix_op    : _ !lone_eq {opchars}.
opchars     : /[-~`!@$%^&*+<>?\/|\\=]/+.
lone_eq     : '=' !opchars.

name        : _ { /[A-Za-z_]/ /[A-Za-z_0-9]/* }
            | _ /'/ { /[^'\\]/* } /'/.

newline     : (!/\n/ blank)* /\n/.
blank       : /\s/ | '#' /./*.

_           : blank*.
"""

def Bicicleta(make_parsing):
    def parse(s):
        return parse.grammar.parse(s).interpret(ast_semantics)[0]
    parse.grammar = grammars.Grammar(grammar_source, make_parsing)
    return parse

## from nonincremental import Parsing
## parse = Bicicleta(Parsing)

## parse('5')
#. ('Literal', ('int', '5'))
## parse('{x: {y: {z: x ++ y{a="b"} <*> z.foo }}}')
#. ('Extend', ('empty',), 'x', ('name_positions', ('hug', ('None',), ('Extend', ('empty',), 'y', ('name_positions', ('hug', ('None',), ('Extend', ('empty',), 'z', ('name_positions', ('hug', ('None',), ('mk_infix', ('mk_infix', ('VarRef', 'x'), '++', ('SelflessExtend', ('None', ('VarRef', 'y')), ('name_positions', ('hug', 'a', ('Literal', 'b'))))), '<*>', ('Call', ('VarRef', 'z'), 'foo')))))))))))
# {x: arg1={y: arg1={z: arg1=x.++{arg1=y{a='b'}}.().<*>{arg1=z.foo}.()}}}

## wtf = parse("{x=42, y=55}.x")
## wtf
#. ('Call', ('SelflessExtend', ('None', ('empty',)), ('name_positions', ('hug', 'x', ('Literal', ('int', '42'))), ('hug', 'y', ('Literal', ('int', '55'))))), 'x')
# {x=42, y=55}.x

## parse("137")
#. ('Literal', ('int', '137'))
## parse('137[yo="dude"]')
#. ('mk_funcall', ('Literal', ('int', '137')), '[]', ('name_positions', ('hug', 'yo', ('Literal', 'dude'))))
# 137{yo='dude'}.[]

## adding = parse("137.'+' {arg1=1}.'()'")
## adding
#. ('Call', ('SelflessExtend', ('None', ('Call', ('Literal', ('int', '137')), '+')), ('name_positions', ('hug', 'arg1', ('Literal', ('int', '1'))))), '()')
# 137.+{arg1=1}.()

## cmping = parse("(137 == 1).if(so=42, else=168)")
## cmping
#. ('mk_funcall', ('Call', ('mk_infix', ('Literal', ('int', '137')), '==', ('Literal', ('int', '1'))), 'if'), '()', ('name_positions', ('hug', 'so', ('Literal', ('int', '42'))), ('hug', 'else', ('Literal', ('int', '168')))))
# 137.=={arg1=1}.().if{so=42, else=168}.()

def make_fac(parse, n):
    fac = parse("""
{env: 
 fac = {fac:   # fac for factorial
        '()' = (fac.n == 0).if(so = 1,
                               else = fac.n * env.fac(n = fac.n-1))}
}.fac(n=%d)""" % n)
    return fac

## fac = make_fac(parse, 4)
## fac
#. ('mk_funcall', ('Call', ('Extend', ('empty',), 'env', ('name_positions', ('hug', 'fac', ('Extend', ('empty',), 'fac', ('name_positions', ('hug', '()', ('mk_funcall', ('Call', ('mk_infix', ('Call', ('VarRef', 'fac'), 'n'), '==', ('Literal', ('int', '0'))), 'if'), '()', ('name_positions', ('hug', 'so', ('Literal', ('int', '1'))), ('hug', 'else', ('mk_infix', ('Call', ('VarRef', 'fac'), 'n'), '*', ('mk_funcall', ('Call', ('VarRef', 'env'), 'fac'), '()', ('name_positions', ('hug', 'n', ('mk_infix', ('Call', ('VarRef', 'fac'), 'n'), '-', ('Literal', ('int', '1')))))))))))))))), 'fac'), '()', ('name_positions', ('hug', 'n', ('Literal', ('int', '4')))))
# {env: fac={fac: ()=fac.n.=={arg1=0}.().if{so=1, else=fac.n.*{arg1=env.fac{n=fac.n.-{arg1=1}.()}.()}.()}.()}}.fac{n=4}.()
