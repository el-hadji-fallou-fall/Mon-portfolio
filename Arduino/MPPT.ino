//----------------------------------------------------------------------------------------------------
// Chargeur Solaire intelligent MPPT 
//  Auteur : El Hadji Fallou Fall
// 

////  Cahier des charges :  //////////////////////////////////////////////////////////////////////////
                                                                                                    //
//    1.Puissance du panneau solaire = 20W                                                          //
                                                                                                    //
//    2.Tension nominale de la batterie = 12V (type plomb-acide)                                   //

//    3.Courant maximum = 5A                                                                        //

//    4.Courant de charge maximum =10A                                                              //

//    5.Tension d'entrée = Panneau solaire avec tension en circuit ouvert de 17 à 25V               //

/////////////////////////////////////////////////////////////////////////////////////////////////////

#include "TimerOne.h"               // Bibliothèque pour le timer hardware
#include <LiquidCrystal_I2C.h>      // Bibliothèque pour l'écran LCD I2C
#include <Wire.h>                   // Bibliothèque pour la communication I2C

//--------------------------------------------------------------------------------------------------
 
//////// Connexions des broches Arduino ////////////////////////////////////////////////////////////

// A0 - Diviseur de tension (panneau solaire)
// A1 - Sortie du capteur ACS 712 
// A2 - Diviseur de tension (batterie)
// A4 - SDA du LCD
// A5 - SCL du LCD
// D2 - Tx de l'ESP8266
// D3 - Rx de l'ESP8266 via le diviseur de tension
// D5 - Bouton de contrôle du rétroéclairage LCD
// D6 - Contrôle de la charge 
// D8 - SD du driver MOSFET 2104
// D9 - IN du driver MOSFET 2104  
// D11- LED verte
// D12- LED jaune
// D13- LED rouge

///////// Définitions ///////////////////////////////////////////////////////////////////////////////

#define SOL_VOLTS_CHAN 0               // Canal ADC pour la tension solaire
#define SOL_AMPS_CHAN 1                // Canal ADC pour le courant solaire
#define BAT_VOLTS_CHAN 2               // Canal ADC pour la tension batterie
#define AVG_NUM 8                      // Nombre de moyennes pour les lectures ADC

// Capteur de courant ACS 712. Courant = (5/(1024 *0.185))*ADC - (2.5/0.185)

#define SOL_AMPS_SCALE  0.026393581    // Facteur d'échelle pour convertir ADC en ampères solaires
#define SOL_VOLTS_SCALE 0.029296875    // Facteur d'échelle pour convertir ADC en volts solaires
#define BAT_VOLTS_SCALE 0.029296875    // Facteur d'échelle pour convertir ADC en volts batterie

#define PWM_PIN 9                      // Broche de sortie PWM (seule la broche 9 disponible pour timer1 à 50kHz)
#define PWM_ENABLE_PIN 8               // Broche de contrôle du driver MOSFET IR2104
#define PWM_FULL 1023                  // Valeur pour 100% de cycle de PWM
#define PWM_MAX 100                    // Valeur max du cycle de PWM (0-100%)
#define PWM_MIN 60                     // Valeur min du cycle de PWM
#define PWM_START 90                   // Valeur de départ du PWM
#define PWM_INC 1                      // Incrément pour l'algorithme MPPT

#define TRUE 1
#define FALSE 0
#define ON TRUE
#define OFF FALSE

#define TURN_ON_MOSFETS digitalWrite(PWM_ENABLE_PIN, HIGH) // Activer le driver MOSFET
#define TURN_OFF_MOSFETS digitalWrite(PWM_ENABLE_PIN, LOW) // Désactiver le driver MOSFET

#define ONE_SECOND 50000              // Nombre d'interruptions pour 1 seconde (période de 20µs)

#define LOW_SOL_WATTS 5.00            // Seuil bas de puissance solaire (5W)
#define MIN_SOL_WATTS 1.00            // Seuil minimal de puissance solaire (1W)
#define MIN_BAT_VOLTS 11.00           // Tension minimale batterie (11V)          
#define MAX_BAT_VOLTS 14.10           // Tension maximale batterie (14.1V)
#define BATT_FLOAT 13.60              // Tension de float de la batterie
#define HIGH_BAT_VOLTS 13.00          // Tension haute batterie (13V)
#define LVD 11.5                      // Seuil de déconnexion basse tension
#define OFF_NUM 9                     // Nombre d'itérations pour l'état OFF
  
// Définition des broches LED
#define LED_RED 10
#define LED_GREEN 11
#define LED_YELLOW 12

// Broche de contrôle de la charge
#define LOAD_PIN 4       

