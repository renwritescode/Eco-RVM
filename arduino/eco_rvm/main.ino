/*
 * Proyecto: Eco-RVM v2.0 (Reverse Vending Machine)
 * Hardware: Arduino UNO + RFID + Keypad + Servo + LCD + Ultrasonico + Buzzer
 * Actualizado: Con soporte para vinculación de tarjetas físicas
 */

#include <Keypad.h>
#include <LiquidCrystal_I2C.h>
#include <MFRC522.h>
#include <SPI.h>
#include <Servo.h>

// ===== PINES ARDUINO UNO =====
#define PIN_SERVO A2
#define PIN_TRIG A3
#define PIN_ECHO 8
#define PIN_RFID_RST 9
#define PIN_RFID_SDA 10
#define PIN_BUZZER 1 // TX pin

// ===== KEYPAD 4X4 =====
const byte ROWS = 4;
const byte COLS = 4;
char keys[ROWS][COLS] = {{'1', '2', '3', 'A'},
                         {'4', '5', '6', 'B'},
                         {'7', '8', '9', 'C'},
                         {'*', '0', '#', 'D'}};
byte rowPins[ROWS] = {2, 3, 4, 5};
byte colPins[COLS] = {6, 7, A0, A1};
Keypad keypad = Keypad(makeKeymap(keys), rowPins, colPins, ROWS, COLS);

// ===== OBJETOS =====
MFRC522 rfid(PIN_RFID_SDA, PIN_RFID_RST);
Servo servoCompuerta;
LiquidCrystal_I2C lcd(0x27, 16, 2); // Cambiar a 0x3F si no funciona

// ===== ÁNGULOS SERVO =====
const int ANGULO_NEUTRAL = 90;
const int ANGULO_ACEPTA = 135;
const int ANGULO_RECHAZA = 45;

// ===== ESTADOS =====
enum Estado {
  ESTADO_IDLE,
  ESTADO_MENU_LOGIN, // NUEVO: Menú para seleccionar RFID o ID
  ESTADO_INGRESO_ID, // NUEVO: Ingresar ID por keypad
  ESTADO_ESPERANDO,
  ESTADO_LISTO,
  ESTADO_PROCESANDO,
  ESTADO_EJECUTANDO,
  ESTADO_VINCULACION // NUEVO
};

Estado estadoActual = ESTADO_IDLE;

// ===== VARIABLES GLOBALES =====
unsigned long tiempoUltimaLectura = 0;
unsigned long tiempoUltimoUltrasonico = 0;
const unsigned long INTERVALO_RFID = 500;
const unsigned long INTERVALO_ULTRASONICO = 200;
const unsigned long TIMEOUT_RESPUESTA = 5000;

String bufferSerial = "";
bool objetoDetectado = false;
unsigned long tiempoEsperaRespuesta = 0;

// Variables de vinculación
String uidTarjetaNueva = "";
String codigoIngresado = "";

// Variables de login por keypad
String idUsuarioIngresado = ""; // NUEVO

// ===== FUNCIONES =====
void setup() {
  Serial.begin(115200);
  while (!Serial)
    ;

  SPI.begin();
  rfid.PCD_Init();

  servoCompuerta.attach(PIN_SERVO);
  servoCompuerta.write(ANGULO_NEUTRAL);

  lcd.init();
  lcd.backlight();

  pinMode(PIN_TRIG, OUTPUT);
  pinMode(PIN_ECHO, INPUT);
  pinMode(PIN_BUZZER, OUTPUT);

  mostrarEnLCD("  ECO-RVM v2.0  ", "Iniciando...");
  delay(2000);
  mostrarEnLCD("Presiona A para", "abrir menu");

  Serial.println("SYSTEM:READY");
}

