//Factory test demo for ATOM_S3 unit, modified by Zell
//V1.5 supported BLE sensor broadcast msg AES-128 CCM decoding, added standalone Thermal_APP_loop, 2.Feb.2023
//V1.4 added BLE sensor broadcast test mode, sensor mac:'A4:C1:38:47:AA:D9'  model:'LYWSD03MMC'    
//V1.3 added fire flame loop code(based on fiery.ino), 18.Jan.2023
//V1.2 added Fillarc boot animation
//V1.1, added MU6886 temp. display
//last edit 18.1.2023 by Zell, tudzl@hotmail.de
//Original code is from m5stack official release for factory test code
#include <Arduino.h>
#include <M5AtomS3L.h>
#include <driver/rmt.h>
#include <WiFi.h>
#include <Wire.h>
#include <BLEClient.h>
#include <I2C_MPU6886.h>
#include <ir_tools.h>
#include <led_strip.h>
//#include <MahonyAHRS.h>
#include "AtomS3_AES128.h"
#include <BLEDevice.h>
#include <BLEUtils.h>
#include <BLEServer.h>
//added by zell to test Mijia sensors
#include <BLEScan.h>
#include <BLEAdvertisedDevice.h>

#define LGFX_USE_V1
#include "LovyanGFX.hpp"
#include <sstream>


#define DEVICE_NAME         "ATOM-S3"
#define SERVICE_UUID        "4fafc201-1fb5-459e-8fcc-c5c9c331914b"
#define CHARACTERISTIC_UUID "beb5483e-36e1-4688-b7f5-ea07361b26a8"

#define NE0_RMT_TX_CHANNEL RMT_CHANNEL_0
#define NEO_GPIO           35
#define NUM_LEDS           1
#define IR_RMT_TX_CHANNEL  RMT_CHANNEL_2
#define IR_GPIO            12

#define LCD_BACKLIGHT_GPIO 16
#define BTN_GPIO 41
#define IMU_ADDR 0x68




//AES
#define MAX_PLAINTEXT_LEN 64
#define AES_KEY_SIZE 128


enum { DEV_UNKNOWN, ATOM_S3, ATOM_S3_LCD };

class M5ATOMS3_GFX : public lgfx::LGFX_Device {
    lgfx::Panel_GC9107 _panel_instance;
    lgfx::Bus_SPI _bus_instance;

   public:
    M5ATOMS3_GFX(void) {
        {
            auto cfg = _bus_instance.config();

            cfg.pin_mosi   = 21;
            cfg.pin_miso   = -1;
            cfg.pin_sclk   = 17;
            cfg.pin_dc     = 33;
            cfg.freq_write = 40000000;

            _bus_instance.config(cfg);
            _panel_instance.setBus(&_bus_instance);
        }
        {
            auto cfg = _panel_instance.config();

            cfg.invert       = false;
            cfg.pin_cs       = 15;
            cfg.pin_rst      = 34;
            cfg.pin_busy     = -1;
            cfg.panel_width  = 128;
            cfg.panel_height = 128;
            cfg.offset_x     = 0;
            cfg.offset_y     = 32;

            _panel_instance.config(cfg);
        }
        // {
        //     auto cfg = _light_instance.config();

        //     cfg.pin_bl      = 18;
        //     cfg.invert      = true;
        //     cfg.freq        = 44100;
        //     cfg.pwm_channel = 7;

        //     _light_instance.config(cfg);
        //     _panel_instance.setLight(&_light_instance);
        // }

        setPanel(&_panel_instance);
    }
};

//GUI
static M5ATOMS3_GFX lcd;
static LGFX_Sprite sprite1(&lcd);
static LGFX_Sprite sprite2(&lcd);
static LGFX_Sprite sprite3(&lcd);
static LGFX_Sprite sprite4(&lcd);
static LGFX_Sprite sprite_fullcreen(&lcd);
static I2C_MPU6886 imu(I2C_MPU6886_DEFAULT_ADDRESS, Wire);
static led_strip_t *strip       = NULL;
static ir_builder_t *ir_builder = NULL;
static uint8_t Screen_center_x = 128/2;
static uint8_t Screen_center_y = 128/2;
static uint8_t circle_r = 16;

