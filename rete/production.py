"""
Really basic production-system interpreter.

A fact is a tuple with no variables.
A pattern is a tuple possibly including variables.
A template is like a pattern.

A rule is a pair (patterns, templates). A rule fires when the patterns
match some facts; the effect is to add new facts by filling out the
templates with variable bindings from the matched patterns.

There's a crude concrete syntax: rules are separated by a blank line;
within a rule, '-->' separates the patterns from the templates. A
variable starts with uppercase, a constant with anything else.
"""

sample_rules = """\
mom Parent Child
--> parent Parent Child

dad Parent Child
--> parent Parent Child

parent G P
parent P C
--> grandparent G C
"""

sample_facts = """\
dad tywin cersei
mom cersei myrcella
"""

## main(sample_rules, sample_facts)
#. parent cersei myrcella
#. parent tywin cersei
#. grandparent tywin myrcella
#. 

append_rules = """\
append Xs Ys Zs
Xs nil
Ys nil
--> 
    Zs nil

append Xs Ys Zs
Xs nil
Ys cons Y Ys'
--> 
    Zs cons Y Zs'
    append Xs Ys' Zs'

append Xs Ys Zs
Xs cons X Xs'
--> 
    Zs cons X Zs'
    append Xs' Ys Zs'
"""

append_facts = """\
a0 cons hello a1
a1 cons world a2
a2 nil
b0 cons goodbye b1
b1 cons cruel b2
b2 cons world b3
b3 nil
append a0 b0 z0
"""

## main(append_rules, append_facts)
#. z0 cons hello :Zs'.2.0.7
#. append a1 b0 :Zs'.2.0.7
#. :Zs'.2.0.7 cons world :Zs'.2.1.9
#. append a2 b0 :Zs'.2.1.9
#. :Zs'.2.1.9 cons goodbye :Zs'.1.3.2.11
#. append a2 b1 :Zs'.1.3.2.11
#. :Zs'.1.3.2.11 cons cruel :Zs'.1.4.2.13
#. append a2 b2 :Zs'.1.4.2.13
#. :Zs'.1.4.2.13 cons world :Zs'.1.5.2.15
#. append a2 b3 :Zs'.1.5.2.15
#. :Zs'.1.5.2.15 nil
#. 

def main(rules_text, facts_text):
    for fact in run(parse_rules(rules_text), parse_factoids(facts_text)):
        print ' '.join(fact)

def parse_rules(text):
    return map(parse_rule, text.split('\n\n'))

def parse_rule(text):
    return make_rule(map(parse_factoids, text.split('-->', 1)))

def make_rule((patterns, templates)):
    return patterns, templates, free_vars(templates) - free_vars(patterns)

def parse_factoids(text):
    "Parse a list of facts, patterns, or templates."
    return [line.split() for line in text.splitlines() if line.strip()]

def free_vars(factoids):
    "Return a set of all variables in factoids."
    return set(x for f in factoids for x in f if is_variable(x))

def run(rules, initial_facts):
    """Yield consequences of rules and initial_facts as long as new
    facts can be deduced."""
    assert all(map(is_fact, initial_facts))

    facts = list(initial_facts)

    def consequences((rule_num, (guard, action, fresh_vars))):
        for env in match_all(guard, facts, [{'#': str(rule_num)}]):
            for v in fresh_vars:
                env = extend(env, v, make_fresh_id(v, env['#']))
            for template in action:
                yield fill(template, env)

    def new_consequences(numbered_rule):
        for fact in consequences(numbered_rule):
            if fact not in facts:
                facts.append(fact)
                yield fact

    more = True
    while more:
        more = False
        for fact in flatmap(new_consequences, enumerate(rules)):
            yield fact
            more = True

def make_fresh_id(v, tag):
    return ':%s.%s' % (v, tag)

def match_all(patterns, facts, envs):
    "Yield all ways of extending an env to match all patterns conjointly."
    def matches(pattern, envs):
        return successful(match(pattern, f, fact, env)
                          for env in envs for f, fact in enumerate(facts))
    return foldr(matches, patterns, envs)

def match(pattern, f, fact, env):
    """Return an extended env matching pattern to fact, or None if
    impossible. If matched, append the fact-number f to result['#'] --
    a record of dependencies."""
    if len(pattern) != len(fact):
        return None
    for x, y in zip(pattern, fact):
        if is_variable(x):
            if x not in env:
                env = extend(env, x, y)
                continue
            x = env[x]
        if x != y:
            return None
    return extend(env, '#', '%s.%s' % (env['#'], f))

def fill(template, env):
    "Instantiate template's variables from env."
    return [env[x] if is_variable(x) else x
            for x in template]

def is_variable(x):
    return isinstance(x, str) and x[:1].isupper()

def is_fact(clause):
    return not any(is_variable(x) for x in clause)

def extend(env, var, val):
    result = dict(env)
    result[var] = val
    return result

def flatmap(f, xs):
    for x in xs:
        for result in f(x):
            yield result

def foldr(f, xs, z):
    for x in reversed(xs):
        z = f(x, z)
    return z

def successful(xs):
    return (x for x in xs if x is not None)
