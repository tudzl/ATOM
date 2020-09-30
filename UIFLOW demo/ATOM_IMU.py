from m5stack import *
from m5ui import *
from uiflow import *
import i2c_bus
import imu

rgb.set_screen([0,0xffffff,0,0xffffff,0,0xFFFFFF,0,0xee7ce5,0,0xFFFFFF,0,0xee7ce5,0xee7ce5,0xee7ce5,0,0xFFFFFF,0,0xee7ce5,0,0xFFFFFF,0,0xffffff,0,0xffffff,0])



imu0 = imu.IMU()


i2c0 = i2c_bus.easyI2C(i2c_bus.PORTA, 0x5C, freq=400000)
print(i2c0.available())
i2c0 = i2c_bus.easyI2C(i2c_bus.PORTA, 0x68, freq=400000)
print(i2c0.scan())
i2c0 = i2c_bus.easyI2C(i2c_bus.PORTA, 0x75, freq=400000)
while 1:
  print('gyro')
  print(imu0.gyro[0])
  print(imu0.gyro[1])
  print(imu0.gyro[2])
  print('pitch roll')
  print(imu0.ypr[1])
  print(imu0.ypr[2])
  wait_ms(50)