#define SCAN_TIME  6 //BLE扫描的间隔10秒
#define BLE_AES128
#define BLE_MAC_Filter 1
#define BLE_debug_show 0
boolean BLE_boradcast_listen_EN = true;
boolean METRIC = true; //不需要公制单位的话设为：false 
BLEScan *pBLEScan;
static float  current_humidity = 0;
float  previous_humidity = 0;
boolean T_valid = 0;
boolean H_valid = 0;
boolean A_valid = 0;
boolean thermal_meter_mode = false;
static float current_temperature = 0;
float previous_temperature = 0;
uint8_t sensor_raw_buf[3];
float Akku_SOC =0; //0-100%
float CelciusToFahrenheit(float Celsius);
String convertFloatToString(float f);
char* output_as_hex(unsigned char* a, size_t a_size);
//boolean BLE_broadcast_debug_mode_EN = true;
boolean BLE_broadcast_debug_mode_EN = false;
boolean BLE_broadcast_MAC_Filter_EN = true;
const uint16_t BLE_THA_braodcast_flag = 0x5858; //3058 no use
uint8_t decode(AES_TestVector testVectorCCM, uint8_t *sensor_raw_val);
class MyAdvertisedDeviceCallbacks : public BLEAdvertisedDeviceCallbacks {
    void onResult(BLEAdvertisedDevice advertisedDevice)
    {
        if(BLE_boradcast_listen_EN){

            if( advertisedDevice.haveName()&& BLE_broadcast_debug_mode_EN) {
                USBSerial.printf("\n\nAdvertised Device: %s\n", advertisedDevice.toString().c_str());
                USBSerial.println("*********************");
                }
            }

        //HUAWEI Band HR-4C8, BAND6
        if (advertisedDevice.haveName() && !advertisedDevice.getName().compare("HUAWEI Band HR-4C8")) {
            USBSerial.print("******Band6 heart rate:******");
            std::string BandServiceData = advertisedDevice.getServiceData();
            uint8_t cBandServiceData[100];
            char charBandServiceData[100];
            BandServiceData.copy((char *)cBandServiceData, BandServiceData.length(), 0);
            for (int i = 0; i < BandServiceData.length(); i++) {
            sprintf(&charBandServiceData[i * 2], "%02x", BandServiceData[i]);

            std::stringstream ss_band;
            ss_band << charBandServiceData; //same as raw data
            USBSerial.print("Payload:");
            USBSerial.println(ss_band.str().c_str());

        
            }
        }

        if (advertisedDevice.haveName() && advertisedDevice.haveServiceData() && !advertisedDevice.getName().compare("LYWSD03MMC")) {
            USBSerial.print("\r\n******Temperature/Humidty BLE:******\r\n");
        std::string strServiceData = advertisedDevice.getServiceData();
        uint8_t cServiceData[100];
        char charServiceData[100];
        //advertisedDevice.getServiceData()-->cServiceData-->charServiceData
        strServiceData.copy((char *)cServiceData, strServiceData.length(), 0);

        for (int i = 0; i < strServiceData.length(); i++) {
          sprintf(&charServiceData[i * 2], "%02x", cServiceData[i]);
        }

        if(BLE_debug_show){
            USBSerial.printf("Advertised Device_%s\n", advertisedDevice.toString().c_str());
            //USBSerial.printf("msg:%s \r\n", advertisedDevice.getServiceData().c_str());

        }
        else {
            USBSerial.printf("Advertised Device_%s\n", advertisedDevice.getAddress().toString().c_str() ) ;
        }
        uint8_t device_fit =0;
       if (BLE_MAC_Filter){
            if (advertisedDevice.getAddress().equals(testVectorCCM_D9.MAC) ){
             USBSerial.printf(">>:Device MAC fit!\r\n");
             device_fit =1;
            }

       }
       
       if(device_fit){
        USBSerial.printf("#>:Last sensor T: %4.2f\r\n",current_temperature);
        USBSerial.printf("#>:Last sensor H: %3.1f\r\n",current_humidity);
        USBSerial.printf("#>:Last Akku SOC: %4f mV\r\n",Akku_SOC);
        std::stringstream ss;
        //not used
       // ss << "fe95" << charServiceData; //ori
       //ss << "95FE" << charServiceData; //same as raw data  95FE58585b0507d9aa4738c1a475ddeb44a10000000626dfb5
       ss << charServiceData;
       //Payload:5858 5b05 07 d9aa4738c1a4 75ddeb44a1 000000 0626df b5
       //                  4                11        16      19    22  
        USBSerial.print("Payload:"); 
        USBSerial.println(ss.str().c_str());
        //char eventLog[256];
        unsigned long value, value2;
        unsigned char charValue[5] = {0,};
        uint8_t MAC_tag[4];
        uint16_t payloadtype= 0x0000;
        uint8_t frame_cnt = 0;
        uint8_t Ext_cnt [3];
        //parse msg for decoding vector:
        payloadtype = (uint16_t) (cServiceData[0]<<8)&0xff00 ;
        payloadtype+= (uint8_t) cServiceData[1];
        //USBSerial.printf(">>:payloadtype : %02X, %02X\n\r", cServiceData[0], cServiceData[1]);
        USBSerial.printf(">>:payloadtype : %04X\r\n", payloadtype);
        if (BLE_THA_braodcast_flag==payloadtype){
            USBSerial.printf("\r\n>>:BLE Encripted frame detected:-------------\r\n");
            frame_cnt = cServiceData[4];

            for(uint8_t idx = 0; idx<5;idx++){
                charValue[idx]=cServiceData[11+idx];
                //ciphertext
                if(idx<4){
                    MAC_tag[idx]= cServiceData[19+idx];
                }
                if(idx<3)
                    Ext_cnt[idx]= cServiceData[16+idx]; 
            } 
            char * encoded;
            encoded = output_as_hex(charValue, testVectorCCM_D9.datasize); //issue here!!!
            //encoded = as_hex(testVectorCCM_D9.ciphertext, testVectorCCM_D9.datasize);
            USBSerial.printf(">>:BLE Cipher  : %s\r\n", encoded);
            free(encoded);
            //sprite4.printf("BLE:%02X%02X-%02X%02X%02X%02X%02X", charServiceData[0], charServiceData[1],charValue[0],charValue[1],charValue[2],charValue[3],charValue[4]);

            //pass data to vector
            testVectorCCM_D9.iv[8]=frame_cnt;
            for(uint8_t idx = 0; idx<5;idx++){
                testVectorCCM_D9.ciphertext[idx] = charValue[idx];
                //ciphertext
                if(idx<4){
                    testVectorCCM_D9.tag[idx]=MAC_tag[idx];
                }
                if(idx<3)
                    testVectorCCM_D9.iv[9+idx]=Ext_cnt[idx]; 
            } 
        
            //decode(testVectorCCM_D9);
            decode(testVectorCCM_D9,sensor_raw_buf);
            payloadtype = sensor_raw_buf[2]<<8;
            payloadtype = payloadtype+sensor_raw_buf[1];
            //for tests
            
            if(0x04==sensor_raw_buf[0])
               T_valid =true;
            else if(0x06==sensor_raw_buf[0])
               H_valid =true;
            else if(0x0A==sensor_raw_buf[0])
               A_valid =true;
            /*
            //USBSerial.printf(">>:proc B\r\n");
            //current_temperature = (float) (value/100.0);
            //current_temperature = (float) value;
            if(T_valid){
              current_temperature = payloadtype/10.0;
              T_valid = false;
            }
            if(H_valid){
              current_humidity = payloadtype/10.0;
              H_valid = false;
            }
            
            */

            sprite4.clear();
            sprite4.setCursor(0,0);
            sprite4.setTextSize(2);
            sprite4.printf("%3.1fC,%3.1f%%", current_temperature,current_humidity);
            sprite4.pushSprite(0, 112);

            if(A_valid){
              Akku_SOC = payloadtype/1000.0;
              A_valid = false;
              sprite4.clear();
              sprite4.setCursor(0,0);
              sprite4.printf("Akk:%3.1f mV", Akku_SOC);
              sprite4.pushSprite(0, 16);
            }



        }
        else {
                USBSerial.printf(">>:NOT a BLE Encripted frame!\n\r");
        }

       }

        /*
        //5th and 21th
        switch (cServiceData[4]) {
          case 0x04:
            sprintf(charValue, "%02X%02X", cServiceData[15], cServiceData[14]);
            value = strtol(charValue, 0, 16);
            if (METRIC)
            {
              current_temperature = (float)value / 10;
            } else
            {
              current_temperature = CelciusToFahrenheit((float)value / 10);
            }
            break;
          case 0x09:
            sprintf(charValue, "%02X%02X", cServiceData[15], cServiceData[14]);
            value = strtol(charValue, 0, 16);
            current_humidity = (float)value / 10;
           USBSerial.printf("HUMIDITY_EVENT:");
           USBSerial.printf(charValue, value);
           USBSerial.println();
            break;
          case 0x17: //0x16
            sprintf(charValue, "%02X", cServiceData[14]);
            value = strtol(charValue, 0, 16);
           USBSerial.printf("BATTERY_EVENT:");
           USBSerial.printf(charValue, value);
           USBSerial.println();
            break;
          case 0x16:
            sprintf(charValue, "%02X%02X", cServiceData[15], cServiceData[14]);
            value = strtol(charValue, 0, 16);
            if (METRIC)
            {
              current_temperature = (float)value / 10;
            } else
            {
              current_temperature = CelciusToFahrenheit((float)value / 10);
            }
           USBSerial.printf("TEMPERATURE_EVENT:");
           USBSerial.printf(charValue, value);
           USBSerial.println();
            sprintf(charValue, "%02X%02X", cServiceData[17], cServiceData[16]);
            value2 = strtol(charValue, 0, 16);
            current_humidity = (float)value2 / 10;
           USBSerial.printf("HUMIDITY_EVENT:" );
           USBSerial.printf(charValue, value2);
           USBSerial.println();
            break;
        }
        */
      }
    }
};

void initBluetooth_BLE()
{
  BLEDevice::init("");
  pBLEScan = BLEDevice::getScan(); //create new scan
  pBLEScan->setAdvertisedDeviceCallbacks(new MyAdvertisedDeviceCallbacks());
  pBLEScan->setActiveScan(true); //active scan uses more power, but get results faster
  pBLEScan->setInterval(60);
  pBLEScan->setWindow(48);
}
#include "cube.hpp"

