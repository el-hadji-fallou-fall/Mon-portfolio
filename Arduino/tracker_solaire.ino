
#include <Servo.h>

Servo servoX;  // Contrôle de l'axe horizontal
Servo servoY;  // Contrôle de l'axe vertical

int ldrTopLeft = A0;
int ldrTopRight = A1;
int ldrBottomLeft = A2;
int ldrBottomRight = A3;

int posX = 90;  // Position initiale du servo horizontal
int posY = 90;  // Position initiale du servo vertical

void setup() {
  servoX.attach(9);   // Broche pour le servo horizontal
  servoY.attach(10);  // Broche pour le servo vertical
  servoX.write(posX);
  servoY.write(posY);
  delay(500);
}

void loop() {
  int tl = analogRead(ldrTopLeft);
  int tr = analogRead(ldrTopRight);
  int bl = analogRead(ldrBottomLeft);
  int br = analogRead(ldrBottomRight);

  int avgTop = (tl + tr) / 2;
  int avgBottom = (bl + br) / 2;
  int avgLeft = (tl + bl) / 2;
  int avgRight = (tr + br) / 2;

  int tolerance = 50;

  if (abs(avgTop - avgBottom) > tolerance) {
    if (avgTop > avgBottom && posY < 180) {
      posY++;
    } else if (avgBottom > avgTop && posY > 0) {
      posY--;
    }
    servoY.write(posY);
  }

  if (abs(avgLeft - avgRight) > tolerance) {
    if (avgLeft > avgRight && posX < 180) {
      posX++;
    } else if (avgRight > avgLeft && posX > 0) {
      posX--;
    }
    servoX.write(posX);
  }

  delay(100);
}
