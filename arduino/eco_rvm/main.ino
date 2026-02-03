/*
 * Proyecto: Eco-RVM (Reverse Vending Machine)
 * Descripción: Sistema de reciclaje automatizado con validación por IA
 * Hardware: Arduino Uno R3 + RFID + Servo + Ultrasonico + LCD I2C
 * Comunicación: Serial USB a 9600 baudios
 */

#include <SPI.h>
#include <MFRC522.h>
#include <Servo.h>
#include <LiquidCrystal_I2C.h>

// Definición de pines
#define PIN_SERVO 9
#define PIN_TRIG 7
#define PIN_ECHO 6
#define PIN_RFID_RST 5
#define PIN_RFID_SDA 10
#define PIN_BUZZER 4
#define PIN_LED_VERDE 2
#define PIN_LED_ROJO 3

// Configuración de componentes
MFRC522 rfid(PIN_RFID_SDA, PIN_RFID_RST);
Servo servoCompuerta;
LiquidCrystal_I2C lcd(0x27, 16, 2);

// Estados del sistema
enum Estado {
  IDLE,
  ESPERANDO_RESPUESTA,
  LISTO_PARA_OBJETO,
  PROCESANDO_OBJETO,
  EJECUTANDO_DECISION
};

Estado estadoActual = IDLE;

// Variables de control no bloqueante
unsigned long tiempoUltimaLectura = 0;
unsigned long tiempoUltimoUltrasonico = 0;
const unsigned long INTERVALO_RFID = 500;
const unsigned long INTERVALO_ULTRASONICO = 200;
const unsigned long TIMEOUT_RESPUESTA = 5000;

// Variables de estado
String bufferSerial = "";
bool objetoDetectado = false;
unsigned long tiempoEsperaRespuesta = 0;

// Prototipos de funciones
void inicializarSistema();
void procesarEstadoIdle();
void procesarEsperandoRespuesta();
void procesarListoParaObjeto();
void procesarProcesandoObjeto();
void procesarEjecutandoDecision();
void leerRFID();
void leerUltrasonico();
void procesarComandosSerial();
void mostrarEnLCD(String linea1, String linea2);
void ejecutarAceptacion();
void ejecutarRechazo();
void emitirSonidoExito();
void emitirSonidoError();
void resetearLEDs();
String obtenerUIDTarjeta();

void setup() {
  inicializarSistema();
}

void loop() {
  // Procesamiento no bloqueante según estado actual
  procesarComandosSerial();
  
  switch (estadoActual) {
    case IDLE:
      procesarEstadoIdle();
      break;
      
    case ESPERANDO_RESPUESTA:
      procesarEsperandoRespuesta();
      break;
      
    case LISTO_PARA_OBJETO:
      procesarListoParaObjeto();
      break;
      
    case PROCESANDO_OBJETO:
      procesarProcesandoObjeto();
      break;
      
    case EJECUTANDO_DECISION:
      procesarEjecutandoDecision();
      break;
  }
}

void inicializarSistema() {
  // Inicializar comunicación serial
  Serial.begin(9600);
  while (!Serial);
  
  // Inicializar SPI para RFID
  SPI.begin();
  rfid.PCD_Init();
  
  // Inicializar servo
  servoCompuerta.attach(PIN_SERVO);
  servoCompuerta.write(0);
  
  // Inicializar LCD
  lcd.init();
  lcd.backlight();
  
  // Configurar pines digitales
  pinMode(PIN_TRIG, OUTPUT);
  pinMode(PIN_ECHO, INPUT);
  pinMode(PIN_BUZZER, OUTPUT);
  pinMode(PIN_LED_VERDE, OUTPUT);
  pinMode(PIN_LED_ROJO, OUTPUT);
  
  // Estado inicial de LEDs
  resetearLEDs();
  
  // Mensaje de bienvenida
  mostrarEnLCD("  ECO-RVM v1.0  ", "Iniciando...");
  delay(2000);
  mostrarEnLCD("Acerque Tarjeta", "     RFID       ");
  
  Serial.println("SYSTEM:READY");
}

void procesarEstadoIdle() {
  // Lectura no bloqueante de RFID
  if (millis() - tiempoUltimaLectura >= INTERVALO_RFID) {
    tiempoUltimaLectura = millis();
    leerRFID();
  }
}

void procesarEsperandoRespuesta() {
  // Verificar timeout
  if (millis() - tiempoEsperaRespuesta > TIMEOUT_RESPUESTA) {
    mostrarEnLCD("Error: Timeout", "Reintente");
    emitirSonidoError();
    digitalWrite(PIN_LED_ROJO, HIGH);
    delay(2000);
    resetearLEDs();
    estadoActual = IDLE;
    mostrarEnLCD("Acerque Tarjeta", "     RFID       ");
  }
}

void procesarListoParaObjeto() {
  // Lectura no bloqueante del ultrasonico
  if (millis() - tiempoUltimoUltrasonico >= INTERVALO_ULTRASONICO) {
    tiempoUltimoUltrasonico = millis();
    leerUltrasonico();
  }
}

void procesarProcesandoObjeto() {
  // Estado pasivo, esperando comando de Python
  // La lógica se maneja en procesarComandosSerial()
}

void procesarEjecutandoDecision() {
  // Estado transitorio, vuelve automáticamente a IDLE después de ejecutar
}

