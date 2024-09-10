#include <stdio.h>
#include <string.h> // For strlen()

int main(int argc, char *argv[]) {
    // Check if the user provided an argument
    if (argc != 2) {
        printf("Usage: %s <string>\n", argv[0]);
        return 1;
    }

    // Get the string from the command line argument
    char *input = argv[1];

    // Find the length of the string
    int len = strlen(input);

    // Print the string in reverse
    for (int i = len - 1; i >= 0; i--) {
        printf("%c", input[i]);
    }
    printf("\n"); // Newline after the reversed string

    return 0;
}