// ===== PROCESAR COMANDOS SERIAL =====
void procesarComandosSerial() {
  if (Serial.available() > 0) {
    String comando = Serial.readStringUntil('\n');
    comando.trim();

    if (comando.length() == 0)
      return;

    // Comandos de respuesta de autenticación
    if (comando.startsWith("USER:OK:")) {
      // Usuario autenticado correctamente
      String nombre = comando.substring(8);
      nombre.trim();
      estadoActual = ESTADO_LISTO;
      mostrarEnLCD("Bienvenido!", nombre);
      beepExito();
      delay(2000);
      mostrarEnLCD("Deposita objeto", "reciclable");
    } else if (comando == "USER:ERROR") {
      // Código inválido
      estadoActual = ESTADO_IDLE;
      mostrarEnLCD("ID no valido", "Reintente");
      beepError();
      delay(2000);
      mostrarEnLCD("Presiona A para", "abrir menu");
    } else if (comando == "USER:NEW") {
      // Usuario nuevo (RFID no registrado)
      estadoActual = ESTADO_IDLE;
      mostrarEnLCD("Usuario nuevo", "Registrese");
      beepError();
      delay(2000);
      mostrarEnLCD("Presiona A para", "abrir menu");
    }
    // Comandos de clasificación de objetos
    else if (comando == "ACCEPTED") {
      // Objeto aceptado
      estadoActual = ESTADO_EJECUTANDO;
      mostrarEnLCD("Material:", "Reciclable");
      delay(1000);
      mostrarEnLCD("Puntos: +10", "Gracias!");
      beepExito();
      abrirCompuerta();
      delay(3000);
      objetoDetectado = false;
      // Volver a idle
      estadoActual = ESTADO_IDLE;
      mostrarEnLCD("Presiona A para", "abrir menu");
      Serial.println("SYSTEM:READY");
    } else if (comando == "REJECTED") {
      // Objeto rechazado
      objetoDetectado = false;
      estadoActual = ESTADO_IDLE;
      mostrarEnLCD("Objeto no", "reciclable");
      beepError();
      delay(3000);
      mostrarEnLCD("Presiona A para", "abrir menu");
      Serial.println("SYSTEM:READY");
    }
  }
}

void loop() {
  procesarComandosSerial();

  switch (estadoActual) {
  case ESTADO_IDLE:
    procesarEstadoIdle();
    break;

  case ESTADO_MENU_LOGIN: // NUEVO
    procesarMenuLogin();
    break;

  case ESTADO_INGRESO_ID: // NUEVO
    procesarIngresoID();
    break;

  case ESTADO_ESPERANDO:
    procesarEsperandoRespuesta();
    break;

  case ESTADO_LISTO:
    procesarListoParaObjeto();
    break;

  case ESTADO_PROCESANDO:
    // Espera pasiva
    break;

  case ESTADO_EJECUTANDO:
    // Trans itorio
    break;

  case ESTADO_VINCULACION:
    procesarModoVinculacion();
    break;
  }
}

// ===== ESTADO: IDLE =====
void procesarEstadoIdle() {
  // Verificar si presionan 'A' para abrir menú
  char tecla = keypad.getKey();
  if (tecla == 'A') {
    estadoActual = ESTADO_MENU_LOGIN;
    mostrarEnLCD("1.RFID  2.ID", "* Cancelar");
    beepTecla();
    return;
  }

  // Lectura RFID normal
  if (millis() - tiempoUltimaLectura >= INTERVALO_RFID) {
    tiempoUltimaLectura = millis();
    leerRFID();
  }
}

// ===== LEER RFID =====
void leerRFID() {
  if (!rfid.PICC_IsNewCardPresent() || !rfid.PICC_ReadCardSerial()) {
    return;
  }

  String uid = obtenerUIDTarjeta();

  // Verificar si es tarjeta nueva (consultar al backend)
  Serial.print("UID:");
  Serial.println(uid);

  estadoActual = ESTADO_ESPERANDO;
  tiempoEsperaRespuesta = millis();
  mostrarEnLCD("Verificando", "usuario...");

  rfid.PICC_HaltA();
  rfid.PCD_StopCrypto1();
}

// ===== ESTADO: ESPERANDO RESPUESTA =====
void procesarEsperandoRespuesta() {
  if (millis() - tiempoEsperaRespuesta > TIMEOUT_RESPUESTA) {
    mostrarEnLCD("Error: Timeout", "Reintente");
    beepError();
    delay(2000);
    estadoActual = ESTADO_IDLE;
    mostrarEnLCD("Acerca tarjeta", "RFID");
  }
}

