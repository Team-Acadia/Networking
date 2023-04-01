#include <falldetectionradar.h>
#include <WiFi.h>

const char* ssid = "PeaceisAwesome";
const char* password = "32439344";
const char* server_address = "192.168.137.76";
int server_port = 80;
FallDetectionRadar radar;
WiFiClient client;
void setup() {
  radar.SerialInit();
  Serial.begin(9600);
  delay(1500);
  Serial.println("Ready");

  bool wifiConnected = false;

  while (!wifiConnected) {
    WiFi.begin(ssid, password);

    Serial.println("Connecting to WiFi...");
    for (int i = 0; i < 10 && WiFi.status() != WL_CONNECTED; i++) {
      delay(1000);
      Serial.print(".");
    }
    Serial.println();

    if (WiFi.status() == WL_CONNECTED) {
      Serial.println("Connected to WiFi!");
      wifiConnected = true;
    }
    else {
      Serial.println("Failed to connect to WiFi. Retrying in 10 seconds...");
      delay(10000);
    }
  }
}

void loop() {
  radar.recvRadarBytes(); //Receive radar data and start processing
  if (radar.newData == true) { //The data is received and transferred to the new list dataMsg[]
    byte dataMsg[radar.dataLen + 1] = { 0x00 };
    dataMsg[0] = 0x55; //Add the header frame as the first element of the array
    for (byte n = 0; n < radar.dataLen; n++)
      dataMsg[n + 1] = radar.Msg[n]; //Frame-by-frame transfer
    radar.newData = false; //A complete set of data frames is saved

    radar.ShowData(dataMsg); //Serial port prints a set of received data frames
    int returned = radar.Fall_inf(dataMsg); //Sleep information output
    if (returned == 1){
       while (!client.connected()){
          Serial.println("Connecting to server");
          client.connect(server_address, server_port);
          delay(1000); // Wait 1 second before trying again
       }
       Serial.println("Connected to server");
      }
  }
}
