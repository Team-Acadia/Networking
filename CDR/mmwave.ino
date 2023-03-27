#include <falldetectionradar.h>
#include <WiFi.h>

const char* ssid = "PeaceisAwesome";
const char* password = "32439344";
const char* server_address = "192.168.137.79";
int server_port = 80;
FallDetectionRadar radar;

void setup()
{
  radar.SerialInit();
  Serial.begin(9600);
  delay(1500);
  Serial.println("Readly");
  WiFi.begin(ssid, password);

  while(WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to Wifi...");
  }

  Serial.println("Connected to WiFi!");
}

void loop()
{
  WiFiClient client;

 //Serial.println("Connected to server");
 radar.recvRadarBytes();                       //Receive radar data and start processing
 if (radar.newData == true) {                  //The data is received and transferred to the new list dataMsg[]
    byte dataMsg[radar.dataLen+1] = {0x00};
    dataMsg[0] = 0x55;                         //Add the header frame as the first element of the array
    for (byte n = 0; n < radar.dataLen; n++)dataMsg[n+1] = radar.Msg[n];  //Frame-by-frame transfer
    radar.newData = false;                     //A complete set of data frames is saved
    
    radar.ShowData(dataMsg);                 //Serial port prints a set of received data frames
    if (Serial.available()){
      String message = Serial.readStringUntil("\n");
      if (message.indexOf("CE")==-1){
          if (!client.connect(server_address, server_port)){
              Serial.println("Failed to connect to server");
              delay(250);
              return;
              }
              Serial.println("Connected to server");
        }
      }
    radar.Fall_inf(dataMsg);                  //Sleep information output
  }
  client.stop();
}
