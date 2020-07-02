from m5stack import *
from m5ui import *
from uiflow import *
from machine import Modbus
from machine import ModbusSlave
#modbus master(slave) test for 16-BV on m5stack fire
#Version v0.2
#1.7.2020, ling zhou

setScreenColor(0x222222)




title0 = M5Title(title="Modebus master v0.2", x=3 , fgcolor=0xFFFFFF, bgcolor=0x0000FF)
label_Slave_add = M5TextBox(20, 60, "Slave:", lcd.FONT_DejaVu24,0xef2a2a, rotate=0)
Funct = M5TextBox(20, 90, "Funct:", lcd.FONT_UNICODE,0xFFFFFF, rotate=0)
Data = M5TextBox(20, 130, "Data:", lcd.FONT_DejaVu24,0x69e70e, rotate=0)
label_BtnA = M5TextBox(47, 217, "Send", lcd.FONT_Default,0xeada4d, rotate=0)


Slave_add = None
RTU_funct = None
value_rx_tmp = None
REG_0 = None

Slave_add = 0x01
RTU_funct = 0x03
REG_0 = 0x00

#modbus = Modbus(1, 115200, 16, 17, Modbus.CRC_BIG) ##bugs!!!  port C 
modbus = Modbus(1, 115200, 21, 22, Modbus.CRC_BIG) ##test ok!  port A 
#26,32
def modbus_recv_cb(x):
  global Slave_add,RTU_funct,value_rx_tmp,REG_0
  Slave_add, RTU_funct, value_rx_tmp = x.read()
  label_Slave_add.setText(str(Slave_add))
  Funct.setText(str(RTU_funct))
  Data.setText(str(value_rx_tmp))

  pass
modbus.set_recv_cb(modbus_recv_cb)

def buttonA_wasPressed():
  global Slave_add, RTU_funct, value_rx_tmp, REG_0
  modbus_s.send(Slave_add, RTU_funct, REG_0, 1234)
  pass
btnA.wasPressed(buttonA_wasPressed)


while 1:
  rgb.setColorAll(0xffcc33)
  wait_ms(100)
  rgb.setColorAll(0x11ccaa)
  wait_ms(100)
