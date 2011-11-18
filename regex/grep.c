#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static void error(const char *plaint) {
    fprintf(stderr, "%s\n", plaint);
    exit(1);
}

enum { max_insns = 8192 };
enum { op_eat, op_jump, op_fork };
static unsigned ninsns;
static int ops[max_insns], args[max_insns];
static char visited[max_insns];

static void spread(unsigned pc, char *set) {
    for (;;) switch (ops[--pc]) {
        case op_eat:
            set[pc] = 1;
            return;
        case op_jump:
            pc = args[pc];
            break;
        case op_fork:
            if (visited[pc]) return;
            visited[pc] = 1;
            spread(args[pc], set);
            break;
        }
}

static int match(unsigned start, const char *input) {
    static char set0[max_insns], set1[max_insns];
    char *agenda = set0, *next = set1;
    memset(agenda, 0, ninsns);
    memset(visited, 0, ninsns);
    spread(start, agenda);
    for (; *input; ++input) {
        memset(next, 0, ninsns);
        memset(visited, 0, ninsns);
        for (unsigned pc = 1; pc < ninsns; ++pc)
            if (agenda[pc] && *input == args[pc])
                spread(pc, next);
        char *tmp = agenda; agenda = next; next = tmp;
    }
    return agenda[0];  // (0 is the accepting state)
}

static void emit1(int op, int arg) {
    if (max_insns <= ninsns) error("Pattern too long");
    ops[ninsns] = op, args[ninsns] = arg, ++ninsns;
}

static unsigned emit(int op, int arg, unsigned state) {
    if (ninsns != state) emit1(op_jump, state);
    emit1(op, arg);
    return ninsns;
}

static const char *pattern, *pp; // start, current parsing position

static int eat(char c) {
    return pattern < pp && pp[-1] == c ? (--pp, 1) : 0;
}

static unsigned parsing(int precedence, unsigned state) {
    unsigned rhs;
    if (pattern == pp || pp[-1] == '(' || pp[-1] == '|')
        rhs = state;
    else if (eat(')')) {
        rhs = parsing(0, state);
        if (!eat('(')) error("Mismatched ')'");
    }
    else if (eat('*')) {
        rhs = emit(op_fork, 0, state); // (The 0 is a placeholder...
        args[rhs-1] = parsing(6, rhs); // ...filled in here.)
    }
    else
        rhs = emit(op_eat, *--pp, state);
    while (pattern < pp && pp[-1] != '(') {
        int prec = pp[-1] == '|' ? 3 : 5;
        if (prec <= precedence) break;
        if (eat('|'))
            rhs = emit(op_fork, rhs, parsing(prec, state));
        else
            rhs = parsing(prec, rhs);
    }
    return rhs;
}

static unsigned parse(const char *string) {
    pattern = string; pp = pattern + strlen(pattern);
    ninsns = 0;
    unsigned state = parsing(0, emit(op_eat, '\0', 0));
    if (pattern != pp) error("Bad pattern");
    return state;
}

int main(int argc, char **argv) {
    if (argc != 2) error("Usage: grep pattern");
    unsigned start_state = parse(argv[1]);
    char line[9999];
    while (fgets(line, sizeof line, stdin)) {
        line[strlen(line) - 1] = '\0';
        if (match(start_state, line))
            puts(line);
    }
    return 0;
}
