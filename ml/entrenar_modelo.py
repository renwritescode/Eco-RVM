"""
Script de Ejemplo para Entrenar Modelo de Clasificación de Reciclables
NOTA: Este es un ejemplo básico. Para producción, usar dataset real.
"""

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import numpy as np
import os

# Configuración
IMG_WIDTH = 224
IMG_HEIGHT = 224
NUM_CLASES = 3
EPOCHS = 50

# Clases de objetos
CLASES = ['botella', 'lata', 'basura']

def crear_modelo():
    """
    Crear modelo CNN para clasificación de reciclables
    Arquitectura basada en MobileNetV2 con Transfer Learning
    """
    
    # Cargar modelo base pre-entrenado (sin capa superior)
    modelo_base = keras.applications.MobileNetV2(
        input_shape=(IMG_WIDTH, IMG_HEIGHT, 3),
        include_top=False,
        weights='imagenet'
    )
    
    # Congelar capas del modelo base
    modelo_base.trainable = False
    
    # Construir modelo completo
    modelo = keras.Sequential([
        modelo_base,
        layers.GlobalAveragePooling2D(),
        layers.Dense(128, activation='relu'),
        layers.Dropout(0.5),
        layers.Dense(NUM_CLASES, activation='softmax')
    ])
    
    # Compilar modelo
    modelo.compile(
        optimizer=keras.optimizers.Adam(learning_rate=0.001),
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    
    return modelo

def crear_dataset_ejemplo():
    """
    ADVERTENCIA: Esto crea un dataset sintético SOLO para demostración.
    Para un sistema real, usar imágenes reales de botellas, latas y basura.
    """
    
    print("[Advertencia] Creando dataset sintético de ejemplo")
    print("[Advertencia] Para producción, usar imágenes reales")
    
    # Generar datos de entrenamiento sintéticos
    num_samples_train = 300
    num_samples_val = 60
    
    # Entrenamiento
    X_train = np.random.rand(num_samples_train, IMG_WIDTH, IMG_HEIGHT, 3)
    y_train = keras.utils.to_categorical(
        np.random.randint(0, NUM_CLASES, num_samples_train),
        NUM_CLASES
    )
    
    # Validación
    X_val = np.random.rand(num_samples_val, IMG_WIDTH, IMG_HEIGHT, 3)
    y_val = keras.utils.to_categorical(
        np.random.randint(0, NUM_CLASES, num_samples_val),
        NUM_CLASES
    )
    
    return (X_train, y_train), (X_val, y_val)

def cargar_dataset_real(directorio_data):
    """
    Cargar dataset real desde estructura de directorios:
    
    data/
    ├── train/
    │   ├── botella/
    │   │   ├── img1.jpg
    │   │   └── img2.jpg
    │   ├── lata/
    │   └── basura/
    └── validation/
        ├── botella/
        ├── lata/
        └── basura/
    """
    
    if not os.path.exists(directorio_data):
        print(f"[Error] Directorio {directorio_data} no existe")
        return None
    
    # Preprocesamiento de imágenes
    data_augmentation = keras.Sequential([
        layers.RandomFlip("horizontal"),
        layers.RandomRotation(0.2),
        layers.RandomZoom(0.2),
    ])
    
    # Generadores de datos
    train_ds = keras.preprocessing.image_dataset_from_directory(
        os.path.join(directorio_data, 'train'),
        image_size=(IMG_WIDTH, IMG_HEIGHT),
        batch_size=32,
        label_mode='categorical'
    )
    
    val_ds = keras.preprocessing.image_dataset_from_directory(
        os.path.join(directorio_data, 'validation'),
        image_size=(IMG_WIDTH, IMG_HEIGHT),
        batch_size=32,
        label_mode='categorical'
    )
    
    # Aplicar data augmentation solo a entrenamiento
    train_ds = train_ds.map(lambda x, y: (data_augmentation(x, training=True), y))
    
    # Optimización de rendimiento
    AUTOTUNE = tf.data.AUTOTUNE
    train_ds = train_ds.cache().prefetch(buffer_size=AUTOTUNE)
    val_ds = val_ds.cache().prefetch(buffer_size=AUTOTUNE)
    
    return train_ds, val_ds

def entrenar_modelo(usar_dataset_real=False, directorio_data='data'):
    """
    Entrenar modelo de clasificación
    """
    
    print("=" * 70)
    print("ENTRENAMIENTO DE MODELO ECO-RVM")
    print("=" * 70)
    
    # Crear modelo
    print("\n[1] Creando arquitectura del modelo...")
    modelo = crear_modelo()
    modelo.summary()
    
    # Cargar datos
    print("\n[2] Cargando datos...")
    
    if usar_dataset_real and os.path.exists(directorio_data):
        print(f"    Cargando dataset real desde {directorio_data}")
        dataset = cargar_dataset_real(directorio_data)
        if dataset:
            train_ds, val_ds = dataset
        else:
            print("    Fallback a dataset sintético")
            (X_train, y_train), (X_val, y_val) = crear_dataset_ejemplo()
            train_ds = None
    else:
        (X_train, y_train), (X_val, y_val) = crear_dataset_ejemplo()
        train_ds = None
    
    # Callbacks
    callbacks = [
        keras.callbacks.EarlyStopping(
            monitor='val_loss',
            patience=5,
            restore_best_weights=True
        ),
        keras.callbacks.ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=3
        ),
        keras.callbacks.ModelCheckpoint(
            'modelo_reciclaje_checkpoint.h5',
            monitor='val_accuracy',
            save_best_only=True
        )
    ]
    
    # Entrenar
    print(f"\n[3] Entrenando modelo por {EPOCHS} épocas...")
    
    if train_ds:
        history = modelo.fit(
            train_ds,
            validation_data=val_ds,
            epochs=EPOCHS,
            callbacks=callbacks
        )
    else:
        history = modelo.fit(
            X_train, y_train,
            validation_data=(X_val, y_val),
            epochs=EPOCHS,
            batch_size=32,
            callbacks=callbacks
        )
    
    # Guardar modelo final
    print("\n[4] Guardando modelo...")
    modelo.save('modelo_reciclaje.h5')
    print("    Modelo guardado como: modelo_reciclaje.h5")
    
    # Métricas finales
    print("\n[5] Métricas finales:")
    print(f"    Precisión entrenamiento: {history.history['accuracy'][-1]:.4f}")
    print(f"    Precisión validación: {history.history['val_accuracy'][-1]:.4f}")
    
    print("\n" + "=" * 70)
    print("ENTRENAMIENTO COMPLETADO")
    print("=" * 70)
    
    return modelo, history

def main():
    """
    Punto de entrada principal
    """
    
    print("\nOPCIONES DE ENTRENAMIENTO:")
    print("1. Dataset sintético (para pruebas rápidas)")
    print("2. Dataset real desde directorio 'data/'")
    print()
    
    opcion = input("Seleccione opción (1 o 2): ").strip()
    
    if opcion == '2':
        if os.path.exists('data'):
            entrenar_modelo(usar_dataset_real=True, directorio_data='data')
        else:
            print("\n[Error] Directorio 'data/' no encontrado")
            print("Cree la estructura:")
            print("  data/train/botella/")
            print("  data/train/lata/")
            print("  data/train/basura/")
            print("  data/validation/botella/")
            print("  data/validation/lata/")
            print("  data/validation/basura/")
    else:
        entrenar_modelo(usar_dataset_real=False)

if __name__ == "__main__":
    main()
