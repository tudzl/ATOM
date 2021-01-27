#LM75BD(NXP) demo, 
#V2.2 19.Jan.2021, 2 sensor support!
#v2.1 13.Jan.2021
#LM75BD(NXP) demo, 13.Jan.2021
#mit INA260 base
from m5stack import *
from m5ui import *
from uiflow import *
from easyIO import *
import i2c_bus
import time


IIC_PORTA = (25,21) # I2C  base 485 PCB for 16BV demo
PMOS_gate_pin = 33
LM75_ADDRESS	 = 0x48
LM75_ADDRESS2	 = 0x49
LM75_TEMP_REGISTER 	 = 0
LM75_CONF_REGISTER 	 = 1
LM75_THYST_REGISTER 	 = 2
LM75_TOS_REGISTER 	 = 3

LM75_CONF_SHUTDOWN  	 = 0
LM75_CONF_OS_COMP_INT 	 = 1
LM75_CONF_OS_POL 	 = 2
LM75_CONF_OS_F_QUE 	 = 3

#para vars
T_alert = 30
T_OS1= (T_alert* 32*8 )
T_OS1_reg_data = T_OS1.to_bytes(2,'b') 

#class LM75(object):
class LM75():
	def __init__(self, mode=LM75_CONF_OS_COMP_INT, address=LM75_ADDRESS):
		self._mode = mode
		self._address = address
		#self._bus = smbus.SMBus(busnum)
		self._bus =i2c_bus.i2c0
		#i2c0.read_reg(0x00, 2))

	def regdata2float (self, regdata):
		return (regdata / 32.0) / 8.0
	def toFah(self, temp):
		return (temp * (9.0/5.0)) + 32.0
	#def setTosReg(value) 
	  #i2c0.write_u16(LM75_TOS_REGISTER,value, byteorder="big") # not working
	  #i2c0.write_mem_data(LM75_TOS_REGISTER, value, i2c_bus.INT16LE)
	  #i2c0.write_data(0, i2c_bus.UINT8LE)
	  #return 0

	def getRawTemp():
		"""Reads the raw temp from the LM75 sensor"""
		#raw = self._bus.read_word_data(self._address, LM75_TEMP_REGISTER) & 0xFFFF
		raw = i2c0.read_reg(LM75_TEMP_REGISTER,2)
		#print "raw: "
		#print raw
		#raw_int = ((raw << 8) & 0xFF00) + (raw >> 8)
		return raw
	def CalcTemp(raw):
		"""calc the temp from the raw LM75 sensor value(11bit), LSB 0.125 C"""
		#raw = self._bus.read_word_data(self._address, LM75_TEMP_REGISTER) & 0xFFFF
		Temp_int = int.from_bytes(raw,'b') #B uint8; b int8
		Temp_F = (Temp_int / 32.0) / 8.0 
		#Temp_F = Temp_F * (9.0/5.0) + 32.0
		#print "raw: "
		#print raw
		#raw_int = ((raw << 8) & 0xFF00) + (raw >> 8)
		return Temp_F
		
	def getTemp(self): #not working!
		"""Reads the temp from the LM75 sensor"""
		#raw = self._bus.read_word_data(self._address, LM75_TEMP_REGISTER) & 0xFFFF
		raw = self._bus.read_reg(LM75_TEMP_REGISTER,2) & 0xFFFF
		#print "raw: "
		#print raw
		#raw = ((raw << 8) & 0xFF00) + (raw >> 8)
		return self.toFah(self.regdata2float(raw))

print('ATOM LM75 Temp measurement program v2.2')
print('Author: Zell, 19.Jan.2021')
tmp_str = None
T_LM75A = 0
T_LM75B = 0
TF1 = 0
TF2 = 0
SensorA_scan_cnt = 0
SensorB_scan_cnt = 0
sys_cnt = 0

