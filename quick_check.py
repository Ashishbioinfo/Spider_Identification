import tensorflow as tf
import os

print("=" * 70)
print("TENSORFLOW & SYSTEM CHECK")
print("=" * 70)

# TensorFlow check
print(f"\nTensorFlow version: {tf.__version__}")
print(f"TensorFlow available: YES")

# Dataset check
dataset_path = 'dataset/spider_images'
if os.path.exists(dataset_path):
    image_count = len([f for f in os.listdir(dataset_path) 
                      if f.lower().endswith(('.jpg', '.png', '.jpeg', '.gif', '.bmp'))])
    print(f"\nDataset path: {dataset_path}")
    print(f"Images found: {image_count}")
    
    if image_count == 0:
        print("\nWARNING: Dataset is empty!")
        print("Add spider images organized by species:")
        print("  dataset/spider_images/")
        print("    Salticidae/")
        print("    Lycosidae/")
        print("    Araneidae/")
        print("    etc...")
else:
    print(f"\nERROR: Dataset path not found: {dataset_path}")

# Model check
model_path = 'model/spider_model.h5'
model_exists = os.path.exists(model_path)
print(f"\nModel file: {model_path}")
print(f"Model exists: {'YES' if model_exists else 'NO - needs training'}")

# Ready to train?
print("\n" + "=" * 70)
if image_count > 0:
    print("READY TO TRAIN: Run 'python train_model_fixed.py'")
else:
    print("NOT READY: Add spider images first, then run training")
print("=" * 70)
