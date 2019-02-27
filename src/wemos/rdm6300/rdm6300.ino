
// from  http://qqtrading.com.my/uart-rfid-reader-module-125khz-rdm6300-w-anthenna

#include <HardwareSerial.h>

HardwareSerial RFID(1);

int i;

void setup()
{
  // use TX=GPIO1 and RX=GPIO3 for
  // baud speed, UART mode, RX pin, TX pin
  RFID.begin(9600, SERIAL_8N1, 3, 1);
  Serial.begin(115200);  // start serial to PC 
  Serial.print("Starting\n");
}

void loop()
{
  if (RFID.available() > 0) 
  {
     i = RFID.read();
     Serial.print(i, DEC);
     Serial.print(" - ");
  } else {
    //Serial.print(".\n");
  }
}
