from m5stack import *
from m5ui import *
from uiflow import *
import machine
#V1.3  improve Btn function!
#v1.2 working version!
#V1.1  add number display support!
#version 1.0 created for 5E9363E1 ATOM matrix to be used as Nidec DC brushless Motot controller












#increase or decrease
def buttonA_wasPressed():
  # global params
  global duty_cycle,DIR
  duty_cycle+=1*DIR
  if (duty_cycle>100):
     duty_cycle =100
  elif (duty_cycle<0):
     duty_cycle = 0
  PWM0.duty(duty_cycle)
  print('duty_cycle: '+str(duty_cycle) )
  pass
btnA.wasPressed(buttonA_wasPressed)


#decrease/increase by 20
def buttonA_pressFor():
  # global params
  global duty_cycle,DIR
  duty_cycle -= 1
  duty_cycle += 20*DIR
  if (duty_cycle>100) :
     duty_cycle =100
  elif (duty_cycle<1):
     duty_cycle = 0
  PWM0.duty(duty_cycle)
  print('Btn long pressed for 0.8s!')
  print('duty_cycle: '+str(duty_cycle) )
  pass
btnA.pressFor(0.8, buttonA_pressFor)


#change increase/decrease Dir
def buttonA_wasDoublePress():
  # global params
  global DIR
  DIR = -1*DIR  
  print('Btn long was double pressed')
  print('duty_cycle DIR: '+str(DIR) )
  pass
btnA.wasDoublePress(buttonA_wasDoublePress)




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





rgb.setColorAll(0xff0000)
wait_ms(250)
rgb.set_screen([0,0,0xf67d2c,0xf91010,0xf67d2c,0,0,0xf67d2c,0xf91010,0xf3f62c,0xf91010,0xf91010,0xf91010,0xf91010,0xf67d2c,0,0,0xf67d2c,0xf91010,0xf3f62c,0,0,0xf67d2c,0xf91010,0xf67d2c])
wait_ms(250)

print('Atom Matrix PWM G26(GROVE_pin3) demo v1.3B')

duty_cycle = 40
DIR = 1;
print('Default duty_cycle: '+str(duty_cycle) )


#min 0%



rgb.setBrightness(10)
PWM0 = machine.PWM(26, freq=1000, duty=50, timer=0)
while True:
  duty_cycle_MSB = int (duty_cycle/10)
  show_num_single(duty_cycle_MSB)
  if(duty_cycle==0):
    rgb.set_screen([0xf3f62c,0xf3f62c,0xf3f62c,0xf3f62c,0xf3f62c,0xf3f62c,0,0,0,0xf3f62c,0xf3f62c,0,0,0,0xf3f62c,0xf3f62c,0,0,0,0xf3f62c,0xf3f62c,0xf3f62c,0xf3f62c,0xf3f62c,0xf3f62c])
  #rgb.set_screen([0,0xFFFFEE,0xFFFFEE,0xFFFFEE,0,0,0xFFFFEE,0,0,0,0,0xFFFFEE,0xFFFFEE,0xFFFFEE,0,0,0,0,0,0xFFFFEE,0,0xFFFFEE,0xFFFFEE,0xFFFFEE,0])
  wait_ms(440)
  duty_cycle_LSB = duty_cycle - duty_cycle_MSB*10
  show_num_single(duty_cycle_LSB)
  if(duty_cycle==0):
    rgb.set_screen([0xf3f62c,0xf3f62c,0xf3f62c,0xf3f62c,0xf3f62c,0xf3f62c,0,0,0,0xf3f62c,0xf3f62c,0,0,0,0xf3f62c,0xf3f62c,0,0,0,0xf3f62c,0xf3f62c,0xf3f62c,0xf3f62c,0xf3f62c,0xf3f62c])

  #rgb.set_screen([0,0,0xFFFFEE,0,0,0,0xFFFFEE,0,0xFFFFEE,0,0,0xFFFFEE,0,0xFFFFEE,0,0,0xFFFFEE,0,0xFFFFEE,0,0,0,0xFFFFEE,0,0])
  wait_ms(440)
  rgb.setBrightness(5)
  if(DIR>0):
    rgb.setColorAll(0x00ee00)
  else:
    rgb.setColorAll(0xbb1100)
  wait_ms(40)
  rgb.setBrightness(10)