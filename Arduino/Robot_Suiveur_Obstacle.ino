#include <AFMotor.h>
#include <NewPing.h>

// === MOTEURS ===
AF_DCMotor leftMotor(1, MOTOR12_1KHZ);
AF_DCMotor rightMotor(2, MOTOR12_1KHZ);

// === CAPTEURS IR ===
#define leftSensor A3
#define rightSensor A4
#define THRESHOLD 500  // Ajuster selon la surface

// === CAPTEUR ULTRASON ===
#define trigPin A0
#define echoPin A1
#define MAX_DISTANCE 200
NewPing sonar(trigPin, echoPin, MAX_DISTANCE);

// === CONFIG ===
bool avoiding = false;

void setup() {
  Serial.begin(9600);
  leftMotor.setSpeed(180);
  rightMotor.setSpeed(180);

  pinMode(leftSensor, INPUT);
  pinMode(rightSensor, INPUT);
}

void loop() {
  int distance = sonar.ping_cm();

  if (distance > 0 && distance <= 10) {
    avoidObstacle();
  } else {
    followLine();
  }

  delay(30);
}

// === FONCTION DE SUIVI DE LIGNE NOIRE ===
void followLine() {
  int leftValue = analogRead(leftSensor);
  int rightValue = analogRead(rightSensor);

  Serial.print("G: ");
  Serial.print(leftValue);
  Serial.print(" | D: ");
  Serial.println(rightValue);

  if (leftValue < THRESHOLD && rightValue < THRESHOLD) {
    // Ligne centrée
    leftMotor.run(FORWARD);
    rightMotor.run(FORWARD);
  } else if (leftValue < THRESHOLD && rightValue >= THRESHOLD) {
    // Tourner à gauche
    leftMotor.run(FORWARD);
    rightMotor.run(BACKWARD);
  } else if (leftValue >= THRESHOLD && rightValue < THRESHOLD) {
    // Tourner à droite
    leftMotor.run(BACKWARD);
    rightMotor.run(FORWARD);
  } else {
    // Ligne perdue
    leftMotor.run(RELEASE);
    rightMotor.run(RELEASE);
  }
}

// === ÉVITEMENT SIMPLE D’OBSTACLE ===
void avoidObstacle() {
  // Stop
  leftMotor.run(RELEASE);
  rightMotor.run(RELEASE);
  delay(200);

  // Recule un peu
  leftMotor.run(BACKWARD);
  rightMotor.run(BACKWARD);
  delay(400);

  // Tourne à gauche pour contourner
  leftMotor.run(BACKWARD);
  rightMotor.run(FORWARD);
  delay(500);

  // Avance un peu avant de reprendre le suivi
  leftMotor.run(FORWARD);
  rightMotor.run(FORWARD);
  delay(600);

  // Stop avant de reprendre la ligne
  leftMotor.run(RELEASE);
  rightMotor.run(RELEASE);
  delay(200);
}