// Broche de contrôle rétroéclairage LCD
#define BACK_LIGHT_PIN 3       

// Définition des caractères personnalisés
byte solar[8] = { // Icône panneau solaire
  0b11111,
  0b10101,
  0b11111,
  0b10101,
  0b11111,
  0b10101,
  0b11111,
  0b00000
};

byte battery[8] = { // Icône batterie
  0b01110,
  0b11011,
  0b10001,
  0b10001,
  0b11111,
  0b11111,
  0b11111,
  0b11111,
};

byte _PWM[8] = { // Icône PWM
  0b11101,
  0b10101,
  0b10101,
  0b10101,
  0b10101,
  0b10101,
  0b10101,
  0b10111,
};

// Variables globales
float sol_amps;                      // Courant solaire (A)
float sol_volts;                     // Tension solaire (V)
float bat_volts;                     // Tension batterie (V) 
float sol_watts;                     // Puissance solaire (W)
float old_sol_watts = 0;             // Puissance solaire précédente
unsigned int seconds = 0;            // Compteur de secondes
unsigned int prev_seconds = 0;       // Secondes précédentes  
unsigned int interrupt_counter = 0;  // Compteur d'interruptions
unsigned long time = 0;              // Temps d'appui du bouton
int delta = PWM_INC;                 // Variable pour algorithme MPPT
int pwm = 0;                         // Rapport cyclique PWM (0-100%)
int back_light_pin_State = 0;        // Etat du bouton rétroéclairage
int load_status = 0;                 // Etat de la charge

// Enumération des états du chargeur
enum charger_mode {off, on, bulk, bat_float} charger_state;

// Initialisation LCD I2C
LiquidCrystal_I2C lcd(0x27, 20, 4);

//--------------------------------------------------------------------------------------------------
// Fonction d'initialisation
//--------------------------------------------------------------------------------------------------
void setup() {
  // Configuration des broches
  pinMode(LED_RED, OUTPUT);
  pinMode(LED_GREEN, OUTPUT);  
  pinMode(LED_YELLOW, OUTPUT);
  pinMode(PWM_ENABLE_PIN, OUTPUT);
  
  // Configuration du timer
  Timer1.initialize(20);
  Timer1.pwm(PWM_PIN, 0);
  TURN_ON_MOSFETS;
  Timer1.attachInterrupt(callback);
  
  // Initialisation série
  Serial.begin(9600);
  
  // Initialisation des variables
  pwm = PWM_START;
  charger_state = on;
  
  // Configuration des entrées/sorties
  pinMode(BACK_LIGHT_PIN, INPUT);
  pinMode(LOAD_PIN, OUTPUT);
  digitalWrite(LOAD_PIN, HIGH); // Charge désactivée par défaut
  
  // Initialisation LCD
  lcd.begin(20, 4);
  lcd.noBacklight();
  lcd.createChar(1, solar);
  lcd.createChar(2, battery);
  lcd.createChar(3, _PWM);
}

//--------------------------------------------------------------------------------------------------
// Boucle principale
//--------------------------------------------------------------------------------------------------
void loop() {
  read_data();          // Lecture des entrées
  run_charger();        // Gestion de la charge
  print_data();         // Affichage série
  load_control();       // Contrôle de la charge
  led_output();         // Gestion des LEDs
  lcd_display();        // Affichage LCD
}

//--------------------------------------------------------------------------------------------------
// Lecture et moyenne des valeurs ADC
//--------------------------------------------------------------------------------------------------
int read_adc(int channel) {
  int sum = 0;
  int temp;
  
  for (int i=0; i<AVG_NUM; i++) {
    temp = analogRead(channel);
    sum += temp;
    delayMicroseconds(50);
  }
  return(sum / AVG_NUM);
}

//--------------------------------------------------------------------------------------------------
// Lecture des données (tension, courant, puissance)
//--------------------------------------------------------------------------------------------------
void read_data() {
  sol_amps = (read_adc(SOL_AMPS_CHAN) * SOL_AMPS_SCALE - 12.01);
  sol_volts = read_adc(SOL_VOLTS_CHAN) * SOL_VOLTS_SCALE;
  bat_volts = read_adc(BAT_VOLTS_CHAN) * BAT_VOLTS_SCALE;
  sol_watts = sol_amps * sol_volts;
}

//--------------------------------------------------------------------------------------------------
// Routine d'interruption du timer (20µs)
//--------------------------------------------------------------------------------------------------
void callback() {
  if (interrupt_counter++ > ONE_SECOND) {
    interrupt_counter = 0;
    seconds++;
  }
}

