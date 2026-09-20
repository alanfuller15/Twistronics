/* Sample C with deliberate, well-known flaws so the audit demo has findings.
   NOT production code — for demonstrating the review-worthiness re-ranker. */
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

void copy_name(char *input) {
    char buf[16];
    strcpy(buf, input);          /* CWE-120: unbounded copy */
    printf(input);               /* CWE-134: format string */
}

int read_config(char *path) {
    char cmd[128];
    sprintf(cmd, "cat %s", path); /* CWE-78-ish: sprintf into fixed buffer */
    return system(cmd);           /* command execution */
}

int main(int argc, char **argv) {
    char *p = malloc(8);
    if (argc > 1) copy_name(argv[1]);
    free(p);
    free(p);                      /* double free */
    return 0;
}
