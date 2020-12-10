from m5stack import *
from m5ui import *
from uiflow import *
import machine
#V1.1  add number display support!
#version 1.0
rgb.setColorAll(0xff0000)

print('Atom Matrix PWM G26 demo v1.0')

duty_cycle = 50

#increase
def buttonA_wasPressed():
  # global params
  global duty_cycle
  duty_cycle+=1
  if (duty_cycle>100):
     duty_cycle =100
  elif (duty_cycle<1):
     duty_cycle = 1
  PWM0.duty(duty_cycle)
  print('duty_cycle: '+str(duty_cycle) )
  pass
btnA.wasPressed(buttonA_wasPressed)

#decrease
def buttonA_pressFor():
  # global params
  global duty_cycle
  duty_cycle -= 10
  if (duty_cycle>100) :
     duty_cycle =100
  elif (duty_cycle<1):
     duty_cycle = 1
  PWM0.duty(duty_cycle)
  print('duty_cycle: '+str(duty_cycle) )
  pass
btnA.pressFor(0.6, buttonA_pressFor)

#display single digit number
def show_num_single(num):
    if (num == 0):
      rgb.set_screen([0,0,0xFFFFFF,0,0,0,0xFFFFFF,0,0xFFFFFF,0,0,0xFFFFFF,0,0xFFFFFF,0,0,0xFFFFFF,0,0xFFFFFF,0,0,0,0xFFFFFF,0,0])
    elif (num == 1):
      rgb.set_screen([0,0,0xFFFFFF,0,0,0,0xFFFFFF,0xFFFFFF,0,0,0,0,0xFFFFFF,0,0,0,0,0xFFFFFF,0,0,0,0,0xFFFFFF,0,0])
    elif (num == 2):
      rgb.set_screen([0,0xFFFFFF,0xFFFFFF,0,0,0xFFFFFF,0,0,0xFFFFFF,0,0,0,0xFFFFFF,0xFFFFFF,0,0,0xFFFFFF,0,0,0,0xFFFFFF,0xFFFFFF,0xFFFFFF,0xFFFFFF,0])
    elif (num == 3):
      rgb.set_screen([0,0xFFFFFF,0xFFFFFF,0,0,0xFFFFFF,0,0,0xFFFFFF,0,0,0,0xFFFFFF,0xFFFFFF,0,0,0xFFFFFF,0,0,0,0xFFFFFF,0xFFFFFF,0xFFFFFF,0xFFFFFF,0])
    elif (num == 4):
      rgb.set_screen([0,0xFFFFFF,0xFFFFFF,0,0,0xFFFFFF,0,0,0xFFFFFF,0,0,0,0xFFFFFF,0xFFFFFF,0,0,0xFFFFFF,0,0,0,0xFFFFFF,0xFFFFFF,0xFFFFFF,0xFFFFFF,0])
    elif (num == 5):
      rgb.set_screen([0,0xFFFFFF,0xFFFFFF,0,0,0xFFFFFF,0,0,0xFFFFFF,0,0,0,0xFFFFFF,0xFFFFFF,0,0,0xFFFFFF,0,0,0,0xFFFFFF,0xFFFFFF,0xFFFFFF,0xFFFFFF,0])
    elif (num == 6):
      rgb.set_screen([0,0xFFFFFF,0xFFFFFF,0,0,0xFFFFFF,0,0,0xFFFFFF,0,0,0,0xFFFFFF,0xFFFFFF,0,0,0xFFFFFF,0,0,0,0xFFFFFF,0xFFFFFF,0xFFFFFF,0xFFFFFF,0])
    elif (num == 7):
      rgb.set_screen([0,0xFFFFFF,0xFFFFFF,0,0,0xFFFFFF,0,0,0xFFFFFF,0,0,0,0xFFFFFF,0xFFFFFF,0,0,0xFFFFFF,0,0,0,0xFFFFFF,0xFFFFFF,0xFFFFFF,0xFFFFFF,0])
    elif (num == 8):
      rgb.set_screen([0,0xFFFFFF,0xFFFFFF,0,0,0xFFFFFF,0,0,0xFFFFFF,0,0,0,0xFFFFFF,0xFFFFFF,0,0,0xFFFFFF,0,0,0,0xFFFFFF,0xFFFFFF,0xFFFFFF,0xFFFFFF,0])
    elif (num == 9):
      rgb.set_screen([0,0xFFFFFF,0xFFFFFF,0,0,0xFFFFFF,0,0,0xFFFFFF,0,0,0,0xFFFFFF,0xFFFFFF,0,0,0xFFFFFF,0,0,0,0xFFFFFF,0xFFFFFF,0xFFFFFF,0xFFFFFF,0])
    
    pass


rgb.setBrightness(10)
PWM0 = machine.PWM(26, freq=1000, duty=50, timer=0)
while True:
  duty_cycle_MSB = int (duty_cycle/10)
  show_num_single(duty_cycle_MSB)
  #rgb.set_screen([0,0xFFFFFF,0xFFFFFF,0xFFFFFF,0,0,0xFFFFFF,0,0,0,0,0xFFFFFF,0xFFFFFF,0xFFFFFF,0,0,0,0,0,0xFFFFFF,0,0xFFFFFF,0xFFFFFF,0xFFFFFF,0])
  wait_ms(240)
  duty_cycle_LSB = duty_cycle - duty_cycle_MSB*10
  show_num_single(duty_cycle_LSB)
  #rgb.set_screen([0,0,0xFFFFFF,0,0,0,0xFFFFFF,0,0xFFFFFF,0,0,0xFFFFFF,0,0xFFFFFF,0,0,0xFFFFFF,0,0xFFFFFF,0,0,0,0xFFFFFF,0,0])
  wait_ms(240)
  rgb.setColorAll(0x00ee00)
  wait_ms(20)
  
  