//--------------------------------------------------------------------------------------------------
// Réglage du rapport cyclique PWM
//--------------------------------------------------------------------------------------------------
void set_pwm_duty() {
  if (pwm > PWM_MAX) {
    pwm = PWM_MAX;
  }
  else if (pwm < PWM_MIN) {
    pwm = PWM_MIN;
  }
  
  if (pwm < PWM_MAX) {
    Timer1.pwm(PWM_PIN, (PWM_FULL * (long)pwm / 100), 20);
  }
  else if (pwm == PWM_MAX) {
    Timer1.pwm(PWM_PIN, (PWM_FULL - 1), 20); // 99.9% pour maintenir la commutation
  }
}

//--------------------------------------------------------------------------------------------------
// Machine à états du chargeur
//--------------------------------------------------------------------------------------------------
void run_charger() {
  static int off_count = OFF_NUM;

  switch (charger_state) {
    case on:
      if (sol_watts < MIN_SOL_WATTS) {
        charger_state = off;
        off_count = OFF_NUM;
        TURN_OFF_MOSFETS;
      }
      else if (bat_volts > (BATT_FLOAT - 0.1)) {
        charger_state = bat_float;
      }
      else if (sol_watts < LOW_SOL_WATTS) {
        pwm = PWM_MAX; // PWM à 100% pour faible puissance
        set_pwm_duty();
      }
      else {
        pwm = ((bat_volts * 10) / (sol_volts / 10)) + 5;
        charger_state = bulk;
      }
      break;
      
    case bulk:
      if (sol_watts < MIN_SOL_WATTS) {
        charger_state = off;
        off_count = OFF_NUM;
        TURN_OFF_MOSFETS;
      }
      else if (bat_volts > BATT_FLOAT) {
        charger_state = bat_float;
      }
      else if (sol_watts < LOW_SOL_WATTS) {
        charger_state = on;
        TURN_ON_MOSFETS;
      }
      else {
        // Algorithme MPPT
        if (old_sol_watts >= sol_watts) {
          delta = -delta;
        }
        pwm += delta;
        old_sol_watts = sol_watts;
        set_pwm_duty();
      }
      break;
      
    case bat_float:
      if (sol_watts < MIN_SOL_WATTS) {
        charger_state = off;
        off_count = OFF_NUM;
        TURN_OFF_MOSFETS;
        set_pwm_duty();
      }
      else if (bat_volts > BATT_FLOAT) {
        TURN_OFF_MOSFETS;
        pwm = PWM_MAX;
        set_pwm_duty();
      }
      else if (bat_volts < BATT_FLOAT) {
        pwm = PWM_MAX;
        set_pwm_duty();
        TURN_ON_MOSFETS;
        if (bat_volts < (BATT_FLOAT - 0.1)) {
          charger_state = bulk;
        }
      }
      break;
      
    case off:
      TURN_OFF_MOSFETS;
      if (off_count > 0) {
        off_count--;
      }
      else if ((bat_volts > BATT_FLOAT) && (sol_volts > bat_volts)) {
        charger_state = bat_float;
      }
      else if ((bat_volts > MIN_BAT_VOLTS) && (bat_volts < BATT_FLOAT) && (sol_volts > bat_volts)) {
        charger_state = bulk;
      }
      break;
      
    default:
      TURN_OFF_MOSFETS;
      break;
  }
}

//--------------------------------------------------------------------------------------------------
// Contrôle de la charge
//--------------------------------------------------------------------------------------------------
void load_control() {
  if ((sol_watts < MIN_SOL_WATTS) && (bat_volts > LVD)) {
    digitalWrite(LOAD_PIN, LOW); // Activation charge la nuit
    load_status = 1;
  }
  else {
    digitalWrite(LOAD_PIN, HIGH); // Désactivation charge le jour
    load_status = 0;
  }
}

//--------------------------------------------------------------------------------------------------
// Affichage des données sur le port série
//--------------------------------------------------------------------------------------------------
void print_data() {
  Serial.print(seconds, DEC);
  Serial.print("      ");

  Serial.print("Charging = ");
  if (charger_state == on) Serial.print("on   ");
  else if (charger_state == off) Serial.print("off  ");
  else if (charger_state == bulk) Serial.print("bulk ");
  else if (charger_state == bat_float) Serial.print("float");
  Serial.print("      ");

  Serial.print("pwm = ");
  Serial.print(pwm, DEC);
  Serial.print("      ");

  Serial.print("Current (panel) = ");
  Serial.print(sol_amps);
  Serial.print("      ");

  Serial.print("Voltage (panel) = ");
  Serial.print(sol_volts);
  Serial.print("      ");

  Serial.print("Power (panel) = ");
  Serial.print(sol_volts);
  Serial.print("      ");

  Serial.print("Battery Voltage = ");
  Serial.print(bat_volts);
  Serial.print("      ");

  Serial.print("\n\r");
}

