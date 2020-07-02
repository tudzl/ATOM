from m5stack import *
from m5ui import *
from uiflow import *
from machine import Modbus
from machine import ModbusSlave

rgb.set_screen([])


modbus_s = ModbusSlave(_AF9_5EaoeXNU9_60_5E_BsS8_, 1, 115200, 26, 32)



Slave_add = None
RTU_funct = None
value_rx_tmp = None
REG_0 = None



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


Slave_add = 1
modbus_s.init_function(RTU_funct, REG_0, 101, ModbusSlave.METHOD_READ)
rgb.setColorAll(0x33ff33)
