from m5stack import *
from m5ui import *
from uiflow import *

rgb.set_screen([0,0,0xFFFFFF,0,0,0,0xFFFFFF,0,0xFFFFFF,0,0xFFFFFF,0,0x4bd425,0,0xFFFFFF,0,0xFFFFFF,0,0xFFFFFF,0,0,0,0xFFFFFF,0,0])





#type-C uart pin 1, 3   ; uart0 is buildin repl, can not be used
uart0 = machine.UART(1, tx=1, rx=3)
uart0.init(115200, bits=8, parity=None, stop=1)
uart0.write('ATOM test, hello!'+"\r\n")

while True:
  if uart1.any():
    flush = uart.read()
    rgb.setColorAll(0xff99ff)
    rgb.setColorAll(0x66ffff)
    rgb.setColorAll(0xff6666)
  rgb.setColorAll(0xfefef0f)
  rgb.setColorAll(0x000000)
  uart1.write('ATOM test, 2020!'+"\r\n")
  wait_ms(1000)