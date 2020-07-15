from m5stack import *
from m5ui import *
from uiflow import *
from machine import ModbusSlave
from machine import UART
import i2c_bus
import unit
from numbers import Number
from micropython import const
#V0.4, Modbus slave is working, send 13 bytes: SL_add+funct_number+len+data(8B)+CRC(2B)
#15.07.2020


#(Slave_address, uart_port,tx,rx)
#modbus_s = ModbusSlave(1, 1, 115200, 25, 21)
modbus_s = ModbusSlave(1, 2, 115200, 22, 19)
uart = machine.UART(1,tx=25, rx=21)  # for 16BV module
#uart = machine.UART(1, tx=26, rx=32) # for Tail485 module
uart.init(115200, bits=8, parity=None, stop=1)

#RS485 modbus RTU
Slave_add = 0x01 
Func_readID = 0x03
fun = None
REG_NUID = 0x01
ID_len = 0x04
REG_addr = None
tmp_data = None
var = None

#sys vars
run_cnt = None
#RFID vars
RFID_ID = None
RFID_ID_pre = None
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



RFID_ID_pre ='00000000'
modbus_s.init_function(4, 1, 100, ModbusSlave.METHOD_WRITE)
modbus_s.init_function(3, 1, 100, ModbusSlave.METHOD_READ)

def calc_crc(data):
    crc = 0xFFFF
    for pos in data:
        crc ^= pos 
        for i in range(8):
            if ((crc & 1) != 0):
                crc >>= 1
                crc ^= 0xA001
            else:
                crc >>= 1
    return crc
#https://stackoverflow.com/questions/39101926/port-modbus-rtu-crc-to-python-from-c-sharp



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
  print('modbus RTU slave sending msg now!'+"\r\n")
  #tmp_msg=(b"\x01\x02")
  
  var = 0x02<<16
  var = var+9999#141071, 0x02270f
  modbus_s.update_function(4, 1, var)
  modbus_s.send(1, 3, 1, var)#slave address, 功能码、寄存器地址、数据

  rgb.setColorAll(0x1f6060)
  '''
  uart.write('data:')
  #uart.write(01)
  uart.write(b"\xAA")
  uart.write(b"\x00")
  '''
  var= 3
  ID_len = len(RFID_ID_pre)
  tmp_msg = bytearray(var)# the array will have that size and will be initialized with null bytes.
  tmp_msg[0] = Slave_add
  tmp_msg[1] = Func_readID
  tmp_msg[2] = ID_len
  #tmp_payload = bytearray(RFID_ID_pre, 'ascii')#not NotImplemented
  #var = 8
  tmp_payload = bytearray(ID_len)
  tmp_payload = RFID_ID_pre
  CRC_bytes = tmp_msg+tmp_payload
  CRC_list= list(CRC_bytes)
  CRC_Res= calc_crc(CRC_list)
  CRC_payload = bytearray(2)
  CRC_payload[0] = CRC_Res>>8
  CRC_payload[1] = (CRC_Res<<8)>>8
  
  '''
  tmp_msg[4] = RFID_ID_pre[1]
  tmp_msg[5] = RFID_ID_pre[2]
  tmp_msg[6] = RFID_ID_pre[3]
  '''
  uart.write(tmp_msg)
  uart.write(tmp_payload)
  uart.write(CRC_payload)
  #tmp_msg[1] = var>>16

  print('Modbus msg sent with frame head:')
  print(str(tmp_msg))
  print("\r\n")
  print('data_payload:')
  print(str(tmp_payload))
  print("\r\n")
  print('data_len:')
  print(str(ID_len))
  print("\r\n")
  print('CRC16:')
  print("%04X"%(CRC_Res))
  print("\r\n")
      
  
  #uart.write(bytes(var))
  rgb.setColorAll(0x0F6640)
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
      RFID_ID_pre = RFID_ID
      TAG_Reg0 = rfid0.readBlockStr(1)
      print('Tag_NUID: '+str(RFID_ID) )
      print('type is:'+ str(type(RFID_ID)) )
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
  #uart.write('Run_cnt:'+str(run_cnt)+"\r\n")
  #run_cnt = (run_cnt if isinstance(run_cnt, Number) else 0) + 1
  wait_ms(200)
