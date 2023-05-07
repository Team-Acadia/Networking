#include <falldetectionradar.h>
FallDetectionRadar radar;
void setup() {
 pinMode(22, OUTPUT);
 pinMode(25, OUTPUT); 
 radar.SerialInit();
 Serial.begin(9600);
 delay(1500);
 Serial.println("Ready");
}
void blinkLED();
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
      blinkLED();
      Serial.println("test");
  }
}
}

void blinkLED(){
  digitalWrite(22, HIGH);
  delay(100);
  digitalWrite(22, LOW);
  delay(100);
  digitalWrite(22, HIGH);
  delay(100);
  digitalWrite(22, LOW);
  delay(100);
    digitalWrite(22, HIGH);
  delay(100);
  digitalWrite(22, LOW);
  delay(100);
 }