extern const unsigned char ATOMS3[];

static void neopixel_init(void);
static void update_neopixel(uint8_t r, uint8_t g, uint8_t b);
static void ir_tx_init(void);
static void ir_tx_test(void);
static void ble_task(void *);
static void ble_task2(void *);
static void wifi_task(void *);
static void BLE_Sensor_task(void *);
uint8_t WIFI_EN = 0;
uint8_t BT_EN = 0;
static uint8_t device_type              = DEV_UNKNOWN;
static uint8_t atom_s3_gpio_list[8]     = {14, 17, 36, 37, 38, 39, 40, 42};
static uint8_t atom_s3_lcd_gpio_list[6] = {14, 17, 36,
                                           37, 40, 42};  // 38, 29 use for IMU
static time_t last_io_reverse_time      = 0;
static time_t last_imu_print_time       = 0;
static time_t last_ir_send_time         = 0;
static time_t last_ble_change_time      = 0;
static time_t last_udp_broadcast_time   = 0;
static time_t last_wifi_scan_time       = 0;

static bool btn_pressd_flag = true;
static int btn_pressd_count = 0;
uint8_t delay_cnt = 1;

static uint32_t ir_addr       = 0x00;
static uint8_t ir_cmd         = 0x20;
static rmt_item32_t *ir_items = NULL;
static size_t ir_length       = 0;

const char *udp_ap_broadcast_addr = "192.168.4.255";
const int udp_broadcast_port      = 3333;

static uint8_t neopixel_color_index   = 0;
static char neopixel_color_name[][6]  = {"Red", "Green", "Blue", "White",
                                         "Black"};
static uint32_t neopixel_color_list[] = {0xFF0000, 0x00FF00, 0x0000FF, 0xFFFFFF,
                                         0x000000};
static uint8_t mac_addr[6];
static char name_buffer[24];
static char PW_buffer[8];


//void decode(AES_TestVector testVectorCCM);

uint32_t circle_color_list[8] = {0xcc3300, 0xff6633, 0xffff66, 0x33cc33,
                                 0x00ffff, 0x0000ff, 0xff3399, 0x990099};
static void boot_animation(void) {
   
    for (size_t c = 0; c < 8; c++) {
        lcd.fillArc(0, lcd.height(), c * 23, (c + 1) * 23, 270, 0,
                           circle_color_list[c]);
        delay(300);
    }
    

    for (uint8_t i = 0; i < 10; i++){
        if (digitalRead(BTN_GPIO) == LOW) {
             delay(5);
        if (digitalRead(BTN_GPIO) == LOW) {
             delay_cnt++;
        }
        delay(45);

    }//500ms

    }
    //addtional 2 to 20 s delay
    USBSerial.printf("Total logo show delay with %d seconds\r\n", delay_cnt*2);
    delay(delay_cnt*2000); //need improve
}

//Fire Flame vars and functions
#define MAXPAL 4

//128*128=16384
uint16_t matrix[16384 + 128]; //why? addtional pixels to heat up bottom pixels.
uint16_t backBuffer565[16384];
uint16_t color[200 * (MAXPAL + 1)]; // 4 palettes and current pallet space.87,   4 color modes of Flames
uint8_t pallet = 1;
uint8_t maxPal = 0;
uint32_t XORRand = 0;

// A standard XOR Shift PRNG but with a floating point twist.
// https://www.doornik.com/research/randomdouble.pdf
float random2(){
  XORRand ^= XORRand << 13;
  XORRand ^= XORRand >> 17;
  XORRand ^= XORRand << 5;
  return (float)((float)XORRand * 2.32830643653869628906e-010f);
}

void makePallets(){
  // 0b00011111 00000000 : blue
  // 0b00000000 11111000 : red
  // 0blll00000 00000hhh : green
  // Flame effect pallet
  for (int i = 0; i < 64; i++){
    uint8_t r = i * 4;
    uint8_t g = 0;
    uint8_t b = 0;
    color[200 + i] = ((b & 0b11111000) << 8) | ((g & 0b11111100) << 3) | (r >> 3);
    r = 255;
    g = i * 4;
    b = 0;
    color[200 + i + 64] = ((b & 0b11111000) << 8) | ((g & 0b11111100) << 3) | (r >> 3);
    r = 255;
    g = 255;
    b = i * 2;
    color[200 + i + 128] = ((b & 0b11111000) << 8) | ((g & 0b11111100) << 3) | (r >> 3);
  }
  uint8_t r = 255;
  uint8_t g = 255;
  uint8_t b = 64 * 2;
  for (int i = 192; i < 200; i++){
    color[200 + i] = ((b & 0b11111000) << 8) | ((g & 0b11111100) << 3) | (r >> 3);
  }   
  // Cold flame effect pallet
  for (int i = 0; i < 200; i++){
    uint8_t r = (i > 100) ? (float)(i-100) * 1.775f: i / 3.0f;
    uint8_t g = (i > 100) ? (float)(i-100) * 1.775f: i / 3.0f;
    uint8_t b = (float)i * 1.275f;
    color[400 + i] = ((b & 0b11111000) << 8) | ((g & 0b11111100) << 3) | (r >> 3);
  }
  // Black and white pallet
  for (int i = 0; i < 200; i++){
    uint8_t r = (float)i * 1.275f;
    uint8_t g = (float)i * 1.275f;
    uint8_t b = (float)i * 1.275f;
    color[600 + i] = ((b & 0b11111000) << 8) | ((g & 0b11111100) << 3) | (r >> 3);
  }
  // Green flame effect pallet
  for (int i = 0; i < 200; i++){
    uint8_t r = (i > 100) ? (float)(i-100) * 1.175f: i / 5.0f;
    uint8_t g = (float)i * 1.275f;
    uint8_t b = (i > 100) ? (float)(i-100) * 1.775f: i / 3.0f;
    color[800 + i] = ((b & 0b11111000) << 8) | ((g & 0b11111100) << 3) | (r >> 3);
  }
}

void usePalette(uint8_t pal){
  uint16_t palOffset = pal * 200;
  for(uint16_t i = 0; i < 200; i++){
    color[i] = color[palOffset + i];
  }
}

void prevPal(){
  if(--pallet == 0) pallet = MAXPAL;
  usePalette(pallet);
}

void nextPal(){
  if(++pallet == MAXPAL + 1) pallet = 1;
  usePalette(pallet);
}

