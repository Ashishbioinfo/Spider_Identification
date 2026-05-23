import tensorflow as tf
import os

model_path = 'model/spider_model.h5'

print("="*60)
print("MODEL DIAGNOSTIC CHECK")
print("="*60)

if not os.path.exists(model_path):
    print(f"❌ Model file NOT FOUND: {model_path}")
else:
    try:
        model = tf.keras.models.load_model(model_path)
        print(f"✓ Model loaded successfully: {model_path}")
        print(f"\nModel Architecture:")
        print(f"  Input shape: {model.input_shape}")
        print(f"  Output shape: {model.output_shape}")
        print(f"  Total layers: {len(model.layers)}")
        print(f"  Total parameters: {model.count_params():,}")
        
        # Check the output layer
        output_layer = model.layers[-1]
        print(f"\nOutput Layer (Last Layer):")
        print(f"  Type: {output_layer.__class__.__name__}")
        print(f"  Output shape: {output_layer.output_shape}")
        
        # Get weights to determine number of classes
        if hasattr(output_layer, 'units'):
            print(f"  Number of classes (units): {output_layer.units}")
        else:
            print(f"  Units: N/A")
            
    except Exception as e:
        print(f"❌ Error loading model: {e}")

print("\n" + "="*60)
print("DATASET CHECK")
print("="*60)

dataset_folder = 'dataset/spider_images'
if os.path.exists(dataset_folder):
    image_count = len([f for f in os.listdir(dataset_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))])
    print(f"Dataset folder: {dataset_folder}")
    print(f"Images in dataset: {image_count}")
    
    if image_count == 0:
        print("⚠️  WARNING: Dataset is EMPTY! No spider images found.")
        print("\nThis explains why the model always returns the same species!")
        print("\nSOLUTION:")
        print("1. Download spider images (at least 50-100 per species)")
        print("2. Organize them in folders by species name (e.g., Salticidae/, Lycosidae/)")
        print("3. Place them in: dataset/spider_images/")
        print("4. Re-train the model with the actual data")
else:
    print(f"❌ Dataset folder NOT FOUND: {dataset_folder}")

print("\n" + "="*60)
