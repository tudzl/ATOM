#INA260 LM75BD(NXP) demo, APIKEY: 5E9363E1
#V2.6 12.feb added btn to increase or decrease T alert function
#V2.5 12.feb  fit to ATOM matrix, add LED display of Temp.
#V2.4 3.Feb.2021, add INA260
#V2.3 27.Jan.2021,  bug solved when sensor A non-exist
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
INA260_ADDRESS	 = 0x40  #1000000 @ A0,A1=GND
LM75_ADDRESS	 = 0x48
LM75_ADDRESS2	 = 0x49

#--------Reg address---------
INA260_REG_CONFIG = const(0x00)  # CONFIGURATION REGISTER (R/W)
INA260_REG_CURRENT = const(0x01)  # SHUNT VOLTAGE REGISTER (R)
INA260_REG_BUSVOLTAGE = const(0x02)  # BUS VOLTAGE REGISTER (R)
INA260_REG_POWER = const(0x03)  # POWER REGISTER (R)
INA260_REG_MASK_ENABLE = const(0x06)  # MASK ENABLE REGISTER (R/W)
INA260_REG_ALERT_LIMIT = const(0x07)  # ALERT LIMIT REGISTER (R/W)
INA260_REG_MFG_UID = const(0xFE)  # MANUFACTURER UNIQUE ID REGISTER (R)
INA260_REG_DIE_UID = const(0xFF)  # DIE UNIQUE ID REGISTER (R)




LM75_TEMP_REGISTER 	 = 0
LM75_CONF_REGISTER 	 = 1
LM75_THYST_REGISTER 	 = 2
LM75_TOS_REGISTER 	 = 3

LM75_CONF_SHUTDOWN  	 = 0
LM75_CONF_OS_COMP_INT 	 = 1
LM75_CONF_OS_POL 	 = 2
LM75_CONF_OS_F_QUE 	 = 3

#global para vars
Current_alert = 5000 # in mA
DIR = 1
T_alert = 55  #in C degree
T_OS1= (T_alert* 32*8 )
T_OS1_reg_data = T_OS1.to_bytes(2,'b') 



#increase or decrease
def buttonA_wasPressed():
  # global params
  global T_alert,DIR
  rgb.set_screen([0xed1212,0xed1212,0xed1212,0xed1212,0xed1212,0xed1212,0,0,0,0xed1212,0xed1212,0,0,0,0xed1212,0xed1212,0,0,0,0xed1212,0xed1212,0xed1212,0xed1212,0xed1212,0xed1212])
  wait_ms(200)
  print('->:buttonA was pressed!, DIR:'+str(DIR))
  T_alert= DIR+T_alert
  if (T_alert>=100):
     T_alert =99
  elif (T_alert<0):
     T_alert = 0
  rgb.setBrightness(15)
  print('T Alert:'+str(T_alert))
  rgb.setColorAll(0x000000)
  TA_MSB = int (T_alert/10.0)
  show_num_single(TA_MSB)
  wait_ms(800)
  TA_LSB = int(T_alert - TA_MSB*10)
  show_num_single(TA_LSB)
  print('T_alert MSB:'+str(TA_MSB))
  print('T_alert LSB:'+str(TA_LSB))
  wait_ms(800) 
  rgb.setBrightness(10)
  rgb.setColorAll(0x022233)
  wait_ms(200) 
  pass
btnA.wasPressed(buttonA_wasPressed)