void Flame_init(){

  M5.begin(true, true, false, false);// bool LCDEnable, bool USBSerialEnable, bool I2CEnable, bool LEDEnable
  USBSerial.println("");
  USBSerial.println("M5AtomS3 Flame app init...");
  USBSerial.println("");
  XORRand = esp_random();
  makePallets();
  usePalette(1);
  WiFi.disconnect();


  sprite3.clear();
  sprite3.setCursor(0, 0);
  sprite3.setTextSize(2);
  sprite3.setTextColor(TFT_SKYBLUE);
  sprite3.printf("Atom Flame Mode!\r\n");
  sprite3.pushSprite(0, 0); 

  /*
  //test
  //sprite1.deletePalette();
  sprite1.createSprite(128,128);
  sprite1.setTextWrap(true);
  sprite1.setTextSize(2);
  sprite1.setTextColor(TFT_SKYBLUE);
  sprite1.printf(" Atom Flame Mode!\r\n");
  sprite1.pushSprite(0, 0); 

    */
  sprite1.deleteSprite();
  sprite2.deleteSprite();
  //sprite3.deleteSprite();
  sprite4.deleteSprite();

  /*

   sprite_fullcreen.setColorDepth(16);
   sprite_fullcreen.createSprite(128, 128);
        sprite_fullcreen.setTextWrap(false);
        sprite_fullcreen.setTextScroll(false);
        sprite_fullcreen.setTextSize(1.3);
        sprite_fullcreen.setTextColor(TFT_SKYBLUE);
  lcd.setCursor(0,0);

    sprite_fullcreen.setCursor(0, 0);
    sprite_fullcreen.clear();
    sprite_fullcreen.printf(" Atom Flame Mode!\r\n");
    //sprite_fullcreen.clear();
    sprite_fullcreen.pushSprite(0,0);
    */
    delay(500);
}


void Flame_APP_loop(){
  //M5.update();
  uint8_t palette_height = 108; //127,128 not working,104 ok, RAM issue?
  sprite3.createSprite(128, palette_height);
  sprite3.clear();
  sprite3.pushSprite(0, 128-palette_height); 
  USBSerial.printf("Created 128*%d sprite! \r\n",palette_height);

  uint16_t pixel_len = 128*palette_height;
  uint16_t pixel_start = 16384 -pixel_len;
  while(1){

    sprite3.clear();
    sprite3.setCursor(0, 0);


    //not working
    //if (M5.Btn.wasReleased()) {
    //if (M5.Btn.wasPressed()) {

    //    nextPal();
   // }
    //press Btn to switch Palette/color
    if (digitalRead(BTN_GPIO) == LOW) {
             delay(5);
        if (digitalRead(BTN_GPIO) == LOW) {
             nextPal();
        }
    }
    // Heat up the bottom of the fire.
    for (uint16_t i = 16384; i < 16384 + 127; i++) {
        matrix[i] = 300.0f * random2();
    }
    // Nasty floating point maths to produce the billowing and nice blending.
    // Floats are accelerated on the ESP32 S3.
    for (uint16_t i = 0; i < 16384; i++) {
        uint16_t pixel = (float)i + 128.0f - random2() + 0.8f;
        float sum = matrix[pixel] + matrix[pixel + 1] + matrix[pixel - 128] + matrix[pixel - 128 + 1];
        uint16_t value = sum * 0.49f * random2() + 0.5f;
        matrix[i] = value;
        if(value > 199) value = 199;
        backBuffer565[i] = color[value];
        //lcd.drawPixel 
    }
    // M5.Lcd.drawBitmap(0, 0, 128, 128, backBuffer565);
     /*
    
    sprite_fullcreen.clear();
    sprite_fullcreen.pushSprite(0,0);
    sprite_fullcreen.setCursor(0,0);
        */
    //sprite3.writePixels(backBuffer565, 16384/2, false );//(pixelcopy_t* param, uint32_t len, bool use_dma) override;
    //sprite3.pushSprite(0, 64); 
    Lcd.pushPixels(backBuffer565, pixel_len); //works ok for current sprite!
    //Lcd.pushPixels(backBuffer565, 16384);//issue: only draw in current sprite(1 to 4) window
    //Lcd.pushPixelsDMA(backBuffer565, 16384);//issue: only draw in current sprite window
    //sprite_fullcreen.pushSprite(0,0);
    //lcd.setCursor(0,0);
    //Lcd.writePixels(backBuffer565, 16384,0); //issue here!
    //lcd.writePixelsDMA
    //lcd.pushPixels  
     delay(10);
  }
}

void Thermal_APP_loop(){

  uint8_t Btn_cnt = 0;


  //lcd.width();
        uint8_t palette_height = 100; //127,128 not working,104 ok, RAM issue?
        uint8_t GUI_T_pos_Y = 8; //127,128 not working,104 ok, RAM issue?
        uint8_t GUI_T_pos_X = 8; //127,128 not working,104 ok, RAM issue?
        uint8_t GUI_H_pos_y = palette_height/2-4; 
        uint8_t GUI_IMU_pos_y = palette_height-12; 
        uint8_t GUI_Akku_pos_y = 80; 
        sprite2.clear();
        sprite2.setCursor(0, 0);
        //sprite2.printf("Thermal_Meter\r\n");
        sprite2.pushSprite(0, 48);
         lcd.clear(TFT_BLACK);
         lcd.drawCenterString("BLE Thermal", lcd.width()/2, 1);
        //lcd.setCursor(25, 16);
        //lcd.printf("%08X", ir_addr);
        lcd.setColor(TFT_GOLD);
        lcd.drawFastHLine(0, 22, 128);
        
    sprite3.createSprite(128, palette_height);
    sprite3.clear();
    sprite3.pushSprite(0, 128-palette_height); 
    USBSerial.printf("Created 128*%d sprite! \r\n",palette_height);
        float t;
  while(1){

        //press Btn to switch Palette/color
    if (digitalRead(BTN_GPIO) == LOW) {
             delay(5);
        if (digitalRead(BTN_GPIO) == LOW) {
             Btn_cnt++;
        }
    }
    if (3<Btn_cnt){
      USBSerial.printf("#>>:Btn_cnt reached %d, exit Thermal_APP_loop now! \r\n",Btn_cnt);
      break;
    }


    sprite3.clear();
    sprite3.setTextColor(TFT_ORANGE);
    sprite3.setTextSize(3);
    sprite3.setCursor(GUI_T_pos_X,GUI_T_pos_Y);
    //sprite3.printf("%4.2f ℃" , current_temperature);
    sprite3.printf("%4.2f C" , current_temperature);
   //sprite4.printf("%3.1fC,%3.1f%%", current_temperature,current_humidity);

   sprite3.setTextColor(TFT_SKYBLUE);
   sprite3.setCursor(GUI_T_pos_X,GUI_H_pos_y);
   sprite3.printf("%3.1f %%\r\n" , current_humidity);
   sprite3.setTextSize(1.4);
   imu.getTemp(&t);

   sprite3.setCursor(0,GUI_IMU_pos_y);
   sprite3.setTextColor(TFT_VIOLET);
   sprite3.printf("IMU_T: %5.2f C\r\n",t);

   sprite3.pushSprite(0, lcd.height()-palette_height); 
   delay(500);//if refresh too fast, will cause LCD flickring
   }

    
}


