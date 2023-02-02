#include "AtomS3_AES128.h"
#include <stdio.h>

char* as_hex(unsigned char const* a, size_t a_size)
{
    char* s = (char*) malloc(a_size * 2 + 1);
    for (size_t i = 0; i < a_size; i++) {
        sprintf(s + i * 2, "%02X", a[i]);
    }
    return s;
}