#display single digit number
def show_num_single(num):
    if (num == 0):
      rgb.set_screen([0,0,0xF0F000,0,0,0,0xF0F000,0,0xF0F000,0,0,0xF0F000,0,0xF0F000,0,0,0xF0F000,0,0xF0F000,0,0,0,0xF0F000,0,0])
    elif (num == 1):
      rgb.set_screen([0,0,0xFFFFEE,0,0,0,0xFFFFEE,0xFFFFEE,0,0,0,0,0xFFFFEE,0,0,0,0,0xFFFFEE,0,0,0,0,0xFFFFEE,0,0])
    elif (num == 2):
      rgb.set_screen([0,0xFFFFEE,0xFFFFEE,0,0,0xFFFFEE,0,0,0xFFFFEE,0,0,0,0xFFFFEE,0xFFFFEE,0,0,0xFFFFEE,0,0,0,0xFFFFEE,0xFFFFEE,0xFFFFEE,0xFFFFEE,0])
    elif (num == 3):
      rgb.set_screen([0,0xFFFFEE,0xFFFFEE,0xFFFFEE,0,0,0,0,0,0xFFFFEE,0,0,0xFFFFEE,0xFFFFEE,0xFFFFEE,0,0,0,0,0xFFFFEE,0,0xFFFFEE,0xFFFFEE,0xFFFFEE,0])
    elif (num == 4):
      rgb.set_screen([0,0,0,0xFFFFEE,0,0,0,0xFFFFEE,0xFFFFEE,0,0,0xFFFFEE,0,0xFFFFEE,0,0,0xFFFFEE,0xFFFFEE,0xFFFFEE,0xFFFFEE,0,0,0,0xFFFFEE,0])
    elif (num == 5):
      rgb.set_screen([0,0xFFFFEE,0xFFFFEE,0xFFFFEE,0,0,0xFFFFEE,0,0,0,0,0xFFFFEE,0xFFFFEE,0xFFFFEE,0,0,0,0,0,0xFFFFEE,0,0xFFFFEE,0xFFFFEE,0xFFFFEE,0])
    elif (num == 6):
      rgb.set_screen([0,0xFFFFEE,0xFFFFEE,0xFFFFEE,0,0,0xFFFFEE,0,0,0,0,0xFFFFEE,0xFFFFEE,0xFFFFEE,0,0,0xFFFFEE,0,0xFFFFEE,0,0,0xFFFFEE,0xFFFFEE,0xFFFFEE,0])
    elif (num == 7):
      rgb.set_screen([0,0xFFFFEE,0xFFFFEE,0xFFFFEE,0,0,0,0,0xFFFFEE,0,0,0,0,0xFFFFEE,0,0,0,0,0xFFFFEE,0,0,0,0,0xFFFFEE,0])
    elif (num == 8):
      rgb.set_screen([0,0xFFFFEE,0xFFFFEE,0xFFFFEE,0,0,0xFFFFEE,0,0xFFFFEE,0,0,0xFFFFEE,0xFFFFEE,0xFFFFEE,0,0,0xFFFFEE,0,0xFFFFEE,0,0,0xFFFFEE,0xFFFFEE,0xFFFFEE,0])
    elif (num == 9):
      rgb.set_screen([0,0xFFFFEE,0xFFFFEE,0xFFFFEE,0,0,0xFFFFEE,0,0xFFFFEE,0,0,0xFFFFEE,0xFFFFEE,0xFFFFEE,0,0,0,0,0xFFFFEE,0,0,0xFFFFEE,0xFFFFEE,0xFFFFEE,0])
    pass
#decrease/increase by DIR
def buttonA_pressFor():
  # global params
  global DIR
  #DIR = -1*DIR
  print('->:buttonA was pressFor 0.8s, DIR:'+str(DIR))
  wait_ms(300)
  pass
btnA.pressFor(0.9, buttonA_pressFor)


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