void setup() {
    USBSerial.begin(115200);
    delay(200);
    USBSerial.println("M5AtomS3 intial version, FW build date: 18.Jan.2023 by Zell");
    delay(200);
    USBSerial.println("FW last update  date: 2.Feb.2023 by Zell");
    USBSerial.println("M5AtomS3 Factory Test+BLE demo V1.4 is booting...");
    esp_efuse_mac_get_default(mac_addr);
    ir_addr = (mac_addr[2] << 24) | (mac_addr[3] << 16) | (mac_addr[4] << 8) |
              mac_addr[5];

    sprintf(name_buffer, DEVICE_NAME "-%02X%02X%02X%02X%02X%02X",
            MAC2STR(mac_addr));

    // 判断型号
    Wire.begin(38, 39);
    Wire.beginTransmission(IMU_ADDR);
    if (Wire.endTransmission() == 0) {
        device_type = ATOM_S3_LCD;
    } else {
        device_type = ATOM_S3;
    }

    // Neo Pixel LED
    neopixel_init();
    update_neopixel((neopixel_color_list[neopixel_color_index] >> 16 & 0xFF),
                    (neopixel_color_list[neopixel_color_index] >> 8 & 0xFF),
                    (neopixel_color_list[neopixel_color_index] & 0xFF));

    // IO初始化
    if (device_type == ATOM_S3) {
        for (size_t i = 0; i < sizeof(atom_s3_gpio_list); i++) {
            pinMode(atom_s3_gpio_list[i], OUTPUT);
            digitalWrite(atom_s3_gpio_list[i], LOW);
        }
        Wire.end();
    } else if (device_type == ATOM_S3_LCD) {
        for (size_t i = 0; i < sizeof(atom_s3_lcd_gpio_list); i++) {
            pinMode(atom_s3_lcd_gpio_list[i], OUTPUT);
            digitalWrite(atom_s3_lcd_gpio_list[i], LOW);
        }
    }

    // ATOM S3 LCD初始化
    if (device_type == ATOM_S3_LCD) {
        // LCD backlight
        pinMode(LCD_BACKLIGHT_GPIO, OUTPUT);
        digitalWrite(LCD_BACKLIGHT_GPIO, HIGH);

        lcd.init();
        lcd.setTextSize(1.8);
        lcd.setTextWrap(false);
        lcd.setTextColor(TFT_WHITE);

        boot_animation();//added by Zell
    
        
        lcd.clear(TFT_WHITE);
        delay(1000);
        if(WIFI_EN){
            lcd.clear(TFT_RED);
            delay(1000);
            lcd.clear(TFT_GREEN);
            delay(1000);
            lcd.clear(TFT_BLUE);
            delay(1000);
            lcd.clear(TFT_ORANGE);
            delay(1000);  
        }
        lcd.clear(TFT_BLACK);
        delay(1000);
        lcd.fillCircle(Screen_center_x,Screen_center_y,circle_r,TFT_GOLD); //( x, y      , r, color);
        delay(300);
        lcd.fillCircle(Screen_center_x,Screen_center_y,circle_r*2,TFT_GREENYELLOW); //( x, y      , r, color);
        lcd.fillCircle(Screen_center_x,Screen_center_y,circle_r,TFT_GOLD); //( x, y      , r, color);
        delay(300);
        lcd.fillCircle(Screen_center_x,Screen_center_y,circle_r*3,TFT_SKYBLUE); //( x, y      , r, color);
        lcd.fillCircle(Screen_center_x,Screen_center_y,circle_r*2,TFT_GREENYELLOW); //( x, y      , r, color);
        lcd.fillCircle(Screen_center_x,Screen_center_y,circle_r,TFT_GOLD); //( x, y      , r, color);
        delay(400);
        lcd.fillCircle(Screen_center_x,Screen_center_y,circle_r*4,TFT_PINK_L); //( x, y      , r, color);
        lcd.fillCircle(Screen_center_x,Screen_center_y,circle_r*3,TFT_SKYBLUE); //( x, y      , r, color);
        lcd.fillCircle(Screen_center_x,Screen_center_y,circle_r*2,TFT_GREENYELLOW); //( x, y      , r, color);
        lcd.fillCircle(Screen_center_x,Screen_center_y,circle_r,TFT_GOLD); //( x, y      , r, color);
        delay(delay_cnt*2000);

        lcd.clear(TFT_BLACK);
        lcd.drawCenterString("ATOM S3 BLE", 64, 1);
        //lcd.setCursor(25, 16);
        //lcd.printf("%08X", ir_addr);
        lcd.drawFastHLine(0, 31, 128);

        sprite1.setColorDepth(16);
        sprite1.createSprite(128, 25);
        sprite1.setTextWrap(false);
        sprite1.setTextScroll(false);
        sprite1.setTextSize(1.3);
        sprite1.setTextColor(TFT_YELLOW);

        sprite2.setColorDepth(16);
        sprite2.createSprite(128, 16);
        sprite2.setTextWrap(false);
        sprite2.setTextScroll(false);
        sprite2.setTextSize(1.3);
        sprite2.setTextColor(TFT_GREEN);

        sprite3.setColorDepth(16);
        sprite3.createSprite(128, 32);//Ori
        //sprite3.createSprite(128, 48); //128,64 crashes
        sprite3.setTextWrap(false);
        sprite3.setTextScroll(false);
        sprite3.setTextSize(1.3);
        sprite3.setTextColor(TFT_SKYBLUE);

        sprite4.setColorDepth(16);
        sprite4.createSprite(128, 25);
        sprite4.setTextWrap(false);
        sprite4.setTextScroll(false);
        sprite4.setTextSize(1.8);
        sprite4.setTextColor(TFT_RED);

        // IMU 初始化
        imu.begin();
    }

    // 按键
    pinMode(BTN_GPIO, INPUT_PULLUP);

    // IR
    ir_tx_init();
    // temp
    // gpio_reset_pin((gpio_num_t)IR_GPIO);
    // pinMode(IR_GPIO, OUTPUT);
    // digitalWrite(IR_GPIO, HIGH);
    if(2<delay_cnt){ 
         USBSerial.println("#>Wifi and BLuetooth enabled!");
         USBSerial.println("#>:BLE sensor scan mode enabled!");
         initBluetooth_BLE();

         delay(500);
         //xTaskCreatePinnedToCore(BLE_Sensor_task, "BLE_Sensor_task", 4096 * 8, NULL, 1, NULL,  APP_CPU_NUM);
         USBSerial.println("#>:Init BLuetooth ! (mode 2)");
        //WIFI
        xTaskCreatePinnedToCore(wifi_task, "wifi_task", 4096 * 8, NULL, 1, NULL, PRO_CPU_NUM);
        USBSerial.println("#>:Created xTask: wifi_task @ APP_core_1!");

         WIFI_EN =0;
         BT_EN =1;
    
     }

    else if (1<delay_cnt){ 
         USBSerial.println("#>Wifi and BLuetooth disabled!");
         USBSerial.println("#>:BLE sensor scan mode enabled!  (mode 1) ");
         initBluetooth_BLE();

         delay(500); //2048+4096=6144
         xTaskCreatePinnedToCore(BLE_Sensor_task, "BLE_Sensor_task", 6144 * 8, NULL, 1, NULL,
                            APP_CPU_NUM);
         USBSerial.println("#>:Created xTask:   BLE_Sensor_task @ APP_core_1!");

         WIFI_EN =0;
         BT_EN =1;
    
     }

    else{ 
    // BLE //include BT init
    USBSerial.println("#>Wifi  disabled!");
        xTaskCreatePinnedToCore(ble_task2, "ble_task2", 4096 * 8, NULL, 1, NULL,
                            APP_CPU_NUM);

    // WIFI
        //xTaskCreatePinnedToCore(wifi_task, "wifi_task", 4096 * 8, NULL, 1, NULL, PRO_CPU_NUM);
        WIFI_EN =0;
        BT_EN =1;
        USBSerial.println("#>Created xTask: BLuetooth ble_task2 @ APP_core_1!(default mode)");
    }
}

