//ESp32 S3 LYWSD03MMC decipher test V1.0 supported by Mbedtls
//Modified by Zell
#include <mbedtls/ccm.h>

#define ESP32
#if defined(ESP8266) || defined(ESP32)
#include <pgmspace.h>
#else
#include <avr/pgmspace.h>
#endif

#define MAX_PLAINTEXT_LEN 64
#define AES_KEY_SIZE 128

#include "M5AtomS3.h"

#define LCD_EN 0

typedef struct TestVector
{
    const char *name;
    uint8_t key[32];
    uint8_t plaintext[MAX_PLAINTEXT_LEN];
    uint8_t ciphertext[MAX_PLAINTEXT_LEN];
    uint8_t authdata[20];
    uint8_t iv[12];
    uint8_t tag[16];
    size_t authsize;
    size_t datasize;
    size_t tagsize;
    size_t ivsize;
} TestVector;

void decode(TestVector testVectorCCM);


static TestVector const testVectorCCM PROGMEM = {
    .name        = "AES-128 CCM BLE ADV",
    .key         = {0xE9, 0xEF, 0xAA, 0x68, 0x73, 0xF9, 0xF9, 0xC8,
                    0x7A, 0x5E, 0x75, 0xA5, 0xF8, 0x14, 0x80, 0x1C},
    .plaintext   = {0x04, 0x10, 0x02, 0xD3, 0x00},
    .ciphertext  = {0xDA, 0x61, 0x66, 0x77, 0xD5},
    .authdata    = {0x11},
    .iv          = {0x78, 0x16, 0x4E, 0x38, 0xC1, 0xA4, 0x5B, 0x05,
                    0x3D, 0x2E, 0x00, 0x00},////nonce: device MAC, device type, frame cnt, ext. cnt
    .tag         = {0x92, 0x98, 0x23, 0x52}, //?
    .authsize    = 1,
    .datasize    = 5,
    .tagsize     = 4,
    .ivsize      = 12
};


//书房？test ok!!!
//A4C13847AAD9, bind key:7b 67 f5 ad19ae233c 02 99 3b c9 4b 70 d0 7f
//payload:95FE58585b05 07 d9aa4738c1a4 75ddeb44a1 000000 0626df b5
static TestVector const testVectorCCM_D9 PROGMEM = {
    .name        = "AES-128 CCM BLE ADV",
    .key         = {0x7B, 0x67, 0xF5, 0xAD, 0x19, 0xAE, 0x23, 0x3C,
                    0x02, 0x99, 0x3B, 0xC9, 0x4B, 0x70, 0xD0, 0x7F},
    .plaintext   = {0x06, 0x10, 0x02, 0xF0, 0x01}, //0x06->Hum!
    .ciphertext  = {0x75, 0xDD, 0xEB, 0x44, 0xA1},
    .authdata    = {0x11},
    .iv          = {0xD9, 0xAA, 0x47, 0x38, 0xC1, 0xA4, 0x5B, 0x05,
                    0x07, 0x00, 0x00, 0x00},////nonce: device MAC, device type, frame cnt, ext. cnt
    .tag         = {0x06, 0x26, 0xdf, 0xb5}, //ending?
    .authsize    = 1,
    .datasize    = 5,
    .tagsize     = 4,
    .ivsize      = 12
};

// LYWSD03MMC, Address: a4:c1:38:81:7e:87
//58585b05 ac 877e8138c1a4 ba28d01951380700dbda3000
static TestVector const testVectorCCM_87 PROGMEM = {
    .name        = "AES-128 CCM BLE ADV",
    .key         = {0xE9, 0xEF, 0xAA, 0x68, 0x73, 0xF9, 0xF9, 0xC8,
                    0x7A, 0x5E, 0x75, 0xA5, 0xF8, 0x14, 0x80, 0x1C},
    .plaintext   = {0x04, 0x10, 0x02, 0xD3, 0x00},
    .ciphertext  = {0xDA, 0x61, 0x66, 0x77, 0xD5},
    .authdata    = {0x11},
    .iv          = {0x87, 0x7E, 0x81, 0x38, 0xC1, 0xA4, 0x5B, 0x05, 
                    0xAC, 0x2E, 0x00, 0x00},//nonce: device MAC, device type, frame cnt, ext. cnt
    .tag         = {0x92, 0x98, 0x23, 0x52},
    .authsize    = 1,
    .datasize    = 5,
    .tagsize     = 4,
    .ivsize      = 12
};

