//Pin Functions
const uint8_t motorLeftSpeedPin = 6;//pwm
const uint8_t motorLeftForwardPin = A0;
const uint8_t motorLeftBackwardPin = A1;

const uint8_t motorRightSpeedPin = 5 ;//pwm
const uint8_t motorRightForwardPin = A2 ;
const uint8_t motorRightBackwardPin = A3 ;

const uint8_t speakerPin = A5 ;
const uint8_t ledPin = 2 ;

//define comm
const uint8_t STOP = 0x00 ;//0000
const uint8_t  FORWARD_DIRECTION = 0x01; //0001
const uint8_t BACKWARD_DIRECTION = 0x02 ;//0010 
const uint8_t LEFT_DIRECTION = 0x04; //0100
const uint8_t RIGHT_DIRECTION = 0x08; //1000
const uint8_t MOTORLEFT = 0x10 ;//0001 0000
const uint8_t MOTORRIGHT = 0x20 ;//0010 0000
const uint8_t SET_SPEED = 0x40 ;//0100 0000

const uint8_t TURN_SPEED_OFFSET = 20;
const uint8_t MINIMUM_MOTOR_SPEED = 100 ;
const uint8_t MAXIMUM_MOTOR_SPEED = 250 ;

struct Motor
{
  byte mSide;
  byte mSpeed;
}motorLeft, motorRight;

struct Command
{
  byte cmdID;
  byte data1;
  byte data2;
  byte checkSum;
};

enum COMMAND_IDS
{
    INVALID_CMD = 0,
    DRIVE = 10
};

byte currentDirection = 0x00;

void dbg_print(const char * s)
{
//#if DEBUG
    Serial.print(s);
//#endif
}

void processCommand(struct Command &command)
{
   //prcess recieved command
   switch(command.cmdID)
   {
     case DRIVE:
          dbg_print("Drive ...");
          driveCar(command);
          break;
     default:
       //unknown command and do nothing
       dbg_print("Invalid cmd received...");
       break;
     }
}


void driveCar(struct Command &command)
{

 if(command.data1 & STOP){
   stopAllMotors();
   dbg_print("Stop ...");
   return;
 }
 if (!(command.data1 & LEFT_DIRECTION) && !(command.data1 & RIGHT_DIRECTION)){
   //if not turning sync the motor speeds
    setAllMotorsSpeed(command.data2);
 }
 if (command.data1 & FORWARD_DIRECTION){
      goForward();
      dbg_print("Drive Forward ...");   
 }else if (command.data1 & BACKWARD_DIRECTION){
   goBackward();
   dbg_print("Drive Backward ...");
 }
 if (command.data1 & LEFT_DIRECTION){
   turnLeft();
   dbg_print("Turn Left ...");
 }else if (command.data1 & RIGHT_DIRECTION){
   turnRight();
   dbg_print("Turn Right ...");
 }else{
   //reset the direction bits
   currentDirection &= (RIGHT_DIRECTION | LEFT_DIRECTION);
 }
 if (command.data1 & SET_SPEED){
   setAllMotorsSpeed(command.data2);
   dbg_print("Set Speed ...");
 }

}

void turnLeft()
{
    //slow down the left motor to turn right
    if (!(currentDirection & LEFT_DIRECTION)){
      motorLeft.mSpeed-=TURN_SPEED_OFFSET; 
      setMotorSpeed(motorLeft);
      currentDirection |= LEFT_DIRECTION;
    }

}

void turnRight()
{
  //slow down the right motor to turn right
  if (!(currentDirection & RIGHT_DIRECTION)){
    motorRight.mSpeed-=TURN_SPEED_OFFSET; 
    setMotorSpeed(motorRight);
    currentDirection |= RIGHT_DIRECTION;
  }
}

void goForward()
{
  //if going backwards then stop motors and then go forward
  if(!(currentDirection & FORWARD_DIRECTION))
  {
    stopAllMotors();
    digitalWrite(motorLeftForwardPin,1);
    digitalWrite(motorRightForwardPin,1);
    setMotorSpeed(motorLeft);
    setMotorSpeed(motorRight);
    currentDirection |= FORWARD_DIRECTION; // set forward direction bit
    currentDirection &= BACKWARD_DIRECTION; // reset backward direction bit
  }
}

void goBackward()
{
  if(!(currentDirection & BACKWARD_DIRECTION))
  {
      //if not going backwards then stop motors and start going backward
    stopAllMotors();
    digitalWrite(motorLeftBackwardPin,1);
    digitalWrite(motorRightBackwardPin,1);
    setMotorSpeed(motorLeft);
    setMotorSpeed(motorRight);
    currentDirection |= BACKWARD_DIRECTION;  // set backward direction bit
    currentDirection &= FORWARD_DIRECTION; // reset forward direction bit
  }
}
void stopAllMotors()
{
  setAllMotorsSpeed(0);
  digitalWrite(motorRightBackwardPin,0);
  digitalWrite(motorLeftBackwardPin,0);
  digitalWrite(motorRightForwardPin,0);
  digitalWrite(motorLeftForwardPin,0);
  delay(200);
}

void setAllMotorsSpeed(byte speedValue)
{
  if(speedValue < MAXIMUM_MOTOR_SPEED && speedValue > MINIMUM_MOTOR_SPEED){
    motorLeft.mSpeed = speedValue;
    motorRight.mSpeed = speedValue;
    setMotorSpeed(motorLeft);
    setMotorSpeed(motorRight);
  }else{
    dbg_print("Motor speed is two high:");
  }

}

void setMotorSpeed(struct Motor &motor)
{
  if(motor.mSide == MOTORLEFT){
    analogWrite(motorLeftSpeedPin, motor.mSpeed);
  }else if (motor.mSide == MOTORRIGHT){
    analogWrite(motorRightSpeedPin, motor.mSpeed);
  }else{
    dbg_print("Error Setting Motor Speed");
  }
}

void setup()
{
  Serial.begin(9600);
  pinMode(speakerPin, OUTPUT);
  pinMode(ledPin, OUTPUT);
  pinMode(motorLeftSpeedPin, OUTPUT);
  pinMode(motorLeftForwardPin, OUTPUT);
  pinMode(motorLeftBackwardPin, OUTPUT);
  pinMode(motorRightSpeedPin, OUTPUT);
  pinMode(motorRightForwardPin, OUTPUT);
  pinMode(motorRightBackwardPin, OUTPUT); 
  motorLeft.mSpeed = MAXIMUM_MOTOR_SPEED;
  motorRight.mSpeed = MAXIMUM_MOTOR_SPEED;
  motorLeft.mSide = MOTORLEFT;
  motorRight.mSide = MOTORRIGHT;

}


void loop()
{
  Command incomingCmd;

  if(Serial.available() >= sizeof(Command)){
    //read the incoming data
    Command *mem = &incomingCmd;
    unsigned char *p = (unsigned char *)mem;
    for(int i=0;i<sizeof(Command);i++)
    {
      unsigned int data = Serial.read();
      Serial.println(data);
      p[i] = data;
    }

    //verify checksum
     byte received_sum = incomingCmd.cmdID + incomingCmd.data1 + incomingCmd.data2;
     if (incomingCmd.cmdID != INVALID_CMD && received_sum == incomingCmd.checkSum) {
       driveCar(incomingCmd);
       dbg_print("Good Cmd - checksum matched");
     } else {
            //Checksum didn't match, don't process the command
       dbg_print("Bad Cmd - invalid cmd or checksum didn't match");

     }

  }
}
