from m5stack import *
from m5ui import *
from uiflow import *
from easyIO import *
from machine import ModbusSlave
from machine import UART
import i2c_bus
import unit
from numbers import Number
import time
from micropython import const
try:
    import struct
except ImportError:
    import ustruct as struct

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
#BMP388

_CHIP_ID = const(0x50)

# pylint: disable=import-outside-toplevel
_REGISTER_CHIPID = const(0x00)
_REGISTER_STATUS = const(0x03)
_REGISTER_PRESSUREDATA = const(0x04)
_REGISTER_TEMPDATA = const(0x07)
_REGISTER_CONTROL = const(0x1B)
_REGISTER_OSR = const(0x1C)
_REGISTER_ODR = const(0x1D)
_REGISTER_CONFIG = const(0x1F)
_REGISTER_CAL_DATA = const(0x31)
_REGISTER_CMD = const(0x7E)
_OSR_SETTINGS = (1, 2, 4, 8, 16, 32)  # pressure and temperature oversampling settings
_IIR_SETTINGS = (0, 2, 4, 8, 16, 32, 64, 128)  # IIR filter coefficients
class BMP3XX:
    """Base class for BMP3XX sensor."""

    def __init__(self):
        chip_id = self._read_byte(_REGISTER_CHIPID)
        if _CHIP_ID != chip_id:
            raise RuntimeError("Failed to find BMP3XX! Chip ID 0x%x" % chip_id)
        self._read_coefficients()
        self.reset()
        self.sea_level_pressure = 1013.25
        """Sea level pressure in hPa."""

    @property
    def pressure(self):
        """The pressure in hPa."""
        return self._read()[0] / 100

    @property
    def temperature(self):
        """The temperature in deg C."""
        return self._read()[1]

    @property
    def altitude(self):
        """The altitude in meters based on the currently set sea level pressure."""
        # see https://www.weather.gov/media/epz/wxcalc/pressureAltitude.pdf
        return 44307.7 * (1 - (self.pressure / self.sea_level_pressure) ** 0.190284)

    @property
    def pressure_oversampling(self):
        """The pressure oversampling setting."""
        return _OSR_SETTINGS[self._read_byte(_REGISTER_OSR) & 0x07]

    @pressure_oversampling.setter
    def pressure_oversampling(self, oversample):
        if oversample not in _OSR_SETTINGS:
            raise ValueError("Oversampling must be one of: {}".format(_OSR_SETTINGS))
        new_setting = self._read_byte(_REGISTER_OSR) & 0xF8 | _OSR_SETTINGS.index(
            oversample
        )
        self._write_register_byte(_REGISTER_OSR, new_setting)

    @property
    def temperature_oversampling(self):
        """The temperature oversampling setting."""
        return _OSR_SETTINGS[self._read_byte(_REGISTER_OSR) >> 3 & 0x07]

    @temperature_oversampling.setter
    def temperature_oversampling(self, oversample):
        if oversample not in _OSR_SETTINGS:
            raise ValueError("Oversampling must be one of: {}".format(_OSR_SETTINGS))
        new_setting = (
            self._read_byte(_REGISTER_OSR) & 0xC7 | _OSR_SETTINGS.index(oversample) << 3
        )
        self._write_register_byte(_REGISTER_OSR, new_setting)

    @property
    def filter_coefficient(self):
        """The IIR filter coefficient."""
        return _IIR_SETTINGS[self._read_byte(_REGISTER_CONFIG) >> 1 & 0x07]

    @filter_coefficient.setter
    def filter_coefficient(self, coef):
        if coef not in _IIR_SETTINGS:
            raise ValueError(
                "Filter coefficient must be one of: {}".format(_IIR_SETTINGS)
            )
        self._write_register_byte(_REGISTER_CONFIG, _IIR_SETTINGS.index(coef) << 1)

    def reset(self):
        """Perform a power on reset. All user configuration settings are overwritten
        with their default state.
        """
        self._write_register_byte(_REGISTER_CMD, 0xB6)

    def _read(self):
        """Returns a tuple for temperature and pressure."""
        # OK, pylint. This one is all kinds of stuff you shouldn't worry about.
        # pylint: disable=invalid-name, too-many-locals

        # Perform one measurement in forced mode
        self._write_register_byte(_REGISTER_CONTROL, 0x13)

        # Wait for *both* conversions to complete
        while self._read_byte(_REGISTER_STATUS) & 0x60 != 0x60:
            time.sleep(0.002)

        # Get ADC values
        data = self._read_register(_REGISTER_PRESSUREDATA, 6)
        adc_p = data[2] << 16 | data[1] << 8 | data[0]
        adc_t = data[5] << 16 | data[4] << 8 | data[3]

        # datasheet, sec 9.2 Temperature compensation
        T1, T2, T3 = self._temp_calib

        pd1 = adc_t - T1
        pd2 = pd1 * T2

        temperature = pd2 + (pd1 * pd1) * T3

        # datasheet, sec 9.3 Pressure compensation
        P1, P2, P3, P4, P5, P6, P7, P8, P9, P10, P11 = self._pressure_calib

        pd1 = P6 * temperature
        pd2 = P7 * temperature ** 2.0
        pd3 = P8 * temperature ** 3.0
        po1 = P5 + pd1 + pd2 + pd3

        pd1 = P2 * temperature
        pd2 = P3 * temperature ** 2.0
        pd3 = P4 * temperature ** 3.0
        po2 = adc_p * (P1 + pd1 + pd2 + pd3)

        pd1 = adc_p ** 2.0
        pd2 = P9 + P10 * temperature
        pd3 = pd1 * pd2
        pd4 = pd3 + P11 * adc_p ** 3.0

        pressure = po1 + po2 + pd4

        # pressure in Pa, temperature in deg C
        return pressure, temperature

    def _read_coefficients(self):
        """Read & save the calibration coefficients"""
        coeff = self._read_register(_REGISTER_CAL_DATA, 21)
        # See datasheet, pg. 27, table 22
        coeff = struct.unpack("<HHbhhbbHHbbhbb", coeff)
        # See datasheet, sec 9.1
        # Note: forcing float math to prevent issues with boards that
        #       do not support long ints for 2**<large int>
        self._temp_calib = (
            coeff[0] / 2 ** -8.0,  # T1
            coeff[1] / 2 ** 30.0,  # T2
            coeff[2] / 2 ** 48.0,
        )  # T3
        self._pressure_calib = (
            (coeff[3] - 2 ** 14.0) / 2 ** 20.0,  # P1
            (coeff[4] - 2 ** 14.0) / 2 ** 29.0,  # P2
            coeff[5] / 2 ** 32.0,  # P3
            coeff[6] / 2 ** 37.0,  # P4
            coeff[7] / 2 ** -3.0,  # P5
            coeff[8] / 2 ** 6.0,  # P6
            coeff[9] / 2 ** 8.0,  # P7
            coeff[10] / 2 ** 15.0,  # P8
            coeff[11] / 2 ** 48.0,  # P9
            coeff[12] / 2 ** 48.0,  # P10
            coeff[13] / 2 ** 65.0,
        )  # P11

    def _read_byte(self, register):
        """Read a byte register value and return it"""
        #return self._read_register(register, 1)[0]
        return self._read_register(register, 1)

    def _read_register(self, register, length):
        """Low level register reading, not implemented in base class"""
        raise NotImplementedError()

    def _write_register_byte(self, register, value):
        """Low level register writing, not implemented in base class"""
        raise NotImplementedError()


