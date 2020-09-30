from m5stack import *
from m5ui import *
from uiflow import *
from easyIO import *
from machine import ModbusSlave
from machine import UART
import i2c_bus
import unit
from numbers import Number
from micropython import const
#IIC address:
#Atom matrix mpu6886 0x68, dec104
#RFID 0x28 dec40
#BMP388 0x77
#V1.1 fit to ATOM Matrix #1, 5E9363E1
#V1.0 changed to fit Base485 PCB demo, IIC: G21(SCL)+ G25(SDA); G22(TX)+G19(RX)
# Base485 PCB: G23-->blue LED; G33-->Green LED top side
#V0.9 improve Modbus send slave response msg function , test ok 28.07.2020
#modbus response time: 30-50 ms@ no active RFID Card
#modbus response time: 350 ms@  active RFID Card

#V0.8 added Modbus send slave response msg function , test ok 27.07.2020
#V0.7 added Modbus_RTU_MasterMsg_parse function, test ok
#SLave address+Func.code+Reg_addr(2B)+number of Words(2B)+CRC(lo first, 2B) = 8 B
#V0.5, Modbus RTU slave is working, send 9 bytes: SL_add+funct_number+len+NUID_data(4B)+CRC(2B)
#V0.4, Modbus slave is working, send 13 bytes: SL_add+funct_number+len+data(8B)+CRC(2B)
#15.07.2020 author: ling ZHOU

#API key Atom lite: 9F7C20BB/
#(Slave_address, uart_port,tx,rx)
#modbus_s = ModbusSlave(1, 1, 115200, 25, 21)
#@modbus_s = ModbusSlave(1, 2, 115200, 22, 19)
#--------GPIO IO def-----------
#from easyIO import *
LED_Green_pin = 33
#digitalWrite(LED_Green_pin, 0)
LED_Blue_pin = 23
#digitalWrite(LED_Blue_pin, 0)

uart = machine.UART(1,tx=22, rx=19)  # for 16BV module
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
RS485_UART = (1,22,19) # TX,RX
#RS485_UART = (1,25,21) # TX,RX
IIC_PORTA = (25,21) # I2C  base 485 PCB for 16BV demo
#IIC_PORTA = (26,32) # I2C  for 16BV demo
unit.PORTA = (25,21)  # seems used in the unit init!unit.get(unit.RFID, unit.PORTA) # fit ATOM?
#i2c0  = i2c_bus.easyI2C((25, 21), 0x28)
print('< Intelligent 16-BV connector with RS485 modbus & NFC program v1.2 Matrix>'+"\r\n");
print('< Author: Ling.Zell, li.zhou@staubli.com, 30.Sep.2020 >'+"\r\n");
print('#-->:i2c_bus.easyI2C(PORTA (25,21) , 0x28, freq=100000)')
print('#-->:RS485_UART: TX_G22,RX_G19@ 115200')
#print('#-->: i2c_bus.easyI2C(i2c_bus.PORTA, 0x28, freq=400000)')
i2c0 = i2c_bus.easyI2C(IIC_PORTA, 0x28, freq=100000)



RFID_ID_pre ='00000000'
#modbus_s.init_function(4, 1, 100, ModbusSlave.METHOD_WRITE)
#modbus_s.init_function(3, 1, 100, ModbusSlave.METHOD_READ)

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

def Modbus_RTU_MasterMsg_parse(msg):
    global Slave_add
    ret = None
    CRC = None
    CRC_Lo = None
    CRC_Hi = None
    # 3 to read NUID 4Bytes data
    # 4 to read user date, assume 8 Bytes?
    # 1 slave address not match
    # 0 unvalid msg,(length  error)
    # -1 errors
    # -2 error with CRC
    # 
    msg_len = len(msg)
    if (msg_len!=8):
        ret = 0
        print("#>:Modbus Msg lengh not equal to 8!")
        return ret
    else:
        CRC = calc_crc(msg[0:-2])
        CRC_Hi = CRC>>8
        CRC_Lo = CRC&0x00FF
        print("#>:Calc CRC:")
        print(str(hex(CRC)))
        #print(str(hex(CRC_Hi)))
        #print(str(hex(CRC_Lo)))
        CRC_Ori = msg[-2]+(msg[-1]<<8)
        print("RX CRC: "+(hex(CRC_Ori)))
        if (CRC!= CRC_Ori):
            ret = -2
            print("#>:Modbus Msg CRC error!")
            return ret
        
    if (msg[0] == Slave_add):
        ret =  msg[1]
        if (ret>5):
            ret = -1
        elif(ret<1):
            ret = -1
        print("Modbus Master Msg parse successful!")
        return ret
    else:
        ret =1
        #print("#>:Modbus slave address not match!")
        return ret
