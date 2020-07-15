from m5stack import *
from m5ui import *
from uiflow import *
from machine import ModbusSlave
#ATOM_modbus_slave  14.07.2020


modbus_s = ModbusSlave(1, 1, 115200, 26, 32)



fun = None
REG_addr = None
tmp_data = None
var = None




def modbus_s_write_cb(x):
  global fun,REG_addr,tmp_data,var
  fun, REG_addr, tmp_data = x.read()
  var = tmp_data[1]
  if fun == 3 and REG_addr == 1:
    modbus_s.update_function(fun, REG_addr, 90)
    #send addr function reg addr value 接收到主机数据包后向主机回应发送的数据包内容
    modbus_s.send(1, 3, 1, 90)
    if var == 9:
      rgb.setColorAll(0x6600cc)
      print('modbus received msg!')

  pass
modbus_s.set_write_cb(modbus_s_write_cb)


def buttonA_wasPressed():
  global fun, REG_addr, tmp_data, var
  modbus_s.update_function(4, 1, 99)
  modbus_s.send(1, 3, 1, 99)
  rgb.setColorAll(0xff6600)
  print('modbus slave send msg!')
  pass
btnA.wasPressed(buttonA_wasPressed)




# 定义Modbus数据操作格式，function为功能码，reg addr为寄存器地址， value为初始默认值， method为读或写操作模式
modbus_s.init_function(4, 2, 100, ModbusSlave.METHOD_WRITE)
modbus_s.init_function(3, 1, 100, ModbusSlave.METHOD_READ)



