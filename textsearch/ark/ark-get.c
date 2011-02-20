#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static void panic (const char *plaint) {
    fprintf (stderr, "%s\n", plaint);
    exit (1);
}

static void sys_panic (const char *plaint) {
    fprintf (stderr, "%s: %s\n", plaint, strerror (errno));
    exit (1);
}

static void blast (FILE *ark, const char *ark_name, long start, long size) {
    if (0 != fseek (ark, start, SEEK_SET))
	sys_panic (ark_name);
    while (0 < size--) {
	int c = getc (ark);
	if (EOF == c)
	    panic ("Premature EOF or I/O error");
	putc (c, stdout);
    }
}

static void ark_get (FILE *ark, const char *ark_name, const char *key) {
    if (0 != fseek (ark, -11, SEEK_END))
	sys_panic (ark_name);
    long catalog_size;
    fscanf (ark, "%ld", &catalog_size);  // XXX check errors
    if (catalog_size <= 0)
	panic ("Bad or empty arkfile");
    if (0 != fseek (ark, -11 - catalog_size, SEEK_END))
	sys_panic (ark_name);
    long offset = 0;
    for (;;) {
	long size;
	fscanf (ark, "%ld ", &size);	// XXX check errors
	char key2[1024];
	if (!fgets (key2, sizeof key2, ark))
	    panic ("Key not found");
	size_t L = strlen (key2);
	if (0 < L)
	    key2[L-1] = '\0';		// strip trailing newline
	if (0 == strcmp (key, key2)) {
	    blast (ark, ark_name, offset, size);
	    return;
	}
	offset += size;
    }
}

int main (int argc, char **argv) {
    if (3 != argc)
	panic ("usage: ark-get arkfile key");
    FILE *f = fopen (argv[1], "rb");
    if (!f)
	sys_panic (argv[1]);
    ark_get (f, argv[1], argv[2]);
    fclose (f);
    return 0;
}