'''
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
'''
def Modbus_send_NUID():
  global Slave_add,Func_readID, RFID_ID_pre,ID_len
  digitalWrite(LED_Green_pin, 1)
  print('modbus RTU slave send NUID data now!'+"\r\n")
  tmp_msg = bytearray(3)# the array will have that size and will be initialized with null bytes.
  tmp_msg[0] = Slave_add
  tmp_msg[1] = Func_readID
  tmp_msg[2] = ID_len
  #tmp_payload = bytearray(RFID_ID_pre, 'ascii')#not NotImplemented
  #for 8 bytes payloads
  #tmp_payload = bytearray(len(RFID_ID_pre))
  #tmp_payload = RFID_ID_pre
  #for 4 bytes payloads
  tmp_var = int(RFID_ID_pre,16)
  data_payload = bytearray(ID_len) #4 bytes
  data_payload[0] = tmp_var>>24
  data_payload[1] = (tmp_var>>16)&0xFF
  data_payload[2] = (tmp_var>>8)&0xFF
  data_payload[3] = tmp_var&0xFF
  CRC_bytes = tmp_msg+data_payload
  #CRC_bytes = tmp_msg+tmp_payload
  CRC_list= list(CRC_bytes)
  CRC_Res= calc_crc(CRC_list)
  CRC_payload = bytearray(2)
  CRC_payload[0] = CRC_Res>>8
  CRC_payload[1] = (CRC_Res<<8)>>8
  uart.write(tmp_msg)
  #uart.write(tmp_payload)
  uart.write(data_payload)
  uart.write(CRC_payload)
  print('Modbus msg sent with frame:')
  print(CRC_list)
  #print(str(CRC_bytes)+str(CRC_payload)) #hex auto converted to ascii
  #print(str(CRC_list2[0:3])+"+["+str(f'{CRC_list2[3]:x}')+str(f'{CRC_list2[4]:x}')+str(f'{CRC_list2[5]:x}')+str(f'{CRC_list2[6]:x}')+"]+["+hex(CRC_Res)+"]")#not supported
  print(str(CRC_list[0:3])+"+["+"{:x}".format(CRC_list[3])+"{:x}".format(CRC_list[4])+"{:x}".format(CRC_list[5])+"{:x}".format(CRC_list[6])+"]" +"+["+"{:x}".format(CRC_payload[0])+"{:x}".format(CRC_payload[1])+"]")
  digitalWrite(LED_Green_pin, 0)
  pass
  
  

