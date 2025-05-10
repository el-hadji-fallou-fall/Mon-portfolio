#include <AFMotor.h>
#include <Servo.h>
#include <NewPing.h>

// Moteurs
AF_DCMotor leftMotor(1, MOTOR12_64KHZ);  
AF_DCMotor rightMotor(2, MOTOR12_64KHZ);

// Capteur à ultrasons
#define trig_pin A0
#define echo_pin A1
#define maximum_distance 200

NewPing sonar(trig_pin, echo_pin, maximum_distance);

// Servo
Servo servo_motor;

boolean goesForward = false;
int distance = 100;
int obstacleCounter = 0;  // Compteur de détections d'obstacles

void setup(){
  servo_motor.attach(10);
  servo_motor.write(90);
  delay(2000);

  distance = readPing();
  delay(100);
  distance = readPing();
  delay(100);
  distance = readPing();
  delay(100);
}

void loop(){
  int distanceRight = 0;
  int distanceLeft = 0;
  delay(50);

  if (distance <= 30){
    obstacleCounter++;  // Incrémenter si obstacle détecté
    moveStop();
    delay(300);
    moveBackward();
    delay(400);
    moveStop();
    delay(300);
    
    // Si 2 obstacles détectés successivement → demi-tour
    if (obstacleCounter >= 2) {
      turnAround();
      obstacleCounter = 0;
    } else {
      distanceRight = lookRight();
      delay(300);
      distanceLeft = lookLeft();
      delay(300);

      if (distanceRight >= distanceLeft){
        turnRight();
      } else {
        turnLeft();
      }
    }
  } else {
    moveForward(); 
    obstacleCounter = 0;  // Réinitialiser si plus d'obstacle
  }

  distance = readPing();
}

// Lecture sonar
int readPing(){
  delay(70);
  int cm = sonar.ping_cm();
  if (cm == 0) cm = 250;
  return cm;
}

// Servo vers la droite
int lookRight(){  
  servo_motor.write(10);
  delay(500);
  int dist = readPing();
  delay(100);
  servo_motor.write(90);
  return dist;
}

// Servo vers la gauche
int lookLeft(){
  servo_motor.write(170);
  delay(500);
  int dist = readPing();
  delay(100);
  servo_motor.write(90);
  return dist;
}

// Mouvement
void moveStop(){
  leftMotor.run(RELEASE);
  rightMotor.run(RELEASE);
}

void moveForward(){
  if (!goesForward) {
    goesForward = true;
    leftMotor.setSpeed(200);
    rightMotor.setSpeed(150);
    leftMotor.run(FORWARD);
    rightMotor.run(FORWARD);
  }
}

void moveBackward(){
  goesForward = false;
  leftMotor.setSpeed(150);
  rightMotor.setSpeed(150);
  leftMotor.run(BACKWARD);
  rightMotor.run(BACKWARD);
}

void turnRight(){
  leftMotor.setSpeed(150);
  rightMotor.setSpeed(150);
  leftMotor.run(FORWARD);
  rightMotor.run(BACKWARD);
  delay(500);
  moveStop();
}

void turnLeft(){
  leftMotor.setSpeed(150);
  rightMotor.setSpeed(150);
  leftMotor.run(BACKWARD);
  rightMotor.run(FORWARD);
  delay(500);
  moveStop();
}

void turnAround(){
  int rightDist = lookRight();
  delay(200);
  int leftDist = lookLeft();
  delay(200);

  leftMotor.setSpeed(150);
  rightMotor.setSpeed(150);

  if (rightDist >= leftDist) {
    // Tourne à droite (sens horaire)
    leftMotor.run(FORWARD);
    rightMotor.run(BACKWARD);
    delay(1000); // durée du demi-tour
  } else {
    // Tourne à gauche (sens anti-horaire)
    leftMotor.run(BACKWARD);
    rightMotor.run(FORWARD);
    delay(1000);
  }

  moveStop();
  delay(200);
}