void loop() {


    // char * encoded;
      //      encoded = output_as_hex(testVectorCCM_D9.ciphertext, testVectorCCM_D9.datasize);
     //free(encoded);
    // 按键
    if (digitalRead(BTN_GPIO) == LOW) {
        delay(5);
        if (digitalRead(BTN_GPIO) == LOW) {
            btn_pressd_flag = true;
            btn_pressd_count++;
            neopixel_color_index += 1;
            if (neopixel_color_index > 4) {
                neopixel_color_index = 0;
            }
        }
        while (digitalRead(BTN_GPIO) == LOW) {
        }
    }
 /*
    //BLE sensor test:
    USBSerial.printf("Start BLE scan for %d seconds...\n", SCAN_TIME);
    BLEScanResults foundDevices = pBLEScan->start(SCAN_TIME);
    int BLE_dev_count = foundDevices.getCount();
    printf("Found device count : %d\n", BLE_dev_count);

*/

    if (btn_pressd_flag) {
        update_neopixel(
            (neopixel_color_list[neopixel_color_index] >> 16 & 0xFF),
            (neopixel_color_list[neopixel_color_index] >> 8 & 0xFF),
            (neopixel_color_list[neopixel_color_index] & 0xFF));

        if (device_type == ATOM_S3_LCD) {
            sprite1.setCursor(0, 0);
            sprite1.clear();
            sprite1.printf("BTN Pressed %d\r\nRGB -> %s\r\n", btn_pressd_count,
                           neopixel_color_name[neopixel_color_index]);
            sprite1.pushSprite(0, 38); //sprite1 location at screen(0,38)
        }
        USBSerial.printf("BTN Pressed %d\r\nRGB -> %s\r\n", btn_pressd_count,
                         neopixel_color_name[neopixel_color_index]);
        btn_pressd_flag = false;
    }

    // IO 翻转  300ms/1S 一次？
    if (millis() - last_io_reverse_time > 1000) {
        if (device_type == ATOM_S3) {
            for (size_t i = 0; i < sizeof(atom_s3_gpio_list); i++) {
                digitalWrite(atom_s3_gpio_list[i],
                             !digitalRead(atom_s3_gpio_list[i]));
            }
        } else if (device_type == ATOM_S3_LCD) {
            for (size_t i = 0; i < sizeof(atom_s3_lcd_gpio_list); i++) {
                digitalWrite(atom_s3_lcd_gpio_list[i],
                             !digitalRead(atom_s3_lcd_gpio_list[i]));
            }
        }
        if (device_type == ATOM_S3_LCD) {
            sprite2.clear();
            sprite2.setCursor(0, 0);
            sprite2.printf("GPIO TEST:  %s\r\n",
                           digitalRead(atom_s3_gpio_list[0]) ? "HIGH" : "LOW");
            sprite2.pushSprite(0, 64);
        }
        // USBSerial.printf("GPIO TEST:  %s\r\n",
        //                  digitalRead(atom_s3_gpio_list[0]) ? "HIGH" : "LOW");
        last_io_reverse_time = millis();
    }

    // IMU
    if ((device_type == ATOM_S3_LCD) &&
        ((millis() - last_imu_print_time) > 300)) {
        float ax;
        float ay;
        float az;
        float gx;
        float gy;
        float gz;
        float t;
        float roll;
        float pitch;
        float yaw;

        imu.getAccel(&ax, &ay, &az);
        imu.getGyro(&gx, &gy, &gz);
        imu.getTemp(&t);

        sprite3.setCursor(0, 0);
        sprite3.clear();
        sprite3.printf("IMU:  %5.2f C\r\n",t);
        sprite3.printf("%0.2f %0.2f %0.2f\r\n", ax, ay, az);
        sprite3.printf("%0.2f %0.2f %0.2f\r\n", gx, gy, gz);
        sprite3.pushSprite(0, 80);
        // USBSerial.printf("IMU %f,%f,%f,%f,%f,%f,%f\r\n", ax, ay, az, gx, gy,
        // gz,
        //                  t);
        last_imu_print_time = millis();  //esp_timer_get_time() / 1000ULL
    }

    if (millis() - last_ir_send_time > 1000) {
        ir_tx_test();
        if (device_type == ATOM_S3_LCD) {
           // sprite4.setCursor(0, 0);
            //sprite4.clear();
            //sprite4.printf("IR: %02X %02X\r\n", ir_addr, ir_cmd);
            //sprite4.printf("BLE: %02X %02X\r\n", ir_addr, ir_cmd); //Changed to BLE msg , updated in BLE callback loop
           // sprite4.pushSprite(0, 112);
        }
        //USBSerial.printf("IR Send >>> addr:%02X cmd:%02X\r\n", ir_addr, ir_cmd);
        last_ir_send_time = millis();
    }

    //flame app
    if (btn_pressd_count>5){
        USBSerial.printf(">: Btn pressed >5, Entering Fire Flame app now..."); 
        Flame_init();
        delay(100);
        Flame_APP_loop();
    }
    if (3==btn_pressd_count){
        USBSerial.printf(">: Btn pressed >5, Entering Thermal_meter_mode now..."); 
        thermal_meter_mode =true;
        sprite1.clear();
        sprite1.pushSprite(0, 38);
        sprite1.deleteSprite();
        sprite2.clear();
        sprite2.setCursor(0, 0);
        sprite2.printf("Thermal_Meter\r\n");
        sprite2.pushSprite(0, 48);

        Thermal_APP_loop();


    }
    

   
    delay(10);//refresh too fast will cause LCD flickring
}

static void neopixel_init(void) {
    // Init RMT
    rmt_config_t config = {.rmt_mode      = RMT_MODE_TX,
                           .channel       = RMT_CHANNEL_0,
                           .gpio_num      = (gpio_num_t)NEO_GPIO,
                           .clk_div       = 80,
                           .mem_block_num = 1,
                           .flags         = 0,
                           .tx_config     = {
                                   .carrier_freq_hz      = 38000,
                                   .carrier_level        = RMT_CARRIER_LEVEL_HIGH,
                                   .idle_level           = RMT_IDLE_LEVEL_LOW,
                                   .carrier_duty_percent = 33,
                                   .carrier_en           = false,
                                   .loop_en              = false,
                                   .idle_output_en       = true,
                           }};
    // set counter clock to 40MHz
    config.clk_div = 2;
    ESP_ERROR_CHECK(rmt_config(&config));
    ESP_ERROR_CHECK(rmt_driver_install(config.channel, 0, 0));
    // install ws2812 driver
    led_strip_config_t strip_config =
        LED_STRIP_DEFAULT_CONFIG(64, (led_strip_dev_t)config.channel);
    strip = led_strip_new_rmt_ws2812(&strip_config);
    if (!strip) {
        USBSerial.printf("Install WS2812 driver failed");
    }
}

static void update_neopixel(uint8_t r, uint8_t g, uint8_t b) {
    ESP_ERROR_CHECK(strip->set_pixel(strip, 0, r, g, b));
    ESP_ERROR_CHECK(strip->refresh(strip, 0));
}

