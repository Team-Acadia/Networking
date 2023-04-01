import network
import socket
import time

# Connect to Wi-Fi
ssid = "PeaceisAwesome"
password = "32439344"
station = network.WLAN(network.STA_IF)
station.active(True)
station.connect(ssid, password)
while not station.isconnected():
    pass
print("Wi-Fi connected:", station.ifconfig())

# Create a socket and listen for incoming connections
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('0.0.0.0', 8080))
s.listen(1)

# Wait for a client to connect and print its IP address
print("Waiting for a client to connect...")
client_sock, client_addr = s.accept()
print("Client connected from", client_addr)

# Send a message to the client and close the connection
client_sock.send("Hello, client!".encode())
client_sock.close()
s.close()

