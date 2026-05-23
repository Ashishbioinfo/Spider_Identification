"""
Spider AI App - Status and Troubleshooting Report
Generated: May 23, 2026
"""

import os
import json

print("\n" + "="*80)
print("SPIDER AI APP - SYSTEM STATUS REPORT")
print("="*80)

# Check dataset
print("\n📁 DATASET STATUS:")
print("-" * 80)
dataset_path = 'dataset/spider_images'
if os.path.exists(dataset_path):
    image_count = len([f for f in os.listdir(dataset_path) 
                      if f.lower().endswith(('.jpg', '.png', '.jpeg', '.gif', '.bmp'))])
    print(f"  Dataset location: {dataset_path}")
    print(f"  Status: {'✓ EXISTS' if os.path.exists(dataset_path) else '❌ MISSING'}")
    print(f"  Images found: {image_count}")
    
    if image_count == 0:
        print("\n  ⚠️  PROBLEM: Dataset is empty!")
        print("  SOLUTION: Add spider images organized by species")
else:
    print(f"  Status: ❌ MISSING ({dataset_path})")

# Check model
print("\n🧠 MODEL STATUS:")
print("-" * 80)
model_path = 'model/spider_model.h5'
print(f"  Model location: {model_path}")
print(f"  Status: {'✓ EXISTS' if os.path.exists(model_path) else '❌ NOT FOUND'}")

if not os.path.exists(model_path):
    print("\n  ⚠️  PROBLEM: Trained model not found!")
    print("  SOLUTION: Train a new model using: python train_model_fixed.py")

# Check class names
class_names_path = 'model/class_names.json'
if os.path.exists(class_names_path):
    with open(class_names_path, 'r') as f:
        classes = json.load(f)
    print(f"  Classes available: {classes}")
else:
    print(f"  Classes file: ❌ NOT FOUND")

# Check API requirements
print("\n⚙️  API REQUIREMENTS:")
print("-" * 80)

requirements = {
    'tensorflow': False,
    'flask': False,
    'flask-cors': False,
    'opencv-python': False,
    'biopython': False,
    'numpy': False
}

try:
    import tensorflow
    requirements['tensorflow'] = True
except:
    pass

try:
    import flask
    requirements['flask'] = True
except:
    pass

try:
    import flask_cors
    requirements['flask-cors'] = True
except:
    pass

try:
    import cv2
    requirements['opencv-python'] = True
except:
    pass

try:
    import Bio
    requirements['biopython'] = True
except:
    pass

try:
    import numpy
    requirements['numpy'] = True
except:
    pass

for pkg, installed in requirements.items():
    status = '✓ INSTALLED' if installed else '❌ MISSING'
    print(f"  {pkg:20s} : {status}")

# Summary
print("\n" + "="*80)
print("ISSUE SUMMARY:")
print("="*80)

issues = []
if not os.path.exists(dataset_path) or \
   len([f for f in os.listdir(dataset_path) if f.lower().endswith(('.jpg', '.png', '.jpeg'))]) == 0:
    issues.append("❌ Dataset is empty - No spider images found")

if not os.path.exists(model_path):
    issues.append("❌ Trained model not found - Model needs to be trained")

missing_packages = [pkg for pkg, installed in requirements.items() if not installed]
if missing_packages:
    issues.append(f"❌ Missing packages: {', '.join(missing_packages)}")

if issues:
    print("\nProblems found:")
    for issue in issues:
        print(f"  {issue}")
else:
    print("\n✓ All systems ready! API should work correctly.")

# Solutions
print("\n" + "="*80)
print("HOW TO FIX:")
print("="*80)

print("\n1️⃣  ADD SPIDER IMAGES:")
print("   - Create folders in dataset/spider_images/ named after spider species")
print("   - Add at least 50-100 images per species")
print("   - Example:")
print("     dataset/spider_images/")
print("     ├── Salticidae/image1.jpg")
print("     ├── Salticidae/image2.jpg")
print("     ├── Lycosidae/image1.jpg")
print("     └── Araneidae/image1.jpg")

print("\n2️⃣  INSTALL MISSING PACKAGES:")
print("   pip install tensorflow flask flask-cors opencv-python biopython")

print("\n3️⃣  TRAIN THE MODEL:")
print("   python train_model_fixed.py")

print("\n4️⃣  RUN THE API:")
print("   python api.py")

print("\n5️⃣  TEST THE API:")
print("   - Navigate to http://localhost:5000 in browser")
print("   - Upload spider image for identification")
print("   - Or use /api/blast-sequence for DNA analysis")

print("\n" + "="*80 + "\n")
