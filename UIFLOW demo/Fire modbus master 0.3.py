from m5stack import *
from m5ui import *
from uiflow import *
from machine import Modbus
#from machine import ModbusMaster #??
from machine import ModbusSlave
#modbus master(slave) test for 16-BV on m5stack fire
#Version v0.3
#24.7.2020, ling zhou
#API KEY 82E66B3E

setScreenColor(0x222222)




title0 = M5Title(title="Modebus master v0.3", x=3 , fgcolor=0xFFFFFF, bgcolor=0x0000FF)
label_Slave_add = M5TextBox(20, 60, "Slave:", lcd.FONT_DejaVu24,0xef2a2a, rotate=0)
Funct = M5TextBox(20, 90, "Funct:", lcd.FONT_DejaVu24,0xFFFFFF, rotate=0)
Funct_code =  M5TextBox(160, 90, "0x03", lcd.FONT_DejaVu24,0xFFFFFF, rotate=0)
Data = M5TextBox(20, 120, "Data:", lcd.FONT_DejaVu24,0x69e70e, rotate=0)
label_SL_add =  M5TextBox(20, 150, "TX-->Addr:", lcd.FONT_DejaVu24,0xef3a2a, rotate=0)
label_SL_var =  M5TextBox(160, 150, "0x01", lcd.FONT_DejaVu24,0xef3a2a, rotate=0)
label_BtnA_info = M5TextBox(40, 220, "Send1", lcd.FONT_DejaVu18,0xeadacd, rotate=0)
label_BtnA_info = M5TextBox(240, 220, "Send2", lcd.FONT_DejaVu18,0xeadacd, rotate=0)
label_msg_tx = M5TextBox(20, 180, "TX_cnt:", lcd.FONT_DejaVu18,0xeadafd, rotate=0)
label_msg_tx_CNT = M5TextBox(160, 180, "0", lcd.FONT_DejaVu18,0xeaeaed, rotate=0)
print('Fire Modebus master v0.3 ')

Slave_add = None
RTU_funct = None
value_rx_tmp = None
REG_0 = None
TX_CNT= None

Slave_add = 0x01
RTU_funct = 0x03
REG_0 = 0x00
TX_CNT = 0

#modbus = Modbus(1, 115200, 17, 16, Modbus.CRC_BIG) ##bugs!!! crashs  port C 
#modbus = Modbus(2, 115200, 16, 17, Modbus.CRC_BIG) ##bugs!!! crashs  port C 
modbus_m = Modbus(1, 115200, 21, 22, Modbus.CRC_BIG) ##test ok!  port A  G_5V_G21_G22
#26,32
def modbus_recv_cb(x):
  global Slave_add,RTU_funct,value_rx_tmp,REG_0
  Slave_add, RTU_funct, value_rx_tmp = x.read()
  label_Slave_add.setText(str(Slave_add))
  Funct.setText(str(RTU_funct))
  Data.setText(str(value_rx_tmp))
  print('Modbus Receved msg from slave! ')
  pass
modbus_m.set_recv_cb(modbus_recv_cb)

def buttonA_wasPressed():
  global Slave_add, RTU_funct, REG_0,TX_CNT
  Slave_add =0x01
  RTU_funct =0x03
  modbus_m.send(Slave_add, RTU_funct, REG_0, 12)
  print('buttonA was Pressed, modbus_s.send! ')
  TX_CNT+=1
  pass
btnA.wasPressed(buttonA_wasPressed)

def buttonC_wasPressed():
  global Slave_add, RTU_funct, value_rx_tmp, REG_0,TX_CNT
  Slave_add =0x02
  RTU_funct =0x04
  modbus_m.send(Slave_add, RTU_funct, REG_0, 90)
  print('buttonC was Pressed, modbus_s.send! ')
  TX_CNT+=1
  print(str(TX_CNT))
  pass
btnC.wasPressed(buttonC_wasPressed)


while 1:
  label_SL_var.setText(str(Slave_add))
  Funct_code.setText(str(RTU_funct))
  label_msg_tx_CNT.setText(str(TX_CNT))
  TX_CNT+=0
  rgb.setColorAll(0xffcc33)
  wait_ms(100)
  rgb.setColorAll(0x11ccaa)
  wait_ms(100)
  