print('ATOM Matrix LM75 Temp measurement and heating control program v2.6')
print('Author: Zell, 12.Feb.2021')
tmp_str = None
Vbus= 0
Current = 0
Power_INA = 0
T_LM75A = 0
T_LM75B = 0
TF1 = 0
TF2 = 0
SensorA_scan_cnt = 0
SensorB_scan_cnt = 0
INA_OK = False
LM75A1_OK = False
LM75A2_OK = False
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
        if (INA260_ADDRESS == addrList[i]):
           rgb.setColorAll(0xEEEEBB)
           print('>:INA260 detected!')
           INA_OK = True
           wait_ms(100)
           
        if (LM75_ADDRESS == addrList[i]):
           print('>:LM75_1 detected!')
           LM75A1_OK = True   
                      
        if (LM75_ADDRESS2 == addrList[i]):
           print('>:LM75_2 detected!')
           LM75A2_OK = True   
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
print('#>:IIC scan finished, main control starts running')
while 1:
    rgb.setBrightness(10)
    if(INA_OK):
      try:
        i2c0 = i2c_bus.easyI2C(IIC_PORTA, INA260_ADDRESS, freq=100000)
        Current_raw = i2c0.read_reg(INA260_REG_CURRENT,2)
        print ('Current_raw: '+str(Current_raw))
         #positive values   
        Current = int.from_bytes(Current_raw, True) #B uint8; b int8;signed 
        #negative values   
        if(Current > 32768):
           Current = Current - 65536
        Current = 1.25*Current
        if ((abs(Current)>1000)):
          print ('Current: '+str(Current/1000.0)+'A')
        else:
          print ('Current: '+str(Current)+'mA')
        
        Voltage_raw = i2c0.read_reg(INA260_REG_BUSVOLTAGE,2)
        Vbus =  int.from_bytes(Voltage_raw, 'b') #B uint8; b int8;signed 
        Vbus = 1.25*Vbus/1000.0
        print ('Vbus: '+str(Vbus)+'V')
        
        Power_raw = i2c0.read_reg(INA260_REG_POWER,2)
        Power_INA =  10.0* int.from_bytes(Power_raw, 'b') #B uint8; b int8;signed 
        print ('Power: '+str(Power_INA)+'mW')
  
      except:
        print('INA260 read error')
        rgb.setColorAll(0xff1133)
        wait_ms(100)
        rgb.setColorAll(0x000000)
        #continue
  
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
        print ('')
        print ('TS1: '+str(TF1)+'C')
        print ('')
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
        #rgb.setColorAll(0xff3311)
        wait_ms(100)
        #rgb.setColorAll(0x000000)
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
         rgb.set_screen([0,0xf52905,0xf52905,0xf52905,0,0xf52905,0xf844ad,0xf844ad,0xf844ad,0xf52905,0xf52905,0xf844ad,0xf8f7f7,0xf844ad,0xf52905,0xf52905,0xf844ad,0xf844ad,0xf844ad,0xf52905,0,0xf52905,0xf52905,0xf52905,0])
         print ('<Low T>:output activated!')
      elif(TF > T_alert+2): #Blue, over T, turn off PMOS
         digitalWrite(PMOS_gate_pin, 0)
         OUT_EN = False
         rgb.set_screen([0,0xdade0d,0xdade0d,0xdade0d,0,0xdade0d,0x1919e1,0,0x1919e1,0xdade0d,0xdade0d,0,0x1919e1,0,0xdade0d,0xdade0d,0x1919e1,0,0x1919e1,0xdade0d,0,0xdade0d,0xdade0d,0xdade0d,0])
         print ('<High T>:output disabled!')
      else: 
         print ('<Window T>:output unchanged')
         #rgb.setColorAll(0x008010) #Green T is in threshold window
         rgb.set_screen([0,0xde1b56,0xde1b56,0xde1b56,0,0xde1b56,0x1bde3c,0x1bde3c,0x1bde3c,0xde1b56,0xde1b56,0x1bde3c,0x1bde3c,0x1bde3c,0xde1b56,0xde1b56,0x1bde3c,0x1bde3c,0x1bde3c,0xde1b56,0,0xde1b56,0xde1b56,0xde1b56,0])
         print ('#PMOS driver gate:'+str(OUT_EN))
      wait_ms(100)
      #rgb.setColorAll(0x001100)
    except:
      print('T->gate control error')
      rgb.setColorAll(0xff1133)
      wait_ms(100)
      rgb.setColorAll(0x000000)
      continue
    
    sys_cnt =sys_cnt+1
    
    if(sys_cnt%10 ==0):
      rgb.setBrightness(15)
      print('T measured:'+str(TF))
      rgb.setColorAll(0x000000)
      TS_MSB = int (TF/10.0)
      show_num_single(TS_MSB)
      wait_ms(500)
      TS_LSB = int(TF - TS_MSB*10)
      show_num_single(TS_LSB)
      print('T MSB:'+str(TS_MSB))
      print('T LSB:'+str(TS_LSB))
      wait_ms(500) 
      rgb.setBrightness(10)
      rgb.setColorAll(0x222200)
    if(sys_cnt%50 ==0):
       print('Sys run cnt:'+str(sys_cnt))