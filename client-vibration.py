import machine
from machine import Pin, ADC 
import utime 
import network
import socket

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect('Bill Wi the science Fi', 'BillBillBill')
while not wlan.isconnected() and wlan.status() >= 0:
    print("Waiting to connect:")
    utime.sleep(1)
 
# Should be connected and have an IP address
wlan.status() # 3 == success
wlan.ifconfig()
print(wlan.ifconfig())

a = Pin("LED",Pin.OUT)

#Initialize Prepherials
POT_Value = ADC(28) 
conversion_factor = 3.3/(65536)

#initialize last 1/10th of a second val
count = 0
#Last 20 is for the runnning avg and so we can plot before and after spike 
last20 = []
for i in range(20):
        last20.append(POT_Value.read_u16() * conversion_factor)
        utime.sleep(0.01)

#Main Application loop
while True:
    a.value(1)
    curr = POT_Value.read_u16() * conversion_factor
    avg = sum(last20)/20
    last20.pop()
    last20.append(POT_Value.read_u16() * conversion_factor)
    #detect spike
    if curr > avg +.01:
        print(curr)
        count = count + 1
        print("Number:",  count, "VOLTAGE SPIKE.  AVG:", avg, "CURR", curr, "difference:", curr-avg, "Percent Diff:", (curr-avg)/avg*100)
        next20 = []
        #get next 20 voltages so we can plot after spike
        for i in range(20):
            next20.append(POT_Value.read_u16() * conversion_factor)
            utime.sleep(0.01)
        print(last20[-5:], next20[0:5])
        ai = socket.getaddrinfo("192.168.68.128", 80) # Address of Web Server
        addr = ai[0][-1]

        # Create a socket and make a HTTP request
        s = socket.socket() # Open socket
        s.connect(addr)
        s.send(str(avg)) # Send request
        ss=str(s.recv(512)) # Store reply
        # Print what we received
        print(ss)
        # Set RGB LED here
        s.close()          # Close socket
        #Allow time for voltage spike to dissapate
        for i in range(40):
            last20.pop()
            last20.append(POT_Value.read_u16() * conversion_factor)
            utime.sleep(0.01)
