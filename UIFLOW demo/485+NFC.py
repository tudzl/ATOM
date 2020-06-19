from m5stack import *
from m5ui import *
from uiflow import *
import i2c_bus
import unit
#Connect this RFID Unit toSDA G25, SCL G21 on  ATOM , IIC adress is 0x28.

# ATOM PORT IO
PORTA = (25,21) # I2C
i2c0  = i2c_bus.easyI2C((25, 21), 0x28)

while 1:
  try:
    print(i2c0.scan())
    print(i2c0.available())
    i2c0.write_u8(0x01, 0xAA)
    rgb.setColorAll(0x001133)
    #rfid0 = unit.get(unit.RFID, unit.PORTA) # not fit to ATOM
    rfid0 = unit.get(unit.RFID, unit.PORTA) # fit ATOM?
    #Connect this Unit to GROVE PORTA on M5Core, IIC adress is 0x28.
    #need improve for unit disconnected case 
    print('RFID module is connected!'+"\r\n");
    break
  except:
    print('RFID module was not detected! Please Check! Main code will not run!!!'+"\r\n");
    rgb.set_screen([0,0,0xFF0000,0,0,0,0xFFFFFF,0,0xFF0000,0,0xFFFFFF,0,0xFF0000,0,0xFFFFFF,0,0xFF0000,0,0xFFFFFF,0,0,0,0xFF0000,0,0])
    wait_ms(10)
    continue

RFID_ID = None
TAG_Reg0 = None
TAG_near = None
run_cnt = None

def buttonA_wasPressed():
  global RFID_ID, TAG_Reg0, TAG_near
  uart.write(str('RFID ID and Reg0 data:')+"\r\n")
  uart1.write(str(str(RFID_ID))+"\r\n")
  uart1.write(str(str(TAG_Reg0))+"\r\n")
  rgb.setColorAll(0x33ff33)
  print('RFID detected with ID:')
  print(str(RFID_ID))
  print('Tag Reg0 data:')
  print(str(TAG_Reg0))
  rgb.setBrightness(20)
  rgb.set_screen([0,0,0xFFFFFF,0,0,0,0xFFFFFF,0,0xFFFFFF,0,0xFFFFFF,0,0x4bd425,0,0xFFFFFF,0,0xFFFFFF,0,0xFFFFFF,0,0,0,0xFFFFFF,0,0])
  wait_ms(50)
  rgb.setBrightness(5)
  pass
btnA.wasPressed(buttonA_wasPressed)


uart = machine.UART(1, tx=26, rx=32)
uart.init(115200, bits=8, parity=None, stop=1)
rgb.set_screen([0,0,0xFFFFFF,0,0,0,0xFFFFFF,0,0xFFFFFF,0,0xFFFFFF,0,0xFFFFFF,0,0xFFFFFF,0,0xFFFFFF,0,0xFFFFFF,0,0,0,0xFFFFFF,0,0])
wait_ms(500)
rgb.setBrightness(5)
run_cnt = 0
print('RFID NTAG213 13.56Mhz intelligent 16-BV connector with RS485 Port code running now!'+"\r\n");
while True:
  rgb.setColorAll(0x000000)
  if rfid0.isCardOn():
    TAG_near = 1
    RFID_ID = rfid0.readUid()
    TAG_Reg0 = rfid0.readBlockStr(1)
    print(rfid0.readUid())
    print(rfid0.readBlockStr(1))
  else:
    TAG_near = 0
    RFID_ID = 0
    TAG_Reg0 = 0
  
  rgb.setColorAll(0xffffff)
  rgb.setColorAll(0x000000)
  run_cnt = (run_cnt if isinstance(run_cnt, Number) else 0) + 1
  wait_ms(200)
