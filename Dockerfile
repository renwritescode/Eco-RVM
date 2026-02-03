# Dockerfile para Eco-RVM Backend
FROM python:3.11-slim

# Variables de entorno
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_ENV=production

# Directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código de la aplicación
COPY backend/ ./backend/
COPY frontend/ ./frontend/
COPY scripts/ ./scripts/
COPY .env.example ./.env

# Crear directorios necesarios
RUN mkdir -p data logs

# Exponer puerto
EXPOSE 5000

# Variables de entorno por defecto
ENV SECRET_KEY=docker-secret-key-change-me
ENV DATABASE_URL=sqlite:///data/eco_rvm.db

# Comando de inicio
CMD ["python", "scripts/run_backend.py"]
