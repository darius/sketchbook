"""
Really basic production-system interpreter.

A fact is a 3-tuple with no variables.
A pattern is a 3-tuple possibly including variables.
A template is like a pattern.

(Actually n-tuples but the n's must all be the same.)

A rule is a pair (patterns, templates). A rule fires when the patterns
match some facts; the effect is to add new facts by filling out the
templates with variable bindings from the matched patterns.

There's a crude concrete syntax: rules are separated by a blank line;
within a rule, '---' separates the patterns from the templates. A
variable starts with uppercase, a constant with anything else.
"""

sample_rules = """\
mom Parent Child
---
parent Parent Child

dad Parent Child
---
parent Parent Child

parent G P
parent P C
---
grandparent G C
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

def main(rules_text, facts_text):
    for fact in run(parse_rules(rules_text), parse_patterns(facts_text)):
        print ' '.join(fact)

def parse_rules(text):
    return map(parse_rule, text.split('\n\n'))

def parse_rule(text):
    patterns, templates = text.split('\n---\n')
    return parse_patterns(patterns), parse_patterns(templates)

def parse_patterns(text):
    return [line.split() for line in text.splitlines()]

def run(rules, initial_facts):
    """Yield consequences of rules and initial_facts as long as new
    facts can be deduced."""
    assert all(map(is_fact, initial_facts))

    facts = list(initial_facts)

    def consequences((guard, action)):
        for env in matching(guard, facts, [{}]):
            for template in action:
                yield fill_out(template, env)

    def new_consequences(rule):
        for fact in consequences(rule):
            if fact not in facts:
                facts.append(fact)
                yield fact

    while True:
        for fact in flatmap(new_consequences, rules):
            yield fact
        else:
            break

def flatmap(f, xs):
    for x in xs:
        for result in f(x):
            yield result

def matching(patterns, facts, envs):
    "Yield all ways of extending an env to match all patterns conjointly."
    if not patterns:
        return envs
    else:
        return matching(patterns[1:], facts,
                        matches(patterns[0], facts, envs))

def matches(pattern, facts, envs):
    "Yield all ways of extending an env to match pattern."
    return successful(match(pattern, fact, env)
                      for env in envs for fact in facts)

def successful(xs):
    return (x for x in xs if x is not None)

def match(pattern, fact, env):
    "Return an extended env matching pattern to fact, or None if impossible."
    assert len(pattern) == len(fact)
    for x, y in zip(pattern, fact):
        if is_variable(x):
            if x not in env:
                env = extend(env, x, y)
                continue
            x = env[x]
        if x != y:
            return None
    return env

def extend(env, var, val):
    result = dict(env)
    result[var] = val
    return result

def fill_out(template, env):
    "Instantiate template's variables from env."
    return [env[x] if is_variable(x) else x
            for x in template]

def is_variable(x):
    return isinstance(x, str) and x[:1].isupper()

def is_fact(clause):
    return not any(is_variable(x) for x in clause)
