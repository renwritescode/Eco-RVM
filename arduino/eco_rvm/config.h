/* 
 * Eco-RVM - Configuración de Hardware
 * Definición de pines y constantes
 */

#ifndef CONFIG_H
#define CONFIG_H

// ==========================================
// Configuración de Pines
// ==========================================

// RFID RC522
#define RFID_SS_PIN     10
#define RFID_RST_PIN    9

// Sensor Ultrasónico HC-SR04
#define ULTRASONIC_TRIG_PIN  7
#define ULTRASONIC_ECHO_PIN  6

// Servo Motor
#define SERVO_PIN       4

// LEDs
#define LED_GREEN_PIN   2
#define LED_RED_PIN     3

// Buzzer
#define BUZZER_PIN      5

// LCD I2C
#define LCD_ADDRESS     0x27
#define LCD_COLS        16
#define LCD_ROWS        2

// ==========================================
// Configuración del Sistema
// ==========================================

// Comunicación Serial
#define SERIAL_BAUDRATE 9600

// Tiempos (en milisegundos)
#define RFID_READ_DELAY     100
#define OBJECT_DETECT_DIST  15    // Distancia en cm para detectar objeto
#define GATE_OPEN_TIME      3000  // Tiempo que permanece abierta la compuerta
#define USER_TIMEOUT        30000 // Tiempo de espera para el usuario

// Servo
#define SERVO_CLOSED_ANGLE  0
#define SERVO_OPEN_ANGLE    90

// Tonos del Buzzer
#define TONE_SUCCESS_FREQ   1000
#define TONE_SUCCESS_DUR    200
#define TONE_ERROR_FREQ     400
#define TONE_ERROR_DUR      500
#define TONE_BEEP_FREQ      800
#define TONE_BEEP_DUR       100

// ==========================================
// Comandos del Protocolo Serial
// ==========================================

#define CMD_RFID_PREFIX     "RFID:"
#define CMD_OBJECT_DETECTED "OBJ_DETECTED"
#define CMD_READY           "READY"
#define CMD_ACCEPTED        "ACCEPTED"
#define CMD_REJECTED        "REJECTED"

// ==========================================
// Mensajes LCD
// ==========================================

#define MSG_WELCOME_L1      "   ECO-RVM"
#define MSG_WELCOME_L2      " Acerca tarjeta"
#define MSG_USER_FOUND_L1   "Usuario:"
#define MSG_INSERT_OBJ_L2   "Inserta objeto"
#define MSG_ANALYZING_L1    "Analizando..."
#define MSG_PLEASE_WAIT_L2  "Por favor espera"
#define MSG_ACCEPTED_L1     "ACEPTADO!"
#define MSG_POINTS_PREFIX   "+10 puntos"
#define MSG_REJECTED_L1     "RECHAZADO"
#define MSG_TRY_AGAIN_L2    "Intenta de nuevo"
#define MSG_USER_NOT_FOUND  "No registrado"
#define MSG_TIMEOUT_L1      "Tiempo agotado"

#endif // CONFIG_H