static void ir_tx_init(void) {
    rmt_config_t rmt_tx_config = {.rmt_mode      = RMT_MODE_TX,
                                  .channel       = RMT_CHANNEL_2,
                                  .gpio_num      = (gpio_num_t)IR_GPIO,
                                  .clk_div       = 80,
                                  .mem_block_num = 1,
                                  .flags         = 0,
                                  .tx_config     = {
                                          .carrier_freq_hz = 38000,
                                          .carrier_level   = RMT_CARRIER_LEVEL_HIGH,
                                          .idle_level      = RMT_IDLE_LEVEL_LOW,
                                          .carrier_duty_percent = 33,
                                          .carrier_en           = false,
                                          .loop_en              = false,
                                          .idle_output_en       = true,
                                  }};

    rmt_tx_config.tx_config.carrier_en = true;
    rmt_config(&rmt_tx_config);
    rmt_driver_install(IR_RMT_TX_CHANNEL, 0, 0);
    ir_builder_config_t ir_builder_config =
        IR_BUILDER_DEFAULT_CONFIG((ir_dev_t)IR_RMT_TX_CHANNEL);
    ir_builder_config.flags |= IR_TOOLS_FLAGS_PROTO_EXT;
    ir_builder = ir_builder_rmt_new_nec(&ir_builder_config);
}

static void ir_tx_test(void) {
    ir_cmd++;
    // USBSerial.printf("Send command 0x%x to address 0x%x\r\n", ir_cmd,
    // ir_addr); Send new key code
    ESP_ERROR_CHECK(ir_builder->build_frame(ir_builder, ir_addr, ir_cmd));
    ESP_ERROR_CHECK(ir_builder->get_result(ir_builder, &ir_items, &ir_length));
    // To send data according to the waveform items.
    rmt_write_items(IR_RMT_TX_CHANNEL, ir_items, ir_length, false);
    // Send repeat code
    vTaskDelay(ir_builder->repeat_period_ms / portTICK_PERIOD_MS);
    ESP_ERROR_CHECK(ir_builder->build_repeat_frame(ir_builder));
    ESP_ERROR_CHECK(ir_builder->get_result(ir_builder, &ir_items, &ir_length));
    rmt_write_items(IR_RMT_TX_CHANNEL, ir_items, ir_length, false);
}
static void BLE_Sensor_task(void *) {


    USBSerial.printf("Start BLE scan for %d seconds...\n", SCAN_TIME);
    BLEScanResults foundDevices = pBLEScan->start(SCAN_TIME);
    int BLE_dev_count = foundDevices.getCount();
    printf("#>::BLE Found device count : %d\n", BLE_dev_count);
    pBLEScan->clearResults();   // delete results fromBLEScan buffer to release memory

}

//runs ok on xtask app_core
static void ble_task2(void *) {
  BLEDevice::init("name_buffer");
  pBLEScan = BLEDevice::getScan(); //create new scan
  pBLEScan->setAdvertisedDeviceCallbacks(new MyAdvertisedDeviceCallbacks());
  pBLEScan->setActiveScan(true); //active scan uses more power, but get results faster
  pBLEScan->setInterval(0x50);
  pBLEScan->setWindow(0x30);// less or equal setInterval value

    static char buffer[64] = {0};

    size_t ble_count = 0;
    while (1) {
        if (millis() - last_ble_change_time > 2000) {
            ble_count++;
            // sprintf(buffer, "Hello world from %s! %d", DEVICE_NAME, millis()
            // / 1000);
            USBSerial.printf("Start BLE scan for %d seconds...\r\n", SCAN_TIME);
            BLEScanResults foundDevices = pBLEScan->start(SCAN_TIME);
            int BLE_dev_count = foundDevices.getCount();
            printf("#>::BLE Found device count : %d\n", BLE_dev_count);
            last_ble_change_time = millis();
            pBLEScan->clearResults();   // delete results fromBLEScan buffer to release memory
        }
        delay(10);
    }
}

static void ble_task(void *) {
    BLEDevice::init(name_buffer);
    BLEServer *pServer                 = BLEDevice::createServer();
    BLEService *pService               = pServer->createService(SERVICE_UUID);
    BLECharacteristic *pCharacteristic = pService->createCharacteristic(
        CHARACTERISTIC_UUID,
        BLECharacteristic::PROPERTY_READ | BLECharacteristic::PROPERTY_WRITE);

    pCharacteristic->setValue("Hello world from " DEVICE_NAME "!");
    pService->start();
    // BLEAdvertising *pAdvertising = pServer->getAdvertising();  // this still
    // is working for backward compatibility
    BLEAdvertising *pAdvertising = BLEDevice::getAdvertising();
    pAdvertising->addServiceUUID(SERVICE_UUID);
    pAdvertising->setScanResponse(true);
    pAdvertising->setMinPreferred(
        0x06);  // functions that help with iPhone connections issue
    pAdvertising->setMinPreferred(0x12);
    BLEDevice::startAdvertising();

    static char buffer[64] = {0};

    size_t ble_count = 0;
    while (1) {
        if (millis() - last_ble_change_time > 1000) {
            ble_count++;
            // sprintf(buffer, "Hello world from %s! %d", DEVICE_NAME, millis()
            // / 1000);
            sprintf(buffer, "Hello world from %s! %d", DEVICE_NAME, ble_count);
            pCharacteristic->setValue(buffer); //BLE broadcast Hello world from
            USBSerial.println("BLE update ok");
            last_ble_change_time = millis();
        }
        delay(10);
    }
}

static void wifi_task(void *) {
    WiFi.mode(WIFI_MODE_APSTA);
    //name and PW
    sprintf(PW_buffer,"12345678");
    WiFi.softAP(name_buffer, PW_buffer);
    //WiFi.softAP(name_buffer, "88888888");
    IPAddress myIP = WiFi.softAPIP();
   // USBSerial.printf("AP Mode:\r\nSSID: %s\r\nPSWD: %s\r\nIP address: ", name_buffer,                     "88888888");
    USBSerial.printf("AP Mode:\r\nSSID: %s\r\nPSWD: %s\r\nIP address: ", name_buffer, PW_buffer);
    USBSerial.println(myIP);
    delay(2000);
    WiFi.disconnect();

    WiFiUDP udp_ap;
    udp_ap.begin(WiFi.softAPIP(), udp_broadcast_port);

    size_t udp_count = 0;
    while (1) {
        if (millis() - last_wifi_scan_time > 30000) {
            USBSerial.println("\r\nWiFi scan start");

            // WiFi.scanNetworks will return the number of networks found
            int n = WiFi.scanNetworks();
            USBSerial.println("WiFi scan done");
            if (n == 0) {
                USBSerial.println("no networks found");
            } else {
                USBSerial.print(n);
                USBSerial.println(" networks found");
                for (int i = 0; i < n; ++i) {
                    // Print SSID and RSSI for each network found
                    USBSerial.print(i + 1);
                    USBSerial.print(": ");
                    USBSerial.print(WiFi.SSID(i));
                    USBSerial.print(" (");
                    USBSerial.print(WiFi.RSSI(i));
                    USBSerial.print(")");
                    USBSerial.println(
                        (WiFi.encryptionType(i) == WIFI_AUTH_OPEN) ? " " : "*");
                    delay(10);
                }
            }
            USBSerial.println("");
            last_wifi_scan_time = millis();
        }

        if (millis() - last_udp_broadcast_time > 1000) {
            udp_count++;
            udp_ap.beginPacket(udp_ap_broadcast_addr, udp_broadcast_port);
            // udp_ap.printf("Seconds since boot: %lu", millis() / 1000);
            udp_ap.printf("Seconds since boot: %lu", udp_count);
            USBSerial.printf("UDP broadcast %s\r\n",
                             udp_ap.endPacket() == 1 ? "OK" : "ERROR");
            last_udp_broadcast_time = millis();
        }
        delay(10);
    }
}


