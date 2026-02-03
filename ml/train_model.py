"""
Entrenamiento de Modelo de IA para Eco-RVM
Dataset: TrashNet de Kaggle
Clasificación Binaria: Aceptado (plastic+metal) vs Rechazado (glass+paper+cardboard+trash)
"""

import os
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping, ReduceLROnPlateau
import matplotlib.pyplot as plt
from datetime import datetime

# Configuración del modelo
CONFIG = {
    'DATASET_PATH': 'dataset-resized',
    'IMG_WIDTH': 224,
    'IMG_HEIGHT': 224,
    'BATCH_SIZE': 32,
    'EPOCHS': 50,
    'LEARNING_RATE': 0.001,
    'VALIDATION_SPLIT': 0.2,
    'MODELO_OUTPUT': 'modelo_reciclaje.h5'
}

# Mapeo de clases según lógica de negocio Eco-RVM
MAPEO_CLASES = {
    'plastic': 'aceptado',   # Botellas plásticas, latas de aluminio
    'metal': 'aceptado',     # Latas metálicas
    'glass': 'rechazado',    # Vidrio (peligroso para la máquina)
    'paper': 'rechazado',    # Papel (no se premia)
    'cardboard': 'rechazado', # Cartón (no se premia)
    'trash': 'rechazado'     # Basura general
}

# Clases finales del modelo
CLASES_FINALES = ['rechazado', 'aceptado']


def verificar_estructura_dataset(dataset_path):
    """
    Verificar que exista la estructura correcta del dataset TrashNet
    """
    print("=" * 70)
    print("VERIFICACIÓN DE DATASET")
    print("=" * 70)
    
    if not os.path.exists(dataset_path):
        print(f"[Error] No se encontró la carpeta: {dataset_path}")
        print("\nPor favor, descargue TrashNet de Kaggle y extraiga en:")
        print(f"  {os.path.abspath(dataset_path)}/")
        return False
    
    carpetas_esperadas = ['glass', 'paper', 'cardboard', 'plastic', 'metal', 'trash']
    carpetas_encontradas = []
    
    for carpeta in carpetas_esperadas:
        ruta_carpeta = os.path.join(dataset_path, carpeta)
        if os.path.exists(ruta_carpeta):
            carpetas_encontradas.append(carpeta)
        else:
            print(f"[Advertencia] Carpeta no encontrada: {carpeta}/")
    
    if len(carpetas_encontradas) == 0:
        print("[Error] No se encontraron carpetas del dataset")
        return False
    
    print(f"[OK] Carpetas encontradas: {len(carpetas_encontradas)}/{len(carpetas_esperadas)}")
    return True


