#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define max_insns 9999

static void panic(const char *plaint) {
    fprintf(stderr, "%s\n", plaint);
    exit(1);
}

typedef enum { op_expect, op_jump, op_split } Op;
static Op ops[max_insns];
static int args[max_insns];
static unsigned cp = 0;  // compile pointer

static char set0[max_insns];
static char set1[max_insns];
static char visited[max_insns];
static char *agenda = set0;
static char *next = set1;

static void spread(unsigned pc, char *result) {
    for (;;) {
        switch (ops[pc]) {
        case op_expect:
            result[pc] = 1;
            return;
        case op_jump:
            pc = args[pc];
            break;
        case op_split:
            if (visited[pc])
                return;
            visited[pc] = 1;
            spread(args[pc], result);
            --pc;
            break;
        }
    }
}

static int match(const char *s) {
    memset(agenda, 0, cp);
    memset(visited, 0, cp);
    spread(cp - 1, agenda);
    for (; *s; ++s) {
        memset(next, 0, cp);
        memset(visited, 0, cp);
        for (unsigned pc = 1; pc < cp; ++pc)
            if (agenda[pc] && *s == args[pc])
                spread(pc - 1, next);
        char *tmp = agenda; agenda = next; next = tmp;
    }
    return agenda[0];  // (0 is the accepting state)
}

static void really_emit(Op op, int arg) {
    if (max_insns <= cp) panic("Pattern too long");
    ops[cp] = op;
    args[cp] = arg;
    ++cp;
}

static int emit(Op op, int arg, unsigned k) { // k for continuation
    if (cp - 1 != k) really_emit(op_jump, k);
    really_emit(op, arg);
    return cp - 1;
}

static const char *pattern, *pp; // start, current parsing position

static int eat(char c) {
    int r = pattern < pp && pp[-1] == c; pp -= r; return r;
}

static int parse_expr(int precedence, unsigned k) {
    int rhs;
    if (pattern == pp || pp[-1] == '|' || pp[-1] == '(')
        rhs = k;
    else if (eat(')')) {
        rhs = parse_expr(0, k);
        if (!eat('(')) panic("Mismatched ')'");
    }
    else if (eat('*')) {
        rhs = emit(op_split, 0, k);
        args[rhs] = parse_expr(6, rhs);
    }
    else
        rhs = emit(op_expect, *--pp, k);
    while (pattern < pp && pp[-1] != '(') {
        int prec = pp[-1] == '|' ? 2 : 4;
        if (prec < precedence) break;
        if (eat('|'))
            rhs = emit(op_split, rhs, parse_expr(prec+1, k));
        else
            rhs = parse_expr(prec+1, rhs);
    }
    return rhs;
}

static void parse(const char *string) {
    pattern = string; pp = pattern + strlen(pattern);
    parse_expr(0, emit(op_expect, '\0', -1)); // (no char from fgets == '\0')
    if (pattern != pp) panic("Bad pattern");
}

int main(int argc, char **argv) {
    if (argc != 2) panic("usage");
    parse(argv[1]);
    char line[9999];
    while (fgets(line, sizeof line, stdin)) {
        line[strlen(line) - 1] = '\0';
        if (match(line))
            puts(line);
    }
    return 0;
}
