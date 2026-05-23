"""
Spider Species Classification Model Training Script
This script trains a MobileNetV2-based neural network to identify spider species
from images.
"""

import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt
import os
from pathlib import Path
import json

# Configuration
IMG_SIZE = (224, 224)
BATCH_SIZE = 32
EPOCHS = 25
DATASET_DIR = 'dataset/spider_images'
MODEL_OUTPUT = 'model/spider_model.h5'
CLASSES_OUTPUT = 'model/class_names.json'

print("="*70)
print("SPIDER SPECIES CLASSIFICATION MODEL TRAINER")
print("="*70)

# Check if dataset exists
if not os.path.exists(DATASET_DIR):
    print(f"\n❌ ERROR: Dataset directory not found: {DATASET_DIR}")
    print("\nTo train the model, you need:")
    print("1. Spider images organized by species in folders:")
    print(f"   {DATASET_DIR}/")
    print("   ├── Salticidae/")
    print("   ├── Lycosidae/")
    print("   ├── Araneidae/")
    print("   └── [other species]/")
    print("\n2. At least 50-100 images per species")
    print("\n3. Supported formats: .jpg, .png, .jpeg, .gif, .bmp")
    exit(1)

# Count images
image_files = list(Path(DATASET_DIR).glob('*/*.jpg')) + \
              list(Path(DATASET_DIR).glob('*/*.png')) + \
              list(Path(DATASET_DIR).glob('*/*.jpeg'))

if len(image_files) == 0:
    print(f"\n❌ ERROR: No images found in {DATASET_DIR}")
    print("\nPlease add spider images organized in subdirectories by species.")
    print(f"\nExample structure:")
    print(f"  {DATASET_DIR}/")
    print(f"  ├── Salticidae/image1.jpg")
    print(f"  ├── Salticidae/image2.jpg")
    print(f"  ├── Lycosidae/image1.jpg")
    print(f"  └── Lycosidae/image2.jpg")
    exit(1)

print(f"\n✓ Found {len(image_files)} spider images in {DATASET_DIR}")

# Load dataset
print("\n📂 Loading dataset...")
try:
    train_ds = tf.keras.preprocessing.image_dataset_from_directory(
        DATASET_DIR,
        image_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        validation_split=0.2,
        subset='training',
        seed=42
    )
    
    val_ds = tf.keras.preprocessing.image_dataset_from_directory(
        DATASET_DIR,
        image_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        validation_split=0.2,
        subset='validation',
        seed=42
    )
    
    class_names = train_ds.class_names
    print(f"✓ Classes found: {class_names}")
    print(f"✓ Number of classes: {len(class_names)}")
    
    # Save class names for API
    os.makedirs('model', exist_ok=True)
    with open(CLASSES_OUTPUT, 'w') as f:
        json.dump(class_names, f, indent=2)
    print(f"✓ Class names saved to {CLASSES_OUTPUT}")
    
except Exception as e:
    print(f"❌ Error loading dataset: {e}")
    exit(1)

# Optimize dataset
AUTOTUNE = tf.data.AUTOTUNE
train_ds = train_ds.prefetch(buffer_size=AUTOTUNE)
val_ds = val_ds.prefetch(buffer_size=AUTOTUNE)

# Data augmentation
print("\n🔧 Setting up data augmentation...")
data_augmentation = tf.keras.Sequential([
    tf.keras.layers.RandomFlip("horizontal"),
    tf.keras.layers.RandomRotation(0.1),
    tf.keras.layers.RandomZoom(0.1),
])

# Normalization
normalization_layer = tf.keras.layers.Rescaling(1./255)

# Build model
print("\n🧠 Building model architecture...")
base_model = tf.keras.applications.MobileNetV2(
    input_shape=(224, 224, 3),
    include_top=False,
    weights='imagenet'
)
base_model.trainable = False  # Freeze pre-trained weights initially

model = tf.keras.Sequential([
    data_augmentation,
    normalization_layer,
    base_model,
    tf.keras.layers.GlobalAveragePooling2D(),
    tf.keras.layers.BatchNormalization(),
    tf.keras.layers.Dense(128, activation='relu'),
    tf.keras.layers.Dropout(0.4),
    tf.keras.layers.Dense(len(class_names), activation='softmax')
])

print("✓ Model architecture created")

# Compile model
print("\n⚙️  Compiling model...")
model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=0.0001),
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

# Callbacks
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau, ModelCheckpoint

early_stop = EarlyStopping(
    monitor='val_loss',
    patience=3,
    restore_best_weights=True
)

reduce_lr = ReduceLROnPlateau(
    monitor='val_loss',
    factor=0.3,
    patience=2,
    min_lr=1e-6
)

model_checkpoint = ModelCheckpoint(
    MODEL_OUTPUT,
    monitor='val_accuracy',
    save_best_only=True,
    mode='max'
)

# Train model
print(f"\n🚀 Training model for {EPOCHS} epochs...")
print("="*70)

history = model.fit(
    train_ds,
    validation_data=val_ds,
    epochs=EPOCHS,
    callbacks=[early_stop, reduce_lr, model_checkpoint],
    verbose=1
)

# Save final model
print(f"\n✓ Training complete! Model saved to {MODEL_OUTPUT}")

# Evaluate on validation set
print("\n📊 Final Evaluation:")
val_loss, val_accuracy = model.evaluate(val_ds, verbose=0)
print(f"  Validation Loss: {val_loss:.4f}")
print(f"  Validation Accuracy: {val_accuracy:.4f} ({val_accuracy*100:.2f}%)")

# Save model
model.save(MODEL_OUTPUT)
print(f"✓ Model saved to {MODEL_OUTPUT}")

print("\n" + "="*70)
print("✅ TRAINING COMPLETE!")
print("="*70)
print(f"Model file: {MODEL_OUTPUT}")
print(f"Classes: {class_names}")
print(f"\nYou can now use the API to identify spider species!")
