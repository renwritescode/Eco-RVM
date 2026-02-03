# ECO-RVM v2.0 🌱♻️

> Sistema inteligente de reciclaje con validación por IA, gamificación y dashboard de impacto ambiental.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Flask](https://img.shields.io/badge/Flask-3.0-green)
![TensorFlow](https://img.shields.io/badge/TensorFlow-2.15-orange)
![License](https://img.shields.io/badge/License-MIT-yellow)

## ✨ Características

- 🎯 **Clasificación IA** - Modelo MobileNetV2 con 94.79% de precisión
- 🏆 **Gamificación** - Niveles, badges, rachas y rankings
- 🎁 **Sistema de Recompensas** - Canjea puntos por premios reales
- 🌍 **Impacto Ambiental** - Dashboard con CO₂ evitado y equivalencias
- 📱 **Interfaz Moderna** - Dashboard responsive con Chart.js
- 🔌 **Hardware Arduino** - RFID, sensores, servos y LCD
- 🐳 **Docker Ready** - Despliegue fácil con contenedores

## 📁 Estructura del Proyecto

```
Eco-RVM/
├── backend/                 # API Flask
│   ├── api/                # Endpoints REST
│   ├── models/             # Modelos SQLAlchemy
│   ├── services/           # Lógica de negocio
│   ├── schemas/            # Validación Marshmallow
│   └── utils/              # Logging y utilidades
├── controller/             # Orquestador del sistema
│   ├── arduino_handler.py  # Comunicación serial
│   ├── vision_system.py    # Cámara + IA
│   └── api_client.py       # Cliente HTTP
├── frontend/               # Interfaz web
│   ├── templates/          # HTML Jinja2
│   └── static/             # CSS, JS, imágenes
├── ml/                     # Machine Learning
│   └── models/             # Modelos entrenados
├── arduino/                # Código Arduino
├── tests/                  # Tests automatizados
├── scripts/                # Scripts de utilidad
├── Dockerfile              # Contenedor Docker
└── docker-compose.yml      # Orquestación
```

## 🚀 Instalación Rápida

### Opción 1: Con Docker (Recomendado)

```bash
# Clonar repositorio
git clone https://github.com/tu-usuario/Eco-RVM.git
cd Eco-RVM

# Iniciar con Docker
docker-compose up --build

# Acceder a http://localhost:5000
```

### Opción 2: Instalación Manual

```bash
# Clonar repositorio
git clone https://github.com/tu-usuario/Eco-RVM.git
cd Eco-RVM

# Crear entorno virtual
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
copy .env.example .env
# Editar .env con tus valores

# Ejecutar backend
python scripts/run_backend.py
```

## ⚙️ Configuración

Copia `.env.example` a `.env` y ajusta los valores:

```env
# Flask
FLASK_ENV=development
SECRET_KEY=tu-clave-secreta

# Arduino
SERIAL_PORT=COM3
SERIAL_BAUDRATE=9600

# Cámara
CAMERA_ID=0

# IA
MODEL_PATH=ml/models/modelo_reciclaje.h5
MIN_CONFIDENCE=0.70

# Puntos
POINTS_PER_RECYCLE=10
```

## 📊 API Endpoints

### Usuarios
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/check_user` | Verificar usuario por UID |
| GET | `/api/usuarios` | Listar usuarios |
| POST | `/api/registrar_usuario` | Registrar usuario |
| GET | `/api/ranking` | Obtener ranking |

### Transacciones
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/add_points` | Agregar puntos |
| GET | `/api/transacciones/<id>` | Historial usuario |
| GET | `/api/transacciones/recientes` | Transacciones recientes |

### Recompensas
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/rewards` | Listar recompensas |
| POST | `/api/rewards/redeem` | Canjear recompensa |
| GET | `/api/rewards/history/<id>` | Historial de canjes |

### Estadísticas
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/stats/general` | Estadísticas generales |
| GET | `/api/stats/impacto` | Impacto ambiental |
| GET | `/api/stats/dashboard` | Dashboard completo |

## 🧪 Testing

```bash
# Ejecutar todos los tests
pytest tests/ -v

# Con cobertura
pytest tests/ -v --cov=backend --cov-report=html

# Abrir reporte de cobertura
start htmlcov/index.html
```

## 🔧 Hardware

### Componentes
- Arduino Uno/Mega
- RFID RC522
- Sensor Ultrasónico HC-SR04
- Servo SG90
- LCD 16x2 I2C
- LEDs (Rojo/Verde)
- Buzzer

### Conexiones
```
RFID RC522:
- SDA  → Pin 10
- SCK  → Pin 13
- MOSI → Pin 11
- MISO → Pin 12
- RST  → Pin 9

Ultrasónico:
- TRIG → Pin 7
- ECHO → Pin 6

Servo: Pin 4
LED Verde: Pin 2
LED Rojo: Pin 3
Buzzer: Pin 5
LCD I2C: A4 (SDA), A5 (SCL)
```

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama (`git checkout -b feature/NuevaCaracteristica`)
3. Commit cambios (`git commit -m 'Add: nueva característica'`)
4. Push a la rama (`git push origin feature/NuevaCaracteristica`)
5. Abre un Pull Request

## 📄 Licencia

MIT License - Ver [LICENSE](LICENSE) para más detalles.

## 👥 Equipo

Desarrollado con 💚 para un mundo más sostenible.

---

<p align="center">
  <strong>ECO-RVM</strong> - Reciclando el futuro, un objeto a la vez 🌍
</p>
