#include <stdio.h>
int main(int argc, char *argv[]) {
    // Check if an argument is passed
    if (argc != 2) {
        printf("Usage: %s <string>\n", argv[0]);
        return 1;
    }

    // Print the argument passed
    printf("%s\n", argv[1]);

    return 0;
}
// argc tells how many arguments are passed. We check if 
// it's 2 because the first argument is always the program name,
// and the second would be the string you provide.

// argv[0] contains the name of the program (./echo), 
// and argv[1] contains the string passed (like ThisIsAString).
// If no string is passed, it prints a usage message.