class BMP3XX_I2C(BMP3XX):
    """Driver for I2C connected BMP3XX. Default address is 0x77 but another address can be passed
       in as an argument"""
    
    def __init__(self, i2c, address=0x77):
        #import adafruit_bus_device.i2c_device as i2c_device

        #self._i2c = i2c_device.I2CDevice(i2c, address)
        #super().__init__()
        return
    

    def _read_register(register, length):
            """Low level register reading over I2C, returns a list of values"""
            result = bytearray(length)
            #i2c.write(bytes([register & 0xFF]))
            #i2c.write_u8(bytes([register & 0xFF]))
            #i2c.readinto(result)
            result = i2c.read_u8(bytes([register & 0xFF]))
            
            return result

    def _write_register_byte(register, value):
            """Low level register writing over I2C, writes one 8-bit value"""
            #i2c.write(bytes((register & 0xFF, value & 0xFF)))
            i2c.write_u8(bytes((register & 0xFF, value & 0xFF)))

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
i2c0 = i2c_bus.easyI2C(IIC_PORTA, 0x77, freq=100000)

#BMP388 demo

#bmp = BMP3XX()
bmp = BMP3XX_I2C(i2c0)
#bmp = BMP3XX_I2C(i2c0)  #TypeError: function takes 1 positional arguments but 2 were given
bmp.pressure_oversampling = 8
bmp.temperature_oversampling = 2


