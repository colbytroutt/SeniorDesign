/* -----------------------------------------------------------------------------
 * Example .ino file for arduino, compiled with CmdMessenger.h and
 * CmdMessenger.cpp in the sketch directory. 
 *----------------------------------------------------------------------------*/

#include <Servo.h>
#include <Math.h>
#include "CmdMessenger.h"

/* Define available CmdMessenger commands */
enum {
    aim,
    t,
    error,
};

Servo yawServo;
Servo pitchServo;
int currentYaw = 90;
int currentPitch = 20;

const int BAUD_RATE = 9600;
CmdMessenger messenger = CmdMessenger(Serial,',',';','/');

/* Create callback functions to deal with incoming messages */

/* callback */
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

/* callback */
void on_unknown_command(void){
    messenger.sendCmd(error,"Command without callback.");
}

/* Attach callbacks for CmdMessenger commands */
void attach_callbacks(void) { 
    messenger.attach(aim, onAim);
    messenger.attach(on_unknown_command);
}

void setup() {
    Serial.begin(BAUD_RATE);
    attach_callbacks();
    yawServo.attach(9);
    yawServo.write(currentYaw);
    pitchServo.attach(10);
    pitchServo.write(currentPitch);
}

void loop() {
    messenger.feedinSerialData();
}

