"""
Spider Species Classification Model Training Script
This script trains a MobileNetV2-based neural network to identify spider species
from images organized in a flat directory structure.
"""

import tensorflow as tf
import numpy as np
import os
import re
import json
from pathlib import Path

# Configuration
IMG_SIZE = (224, 224)
BATCH_SIZE = 32
EPOCHS = 25
DATASET_DIR = 'dataset/spider_images'
MODEL_OUTPUT = 'model/spider_model.keras'
CLASSES_OUTPUT = 'model/class_names.json'

print("="*70)
print("SPIDER SPECIES CLASSIFICATION MODEL TRAINER (FLAT DIRECTORY MODE)")
print("="*70)

# 1. Check if dataset directory exists
if not os.path.exists(DATASET_DIR):
    print(f"\n❌ ERROR: Dataset directory not found: {DATASET_DIR}")
    print("\nPlease verify your dataset path contains your organized images.")
    exit(1)

# 2. Gather all images directly inside the directory
image_paths = list(Path(DATASET_DIR).glob('*.jpg')) + \
              list(Path(DATASET_DIR).glob('*.png')) + \
              list(Path(DATASET_DIR).glob('*.jpeg')) + \
              list(Path(DATASET_DIR).glob('*.bmp'))

if len(image_paths) == 0:
    print(f"\n❌ ERROR: No images found directly in {DATASET_DIR}")
    print("Ensure your file naming convention looks like: Black_Widow_1.jpg or Salticidae_1.png")
    exit(1)

print(f"\n✓ OK: Found {len(image_paths)} spider images in {DATASET_DIR}")

# 3. Dynamically extract class names from prefixes
discovered_classes = set()
for p in image_paths:
    match = re.match(r"^([a-zA-Z_]+)_\d+", p.name)
    if match:
        discovered_classes.add(match.group(1))
    else:
        discovered_classes.add(p.name.split('_')[0])

class_names = sorted(list(discovered_classes))
print(f"✓ OK: Detected Classes from filenames: {class_names}")
print(f"✓ OK: Number of classes: {len(class_names)}")

if len(class_names) < 2:
    print("\n❌ ERROR: Only one class detected. Neural networks require at least 2 classes to differentiate.")
    exit(1)

os.makedirs('model', exist_ok=True)
with open(CLASSES_OUTPUT, 'w') as f:
    json.dump(class_names, f, indent=2)
print(f"✓ OK: Class names successfully saved to {CLASSES_OUTPUT}")


# 4. Build TensorFlow Pipeline manually to parse flat structures
print("\n[LOADING] Building image streaming dataset...")

def load_and_preprocess_image(path_str):
    img_raw = tf.io.read_file(path_str)
    img_tensor = tf.image.decode_image(img_raw, channels=3, expand_animations=False)
    img_resized = tf.image.resize(img_tensor, IMG_SIZE)
    return img_resized

all_paths = [str(p) for p in image_paths]
all_labels = []
for p in image_paths:
    match = re.match(r"^([a-zA-Z_]+)_\d+", p.name)
    lbl = match.group(1) if match else p.name.split('_')[0]
    all_labels.append(class_names.index(lbl))

path_ds = tf.data.Dataset.from_tensor_slices(all_paths)
image_ds = path_ds.map(load_and_preprocess_image, num_parallel_calls=tf.data.AUTOTUNE)
label_ds = tf.data.Dataset.from_tensor_slices(all_labels)
dataset = tf.data.Dataset.zip((image_ds, label_ds)).shuffle(buffer_size=len(all_paths), seed=42)

DATASET_SIZE = len(all_paths)
train_size = int(0.8 * DATASET_SIZE)

train_ds = dataset.take(train_size)
val_ds = dataset.skip(train_size)

# 5. Data Augmentation (Applied *ONLY* to the training stream pipeline, not the model layers)
print("\n[SETUP] Setting up data augmentation pipeline...")
data_augmentation = tf.keras.Sequential([
    tf.keras.layers.RandomFlip("horizontal"),
    tf.keras.layers.RandomRotation(0.1),
    tf.keras.layers.RandomZoom(0.1),
])

# Augment only training images natively
train_ds = train_ds.map(lambda x, y: (data_augmentation(x, training=True), y), num_parallel_calls=tf.data.AUTOTUNE)

# Batch and optimize streaming setup
train_ds = train_ds.batch(BATCH_SIZE).prefetch(buffer_size=tf.data.AUTOTUNE)
val_ds = val_ds.batch(BATCH_SIZE).prefetch(buffer_size=tf.data.AUTOTUNE)


# 6. Build the Clean Neural Network Architecture
print("\n[SETUP] Initializing MobileNetV2 Base Model...")
normalization_layer = tf.keras.layers.Rescaling(1./255)

base_model = tf.keras.applications.MobileNetV2(
    input_shape=(224, 224, 3),
    include_top=False,
    weights='imagenet'
)
base_model.trainable = False 

model = tf.keras.Sequential([
    normalization_layer,  # Expects raw 0-255 arrays directly from your Flask pipeline
    base_model,
    tf.keras.layers.GlobalAveragePooling2D(),
    tf.keras.layers.BatchNormalization(),
    tf.keras.layers.Dense(128, activation='relu'),
    tf.keras.layers.Dropout(0.4),
    tf.keras.layers.Dense(len(class_names), activation='softmax')
])

print("✓ OK: Model network architecture compiled clean.")


# 7. Compile Model Configurations
print("\n[SETUP] Finalizing model compiling settings...")
model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=0.0001),
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau, ModelCheckpoint

early_stop = EarlyStopping(monitor='val_loss', patience=4, restore_best_weights=True)
reduce_lr = ReduceLROnPlateau(monitor='val_loss', factor=0.3, patience=2, min_lr=1e-6)
model_checkpoint = ModelCheckpoint(MODEL_OUTPUT, monitor='val_accuracy', save_best_only=True, mode='max')


# 8. Start Model Training Fits
print(f"\n[TRAINING] Commencing model optimization across {EPOCHS} Epochs...")
print("="*70)

history = model.fit(
    train_ds,
    validation_data=val_ds,
    epochs=EPOCHS,
    callbacks=[early_stop, reduce_lr, model_checkpoint],
    verbose=1
)

# 9. Output Training Evaluation results
print("\n[RESULTS] Processing Final Model Metrics:")
val_loss, val_accuracy = model.evaluate(val_ds, verbose=0)
print(f"  Validation Evaluation Loss: {val_loss:.4f}")
print(f"  Validation Evaluation Accuracy: {val_accuracy:.4f} ({val_accuracy*100:.2f}%)")

model.save(MODEL_OUTPUT)
print(f"✓ Success: Core weights completely written to -> {MODEL_OUTPUT}")
print("="*70)