#i2c0 = i2c_bus.easyI2C((26, 32), LM75_ADDRESS, freq=100000)
i2c0 = i2c_bus.easyI2C(IIC_PORTA, LM75_ADDRESS2, freq=100000)
LM75_sensor = LM75
Scan_EN = True
OUT_EN = True
while (Scan_EN):
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
        Scan_EN = False
      else:
        rgb.setColorAll(0x101000)
        Scan_EN = True
      #lcd.print("%02x%%" % ((addrList)), 10, 100, COLOR_GREEN)
      #lcd.print("0x", 10, 80, 0xFFAAAA)
      #------display in hex format
      wait_ms(500)
      rgb.setColorAll(0x000000)
      pass
    except:
      print('IIC scan error')
      rgb.setColorAll(0xff1133)
      wait_ms(100)
      rgb.setColorAll(0x000000)
      continue
while 1:
    if(SensorA_scan_cnt ==0 ):
      try :
        rgb.setColorAll(0x222200)
        #tmp_str = i2c0.scan()
        #print(tmp_str)
        #label0.setText(str(tmp_str))
        #T_LM75A= i2c0.read_reg(LM75_TEMP_REGISTER, 2)
        i2c0 = i2c_bus.easyI2C(IIC_PORTA, LM75_ADDRESS, freq=100000)
        T_LM75A = LM75_sensor.getRawTemp()
        TF1 = LM75_sensor.CalcTemp(T_LM75A)
        print ('TS1: '+str(TF1)+'C')
        #i2c0 = i2c_bus.easyI2C(IIC_PORTA, LM75_ADDRESS2, freq=100000)
        #T_LM75B = LM75_sensor.getRawTemp()
        #TF2 = LM75_sensor.CalcTemp(T_LM75B)
        #print ('TS2: '+str(TF2)+'C')
      except:
        SensorA_scan_cnt = 50
        print('LM75_A read error')
        rgb.setColorAll(0xff1133)
        wait_ms(100)
        rgb.setColorAll(0x000000)
        #continue
    else:
      SensorA_scan_cnt =SensorA_scan_cnt-1 #count to skip scan non-exist sensor
      
    if(SensorB_scan_cnt ==0 ):
      try :
        i2c0 = i2c_bus.easyI2C(IIC_PORTA, LM75_ADDRESS2, freq=100000)
        T_LM75B = LM75_sensor.getRawTemp()
        TF2 = LM75_sensor.CalcTemp(T_LM75B)
        print ('TS2: '+str(TF2)+'C')
        
        
      except:
        SensorB_scan_cnt = 50
        print('LM75_B read error')
        rgb.setColorAll(0xff3311)
        wait_ms(100)
        rgb.setColorAll(0x000000)
        #continu
    else:
      SensorB_scan_cnt =SensorB_scan_cnt-1 #count to skip scan non-exist sensor
      
    if(SensorA_scan_cnt*SensorB_scan_cnt>0):
       print('->:LM75 sensor does not exist!!!')
       rgb.setColorAll(0xEE0101)
       wait_ms(10)
       continue
       #wait_ms(100)
       
    try :  
      if (TF1>=TF2):
          TF = TF1
      else:
          TF = TF2
      if (TF < T_alert): #Red, under T, turn on PMOS
         digitalWrite(PMOS_gate_pin, 1)
         OUT_EN = True
         rgb.setColorAll(0xB73600)
         print ('<Low T>:output activated!')
      elif(TF > T_alert+2): #Blue, over T, turn off PMOS
         digitalWrite(PMOS_gate_pin, 0)
         OUT_EN = False
         rgb.setColorAll(0x0016B0)
         print ('<High T>:output disabled!')
      else: 
         print ('<Window T>:output unchanged')
         rgb.setColorAll(0x008010) #Green T is in threshold window
         print ('#PMOS driver gate:'+str(OUT_EN))
      wait_ms(300)
      rgb.setColorAll(0x001100)
    except:
      print('T->gate control error')
      rgb.setColorAll(0xff1133)
      wait_ms(100)
      rgb.setColorAll(0x000000)
      continue
    sys_cnt =sys_cnt+1
    if(sys_cnt%50 ==0):
       print('Sys run cnt:'+str(sys_cnt))
  
   
    
'''--------debug output----------
<Low T>:output activated!
TS1: 28.25C
TS2: 25.5C
<Low T>:output activated!
TS1: 28.375C
TS2: 25.5C
<Low T>:output activated!
'''

  