def buttonA_wasPressed():
  global fun, REG_addr, tmp_data, var
  print('modbus RTU slave sending msg now!'+"\r\n")
  #tmp_msg=(b"\x01\x02")
  digitalWrite(LED_Green_pin, 1)
  #modbus_s.update_function(4, 1, var)
  #modbus_s.send(1, 3, 1, var)#slave address, 功能码、寄存器地址、数据

  #rgb.setColorAll(0x1f6060)
  rgb.set_screen([0x0df21c,0,0x89e6cf,0,0x0df21c,0,0,0x0df21c,0,0,0x89e6cf,0x0df21c,0x0db3c9,0x0df21c,0x89e6cf,0,0,0x0df21c,0,0,0x0df21c,0,0x89e6cf,0,0x0df21c])
  '''
  uart.write('data:')
  #uart.write(01)
  uart.write(b"\xAA")
  uart.write(b"\x00")
  '''
  var= 3
  #ID_len = len(RFID_ID_pre)
  tmp_msg = bytearray(var)# the array will have that size and will be initialized with null bytes.
  tmp_msg[0] = Slave_add
  tmp_msg[1] = Func_readID
  tmp_msg[2] = ID_len
  #tmp_payload = bytearray(RFID_ID_pre, 'ascii')#not NotImplemented
  #for 8 bytes payloads
  tmp_payload = bytearray(len(RFID_ID_pre))
  tmp_payload = RFID_ID_pre
  #for 4 bytes payloads
  tmp_var = int(RFID_ID_pre,16)
  data_payload = bytearray(ID_len)
  data_payload[0] = tmp_var>>24
  data_payload[1] = (tmp_var>>16)&0xFF
  data_payload[2] = (tmp_var>>8)&0xFF
  data_payload[3] = tmp_var&0xFF
  CRC_bytes = tmp_msg+data_payload
  #CRC_bytes = tmp_msg+tmp_payload
  CRC_list= list(CRC_bytes)
  CRC_Res= calc_crc(CRC_list)
  CRC_payload = bytearray(2)
  CRC_payload[0] = CRC_Res>>8
  CRC_payload[1] = (CRC_Res<<8)>>8
  uart.write(tmp_msg)
  #uart.write(tmp_payload)
  uart.write(data_payload)
  uart.write(CRC_payload)
  #tmp_msg[1] = var>>16
  rgb.set_screen([0x0df21c,0,0x89e6cf,0,0x0df21c,0,0,0x0df21c,0,0,0x89e6cf,0x0df21c,0x01ee01,0x0df21c,0x89e6cf,0,0,0x0df21c,0,0,0x0df21c,0,0x89e6cf,0,0x0df21c])
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
  digitalWrite(LED_Green_pin, 0)
  pass
btnA.wasPressed(buttonA_wasPressed)



rgb.setColorAll(0x666633)
digitalWrite(LED_Green_pin, 1)
while 1:
  print('#-->:i2c init now...')  
  try:
    print(' i2c0.scan results:')
    addrList=i2c0.scan()
    Dev_cnt=len(addrList)
    print(addrList)
    wait_ms(10)
    print(' i2c device available ?:'+str(i2c0.available()))
    print(' i2c device number:'+str(Dev_cnt))
    #i2c0.write_u8(0x01, 0xAA)
    wait_ms(20)
    #rgb.setColorAll(0x001133)
    rgb.set_screen([0xe7fd3f,0,0xe7fd3f,0,0,0,0,0,0xca3ffd,0xca3ffd,0x3fabfd,0,0x3fabfd,0xca3ffd,0,0x3fabfd,0,0x3fabfd,0xca3ffd,0xca3ffd,0,0,0,0,0])
    #rfid0 = unit.get(unit.RFID, unit.PORTA) # not fit to ATOM
    rfid0 = unit.get(unit.RFID, unit.PORTA) # fit ATOM?
    #rfid0 = unit.get(unit.RFID, unit.(25,21)) # fit ATOM?
    #Connect this Unit to GROVE PORTA on M5Core, IIC adress is 0x28.
    #need improve for unit disconnected case 
    print(' RFID module is connected!'+"\r\n")
    break
  except:
    digitalWrite(LED_Blue_pin, 1)
    print(' RFID module was not detected! Please Check! Main code will not run!!!'+"\r\n")
    rgb.set_screen([0xfd3f3f,0xfd3f3f,0xfd3f3f,0,0x823ffd,0xfd3f3f,0,0xfd3f3f,0x823ffd,0,0xfd3f3f,0,0xfd3f3f,0x823ffd,0,0xfd3f3f,0,0xfd3f3f,0x823ffd,0,0xfd3f3f,0,0xfd3f3f,0,0x823ffd])
    #rgb.setColorAll(0xFF0000)
    #rgb.set_screen([0,0,0xFF0000,0,0,0,0xFFFFFF,0,0xFF0000,0,0xFFFFFF,0,0xFF0000,0,0xFFFFFF,0,0xFF0000,0,0xFFFFFF,0,0,0,0xFF0000,0,0])
    wait_ms(500)
    continue
print('#-->:i2c init end')


