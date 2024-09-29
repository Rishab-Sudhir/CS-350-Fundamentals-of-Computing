/*******************************************************************************
* Time Functions Library (implementation)
*
* Description:
*     A library to handle various time-related functions and operations.
*
* Author:
*     Renato Mancuso <rmancuso@bu.edu>
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
*     Ensure to link against the necessary dependencies when compiling and
*     using this library. Modifications or improvements are welcome. Please
*     refer to the accompanying documentation for detailed usage instructions.
*
*******************************************************************************/

#include "timelib.h"
#include <errno.h>

/* Return the number of clock cycles elapsed when waiting for
 * wait_time seconds using sleeping functions */
uint64_t get_elapsed_sleep(long sec, long nsec)
{
    // Step 1: Capture the CPU clock cycles before sleeping
    uint64_t start_cycles;
    get_clocks(start_cycles);

    // Step 2: Sleep for the specified time
    struct timespec delay;
    delay.tv_sec = sec;
    delay.tv_nsec = nsec;

    // nanosleep might return early due to signals, so we loop until the full time has passed
    while (nanosleep(&delay, &delay) == -1 && errno == EINTR) {
        // nanosleep interrupted by a signal, continue sleeping
        continue;
    }

    // Step 3: Capture the CPU clock cycles after sleeping
    uint64_t end_cycles;
    get_clocks(end_cycles);

    // Step 4: Return the difference between after-sleep and before-sleep cycles
    return end_cycles - start_cycles;
}

/* Return the number of clock cycles elapsed when waiting for
 * wait_time seconds using busy-waiting functions */
uint64_t get_elapsed_busywait(long sec, long nsec)
{
    // Step 1: Get the current time (begin_timestamp)
    struct timespec begin_timestamp, current_timestamp, wait_time;
    
    // Initialize the waiting time
    wait_time.tv_sec = sec;
    wait_time.tv_nsec = nsec;
    
    // Get the start time (begin_timestamp)
    clock_gettime(CLOCK_MONOTONIC, &begin_timestamp);

    // Step 2: Snapshot the current TSC (before busy-waiting)
    uint64_t start_cycles;
    get_clocks(start_cycles);
    
    // Step 3: Busy-wait loop until enough time has passed
    while (1) {
        // Get the current time
        clock_gettime(CLOCK_MONOTONIC, &current_timestamp);
        
        // Check if the elapsed time is greater than or equal to the wait_time
        struct timespec elapsed_time;
        elapsed_time.tv_sec = current_timestamp.tv_sec - begin_timestamp.tv_sec;
        elapsed_time.tv_nsec = current_timestamp.tv_nsec - begin_timestamp.tv_nsec;

        // Handle potential negative nanoseconds by borrowing from seconds
        if (elapsed_time.tv_nsec < 0) {
            elapsed_time.tv_sec -= 1;
            elapsed_time.tv_nsec += NANO_IN_SEC;
        }
        
        // Use timespec_cmp to compare elapsed_time and wait_time
        if (timespec_cmp(&elapsed_time, &wait_time) >= 0) {
            // Elapsed time is equal to or greater than wait time
            break;
        }
    }
    
    // Step 4: Snapshot the TSC again (after busy-waiting)
    uint64_t end_cycles;
    get_clocks(end_cycles);
    
    // Step 5: Return the difference in clock cycles
    return end_cycles - start_cycles;
}


/* Utility function to add two timespec structures together. The input
 * parameter a is updated with the result of the sum. */
void timespec_add (struct timespec * a, struct timespec * b)
{
	/* Try to add up the nsec and see if we spill over into the
	 * seconds */
	time_t addl_seconds = b->tv_sec;
	a->tv_nsec += b->tv_nsec;
	if (a->tv_nsec > NANO_IN_SEC) {
		addl_seconds += a->tv_nsec / NANO_IN_SEC;
		a->tv_nsec = a->tv_nsec % NANO_IN_SEC;
	}
	a->tv_sec += addl_seconds;
}

/* Utility function to compare two timespec structures. It returns 1
 * if a is in the future compared to b; -1 if b is in the future
 * compared to a; 0 if they are identical. */
int timespec_cmp(struct timespec *a, struct timespec *b)
{
	if(a->tv_sec == b->tv_sec && a->tv_nsec == b->tv_nsec) {
		return 0;
	} else if((a->tv_sec > b->tv_sec) ||
		  (a->tv_sec == b->tv_sec && a->tv_nsec > b->tv_nsec)) {
		return 1;
	} else {
		return -1;
	}
}

// /* Busywait for the amount of time described via the delay
//  * parameter */
// uint64_t busywait_timespec(struct timespec delay)
// {
// 	/* IMPLEMENT ME! (Optional but useful) */
// }