char* as_hex(unsigned char const* a, size_t a_size)
{
    char* s = (char*) malloc(a_size * 2 + 1);
    for (size_t i = 0; i < a_size; i++) {
        sprintf(s + i * 2, "%02X", a[i]);
    }
    return s;
}






void setup() {

  M5.begin(true, true, true,
             false);  
  if (LCD_EN)           
     M5.Lcd.printf("BLE AES-128 CCM decipher test\r\n");
  Serial.begin(115200);
  Serial.println("LYWSD03MMC decipher test V1.0 supported by Mbedtls");
  USBSerial.printf("whoAmI() = 0x%02x\n", M5.IMU.whoAmI());
  USBSerial.println("LYWSD03MMC decipher test V1.0 supported by Mbedtls");

  int ret = 0;
  uint8_t plaintext[MAX_PLAINTEXT_LEN];

  USBSerial.println("Test vector for BLE ADV packet");
  char * encoded;
  encoded = as_hex(testVectorCCM.key, AES_KEY_SIZE/8);
 USBSerial.printf("Key        : %s\n\r", encoded);
  free(encoded);
  encoded = as_hex(testVectorCCM.iv, testVectorCCM.ivsize);
 USBSerial.printf("Iv         : %s\n\r", encoded);
  free(encoded);
  encoded = as_hex(testVectorCCM.ciphertext, testVectorCCM.datasize);
 USBSerial.printf("Cipher     : %s\n\r", encoded);
  free(encoded);
  encoded = as_hex(testVectorCCM.plaintext, testVectorCCM.datasize);
 USBSerial.printf("Plaintext  : %s\n\r", encoded);
  free(encoded);
  encoded = as_hex(testVectorCCM.tag, testVectorCCM.tagsize);
 USBSerial.printf("Tag        : %s\n\r", encoded);
  free(encoded);
  
  mbedtls_ccm_context* ctx;
  ctx = (mbedtls_ccm_context*) malloc(sizeof(mbedtls_ccm_context));
  mbedtls_ccm_init(ctx);
  ret = mbedtls_ccm_setkey(ctx,
    MBEDTLS_CIPHER_ID_AES,
    testVectorCCM.key,
    AES_KEY_SIZE
  );
  if (ret) {
   USBSerial.println("CCM setkey failed.");
  }
  ret = mbedtls_ccm_auth_decrypt(ctx,
    testVectorCCM.datasize,
    testVectorCCM.iv,
    testVectorCCM.ivsize,
    testVectorCCM.authdata,
    testVectorCCM.authsize,
    testVectorCCM.ciphertext,
    plaintext,
    testVectorCCM.tag,
    testVectorCCM.tagsize 
  );

  if (ret) {
    if (ret == MBEDTLS_ERR_CCM_AUTH_FAILED) {
     USBSerial.println("Authenticated decryption failed.");
    } else if (ret == MBEDTLS_ERR_CCM_BAD_INPUT) {
     USBSerial.println("Bad input parameters to the function.");
    } else if (ret == MBEDTLS_ERR_CCM_HW_ACCEL_FAILED) {
     USBSerial.println("CCM hardware accelerator failed."); 
    } 
  } 
  else {
   USBSerial.println("Decryption successful");
   
  }
  
  encoded = as_hex(plaintext, testVectorCCM.datasize);
  USBSerial.printf("Plaintext  : %s \n\r", encoded);
  
  USBSerial.println("Decryption ends here!");
  free(encoded);

  mbedtls_ccm_free(ctx);  

  USBSerial.println("-------------test data ends here--------------------------------"); 
}

void loop() {

  decode(testVectorCCM_D9);
  delay(1000);
}


