#include <AFMotor.h>
#include <SoftwareSerial.h>

// Création d'une liaison série sur les pins 2 (RX) et 3 (TX)
SoftwareSerial BT(2, 3); // RX, TX

AF_DCMotor motorGauche(1);
AF_DCMotor motorDroite(2);

String commande = "";

void setup() {
  BT.begin(9600);     // Démarre la communication Bluetooth
  Serial.begin(9600); // Pour déboguer via moniteur série
}

void loop() {
  while (BT.available()) {
    char c = BT.read();
    commande += c;
    delay(2); // Petit délai pour s'assurer de recevoir tout le mot
  }

  if (commande.length() > 0) {
    Serial.println("Commande reçue: " + commande); // Pour debug

    if (commande == "avant") {
      motorGauche.setSpeed(200);
      motorDroite.setSpeed(200);
      motorGauche.run(FORWARD);
      motorDroite.run(FORWARD);
    } 
    else if (commande == "arriere") {
      motorGauche.run(BACKWARD);
      motorDroite.run(BACKWARD);
    } 
    else if (commande == "gauche") {
      motorGauche.run(BACKWARD);
      motorDroite.run(FORWARD);
    } 
    else if (commande == "droite") {
      motorGauche.run(FORWARD);
      motorDroite.run(BACKWARD);
    } 
    else if (commande == "stop") {
      motorGauche.run(RELEASE);
      motorDroite.run(RELEASE);
    }

    commande = ""; // Réinitialise la commande après exécution
  }
}
