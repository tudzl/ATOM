/****************************************************************
 * 
 * This Example is used to test IRbutton based on ATOM Matrix
 * Serial.println("GREE A/C remote is in the following state:");
 * https://www.arduino.cn/thread-98105-1-1.html
 * https://www.arduino.cn/thread-98106-1-1.html
 * Arduino tools Setting 
 * -board : M5StickC
 * -Upload Speed: 115200 / 750000 / 1500000
 * 
****************************************************************/
/* Copyright 2016, 2018 David Conran
*  Copyright 2020 Sadid Rafsun Tulon
*
* An IR LED circuit *MUST* be connected to the ESP8266 on a pin
* as specified by kIrLed below.
*
* TL;DR: The IR LED needs to be driven by a transistor for a good result.
*
* Suggested circuit:
*     https://github.com/crankyoldgit/IRremoteESP8266/wiki#ir-sending
*
* Common mistakes & tips:   * Don't just connect the IR LED directly to the pin, it won't
* 
*     have enough current to drive the IR LED effectively.
*   * Make sure you have the IR LED polarity correct.
*     See: https://learn.sparkfun.com/tutorials/polarity/diode-and-led-polarity
*   * Typical digital camera/phones can be used to see if the IR LED is flashed.
*     Replace the IR LED with a normal LED if you don't have a digital camera
*     when debugging.
*   * Avoid using the following pins unless you really know what you are doing:
*     * Pin 0/D3: Can interfere with the boot/program mode & support circuits.
*     * Pin 1/TX/TXD0: Any serial transmissions from the ESP8266 will interfere.
*     * Pin 3/RX/RXD0: Any serial transmissions to the ESP8266 will interfere.
*   * ESP-01 modules are tricky. We suggest you use a module with more GPIOs
*     for your first time. e.g. ESP-12 etc.
*/
#include "M5Atom.h"
//#include <Arduino.h>
#include <IRremoteESP8266.h>
#include <IRsend.h>
#include <ir_Gree.h>

uint16_t run_cnt = 0;
const uint16_t kIrLed = 12;  // ESP8266 GPIO pin to use. Recommended: 4 (D2).
IRGreeAC ac(kIrLed);  // Set the GPIO to be used for sending messages.

uint8_t DisBuff[2 + 5 * 5 * 3];

void setBuff(uint8_t Rdata, uint8_t Gdata, uint8_t Bdata)
{
    DisBuff[0] = 0x05;
    DisBuff[1] = 0x05;
    for (int i = 0; i < 25; i++)
    {
        DisBuff[2 + i * 3 + 0] = Rdata;
        DisBuff[2 + i * 3 + 1] = Gdata;
        DisBuff[2 + i * 3 + 2] = Bdata;
    }
}





void printState() {
  // Display the settings.
  Serial.println("GREE A/C remote is in the following state:");
  Serial.printf("  %s\n", ac.toString().c_str());
  // Display the encoded IR sequence.
  unsigned char* ir_code = ac.getRaw();
  Serial.print("IR Code: 0x");
  for (uint8_t i = 0; i < kGreeStateLength; i++)
    Serial.printf("%02X", ir_code[i]);
  Serial.println();
}

void setup() {


    M5.begin(true, false, true);
    delay(10);
    setBuff(0xff, 0x00, 0x00);
    M5.dis.displaybuff(DisBuff);
    
  ac.begin();
  Serial.begin(115200);
  delay(200);
  Serial.println("<<GREE AC IR remote control test app v1.0 for ATOM Matix.");
  // Set up what we want to send. See ir_Gree.cpp for all the options.
  // Most things default to off.
  Serial.println("Default state of the remote.");
  printState();
  Serial.println("Setting desired state for A/C.");
  ac.on();
  ac.setFan(1);
  // kGreeAuto, kGreeDry, kGreeCool, kGreeFan, kGreeHeat
  ac.setMode(kGreeCool);
  ac.setTemp(26);  // 16-30C
  ac.setSwingVertical(true, kGreeSwingAuto);
  ac.setXFan(false);
  ac.setLight(false);
  ac.setSleep(false);
  ac.setTurbo(false);
}

void loop() {
  // Now send the IR signal.
//#if SEND_GREE
if (M5.Btn.wasPressed())
    {
      setBuff(0x40, 0x00, 0x00);//red
      M5.dis.displaybuff(DisBuff);
      Serial.println("Sending IR command to GREE A/C .../r/n");
      ac.send();
  //#endif  // SEND_GREE
  }
  if(run_cnt%20==0){
    setBuff(0x20, 0x20, 0x20);//white
    printState();
  }
  delay(200);
  //delay(50);
  
  M5.dis.displaybuff(DisBuff);
  M5.update();
  run_cnt++;
}