void decode(TestVector testVectorCCM){
  int ret = 0;
  uint8_t plaintext[MAX_PLAINTEXT_LEN];
  char * encoded;
  char * decoded;
  uint16_t value=0;

  USBSerial.println("Original Test vector contents for BLE ADV packet decoding:");
 
  encoded = as_hex(testVectorCCM.key, AES_KEY_SIZE/8);
  USBSerial.printf("Key        : %s\n\r", encoded);
  free(encoded);
  encoded = as_hex(testVectorCCM.iv, testVectorCCM.ivsize);
 USBSerial.printf("Iv         : %s\n\r", encoded);
  free(encoded);
  encoded = as_hex(testVectorCCM.ciphertext, testVectorCCM.datasize);
 USBSerial.printf("Cipher     : %s\n\r", encoded);
  free(encoded);
  encoded = as_hex(testVectorCCM.plaintext, testVectorCCM.datasize);
 USBSerial.printf("Plaintext  : %s\n\r", encoded);
  free(encoded);
  encoded = as_hex(testVectorCCM.tag, testVectorCCM.tagsize);
 USBSerial.printf("Tag        : %s\n\r", encoded);
  free(encoded);
 USBSerial.println(">:start decoding...");
  mbedtls_ccm_context* ctx;
  ctx = (mbedtls_ccm_context*) malloc(sizeof(mbedtls_ccm_context));
  mbedtls_ccm_init(ctx);
  ret = mbedtls_ccm_setkey(ctx,
    MBEDTLS_CIPHER_ID_AES,
    testVectorCCM.key,
    AES_KEY_SIZE
  );
  if (ret) {
   USBSerial.println("CCM setkey failed.");
  }
  ret = mbedtls_ccm_auth_decrypt(ctx,
    testVectorCCM.datasize,
    testVectorCCM.iv,
    testVectorCCM.ivsize,
    testVectorCCM.authdata,
    testVectorCCM.authsize,
    testVectorCCM.ciphertext,
    plaintext,
    testVectorCCM.tag,
    testVectorCCM.tagsize 
  );

  if (ret) {
    if (ret == MBEDTLS_ERR_CCM_AUTH_FAILED) {
     USBSerial.println("Authenticated decryption failed.");
    } else if (ret == MBEDTLS_ERR_CCM_BAD_INPUT) {
     USBSerial.println("Bad input parameters to the function.");
    } else if (ret == MBEDTLS_ERR_CCM_HW_ACCEL_FAILED) {
     USBSerial.println("CCM hardware accelerator failed."); 
    } 
  } 
  else {
   USBSerial.println("-------Decryption successful-----------");
   if (LCD_EN) 
    M5.Lcd.printf("Decryption successful\r\n");
  }
  
  decoded = as_hex(plaintext, testVectorCCM.datasize);// (text, 5), issue for Akku info(4bytes)?

  USBSerial.printf("Plaintext : %s\n\r", decoded);
  if (LCD_EN) {
    M5.Lcd.printf("Plaintext :\n\r");
    M5.Lcd.printf("%s\n\r",decoded);
  }

  
  /*
  char type_flag = plaintext[0];
  char charValue[5];
  float T_Value,H_Value,Akku_Value;
  
  
    switch (type_flag) {
          case 0x04: //T
            sprintf(charValue, "%02X%02X", plaintext[4], plaintext[3]);
            value = strtol(charValue, 0, 16);
            T_Value = value/100;
            USBSerial.printf(">:current_temperature: %5.2f",T_Value);
              //current_temperature = (float)value / 10;

            break;
          case 0x06: //Hum
            sprintf(charValue, "%02X%02X", plaintext[4], plaintext[3]);
            value = strtol(charValue, 0, 16);
            H_Value = value/10;
            USBSerial.printf(">:current_Humidty: %3.1f %%\r\n",H_Value);
            if (LCD_EN) {
              M5.Lcd.printf(">:current_Humidty:\r\n");
              M5.Lcd.printf(">:%3.1f %%\r\n",H_Value);
            }


            break;
          case 0x0A://Akku
            sprintf(charValue, "%02X%02X", plaintext[4], plaintext[3]);
            value = strtol(charValue, 0, 16);
            Akku_Value = value/1000;
            USBSerial.printf(">:current_akku: %4.3f",Akku_Value);

            break;
    }

  */
  free(encoded);
  free(decoded);
  //free(value);



  mbedtls_ccm_free(ctx);  
  USBSerial.println("Decode process ended!");
}
