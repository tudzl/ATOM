from m5stack import *
from m5ui import *
from uiflow import *
from machine import Modbus
import time

#V0.1 30.06.2020 test for 16BV demo modbus RTU mastre
print('< Intelligent 16-BV connector with RS485 Port & NFC program v1.1 >'+"\r\n");
print('< Author: Ling.Zell, li.zhou@staubli.com, 19.June.2020 >'+"\r\n");
print('#-->:i2c_bus.easyI2C(PORTA, 0x28, freq=100000)')

RS485_UART = (1,26,32) # TX,RX using Grove port
modbus = Modbus(1, 115200, 26, 32, Modbus.CRC_BIG)



REG_0 = None
RTU_funct = None
Slave_add = None
value = None
true_tmp = None



def modbus_recv_cb(x):
  global REG_0,RTU_funct,Slave_add,value,true_tmp
  Slave_add, RTU_funct, REG_0 = x.read()
  value = modbus.read()
  print(modbus.read())
  rgb.setColorAll(0xffffff)
  wait_ms(100)

  pass
modbus.set_recv_cb(modbus_recv_cb)


true_tmp = 1
Slave_add = 90
RTU_funct = 3
REG_0 = 1
modbus.send(Slave_add, RTU_funct, REG_0, 0)
while true_tmp:
  rgb.setColorAll(0x33cc00)
  modbus.send(Slave_add, RTU_funct, REG_0, 0)
  wait_ms(100)
  rgb.setColorAll(0xff6600)
  print(modbus.any())
  print(modbus.read())
  wait_ms(100)
  rgb.setColorAll(0x000000)
