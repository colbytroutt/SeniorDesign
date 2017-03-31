/* -----------------------------------------------------------------------------
 * Example .ino file for arduino, compiled with CmdMessenger.h and
 * CmdMessenger.cpp in the sketch directory. 
 *----------------------------------------------------------------------------*/

#include <Servo.h>
#include <Math.h>
#include "CmdMessenger.h"

#define SERVO_ONE 3
#define SERVO_TWO 9
#define TRIGGER_ONE 4
#define TRIGGER_TWO 8
#define FLY_ONE 2
#define FLY_TWO 7

/* Define available CmdMessenger commands */
enum {
    aim,
    start,
    fire,
    error,
    halt,
};

Servo yawServo;
Servo pitchServo;
int currentYaw = 90;
int currentPitch = 20;

const int BAUD_RATE = 9600;
CmdMessenger messenger = CmdMessenger(Serial,',',';','/');

void onStart(void) {
    digitalWrite(FLY_ONE, HIGH);
    digitalWrite(FLY_TWO, HIGH);
}

void onHalt(void) {
    digitalWrite(FLY_ONE, LOW);
    digitalWrite(FLY_TWO, LOW);
}

/* Create callback functions to deal with incoming messages */
void onAim(void){

    int yaw = messenger.readBinArg<int>();
    int pitch = messenger.readBinArg<int>();

    int absoluteYaw = currentYaw+yaw;
    int absolutePitch = currentPitch+pitch;
    
    if(absoluteYaw > 180) {
      absoluteYaw = 180;
    } else if(absoluteYaw < 0) {
      absoluteYaw = 0;
    }

    if(absolutePitch > 40) {
      absolutePitch = 40;
    } else if(absolutePitch < 0) {
      absolutePitch = 0;
    }
    
    yawServo.write(absoluteYaw);
    pitchServo.write(absolutePitch);

    currentYaw = absoluteYaw;
    currentPitch = absolutePitch;
}

void onFire(void) {
    digitalWrite(TRIGGER_ONE, HIGH);
    digitalWrite(TRIGGER_TWO, HIGH);
    delay(1000);
    digitalWrite(TRIGGER_ONE, LOW);
    digitalWrite(TRIGGER_TWO, LOW);
}

/* callback */
void on_unknown_command(void){
    messenger.sendCmd(error,"Command without callback.");
}

/* Attach callbacks for CmdMessenger commands */
void attach_callbacks(void) { 
    messenger.attach(aim, onAim);
    messenger.attach(fire, onFire);
    messenger.attach(on_unknown_command);
    messenger.attach(halt, onHalt);
    messenger.attach(start, onStart);
}

void setup() {
    Serial.begin(BAUD_RATE);
    attach_callbacks();
    yawServo.attach(SERVO_ONE);
    yawServo.write(currentYaw);
    pitchServo.attach(SERVO_TWO);
    pitchServo.write(currentPitch);
    pinMode(FLY_ONE, OUTPUT);
    pinMode(FLY_TWO, OUTPUT);
    pinMode(TRIGGER_ONE, OUTPUT);
    pinMode(TRIGGER_TWO, OUTPUT);
}

void loop() {
    messenger.feedinSerialData();
}

