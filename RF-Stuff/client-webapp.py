import network
import urequests

# Define Wi-Fi credentials
SSID = "PeaceisAwesome"
PASSWORD = "32439344"

# Connect to Wi-Fi
wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(SSID, PASSWORD)

# Wait until the Wi-Fi connection is established
while not wifi.isconnected():
    pass

# Define the endpoint URL and data for the POST request
URL = "https://server-domum.herokuapp.com/"
DATA = {"data": "Fall detected by vibration 1"}

# Send the POST request
response = urequests.post(URL, json=DATA)

# Print the response from the server
print(response.text)

# Disconnect from Wi-Fi
wifi.disconnect()
wifi.active(False)

