// Let's recode the FSM's at the start of psnoise.c.

#include <ctype.h>
#include <stdio.h>
#include <string.h>

// Adapted from psnoise.c
static int among (const char *s, int c) {
    return c && strchr (s, c) != NULL;
}
static int israd  (int c) { return '#' == c; }
static int isdot  (int c) { return '.' == c; }
static int ise    (int c) { return among ("eE", c); }
static int issign (int c) { return among ("+-", c); }

// Now my turn. This is totally unhygienic.

typedef enum { no, yes } Flag;

#define maybe(test)  ((test) && (++s, yes))
#define after(test)       if (maybe (test))
#define one(test)    do { if (!maybe (test)) return no; } while (0)
#define many(test)   do { while (maybe (test)) {} } while (0)

#define accept()     do { if (!*s) return yes; } while (0)
#define end()        do { accept (); return no; } while (0)

// sign? digit+ $
static Flag fsm_dec (const char *s) {
    maybe (issign (*s));
    one (isdigit (*s));
    many (isdigit (*s));
    end ();
}

// digit+ rad alnum+ $
static Flag fsm_rad (const char *s) {
    one (isdigit (*s));
    many (isdigit (*s));
    one (israd (*s));
    one (isalnum (*s));
    many (isalnum (*s));
    end ();
}

// sign? (digit+ (dot digit*)? | digit* dot digit+) (e sign? digit+)? $
static Flag fsm_real0 (const char *s) {
    // This version tries to imitate psnoise's fsm exactly.
    maybe (issign (*s));
    after (isdigit (*s)) {
        many (isdigit (*s));
        accept ();
        after (isdot (*s)) goto digitsexp; else goto exponent;
    } else {
        one (isdot (*s));
        one (isdigit (*s));
    }
 digitsexp:
    many (isdigit (*s));
    accept ();
 exponent:
    one (ise (*s));
    maybe (issign (*s));
    one (isdigit (*s));
    many (isdigit (*s));
    end ();
}

// sign? (digit+ (dot digit*)? | digit* dot digit+) (e sign? digit+)? $
static Flag fsm_real1 (const char *s) {
    // This version written as I naturally would. Both untested.
    maybe (issign (*s));
    after (isdigit (*s)) {
        many (isdigit (*s));
        after (isdot (*s)) {
            many (isdigit (*s));
        }
    } else {
        one (isdot (*s));
        one (isdigit (*s));
        many (isdigit (*s));
    }
    after (ise (*s)) {
        maybe (issign (*s));
        one (isdigit (*s));
        many (isdigit (*s));
    }
    end ();
}

// sign? (digit|dot)* {ndigits>0} {ndots<=1} (e sign? digit+)? $
static Flag fsm_real (const char *s) {
    // This version simplified with some auxiliary state.
    Flag seen_dot = no, seen_digit = no;
    maybe (issign (*s));
    many (isdigit (*s) && (seen_digit = yes)
          || isdot (*s) && !seen_dot && (seen_dot = yes));
    if (!seen_digit) return no;
    after (ise (*s)) {
        maybe (issign (*s));
        one (isdigit (*s));
        many (isdigit (*s));
    }
    end ();
}

static int ntests = 0;
static int nfailures = 0;

static void expect (Flag expected, Flag (*fsm)(const char *), const char *s) {
    ++ntests;
    if (expected != fsm (s)) {
        printf ("FAIL: expected %d for '%s'\n", expected, s);
        ++nfailures;
    }
}

static void test_dec (Flag (*fsm)(const char *)) {
    expect (no,  fsm, "");
    expect (yes, fsm, "0");
    expect (yes, fsm, "-137");
    expect (yes, fsm, "+42");
    expect (no,  fsm, "-13hello7");
}

static void test_real (Flag expected, const char *s) {
    expect (expected, fsm_real0, s);
    expect (expected, fsm_real1, s);
    expect (expected, fsm_real,  s);
}

int main () {
    test_dec (fsm_dec);

    expect (no,  fsm_rad, "");
    expect (no,  fsm_rad, "1#");
    expect (no,  fsm_rad, "1##");
    expect (yes, fsm_rad, "1#2"); // N.B. not actually a good radix literal
    expect (yes, fsm_rad, "36#yowbaby42");
    expect (no,  fsm_rad, "36#yow.baby42");

    test_dec (fsm_real0);
    test_dec (fsm_real1);
    test_dec (fsm_real);

    test_real (no, "");
    test_real (no, ".");
    test_real (no, "-.");
    test_real (no, "e15");
    test_real (no, "+e0");
    test_real (no, "x");
    test_real (no, "12y");
    test_real (no, "0.0e0z");
    test_real (no, "0.0.");

    test_real (yes, "0.");
    test_real (yes, ".0");
    test_real (yes, "+3.14159265358979");
    test_real (yes, "1e+501");
    test_real (yes, "-34.77e-15");
    test_real (yes, ".24e2");
    test_real (yes, "1e6");

    if (0 == nfailures) {
        printf ("All %d tests passed.\n", ntests);
        return 0;
    } else {
        printf ("%d tests FAILED out of %d.\n", nfailures, ntests);
        return 1;
    }
}