// ===== ESTADO: LISTO PARA OBJETO =====
void procesarListoParaObjeto() {
  if (millis() - tiempoUltimoUltrasonico >= INTERVALO_ULTRASONICO) {
    tiempoUltimoUltrasonico = millis();
    leerUltrasonico();
  }
}

// ===== LEER ULTRASÓNICO =====
void leerUltrasonico() {
  digitalWrite(PIN_TRIG, LOW);
  delayMicroseconds(2);
  digitalWrite(PIN_TRIG, HIGH);
  delayMicroseconds(10);
  digitalWrite(PIN_TRIG, LOW);

  long duracion = pulseIn(PIN_ECHO, HIGH, 30000);
  float distancia = duracion * 0.034 / 2.0;

  // Rango 3-15cm: evita falsos positivos (bandeja vacía >15cm) y objetos muy
  // cerca (<3cm)
  if (distancia >= 3 && distancia <= 15 && !objetoDetectado) {
    objetoDetectado = true;
    estadoActual = ESTADO_PROCESANDO;
    mostrarEnLCD("Objeto detectado", "Analizando...");
    Serial.println("STATUS:CHECK");
  }
}

// ===== MODO VINCULACIÓN =====
void procesarModoVinculacion() {
  char tecla = keypad.getKey();

  if (tecla) {
    beepTecla();

    if (tecla == '#') {
      // Confirmar código
      if (codigoIngresado.length() == 6) {
        Serial.print("LINK:");
        Serial.print(uidTarjetaNueva);
        Serial.print(":");
        Serial.println(codigoIngresado);

        mostrarEnLCD("Vinculando...", "");
        estadoActual = ESTADO_ESPERANDO;
        tiempoEsperaRespuesta = millis();
      } else {
        mostrarEnLCD("Codigo invalido", "Debe ser 6 dig.");
        beepError();
        delay(1500);
        iniciarModoVinculacion(uidTarjetaNueva);
      }
    } else if (tecla == '*') {
      // Cancelar
      codigoIngresado = "";
      estadoActual = ESTADO_IDLE;
      mostrarEnLCD("Cancelado", "");
      delay(1000);
      mostrarEnLCD("Acerca tarjeta", "RFID");
    } else if (codigoIngresado.length() < 6) {
      // Solo permitir 0-9 y A-D
      codigoIngresado += tecla;
      mostrarEnLCD("Codigo:", codigoIngresado);
    }
  }
}

// ===== PROCESAR MENÚ LOGIN =====
void procesarMenuLogin() {
  char tecla = keypad.getKey();

  if (tecla) {
    beepTecla();

    if (tecla == '1') {
      // Opción RFID
      estadoActual = ESTADO_IDLE;
      mostrarEnLCD("Presiona A para", "abrir menu");
    } else if (tecla == '2') {
      // Ingresar ID manualmente
      estadoActual = ESTADO_INGRESO_ID;
      idUsuarioIngresado = "";
      mostrarEnLCD("Ingrese ID:", "______");
    } else if (tecla == '*') {
      // Cancelar
      estadoActual = ESTADO_IDLE;
      mostrarEnLCD("Cancelado", "");
      delay(1000);
      mostrarEnLCD("Presiona A para", "abrir menu");
    }
  }
}

// ===== PROCESAR INGRESO ID =====
void procesarIngresoID() {
  char tecla = keypad.getKey();

  if (tecla) {
    beepTecla();

    // Números 0-9 y letras A-D son válidos para el código
    if ((tecla >= '0' && tecla <= '9') || (tecla >= 'A' && tecla <= 'D')) {
      if (idUsuarioIngresado.length() < 6) {
        idUsuarioIngresado += tecla;
        actualizarPantallaID();
      }
    }
    // * borra el último dígito
    else if (tecla == '*') {
      if (idUsuarioIngresado.length() > 0) {
        idUsuarioIngresado.remove(idUsuarioIngresado.length() - 1);
        actualizarPantallaID();
      } else {
        // Si no hay nada que borrar, cancelar y volver
        estadoActual = ESTADO_IDLE;
        mostrarEnLCD("Cancelado", "");
        delay(1000);
        mostrarEnLCD("Presiona A para", "abrir menu");
      }
    }
    // # confirma el código
    else if (tecla == '#') {
      if (idUsuarioIngresado.length() == 6) {
        Serial.print("LOGIN:");
        Serial.println(idUsuarioIngresado);

        estadoActual = ESTADO_ESPERANDO;
        tiempoEsperaRespuesta = millis();
        mostrarEnLCD("Verificando...", "");
        idUsuarioIngresado = "";
      } else {
        mostrarEnLCD("ID debe ser", "6 digitos");
        beepError();
        delay(1500);
        actualizarPantallaID();
      }
    }
  }
}

