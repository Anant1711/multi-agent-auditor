#include <stdio.h>
#include <stdlib.h>

void process_data(int *data) {
    if (data == NULL) return;
    
    // MISRA Violation: dynamic memory allocation (Rule 21.3)
    int *buffer = (int*)malloc(10 * sizeof(int));
    
    // MISRA Violation: pointer arithmetic (Rule 18.4)
    buffer = buffer + 1;
    
    // MISRA Violation: unsafe casting
    float f = (float)(*data);
    
    printf("Processed %f\n", f);
}

int main() {
    int val = 42;
    process_data(&val);
    return 0;
}