def contar_imagenes_por_clase(dataset_path):
    """
    Contar cuántas imágenes hay en cada categoría original y mapeada
    """
    print("\n" + "=" * 70)
    print("ANÁLISIS DE DISTRIBUCIÓN DE DATOS")
    print("=" * 70)
    
    carpetas_originales = ['glass', 'paper', 'cardboard', 'plastic', 'metal', 'trash']
    conteo_original = {}
    conteo_mapeado = {'aceptado': 0, 'rechazado': 0}
    
    print("\n[Conteo por Categoría Original]")
    print("-" * 70)
    
    for carpeta in carpetas_originales:
        ruta_carpeta = os.path.join(dataset_path, carpeta)
        if os.path.exists(ruta_carpeta):
            archivos = [f for f in os.listdir(ruta_carpeta) 
                       if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
            cantidad = len(archivos)
            conteo_original[carpeta] = cantidad
            
            # Mapear a clase final
            clase_mapeada = MAPEO_CLASES.get(carpeta, 'rechazado')
            conteo_mapeado[clase_mapeada] += cantidad
            
            print(f"  {carpeta:12s}: {cantidad:4d} imágenes → [{clase_mapeada.upper()}]")
        else:
            conteo_original[carpeta] = 0
            print(f"  {carpeta:12s}: [NO ENCONTRADA]")
    
    print("\n[Conteo por Clase Final del Modelo]")
    print("-" * 70)
    print(f"  RECHAZADO (0): {conteo_mapeado['rechazado']:4d} imágenes")
    print(f"  ACEPTADO  (1): {conteo_mapeado['aceptado']:4d} imágenes")
    print(f"  TOTAL        : {sum(conteo_mapeado.values()):4d} imágenes")
    
    # Calcular balance de clases
    total = sum(conteo_mapeado.values())
    if total > 0:
        porcentaje_aceptado = (conteo_mapeado['aceptado'] / total) * 100
        porcentaje_rechazado = (conteo_mapeado['rechazado'] / total) * 100
        
        print(f"\n[Balance de Clases]")
        print(f"  RECHAZADO: {porcentaje_rechazado:.1f}%")
        print(f"  ACEPTADO : {porcentaje_aceptado:.1f}%")
        
        # Advertencia si hay desbalance severo
        if porcentaje_aceptado < 30 or porcentaje_aceptado > 70:
            print("\n  [Advertencia] Desbalance de clases detectado")
            print("  Considere usar class_weight durante el entrenamiento")
    
    return conteo_original, conteo_mapeado


def crear_estructura_clases_binarias(dataset_path, output_path='dataset-binario'):
    """
    Reorganizar dataset en estructura binaria: aceptado / rechazado
    """
    print("\n" + "=" * 70)
    print("REORGANIZACIÓN DE DATASET A ESTRUCTURA BINARIA")
    print("=" * 70)
    
    import shutil
    
    # Crear directorios de salida
    for clase in CLASES_FINALES:
        os.makedirs(os.path.join(output_path, clase), exist_ok=True)
    
    # Copiar archivos según mapeo
    for carpeta_origen, clase_destino in MAPEO_CLASES.items():
        ruta_origen = os.path.join(dataset_path, carpeta_origen)
        ruta_destino = os.path.join(output_path, clase_destino)
        
        if not os.path.exists(ruta_origen):
            continue
        
        archivos = [f for f in os.listdir(ruta_origen) 
                   if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        
        print(f"  Copiando {len(archivos)} archivos de {carpeta_origen}/ → {clase_destino}/")
        
        for archivo in archivos:
            # Agregar prefijo para evitar colisiones de nombres
            nuevo_nombre = f"{carpeta_origen}_{archivo}"
            shutil.copy2(
                os.path.join(ruta_origen, archivo),
                os.path.join(ruta_destino, nuevo_nombre)
            )
    
    print(f"\n[OK] Dataset binario creado en: {output_path}/")
    return output_path


def crear_generadores_datos(dataset_path):
    """
    Crear generadores de datos con Data Augmentation específico
    para simular condiciones reales de la caja de reciclaje
    """
    print("\n" + "=" * 70)
    print("CONFIGURACIÓN DE DATA AUGMENTATION")
    print("=" * 70)
    
    # Data Augmentation para entrenamiento
    # Simula condiciones de iluminación variable dentro de la caja
    train_datagen = ImageDataGenerator(
        rescale=1./255,
        validation_split=CONFIG['VALIDATION_SPLIT'],
        rotation_range=40,           # Rotación de objetos
        width_shift_range=0.2,       # Desplazamiento horizontal
        height_shift_range=0.2,      # Desplazamiento vertical
        shear_range=0.2,             # Transformación de corte
        zoom_range=0.2,              # Zoom in/out
        brightness_range=[0.5, 1.5], # Simular oscuridad de la caja
        horizontal_flip=True,        # Espejo horizontal
        fill_mode='nearest'
    )
    
    # Solo rescalado para validación
    val_datagen = ImageDataGenerator(
        rescale=1./255,
        validation_split=CONFIG['VALIDATION_SPLIT']
    )
    
    print("\n[Configuración de Augmentation]")
    print("  - Rotación: ±40 grados")
    print("  - Zoom: ±20%")
    print("  - Shear: ±20%")
    print("  - Brillo: 50% a 150% (simula oscuridad de caja)")
    print("  - Flip horizontal: Sí")
    print("  - Validación: Solo rescalado")
    
    # Generador de entrenamiento
    train_generator = train_datagen.flow_from_directory(
        dataset_path,
        target_size=(CONFIG['IMG_WIDTH'], CONFIG['IMG_HEIGHT']),
        batch_size=CONFIG['BATCH_SIZE'],
        class_mode='binary',  # Clasificación binaria
        subset='training',
        shuffle=True,
        seed=42
    )
    
    # Generador de validación
    validation_generator = val_datagen.flow_from_directory(
        dataset_path,
        target_size=(CONFIG['IMG_WIDTH'], CONFIG['IMG_HEIGHT']),
        batch_size=CONFIG['BATCH_SIZE'],
        class_mode='binary',
        subset='validation',
        shuffle=False,
        seed=42
    )
    
    print(f"\n[Generadores Creados]")
    print(f"  Entrenamiento: {train_generator.samples} imágenes")
    print(f"  Validación: {validation_generator.samples} imágenes")
    print(f"  Clases: {train_generator.class_indices}")
    
    return train_generator, validation_generator


def crear_modelo_cnn():
    """
    Crear modelo CNN con Transfer Learning usando MobileNetV2
    Optimizado para clasificación binaria
    """
    print("\n" + "=" * 70)
    print("CONSTRUCCIÓN DEL MODELO")
    print("=" * 70)
    
    # Modelo base pre-entrenado
    base_model = keras.applications.MobileNetV2(
        input_shape=(CONFIG['IMG_WIDTH'], CONFIG['IMG_HEIGHT'], 3),
        include_top=False,
        weights='imagenet'
    )
    
    # Congelar capas del modelo base
    base_model.trainable = False
    
    # Construir modelo completo
    modelo = keras.Sequential([
        base_model,
        layers.GlobalAveragePooling2D(),
        layers.Dropout(0.3),
        layers.Dense(128, activation='relu'),
        layers.Dropout(0.5),
        layers.Dense(1, activation='sigmoid')  # Salida binaria
    ], name='EcoRVM_Classifier')
    
    # Compilar modelo
    modelo.compile(
        optimizer=keras.optimizers.Adam(learning_rate=CONFIG['LEARNING_RATE']),
        loss='binary_crossentropy',
        metrics=['accuracy', keras.metrics.Precision(), keras.metrics.Recall()]
    )
    
    print("\n[Arquitectura del Modelo]")
    print(f"  Base: MobileNetV2 (ImageNet)")
    print(f"  Capa Dense: 128 neuronas + ReLU")
    print(f"  Salida: 1 neurona + Sigmoid (binario)")
    print(f"  Optimizador: Adam (lr={CONFIG['LEARNING_RATE']})")
    print(f"  Loss: Binary Crossentropy")
    
    return modelo


def entrenar_modelo(train_gen, val_gen):
    """
    Entrenar el modelo con callbacks
    """
    print("\n" + "=" * 70)
    print("ENTRENAMIENTO DEL MODELO")
    print("=" * 70)
    
    # Crear modelo
    modelo = crear_modelo_cnn()
    
    # Callbacks
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    callbacks = [
        ModelCheckpoint(
            filepath=f'modelo_checkpoint_{timestamp}.h5',
            monitor='val_accuracy',
            save_best_only=True,
            verbose=1
        ),
        EarlyStopping(
            monitor='val_loss',
            patience=8,
            restore_best_weights=True,
            verbose=1
        ),
        ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=4,
            min_lr=1e-7,
            verbose=1
        )
    ]
    
    # Calcular steps
    steps_per_epoch = train_gen.samples // CONFIG['BATCH_SIZE']
    validation_steps = val_gen.samples // CONFIG['BATCH_SIZE']
    
    print(f"\n[Configuración de Entrenamiento]")
    print(f"  Épocas: {CONFIG['EPOCHS']}")
    print(f"  Batch size: {CONFIG['BATCH_SIZE']}")
    print(f"  Steps por época: {steps_per_epoch}")
    print(f"  Validation steps: {validation_steps}")
    print("\n[Iniciando entrenamiento...]")
    print("-" * 70)
    
    # Entrenar
    history = modelo.fit(
        train_gen,
        steps_per_epoch=steps_per_epoch,
        epochs=CONFIG['EPOCHS'],
        validation_data=val_gen,
        validation_steps=validation_steps,
        callbacks=callbacks,
        verbose=1
    )
    
    return modelo, history


def guardar_modelo_final(modelo, nombre_archivo):
    """
    Guardar modelo entrenado
    """
    modelo.save(nombre_archivo)
    print(f"\n[OK] Modelo guardado como: {nombre_archivo}")
    
    # Guardar también en formato TFLite para optimización
    try:
        converter = tf.lite.TFLiteConverter.from_keras_model(modelo)
        tflite_model = converter.convert()
        
        nombre_tflite = nombre_archivo.replace('.h5', '.tflite')
        with open(nombre_tflite, 'wb') as f:
            f.write(tflite_model)
        
        print(f"[OK] Modelo TFLite guardado: {nombre_tflite}")
    except Exception as e:
        print(f"[Advertencia] No se pudo generar TFLite: {e}")


def visualizar_metricas(history):
    """
    Graficar métricas de entrenamiento
    """
    print("\n[Generando gráficas de métricas...]")
    
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    
    # Accuracy
    axes[0, 0].plot(history.history['accuracy'], label='Train')
    axes[0, 0].plot(history.history['val_accuracy'], label='Validation')
    axes[0, 0].set_title('Accuracy')
    axes[0, 0].set_xlabel('Época')
    axes[0, 0].set_ylabel('Accuracy')
    axes[0, 0].legend()
    axes[0, 0].grid(True)
    
    # Loss
    axes[0, 1].plot(history.history['loss'], label='Train')
    axes[0, 1].plot(history.history['val_loss'], label='Validation')
    axes[0, 1].set_title('Loss')
    axes[0, 1].set_xlabel('Época')
    axes[0, 1].set_ylabel('Loss')
    axes[0, 1].legend()
    axes[0, 1].grid(True)
    
    # Precision
    axes[1, 0].plot(history.history['precision'], label='Train')
    axes[1, 0].plot(history.history['val_precision'], label='Validation')
    axes[1, 0].set_title('Precision')
    axes[1, 0].set_xlabel('Época')
    axes[1, 0].set_ylabel('Precision')
    axes[1, 0].legend()
    axes[1, 0].grid(True)
    
    # Recall
    axes[1, 1].plot(history.history['recall'], label='Train')
    axes[1, 1].plot(history.history['val_recall'], label='Validation')
    axes[1, 1].set_title('Recall')
    axes[1, 1].set_xlabel('Época')
    axes[1, 1].set_ylabel('Recall')
    axes[1, 1].legend()
    axes[1, 1].grid(True)
    
    plt.tight_layout()
    plt.savefig('metricas_entrenamiento.png', dpi=150)
    print("[OK] Gráficas guardadas en: metricas_entrenamiento.png")
    plt.close()


def main():
    """
    Flujo principal de entrenamiento
    """
    print("\n" + "=" * 70)
    print("ECO-RVM - ENTRENAMIENTO DE MODELO DE IA")
    print("Dataset: TrashNet")
    print("Clasificación: Binaria (Aceptado vs Rechazado)")
    print("=" * 70)
    
    # Verificar dataset
    if not verificar_estructura_dataset(CONFIG['DATASET_PATH']):
        return
    
    # Contar imágenes
    contar_imagenes_por_clase(CONFIG['DATASET_PATH'])
    
    # Reorganizar dataset a estructura binaria
    dataset_binario = crear_estructura_clases_binarias(CONFIG['DATASET_PATH'])
    
    # Crear generadores de datos
    train_gen, val_gen = crear_generadores_datos(dataset_binario)
    
    # Entrenar modelo
    modelo, history = entrenar_modelo(train_gen, val_gen)
    
    # Guardar modelo final
    guardar_modelo_final(modelo, CONFIG['MODELO_OUTPUT'])
    
    # Visualizar métricas
    visualizar_metricas(history)
    
    # Resumen final
    print("\n" + "=" * 70)
    print("ENTRENAMIENTO COMPLETADO")
    print("=" * 70)
    print(f"Accuracy final (validación): {history.history['val_accuracy'][-1]:.4f}")
    print(f"Precision final: {history.history['val_precision'][-1]:.4f}")
    print(f"Recall final: {history.history['val_recall'][-1]:.4f}")
    print(f"\nModelo listo para usar en main_controller.py")
    print("=" * 70)


if __name__ == "__main__":
    main()
