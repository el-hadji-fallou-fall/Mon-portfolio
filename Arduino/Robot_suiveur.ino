#include <AFMotor.h>

// Capteurs IR
#define leftSensor A3
#define rightSensor A4

// Seuillage à ajuster selon ton capteur et la lumière ambiante
#define THRESHOLD 500

// Seulement 2 moteurs utilisés
AF_DCMotor leftMotor(1, MOTOR12_1KHZ);  // Moteur gauche
AF_DCMotor rightMotor(2, MOTOR12_1KHZ); // Moteur droit

void setup() {
  Serial.begin(9600);

  // Vitesse initiale des moteurs
  leftMotor.setSpeed(180);
  rightMotor.setSpeed(180);

  pinMode(leftSensor, INPUT);
  pinMode(rightSensor, INPUT);
}

void loop() {
  int leftValue = analogRead(leftSensor);
  int rightValue = analogRead(rightSensor);

  Serial.print("Gauche: ");
  Serial.print(leftValue);
  Serial.print(" | Droite: ");
  Serial.println(rightValue);

  // Ligne noire détectée par les deux capteurs → avancer
  if (leftValue < THRESHOLD && rightValue < THRESHOLD) {
    leftMotor.run(FORWARD);
    rightMotor.run(FORWARD);
  }
  // Ligne à gauche → tourner à gauche
  else if (leftValue < THRESHOLD && rightValue >= THRESHOLD) {
    leftMotor.run(FORWARD);
    rightMotor.run(BACKWARD);
  }
  // Ligne à droite → tourner à droite
  else if (leftValue >= THRESHOLD && rightValue < THRESHOLD) {
    leftMotor.run(BACKWARD);
    rightMotor.run(FORWARD);
  }
  // Ligne perdue → arrêter
  else {
    leftMotor.run(RELEASE);
    rightMotor.run(RELEASE);
  }

  delay(50);
}