run_cnt = 0
RTU_master = None
TAG_near = 0
RFID_ID = 0
TAG_Reg0 = 0
RTU_CMD_code= 0 # function code parsed from received master messages
print('#-->: Main code loop running now...')
digitalWrite(LED_Blue_pin, 0)
digitalWrite(LED_Green_pin, 0)
while True:
  #rgb.setColorAll(0x000000)
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
      #print('type is:'+ str(type(RFID_ID)) )
      #print('#:Raw_ID: '+rfid0.readUid() )
      print('Tag_Reg1: '+rfid0.readBlockStr(1))
      print('Tag_Reg2: '+rfid0.readBlockStr(2))
      print('Tag_Reg3: '+rfid0.readBlockStr(3))
      #print('Tag_Reg4: '+rfid0.readBlockStr(4))
      #print('Tag_Reg5: '+rfid0.readBlockStr(5))
      #print('Tag_Reg6: '+rfid0.readBlockStr(6))
      #print('Tag_Reg7: '+rfid0.readBlockStr(7))
      #print('Tag_Reg8: '+rfid0.readBlockStr(8))
      #print('Tag_Reg9: '+rfid0.readBlockStr(9))
    except:
      print('#: Error occurs when RFID module reading the tag!'+"\r\n")
      continue
    wait_ms(5)
    rgb.setBrightness(5)
  else:
    TAG_near = 0
    RFID_ID = 0
    TAG_Reg0 = 0
  #----UART read from master
  if uart.any():
     print('Uart/Modbus Receved raw msg:')
     digitalWrite(LED_Blue_pin, 1)
     #print((uart.read()).decode(), 0, 0, 0xffffff)
     #print((uart.read()).decode())#bugs  UnicodeError: 
     RTU_master =uart.read()
     print((RTU_master))
     RTU_CMD_code = Modbus_RTU_MasterMsg_parse(RTU_master)
     print('Modbus request code:')
     print(str(RTU_CMD_code))
     if (RTU_CMD_code == Func_readID):
         rgb.setBrightness(16)
         rgb.setColorAll(0xdddd00)
         Modbus_send_NUID()
         wait_ms(50)
         rgb.setBrightness(5)
         rgb.setColorAll(0x000000)
     else:
         print('Modbus received wrong msg!!!')
         rgb.setBrightness(16)
         rgb.setColorAll(0xee1010)
         #Modbus_send_NUID()
         wait_ms(50)
         rgb.setBrightness(5)
         rgb.setColorAll(0x000000)
     digitalWrite(LED_Blue_pin, 0)
       
     #print(uart.read())#bugs  UnicodeError:
     #print('decode msg len: ')
     #print(str(len(RTU_master)))#None
     #print((uart.read()).decode()) 
     '''
     #Traceback (most recent call last):
     File "main.py", line 234, in <module>
     AttributeError: 'NoneType' object has no attribute 'decode'
     MicroPython f55bb7394-dirty on 2020-07-10; M5Stack with ESP32
     '''
  if(run_cnt % 10 ==0):
     #rgb.setColorAll(0x2f4fef)
     rgb.set_screen([0,0,0xFFFFFF,0,0,0,0xFFFFFF,0,0xFFFFFF,0,0xFFFFFF,0,0,0,0xFFFFFF,0,0xFFFFFF,0,0xFFFFFF,0,0,0,0xFFFFFF,0,0])
     wait_ms(10)
  if(run_cnt % 12 ==0):
     rgb.set_screen([0,0,0,0,0,0,0,0xfdb73f,0,0,0,0xfdb73f,0,0xfdb73f,0,0,0,0xfdb73f,0,0,0,0,0,0,0])
     wait_ms(10)
  if(run_cnt % 13 ==0):
     rgb.set_screen([0,0,0,0,0,0,0,0,0,0,0,0,0xfd3f3f,0,0,0,0,0,0,0,0,0,0,0,0])
     wait_ms(10)
     #rgb.setColorAll(0x000000)
  #run_cnt = run_cnt +1
  run_cnt = (run_cnt if isinstance(run_cnt, Number) else 0) + 1
  print('#-->:Run_cnt:'+str(run_cnt)+"\r\n")
  #uart.write('Run_cnt:'+str(run_cnt)+"\r\n")
  #run_cnt = (run_cnt if isinstance(run_cnt, Number) else 0) + 1
  wait_ms(20)