void leerRFID() {
  // Verificar si hay tarjeta presente
  if (!rfid.PICC_IsNewCardPresent()) {
    return;
  }
  
  // Intentar leer la tarjeta
  if (!rfid.PICC_ReadCardSerial()) {
    return;
  }
  
  // Obtener UID
  String uid = obtenerUIDTarjeta();
  
  // Enviar UID a Python
  Serial.print("UID:");
  Serial.println(uid);
  
  // Actualizar estado
  estadoActual = ESPERANDO_RESPUESTA;
  tiempoEsperaRespuesta = millis();
  mostrarEnLCD("Verificando", "Usuario...");
  
  // Detener lectura de tarjeta
  rfid.PICC_HaltA();
  rfid.PCD_StopCrypto1();
}

void leerUltrasonico() {
  // Generar pulso de trigger
  digitalWrite(PIN_TRIG, LOW);
  delayMicroseconds(2);
  digitalWrite(PIN_TRIG, HIGH);
  delayMicroseconds(10);
  digitalWrite(PIN_TRIG, LOW);
  
  // Leer tiempo de echo
  long duracion = pulseIn(PIN_ECHO, HIGH, 30000);
  
  // Calcular distancia en cm
  float distancia = duracion * 0.034 / 2.0;
  
  // Verificar detección (menos de 15 cm)
  if (distancia > 0 && distancia < 15 && !objetoDetectado) {
    objetoDetectado = true;
    estadoActual = PROCESANDO_OBJETO;
    mostrarEnLCD("Objeto Detectado", "Analizando...");
    
    // Enviar señal a Python
    Serial.println("STATUS:CHECK");
  }
}

void procesarComandosSerial() {
  while (Serial.available() > 0) {
    char caracter = Serial.read();
    
    if (caracter == '\n') {
      // Procesar comando completo
      bufferSerial.trim();
      
      if (bufferSerial == "OK") {
        // Usuario válido
        estadoActual = LISTO_PARA_OBJETO;
        objetoDetectado = false;
        mostrarEnLCD("Inserte Objeto", "Reciclable");
        digitalWrite(PIN_LED_VERDE, HIGH);
        
      } else if (bufferSerial == "ERROR") {
        // Usuario no válido
        mostrarEnLCD("Tarjeta Invalida", "Reintente");
        emitirSonidoError();
        digitalWrite(PIN_LED_ROJO, HIGH);
        delay(2000);
        resetearLEDs();
        estadoActual = IDLE;
        mostrarEnLCD("Acerque Tarjeta", "     RFID       ");
        
      } else if (bufferSerial == "CMD:ACCEPT") {
        // Objeto aceptado
        ejecutarAceptacion();
        
      } else if (bufferSerial == "CMD:REJECT") {
        // Objeto rechazado
        ejecutarRechazo();
      }
      
      bufferSerial = "";
      
    } else {
      bufferSerial += caracter;
    }
  }
}

void ejecutarAceptacion() {
  estadoActual = EJECUTANDO_DECISION;
  
  // Mostrar en LCD
  mostrarEnLCD("   ACEPTADO!    ", "  +10 Puntos!   ");
  
  // LED verde
  resetearLEDs();
  digitalWrite(PIN_LED_VERDE, HIGH);
  
  // Sonido de éxito
  emitirSonidoExito();
  
  // Mover servo a 90 grados
  servoCompuerta.write(90);
  delay(2000);
  
  // Regresar servo a posición inicial
  servoCompuerta.write(0);
  delay(1000);
  
  // Volver a estado inicial
  resetearLEDs();
  estadoActual = IDLE;
  mostrarEnLCD("Acerque Tarjeta", "     RFID       ");
}

void ejecutarRechazo() {
  estadoActual = EJECUTANDO_DECISION;
  
  // Mostrar en LCD
  mostrarEnLCD("   RECHAZADO    ", "No Reciclable");
  
  // LED rojo
  resetearLEDs();
  digitalWrite(PIN_LED_ROJO, HIGH);
  
  // Sonido de error
  emitirSonidoError();
  
  delay(2000);
  
  // Volver a estado inicial
  resetearLEDs();
  estadoActual = IDLE;
  mostrarEnLCD("Acerque Tarjeta", "     RFID       ");
}

void mostrarEnLCD(String linea1, String linea2) {
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print(linea1);
  lcd.setCursor(0, 1);
  lcd.print(linea2);
}

void emitirSonidoExito() {
  // Tono ascendente
  tone(PIN_BUZZER, 1000, 150);
  delay(200);
  tone(PIN_BUZZER, 1500, 150);
  delay(200);
  tone(PIN_BUZZER, 2000, 200);
  delay(250);
}

void emitirSonidoError() {
  // Tono descendente
  tone(PIN_BUZZER, 800, 200);
  delay(250);
  tone(PIN_BUZZER, 400, 300);
  delay(350);
}

void resetearLEDs() {
  digitalWrite(PIN_LED_VERDE, LOW);
  digitalWrite(PIN_LED_ROJO, LOW);
}

String obtenerUIDTarjeta() {
  String uid = "";
  for (byte i = 0; i < rfid.uid.size; i++) {
    if (rfid.uid.uidByte[i] < 0x10) {
      uid += "0";
    }
    uid += String(rfid.uid.uidByte[i], HEX);
  }
  uid.toUpperCase();
  return uid;
}