String convertFloatToString(float f)
{
  String s = String(f, 1);
  return s;
}

//转换成华氏的自定义函数
float CelciusToFahrenheit(float Celsius)
{
  float Fahrenheit = 0;
  Fahrenheit = Celsius * 9 / 5 + 32;
  return Fahrenheit;
}

//通过使用属性标记一段代码，IRAM_ATTR我们声明编译后的代码将放置在 ESP32 的内部 RAM (IRAM) 中。
void IRAM_ATTR resetModule() {
  ets_printf("reboot\n");
  esp_restart();
}



char* output_as_hex(unsigned char* a, size_t a_size)
{
    char* s = (char*) malloc(a_size * 2 + 1);
    for (size_t i = 0; i < a_size; i++) {
        sprintf(s + i * 2, "%02X", a[i]);
    }
    return s;
}

uint8_t decode(AES_TestVector testVectorCCM, uint8_t *sensor_raw_val){
  int ret = 0;
  uint8_t plaintext[MAX_PLAINTEXT_LEN];
  char * encoded;
  char * decoded;
  //uint16_t value=0;
  long  value=0;
  mbedtls_ccm_context* ctx;

  USBSerial.println("Original Test vector contents for BLE ADV packet decoding:");
 
  encoded = output_as_hex(testVectorCCM.key, AES_KEY_SIZE/8);
  USBSerial.printf("Key        : %s\n\r", encoded);
  free(encoded);
  encoded = output_as_hex(testVectorCCM.iv, testVectorCCM.ivsize);
 USBSerial.printf("Iv         : %s\n\r", encoded);
  free(encoded);
  encoded = output_as_hex(testVectorCCM.ciphertext, testVectorCCM.datasize);
 USBSerial.printf("Cipher     : %s\n\r", encoded);
  free(encoded);
  encoded = output_as_hex(testVectorCCM.plaintext, testVectorCCM.datasize);
 USBSerial.printf("Plaintext  : %s\n\r", encoded);
  free(encoded);
  encoded = output_as_hex(testVectorCCM.tag, testVectorCCM.tagsize);
 USBSerial.printf("Tag        : %s\n\r", encoded);
  free(encoded);
 USBSerial.println(">:start decoding...");
 
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
   USBSerial.println("-------Decryption loop successful-----------");
   ret =1;
  //if (LCD_EN)
  //  M5.Lcd.printf("Decryption successful\r\n");
  }
  
  decoded = output_as_hex(plaintext, testVectorCCM.datasize);// (text, 5), issue for Akku info(4bytes)?

  USBSerial.printf("Plaintext : %s\r\n", decoded);
  //if (LCD_EN) {
  //  M5.Lcd.printf("Plaintext :\n\r");
  //  M5.Lcd.printf("%s\n\r",decoded);
 // }
  free(decoded);
  
  
  uint8_t type_flag = plaintext[0];
  uint16_t value_tmp =0;
  char SensorValue[5];
  //float T_Value,H_Value,Akku_Value;
  sensor_raw_val[0]=type_flag;
  sensor_raw_val[1]=plaintext[3];
  sensor_raw_val[2]=plaintext[4];
  
  USBSerial.printf(">>:Now calc Sesnor values...\r\n");
  //Arduino test ok, but platformIO hex, crash after USBSerial.printf(">>:proc B\r\n");
    switch (type_flag) {
          case 0x04: //T
            USBSerial.printf(">>:case 0x04");//debug only
            sprintf(SensorValue, "%02X%02X", (char) plaintext[4], (char) plaintext[3]);
            USBSerial.printf(">>:proc A\r\n");
            value = strtol(SensorValue, 0, 16);// issue here
            value_tmp = plaintext[4]<<8;
            value_tmp = value_tmp+plaintext[3];
            USBSerial.printf(">>:proc B\r\n");
            //current_temperature = (float) (value/100.0);
            //current_temperature = (float) value;
            current_temperature= (float) value_tmp;
            USBSerial.printf(">>:proc C\r\n");
            current_temperature =current_temperature/10.0;//issue here?, xtask on different core?
            //USBSerial.printf(">:current_temperature: %5.2f\r\n",value_tmp/10);////issue here!,
              //current_temperature = (float)value / 10;
            //current_temperature=T_Value;
            break;
          case 0x06: //Hum
            USBSerial.printf(">>:case 0x06");//debug only
            sprintf(SensorValue, "%02X%02X", plaintext[4], plaintext[3]);
            USBSerial.printf(">>:proc A\r\n");//debug only
            value = strtol(SensorValue, 0, 16);
            USBSerial.printf(">>:proc B\r\n");
            current_humidity =  (float)value;
            current_humidity = current_humidity/(float)10;//issue here!
            USBSerial.printf(">>:proc C\r\n");
            
            //USBSerial.printf(">:current_Humidty: %3.1f %%\r\n",value_tmp/10);
            //current_humidity=H_Value;
            break;
          case 0x0A://Akku
            USBSerial.printf(">>:case 0x0A");
            sprintf(SensorValue, "%02X%02X", plaintext[4], plaintext[3]);
            value = strtol(SensorValue, 0, 16);
            Akku_SOC =  (float)value;
            Akku_SOC = Akku_SOC/1000.0;
            
            //USBSerial.printf(">:current_akku: %4.3f\r\n",Akku_SOC);
            //Akku_SOC = Akku_Value;
            break;

          default: 
             USBSerial.printf(">:undefined sensor value..."); 
    }
    USBSerial.printf(">>:Switch end\r\n"); //debug only

  
  //free(encoded); //issue here! causing bad heap error reboot!!!
 
  //free(value);

  mbedtls_ccm_free(ctx);  
  USBSerial.println("*****Decode process ended!*****");
  return ret;
  
}



/*

Payload:58585b05aad9aa4738c1a461e41a149a060000fe8fc1e6
>>:payloadtype : 5858


>>:BLE Encripted frame detected:-------------
>>:BLE Cipher  : 61E41A149A

Original Test vector contents for BLE ADV packet decoding:
Key        : 7B67F5AD19AE233C02993BC94B70D07F

Iv         : D9AA4738C1A45B05AA060000

Cipher     : 61E41A149A

Plaintext  : 061002F001

Tag        : FE8FC1E6

>:start decoding...
-------Decryption loop successful-----------
Plaintext : 0610023802
>>:Now calc Sesnor values...
>>:case 0x06>>:proc A
>>:proc B
>>:proc C

 //test for decode func:
            char SensorValue[2]={0x00,0x83};

            //uint16_t value = strtol(SensorValue, 0, 16);// issue here
            uint16_t valuetmp = SensorValue[0]<<8;
            valuetmp = valuetmp+SensorValue[1];
            USBSerial.printf(">>:proc 1\r\n");
            //current_temperature = (float) (value/100.0);
            current_temperature = valuetmp;
            USBSerial.printf(">>:proc 2\r\n");
            current_temperature =current_temperature/10;
            USBSerial.printf(">:current_temperature: %5.2f\r\n",current_temperature);

*/