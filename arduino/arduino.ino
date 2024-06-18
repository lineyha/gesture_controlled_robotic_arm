#include <Servo.h>

Servo servo[4];

int x;
int y;
int z;
int claw;

void setup()
{
    Serial.begin(9600);
    servo[0].write(93);
    servo[1].write(80);
    servo[2].write(115);
    servo[3].write(150);
    servo[0].attach(5); // x
    servo[1].attach(6); // y
    servo[2].attach(7); // z
    servo[3].attach(8); // claw
    setDefault();
}

byte angle[4];
byte pre_angle[4];
long t = millis();

bool open = true;

void loop()
{
    if (Serial.available())
    {
        Serial.readBytes(angle, 4);
        servo[0].write(angle[0]);
        servo[1].write(angle[1]);
        servo[2].write(angle[2]);
        servo[3].write(angle[3]);
            
        t = millis();
    }

    if (millis() - t > 6000)
    {
      setDefault();
    }

}

void setDefault(){
  x = servo[0].read();
  y = servo[1].read();
  z = servo[2].read();
  claw = servo[3].read();
  if(x>93){
    for(;x>93; x--){
      servo[0].write(x);
      delay(30);
    }
  }
  else{
    for(;x<93; x++){
    servo[0].write(x);
    delay(30);
    }
  }
  if(y>80){
    for(;y>80; y--){
      servo[1].write(y);
      delay(30);
    }
  }
  else{
    for(;y<80; y++){
      servo[1].write(y);
      delay(30);
      }
  }

  if(z>115){
    for(;z>115 ; z--){
      servo[2].write(z);
      delay(30);
      }
    }
  else{
    for(;z<115 ; z++){
      servo[2].write(z);
      delay(30);
      }
    }

  if(claw>150){
    for(;claw>150; claw--){
      servo[3].write(claw);
      delay(30);
      }
    }
  else{
    for(;claw < 150 ; claw++){
    servo[3].write(claw);
    delay(30);
    }
  }

}
