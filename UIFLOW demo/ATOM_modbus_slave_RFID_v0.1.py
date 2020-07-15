from m5stack import *
from m5ui import *
from uiflow import *
from machine import ModbusSlave
import i2c_bus
import unit
from numbers import Number
from micropython import const
#ATOM_modbus_slave+RFID  14.07.2020

modbus_s = ModbusSlave(1, 1, 115200, 25, 21)



fun = None
REG_addr = None
tmp_data = None
var = None

#sys vars
run_cnt = None
#RFID vars
RFID_ID = None
TAG_Reg0 = None
TAG_near = None
# ATOM PORT IO 
RS485_UART = (1,25,21) # TX,RX
IIC_PORTA = (26,32) # I2C  for 16BV demo
unit.PORTA = (26,32)  # seems used in the unit init!unit.get(unit.RFID, unit.PORTA) # fit ATOM?
#i2c0  = i2c_bus.easyI2C((25, 21), 0x28)
print('< Intelligent 16-BV connector with RS485 Port & NFC program v1.6 >'+"\r\n");
print('< Author: Ling.Zell, li.zhou@staubli.com, 09.July.2020 >'+"\r\n");
print('#-->:i2c_bus.easyI2C(PORTA, 0x28, freq=100000)')
print('#-->:RS485_UART: TX_G25,RX_G21@ 115200')
#print('#-->: i2c_bus.easyI2C(i2c_bus.PORTA, 0x28, freq=400000)')
i2c0 = i2c_bus.easyI2C(IIC_PORTA, 0x28, freq=100000)

#Init function reg addr value method 定义Modbus数据操作格式，(fun,reg,value): function为功能码，reg addr为寄存器地址， value为初始默认值， method为读或写操作模式
modbus_s.init_function(4, 1, 100, ModbusSlave.METHOD_WRITE)
modbus_s.init_function(3, 1, 100, ModbusSlave.METHOD_READ)

def modbus_s_write_cb(x):
  global fun,REG_addr,tmp_data,var
  fun, REG_addr, tmp_data = x.read()
  var = tmp_data[1]
  if fun == 4 and REG_addr == 1:
    modbus_s.update_function(fun, REG_addr, 90)
    modbus_s.send(1, 3, 1, 90)
    if var == 9:
      rgb.setColorAll(0x6600cc)
      print('modbus received msg!')

  pass
modbus_s.set_write_cb(modbus_s_write_cb)

def buttonA_wasPressed():
  global fun, REG_addr, tmp_data, var
  print('modbus slave send msg!')
  #modbus_s.update_function(4, 1, 99)
  modbus_s.send(1, 3, 1, 99)#slave address, 功能码、寄存器地址、数据
  rgb.setColorAll(0xff6600)
  pass
btnA.wasPressed(buttonA_wasPressed)



rgb.setColorAll(0x666633)
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
    rgb.setColorAll(0xFF0000)
    #rgb.set_screen([0,0,0xFF0000,0,0,0,0xFFFFFF,0,0xFF0000,0,0xFFFFFF,0,0xFF0000,0,0xFFFFFF,0,0xFF0000,0,0xFFFFFF,0,0,0,0xFF0000,0,0])
    wait_ms(500)
    continue
print('#-->:i2c init end');


run_cnt = 0

TAG_near = 0
RFID_ID = 0
TAG_Reg0 = 0
print('#-->: Main code loop running now...');
while True:
  rgb.setColorAll(0x000000)
  #print('Check Tag existence:'+"\r\n")
  if rfid0.isCardOn():
    rgb.setBrightness(15)
    rgb.setColorAll(0x11ff11)
    print('Tag available!'+"\r\n")
    TAG_near = 1
    try:
      RFID_ID = rfid0.readUid() # 5 bytes in String format
      RFID_ID=RFID_ID[:-2] # delete last byte of ID data, resulting 4 Bytes NUID!
      TAG_Reg0 = rfid0.readBlockStr(1)
      print('Tag_NUID: '+str(RFID_ID) )
      print('#:Raw_ID: '+rfid0.readUid() )
      print('Tag_Reg1: '+rfid0.readBlockStr(1))
      print('Tag_Reg2: '+rfid0.readBlockStr(2))
      print('Tag_Reg3: '+rfid0.readBlockStr(3))
      print('Tag_Reg4: '+rfid0.readBlockStr(4))
      print('Tag_Reg5: '+rfid0.readBlockStr(5))
      print('Tag_Reg6: '+rfid0.readBlockStr(6))
      print('Tag_Reg7: '+rfid0.readBlockStr(7))
      print('Tag_Reg8: '+rfid0.readBlockStr(8))
      print('Tag_Reg9: '+rfid0.readBlockStr(9))
    except:
      print('#: Error occurs when RFID module reading the tag!'+"\r\n")
      continue
    wait_ms(50)
    rgb.setBrightness(5)
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
  wait_ms(200)
