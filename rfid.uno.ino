#include <SPI.h>
#include <MFRC522.h>
#define SDAPIN 10
#define RESETPIN 8

byte FoundTag;
byte ReadTag;
byte TagData[MAX_LEN];
byte TagSerialNumber[5];
MFRC522 nfc(SDAPIN,RESETPIN);

void setup() {
  SPI.begin();
  Serial.begin(115200);
  nfc.begin();
  byte version = nfc.getFirmwareVersion();
  if(!version) {
    Serial.print("Didn't find RC522 board.");
  }
  else {
    Serial.println("OK");
  }
} 

void loop() {
  delay(450);
  FoundTag = nfc.requestTag(MF1_REQIDL, TagData);  
  if (FoundTag == MI_OK){
    char dataString[10];
    ReadTag = nfc.antiCollision(TagData);
    memcpy(TagSerialNumber, TagData, 5);
    sprintf(dataString,"%02X%02X%02X%02X%02X",TagSerialNumber[0],TagSerialNumber[1],TagSerialNumber[2],TagSerialNumber[3],TagSerialNumber[4]);
    Serial.println(dataString); 
  }
}
