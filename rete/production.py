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

def main(rules_text, facts_text):
    for fact in run(parse_rules(rules_text), parse_factoids(facts_text)):
        print ' '.join(fact)

def parse_rules(text):
    return map(parse_rule, text.split('\n\n'))

def parse_rule(text):
    return map(parse_factoids, text.split('-->', 1))

def parse_factoids(text):
    "Parse a list of facts, patterns, or templates."
    return [line.split() for line in text.splitlines()]

def run(rules, initial_facts):
    """Yield consequences of rules and initial_facts as long as new
    facts can be deduced."""
    assert all(map(is_fact, initial_facts))

    facts = list(initial_facts)

    def consequences((guard, action)):
        for env in match_all(guard, facts, [{}]):
            for template in action:
                yield fill(template, env)

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

def match_all(patterns, facts, envs):
    "Yield all ways of extending an env to match all patterns conjointly."
    def matches(pattern, envs):
        return successful(match(pattern, fact, env)
                          for env in envs for fact in facts)
    return foldr(matches, patterns, envs)

def match(pattern, fact, env):
    "Return an extended env matching pattern to fact, or None if impossible."
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
    return env

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
