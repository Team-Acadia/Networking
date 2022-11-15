#include <SoftwareSerial.h>
const byte rxPin = 2; 
const byte txPin = 3; 

SoftwareSerial ESP8266 (rxPin, txPin);

void setup() 
{
  Serial.begin(9600);
  ESP8266.begin(9600);  
  delay(1000);         
}

void loop() 
{
  delay(1000);
  Serial.println("Sending an AT command...");
  ESP8266.print("AT/r/n");
  delay(30);
  while (ESP8266.available())
  {
     Serial.println("...");
     String inData = ESP8266.readStringUntil('\n');
     Serial.println("Got response from ESP8266: " + inData);
  }  
}