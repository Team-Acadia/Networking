import machine
from machine import Pin, ADC 
import utime 
 
#Initialize Prepherials
rf = Pin(1,Pin.OUT)

POT_Value = ADC(26) 
conversion_factor = 3.3/(65536)

#initialize last 1/10th of a second val

last20 = []
for i in range(20):
        last20.append(POT_Value.read_u16() * conversion_factor)
        utime.sleep(0.01)

#Main Application loop 
while True:
    curr = POT_Value.read_u16() * conversion_factor
    #print(curr)
    avg = sum(last20)/20
    if curr - .01 > avg:
        ##rf.value(1)
        print("VOLTAGE SPIKE.  AVG:", avg, "CURR", curr)
    #else:
        #print(avg, curr)
    last20.pop(0)
    last20.append(curr)
    utime.sleep(0.01)
