from m5stack import *
from m5ui import *
from uiflow import *
import time
#Atom + tail485 code
#V0.9  18.06.2020
#uart type_C bugs!!!




from numbers import Number

run_cnt = None
flush = None


def buttonA_wasPressed():
  global run_cnt, flush
  uart.write('ATOM RS485 test, hello!'+"\r\n")
  #uart_USB
  print('ATOM RS485 msg sent, run_cnt:'+str(run_cnt)+"\r\n");
  #rgb.setColorAll(0x99ff99)
  rgb.setBrightness(20)
  rgb.set_screen([0,0,0xFFFFFF,0,0,0,0xFFFFFF,0,0xFFFFFF,0,0xFFFFFF,0,0x4bd425,0,0xFFFFFF,0,0xFFFFFF,0,0xFFFFFF,0,0,0,0xFFFFFF,0,0])
  wait_ms(50)
  rgb.setBrightness(5)
  pass
btnA.wasPressed(buttonA_wasPressed)



uart = machine.UART(1, tx=26, rx=32)
#uart = machine.UART(1, tx=32, rx=26)# ori  bugs
uart.init(115200, bits=8, parity=None, stop=1)
run_cnt = 0
#rgb.set_screen([0,0,0xFFFFFF,0,0,0,0xFFFFFF,0,0xFFFFFF,0,0xFFFFFF,0,0,0,0xFFFFFF,0,0xFFFFFF,0,0xFFFFFF,0,0,0,0xFFFFFF,0,0])
rgb.set_screen([0,0,0xFFFFFF,0,0,0,0xFFFFFF,0,0xFFFFFF,0,0xFFFFFF,0,0xEF11EE,0,0xFFFFFF,0,0xFFFFFF,0,0xFFFFFF,0,0,0,0xFFFFFF,0,0])
#rgb.set_screen([0,0,0xFFFFFF,0,0,0,0xFFFFFF,0,0xFFFFFF,0,0xFFFFFF,0,0xFFFFFF,0,0xFFFFFF,0,0xFFFFFF,0,0xFFFFFF,0,0,0,0xFFFFFF,0,0])
wait_ms(500)
rgb.setBrightness(5)
while True:
  if uart.any():
    flush = uart.read()
    rgb.setColorAll(0xff99ff)
    rgb.setColorAll(0x66ffff)
    rgb.setColorAll(0xff6666)
  rgb.setColorAll(0xffffff)
  rgb.setColorAll(0x000000)
  run_cnt = (run_cnt if isinstance(run_cnt, Number) else 0) + 1
  wait_ms(200)
