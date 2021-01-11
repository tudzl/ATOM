#ATOM IIC scan demo
#11.Jan.2021
from m5stack import *
from m5ui import *
from uiflow import *
import i2c_bus
import time

#ATOM IIC scan demo
#11.Jan.2021
print('ATOM IIC scan demo v2.0')
addrList = None
Dev_cnt = 0

#i2c0 = i2c_bus.easyI2C(i2c_bus.PORTA, 0x68, freq=100000)
i2c0 = i2c_bus.easyI2C((26, 32), 0x68, freq=100000)
while 1:
    try :
      addrList = i2c0.scan()
      Dev_cnt=len(addrList)
      print('IIC scan results:')
      #print(addrList)
      #print("0x")
      for i in range(0, Dev_cnt, 1):
        print('0x'+'%2x%%'%((addrList[i])))
        
      print('Total device:'+str(Dev_cnt))
      if (Dev_cnt>0):
        rgb.setColorAll(0x03ff13)
      else:
        rgb.setColorAll(0x101000)
      #lcd.print("%02x%%" % ((addrList)), 10, 100, COLOR_GREEN)
      #lcd.print("0x", 10, 80, 0xFFAAAA)
      #------display in hex format
      wait_ms(500)
      rgb.setColorAll(0x000000)
      pass
    except:
      print('scan error')
      rgb.setColorAll(0xff1133)
      wait_ms(100)
      rgb.setColorAll(0x000000)
      continue