// ===== ACTUALIZAR PANTALLA ID =====
void actualizarPantallaID() {
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Ingrese ID:");
  lcd.setCursor(0, 1);

  for (int i = 0; i < 6; i++) {
    if (i < idUsuarioIngresado.length()) {
      lcd.print(idUsuarioIngresado[i]);
    } else {
      lcd.print("_");
    }
  }

  lcd.setCursor(7, 1);
  lcd.print("*<  #OK");
}

void iniciarModoVinculacion(String uid) {
  estadoActual = ESTADO_VINCULACION;
  uidTarjetaNueva = uid;
  codigoIngresado = "";
  mostrarEnLCD("Ingresa codigo:", "# confirma");
}

// ===== SERVO COMPUERTA =====
void abrirCompuerta() {
  // Mover servo para aceptar objeto
  moverServo(ANGULO_ACEPTA);
  delay(2000);
  // Volver a posición neutral
  moverServo(ANGULO_NEUTRAL);
}

// ===== ACEPTACIÓN =====
void ejecutarAceptacion() {
  estadoActual = ESTADO_EJECUTANDO;

  mostrarEnLCD("  ACEPTADO!", "+10 Puntos!");
  beepExito();

  // Inclinar DERECHA
  moverServo(ANGULO_ACEPTA);
  delay(2000);

  // Volver a neutral
  moverServo(ANGULO_NEUTRAL);
  delay(1000);

  estadoActual = ESTADO_IDLE;
  mostrarEnLCD("Acerca tarjeta", "RFID");
}

// ===== RECHAZO =====
void ejecutarRechazo() {
  estadoActual = ESTADO_EJECUTANDO;

  mostrarEnLCD("  RECHAZADO", "No reciclable");
  beepError();

  // Inclinar IZQUIERDA
  moverServo(ANGULO_RECHAZA);
  delay(2000);

  // Volver a neutral
  moverServo(ANGULO_NEUTRAL);
  delay(1000);

  estadoActual = ESTADO_IDLE;
  mostrarEnLCD("Acerca tarjeta", "RFID");
}

// ===== MOVER SERVO SUAVE =====
void moverServo(int destino) {
  int actual = servoCompuerta.read();
  int paso = (destino > actual) ? 1 : -1;

  while (actual != destino) {
    actual += paso;
    servoCompuerta.write(actual);
    delay(15);
  }
}

// ===== SONIDOS =====
void beepExito() {
  tone(PIN_BUZZER, 523, 100);
  delay(120);
  tone(PIN_BUZZER, 659, 100);
  delay(120);
  tone(PIN_BUZZER, 784, 200);
  delay(220);
  noTone(PIN_BUZZER);
}

void beepError() {
  tone(PIN_BUZZER, 200, 300);
  delay(350);
  tone(PIN_BUZZER, 150, 300);
  delay(350);
  noTone(PIN_BUZZER);
}

void beepTecla() {
  tone(PIN_BUZZER, 1000, 50);
  delay(60);
  noTone(PIN_BUZZER);
}

// ===== LCD =====
void mostrarEnLCD(String linea1, String linea2) {
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print(linea1);
  lcd.setCursor(0, 1);
  lcd.print(linea2);
}

// ===== UID =====
String obtenerUIDTarjeta() {
  String uid = "";
  for (byte i = 0; i < rfid.uid.size; i++) {
    if (rfid.uid.uidByte[i] < 0x10)
      uid += "0";
    uid += String(rfid.uid.uidByte[i], HEX);
  }
  uid.toUpperCase();
  return uid;
}
