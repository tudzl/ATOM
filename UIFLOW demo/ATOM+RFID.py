from m5stack import *
from m5ui import *
from uiflow import *
import i2c_bus
import unit
from numbers import Number
#V1.1 19.06.2020 working!
#Connect this RFID Unit toSDA G25, SCL G21 on  ATOM , IIC adress is 0x28. (DEC 40)

# ATOM PORT IO
IIC_PORTA = (25,21) # I2C
unit.PORTA = (25,21)  # seems used in the unit init!unit.get(unit.RFID, unit.PORTA) # fit ATOM?
#i2c0  = i2c_bus.easyI2C((25, 21), 0x28)
print('#-->:i2c_bus.easyI2C(PORTA, 0x28, freq=100000)')
#print('#-->: i2c_bus.easyI2C(i2c_bus.PORTA, 0x28, freq=400000)')
i2c0 = i2c_bus.easyI2C(IIC_PORTA, 0x28, freq=100000)


#sys vars
run_cnt = None
#RFID vars
RFID_ID = None
TAG_Reg0 = None
TAG_near = None


# Top Btn to write tag, send 485 test only
def buttonA_wasPressed():
  #global cnt
  global RFID_ID, TAG_Reg0, TAG_near
  print('#-->:BtnA was pressed!'+"\r\n")
  if TAG_near:
     rfid0.writeBlock(1,'16BV_001')
     print('#-->:RFID write data to TAG REG1: 16BV_001'+"\r\n")
  rgb.setBrightness(20)
  rgb.set_screen([0,0,0xFFFFFF,0,0,0,0xFFFFFF,0,0xFFFFFF,0,0xFFFFFF,0,0x4bd425,0,0xFFFFFF,0,0xFFFFFF,0,0xFFFFFF,0,0,0,0xFFFFFF,0,0])
  wait_ms(100)
  rgb.setBrightness(5)
  print('#-->:RS485 send tag data now...'+"\r\n")
  uart.write(str('RFID ID and Reg1 data:')+"\r\n")
  uart.write(str(str(RFID_ID))+"\r\n")
  uart.write(str(str(TAG_Reg0))+"\r\n")
  rgb.setColorAll(0x33ff33)
  pass
btnA.wasPressed(buttonA_wasPressed)



while 1:
  try:
    print('i2c0.scan results:');
    print(i2c0.scan())
    wait_ms(10)
    print('i2c device available ?:');
    print(i2c0.available())
    #i2c0.write_u8(0x01, 0xAA)
    wait_ms(20)
    rgb.setColorAll(0x001133)
    #rfid0 = unit.get(unit.RFID, unit.PORTA) # not fit to ATOM
    rfid0 = unit.get(unit.RFID, unit.PORTA) # fit ATOM?
    #rfid0 = unit.get(unit.RFID, unit.(25,21)) # fit ATOM?
    #Connect this Unit to GROVE PORTA on M5Core, IIC adress is 0x28.
    #need improve for unit disconnected case 
    print('RFID module is connected!'+"\r\n");
    break
  except:
    print('RFID module was not detected! Please Check! Main code will not run!!!'+"\r\n");
    rgb.set_screen([0,0,0xFF0000,0,0,0,0xFFFFFF,0,0xFF0000,0,0xFFFFFF,0,0xFF0000,0,0xFFFFFF,0,0xFF0000,0,0xFFFFFF,0,0,0,0xFF0000,0,0])
    wait_ms(500)
    continue
print('#-->:i2c init end');


uart = machine.UART(1, tx=26, rx=32)
uart.init(115200, bits=8, parity=None, stop=1)
rgb.set_screen([0,0,0xFFFFFF,0,0,0,0xFFFFFF,0,0xFFFFFF,0,0xFFFFFF,0,0xFFFFFF,0,0xFFFFFF,0,0xFFFFFF,0,0xFFFFFF,0,0,0,0xFFFFFF,0,0])
wait_ms(500)
rgb.setBrightness(5)
run_cnt = 0

TAG_near = 0
RFID_ID = 0
TAG_Reg0 = 0
print('RFID NTAG213 13.56Mhz intelligent 16-BV connector with RS485 Port code running now!'+"\r\n");
while True:
  rgb.setColorAll(0x000000)
  #print('Check Tag existence:'+"\r\n")
  if rfid0.isCardOn():
    print('Tag available!'+"\r\n")
    TAG_near = 1
    RFID_ID = rfid0.readUid()
    TAG_Reg0 = rfid0.readBlockStr(1)
    print('Tag_ID: '+rfid0.readUid())
    print('Tag_Reg1: '+rfid0.readBlockStr(1))
    wait_ms(50)
  else:
    TAG_near = 0
    RFID_ID = 0
    TAG_Reg0 = 0
  rgb.setColorAll(0xffffff)
  rgb.setColorAll(0x000000)
  #run_cnt = run_cnt +1
  run_cnt = (run_cnt if isinstance(run_cnt, Number) else 0) + 1
  print('#-->:Run_cnt:'+str(run_cnt)+"\r\n")
  #run_cnt = (run_cnt if isinstance(run_cnt, Number) else 0) + 1
  wait_ms(400)