//--------------------------------------------------------------------------------------------------
// Gestion des LEDs indicateurs
//--------------------------------------------------------------------------------------------------
void led_output() {
  if(bat_volts > 14.1) {
      leds_off_all();
      digitalWrite(LED_YELLOW, HIGH); // Batterie surchargée
  } 
  else if(bat_volts > 11.9 && bat_volts < 14.1) {
      leds_off_all();
      digitalWrite(LED_GREEN, HIGH); // Batterie OK
  } 
  else if(bat_volts < 11.8) {
      leds_off_all();
      digitalWrite(LED_RED, HIGH); // Batterie faible
  } 
}

//--------------------------------------------------------------------------------------------------
// Extinction de toutes les LEDs
//--------------------------------------------------------------------------------------------------
void leds_off_all() {
  digitalWrite(LED_GREEN, LOW);
  digitalWrite(LED_RED, LOW);
  digitalWrite(LED_YELLOW, LOW);
}

//--------------------------------------------------------------------------------------------------
// Affichage sur LCD
//--------------------------------------------------------------------------------------------------
void lcd_display() {
  // Gestion du rétroéclairage
  back_light_pin_State = digitalRead(BACK_LIGHT_PIN);
  if (back_light_pin_State == HIGH) {
    time = millis();
  }
 
  // Affichage des données solaires
  lcd.setCursor(0, 0);
  lcd.print("SOL");
  lcd.setCursor(4, 0);
  lcd.write(1); // Icône solaire
  lcd.setCursor(0, 1);
  lcd.print(sol_volts);
  lcd.print("V"); 
  lcd.setCursor(0, 2);
  lcd.print(sol_amps);
  lcd.print("A");  
  lcd.setCursor(0, 3);
  lcd.print(sol_watts);
  lcd.print("W "); 
  
  // Affichage des données batterie
  lcd.setCursor(8, 0);
  lcd.print("BAT");
  lcd.setCursor(12, 0);
  lcd.write(2); // Icône batterie
  lcd.setCursor(8, 1);
  lcd.print(bat_volts);
  lcd.setCursor(8,2);
  
  // Affichage état chargeur
  if (charger_state == on) {
    lcd.print("     ");  
    lcd.setCursor(8,2);
    lcd.print("on");
  }
  else if (charger_state == off) {
    lcd.print("     ");
    lcd.setCursor(8,2);
    lcd.print("off");
  }
  else if (charger_state == bulk) {
    lcd.print("     ");
    lcd.setCursor(8,2);
    lcd.print("bulk");
  }
  else if (charger_state == bat_float) {
    lcd.print("     ");
    lcd.setCursor(8,2);
    lcd.print("float");
  }
  
  // Affichage état de charge batterie
  lcd.setCursor(8,3);
  if (bat_volts >= 12.7) lcd.print("100%");
  else if (bat_volts >= 12.5) lcd.print("90%");
  else if (bat_volts >= 12.42) lcd.print("80%");
  else if (bat_volts >= 12.32) lcd.print("70%");
  else if (bat_volts >= 12.2) lcd.print("60%");
  else if (bat_volts >= 12.06) lcd.print("50%");
  else if (bat_volts >= 11.90) lcd.print("40%");
  else if (bat_volts >= 11.75) lcd.print("30%");
  else if (bat_volts >= 11.58) lcd.print("20%");
  else if (bat_volts >= 11.31) lcd.print("10%");
  else lcd.print("0%");
  
  // Affichage PWM
  lcd.setCursor(15,0);
  lcd.print("PWM");
  lcd.setCursor(19,0);
  lcd.write(3); // Icône PWM
  lcd.setCursor(15,1);
  lcd.print("   ");
  lcd.setCursor(15,1);
  lcd.print(pwm); 
  lcd.print("%");
  
  // Affichage état charge
  lcd.setCursor(15,2);
  lcd.print("Load");
  lcd.setCursor(15,3);
  if (load_status == 1) {  
    lcd.print("   ");
    lcd.setCursor(15,3);
    lcd.print("On");
  }
  else { 
    lcd.print("   ");
    lcd.setCursor(15,3);
    lcd.print("Off");
  }
  
  // Gestion temporisation rétroéclairage
  backLight_timer();
}

//--------------------------------------------------------------------------------------------------
// Gestion du rétroéclairage LCD (90s)
//--------------------------------------------------------------------------------------------------
void backLight_timer() {
  if((millis() - time) <= 90000) {
      lcd.backlight(); // Allumer pendant 90s après dernier appui  
  }
  else {
      lcd.noBacklight(); // Eteindre après 90s
  }
}