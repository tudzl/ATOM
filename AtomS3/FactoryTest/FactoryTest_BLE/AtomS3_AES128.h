//Head for decoding AES-128 CCM messages
#ifndef BLE_AES128
#define BLE_AES128


//#if defined(BLE_AES128)
#define MAX_PLAINTEXT_LEN 64
#define AES_KEY_SIZE 128

#if defined(_M5ATOMS3_H_)|| defined(ESP32)
#include <pgmspace.h>
#endif

#include <mbedtls/ccm.h>



typedef struct AES_TestVector
{
    const char *name;
    uint8_t key[32];
    uint8_t plaintext[MAX_PLAINTEXT_LEN];
    uint8_t ciphertext[MAX_PLAINTEXT_LEN];
    uint8_t authdata[20];
    uint8_t iv[12];//nonce: device MAC, device type, frame cnt, ext. cnt
    uint8_t tag[16];//msg frame ending?
    uint8_t MAC[6] ; //MAC address
    size_t authsize;
    size_t datasize; //def 5
    size_t tagsize;
    size_t ivsize;
} AES_TestVector;



static AES_TestVector testVectorCCM_D9 PROGMEM = {
    .name        = "AES-128 CCM BLE ADV",
    .key         = {0x7B, 0x67, 0xF5, 0xAD, 0x19, 0xAE, 0x23, 0x3C,
                    0x02, 0x99, 0x3B, 0xC9, 0x4B, 0x70, 0xD0, 0x7F},
    .plaintext   = {0x06, 0x10, 0x02, 0xF0, 0x01}, //0x06->Hum!
    .ciphertext  = {0x75, 0xDD, 0xEB, 0x44, 0xA1},
    .authdata    = {0x11},
    .iv          = {0xD9, 0xAA, 0x47, 0x38, 0xC1, 0xA4, 0x5B, 0x05,
                    0x07, 0x00, 0x00, 0x00},////nonce: device MAC, device type, frame cnt, ext. cnt
    .tag         = {0x06, 0x26, 0xdf, 0xb5}, //ending?
    .MAC         = {0xA4, 0xC1, 0x38, 0x47, 0xAA, 0xD9}, //MAC address
    .authsize    = 1,
    .datasize    = 5,
    .tagsize     = 4,
    .ivsize      = 12
};
char* as_hex(unsigned char const* a, size_t a_size);
char* output_as_hex(unsigned char* a, size_t a_size);

#endif