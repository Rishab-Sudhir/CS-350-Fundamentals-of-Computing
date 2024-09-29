/*******************************************************************************
* CPU Clock Measurement Using RDTSC
*
* Description:
*     This C file provides functions to compute and measure the CPU clock using
*     the `rdtsc` instruction. The `rdtsc` instruction returns the Time Stamp
*     Counter, which can be used to measure CPU clock cycles.
*
* Author:
*     Renato Mancuso
*
* Affiliation:
*     Boston University
*
* Creation Date:
*     September 10, 2023
*
* Last Update:
*     September 9, 2024
*
* Notes:
*     Ensure that the platform supports the `rdtsc` instruction before using
*     these functions. Depending on the CPU architecture and power-saving
*     modes, the results might vary. Always refer to the CPU's official
*     documentation for accurate interpretations.
*
*******************************************************************************/

#include <stdio.h>
#include <string.h>
#include <time.h>
#include <stdint.h>
#include <stdlib.h>
#include <unistd.h>

#include "timelib.h"

int main(int argc, char *argv[])
{
    // **Argument Validation**
    if (argc != 4) {
        fprintf(stderr, "Usage: %s <seconds> <nanoseconds> <s|b>\n", argv[0]);
        return EXIT_FAILURE;
    }

    // **Parse Command-Line Arguments**
    char *endptr;
    long sec = strtol(argv[1], &endptr, 10);
    if (*endptr != '\0' || sec < 0) {
        fprintf(stderr, "Invalid seconds value.\n");
        return EXIT_FAILURE;
    }

    long nsec = strtol(argv[2], &endptr, 10);
    if (*endptr != '\0' || nsec < 0 || nsec >= NANO_IN_SEC) {
        fprintf(stderr, "Invalid nanoseconds value.\n");
        return EXIT_FAILURE;
    }

    char method_char = argv[3][0];
    if (method_char != 's' && method_char != 'b') {
        fprintf(stderr, "Invalid method. Use 's' for sleep or 'b' for busy-wait.\n");
        return EXIT_FAILURE;
    }

    // **Select Method**
    const char *method_str = (method_char == 's') ? "SLEEP" : "BUSYWAIT";

    // **Perform Measurement**
    uint64_t elapsed_cycles;
    if (method_char == 's') {
        elapsed_cycles = get_elapsed_sleep(sec, nsec);
    } else {
        elapsed_cycles = get_elapsed_busywait(sec, nsec);
    }

    // **Compute Clock Speed**
    double wait_time_sec = sec + (double)nsec / NANO_IN_SEC;
    double clock_speed_mhz = (double)elapsed_cycles / (wait_time_sec * 1e6); // Convert cycles per second to MHz

    // **Produce Output**
    printf("WaitMethod: %s\n", method_str);
    printf("WaitTime: %ld %ld\n", sec, nsec);
    printf("ClocksElapsed: %llu\n", (unsigned long long)elapsed_cycles);
    printf("ClockSpeed: %.2f\n", clock_speed_mhz);

    return EXIT_SUCCESS;
}