RFID_ID_pre ='00000000'


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
  
  





rgb.setColorAll(0x666633)
digitalWrite(LED_Green_pin, 1)
while 1:
  print('#-->:i2c init now...')  
  try:
    rgb.set_screen([0xe7fd3f,0,0xe7fd3f,0,0,0,0,0,0xca3ffd,0xca3ffd,0x3fabfd,0,0x3fabfd,0xca3ffd,0,0x3fabfd,0,0x3fabfd,0xca3ffd,0xca3ffd,0,0,0,0,0])
    print(' i2c0.scan results:')
    addrList=i2c0.scan()
    Dev_cnt=len(addrList)
    print(addrList)#DEC
    wait_ms(10)
    print(' i2c device available ?:'+str(i2c0.available()))# --> specified slave address
    print(' i2c device number:'+str(Dev_cnt))
    #i2c0.write_u8(0x01, 0xAA)
    wait_ms(50)
    #rgb.setColorAll(0x001133)
    
    for i in range(0, Dev_cnt, 1):
     if (104==addrList[i]): #MPU6886
        rgb.set_screen([0x3ffda1,0x3f91fd,0x3f91fd,0x3f91fd,0,0x3f91fd,0x3ffda1,0,0,0x3f91fd,0x3f91fd,0,0xe7fd3f,0,0x3f91fd,0x3f91fd,0,0,0x3ffda1,0x3f91fd,0,0x3f91fd,0x3f91fd,0x3f91fd,0x3ffda1])
        print(' MPU6886 sensor is connected!')
        wait_ms(500)
     if (119==addrList[i]): #BMP388
        rgb.set_screen([0,0xffffff,0,0xffffff,0,0xFFFFFF,0,0xee7ce5,0,0xFFFFFF,0,0xee7ce5,0xee7ce5,0xee7ce5,0,0xFFFFFF,0,0xee7ce5,0,0xFFFFFF,0,0xffffff,0,0xffffff,0])
        print(' BMP388 sensor is connected!')
        wait_ms(500)
    #rfid0 = unit.get(unit.RFID, unit.PORTA) # not fit to ATOM
    #rfid0 = unit.get(unit.RFID, unit.PORTA) # fit ATOM?
    #rfid0 = unit.get(unit.RFID, unit.(25,21)) # fit ATOM?
    #Connect this Unit to GROVE PORTA on M5Core, IIC adress is 0x28.
    #need improve for unit disconnected case 
    #print(' RFID module is connected!'+"\r\n")
    
    break
  except:
    digitalWrite(LED_Blue_pin, 1)
    print(' IIC not detected! Please Check! Main code will not run!!!'+"\r\n")
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
  print('#-->:BMP388 scanning now...')  
  BMP_temp=bmp.temperature
  try:
    rgb.set_screen([0xe7fd3f,0,0xe7fd3f,0,0,0,0,0,0xca3ffd,0xca3ffd,0x3fabfd,0,0x3fabfd,0xca3ffd,0,0x3fabfd,0,0x3fabfd,0xca3ffd,0xca3ffd,0,0,0,0,0])

    print(
        "Pressure: {:6.1f}  Temperature: {:5.2f}".format(bmp.pressure, bmp.temperature)
    )
    
  except:
    digitalWrite(LED_Blue_pin, 1)
    print(' IIC BMP388 readout failed!!!'+"\r\n")
    rgb.set_screen([0xfd3f3f,0xfd3f3f,0xfd3f3f,0,0x823ffd,0xfd3f3f,0,0xfd3f3f,0x823ffd,0,0xfd3f3f,0,0xfd3f3f,0x823ffd,0,0xfd3f3f,0,0xfd3f3f,0x823ffd,0,0xfd3f3f,0,0xfd3f3f,0,0x823ffd])
    #rgb.setColorAll(0xFF0000)
    #rgb.set_screen([0,0,0xFF0000,0,0,0,0xFFFFFF,0,0xFF0000,0,0xFFFFFF,0,0xFF0000,0,0xFFFFFF,0,0xFF0000,0,0xFFFFFF,0,0,0,0xFF0000,0,0])
    wait_ms(500)
    continue
  
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
  wait_ms(200)
