from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2
import numpy as np
import os
from pathlib import Path
import json
from werkzeug.utils import secure_filename

# Try to import TensorFlow, but continue if it fails
try:
    import tensorflow as tf
    from tensorflow import keras
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False
    print("⚠ TensorFlow not available - model loading disabled")

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
DATASET_FOLDER = 'dataset/spider_images'
MODEL_PATH = 'model/spider_model.h5'  # Path to your Keras model
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}

# Create uploads folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Global model and spider database
MODEL = None
SPIDER_DATABASE = {}
CLASS_NAMES = []  # Will store spider species names in order

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def load_dataset_images():
    """Load spider species names from dataset folder for class mapping"""
    global CLASS_NAMES
    species_set = set()
    
    if os.path.exists(DATASET_FOLDER):
        for filename in os.listdir(DATASET_FOLDER):
            if allowed_file(filename):
                # Extract species name from filename
                # Expected format: species_name_number.extension
                name_parts = filename.rsplit('.', 1)[0].split('_')
                
                # Remove the trailing number
                if name_parts[-1].isdigit():
                    species_name = ' '.join(name_parts[:-1]).title()
                else:
                    species_name = ' '.join(name_parts).title()
                
                species_set.add(species_name)
    
    CLASS_NAMES = sorted(list(species_set))
    print(f"\nSpider species classes: {CLASS_NAMES}")
    print(f"Total classes: {len(CLASS_NAMES)}")
    return CLASS_NAMES

def load_model_from_disk():
    """Load the Keras model from disk"""
    global MODEL
    
    if not TENSORFLOW_AVAILABLE:
        print("⚠ TensorFlow not available - skipping model load")
        return False
    
    try:
        if os.path.exists(MODEL_PATH):
            MODEL = keras.models.load_model(MODEL_PATH)
            print(f"✓ Model loaded successfully from {MODEL_PATH}")
            print(f"  Model input shape: {MODEL.input_shape}")
            return True
        else:
            print(f"⚠ Model file not found at {MODEL_PATH}")
            print(f"  Expected path: {os.path.abspath(MODEL_PATH)}")
            return False
    except Exception as e:
        print(f"✗ Error loading model: {e}")
        return False

def preprocess_image(image_path, target_size=(224, 224)):
    """Preprocess image for the neural network"""
    try:
        # Read image
        img = cv2.imread(image_path)
        if img is None:
            return None
        
        # Convert BGR to RGB (OpenCV reads in BGR)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Resize to target size
        img = cv2.resize(img, target_size)
        
        # Normalize pixel values to 0-1 range
        img = img.astype('float32') / 255.0
        
        # Add batch dimension [H, W, C] -> [1, H, W, C]
        img = np.expand_dims(img, axis=0)
        
        return img
    except Exception as e:
        print(f"Error preprocessing image: {e}")
        return None


@app.route('/api/identify-spider-image', methods=['POST'])
def identify_spider_image():
    """Identify spider species from uploaded image using the trained neural network"""
    try:
        # Check if TensorFlow is available
        if not TENSORFLOW_AVAILABLE:
            return jsonify({
                'success': False,
                'message': 'TensorFlow not installed. Please install with: pip install tensorflow'
            }), 500
        
        # Check if model is loaded
        if MODEL is None:
            return jsonify({
                'success': False,
                'message': 'Model not loaded. Please ensure the model file exists at: ' + MODEL_PATH
            }), 500
        
        # Check if file is in request
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'message': 'No file part in the request'
            }), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'message': 'No file selected'
            }), 400
        
        if not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'message': 'Invalid file type. Allowed types: ' + ', '.join(ALLOWED_EXTENSIONS)
            }), 400
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        # Preprocess image
        processed_image = preprocess_image(filepath)
        
        if processed_image is None:
            return jsonify({
                'success': False,
                'message': 'Could not process image. Please ensure it is a valid image file.'
            }), 400
        
        # Make prediction
        predictions = MODEL.predict(processed_image, verbose=0)
        
        # Get the class with highest confidence
        predicted_class_idx = np.argmax(predictions[0])
        confidence = float(predictions[0][predicted_class_idx])
        
        # Map class index to spider species name
        if predicted_class_idx < len(CLASS_NAMES):
            species_name = CLASS_NAMES[predicted_class_idx]
        else:
            species_name = "Unknown Spider Species"
        
        # Return result
        return jsonify({
            'success': True,
            'species': species_name,
            'confidence': confidence,
            'all_predictions': [
                {
                    'species': CLASS_NAMES[i],
                    'confidence': float(predictions[0][i])
                }
                for i in range(len(CLASS_NAMES))
            ],
            'message': 'Spider identified successfully'
        })
    
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500

@app.route('/api/spider-species', methods=['GET'])
def get_spider_species():
    """Get list of all spider species the model can identify"""
    species_list = [
        {
            'name': species,
            'scientific_name': species,
            'description': f'Spider species: {species}'
        }
        for species in CLASS_NAMES
    ]
    
    return jsonify({
        'success': True,
        'species': species_list,
        'total': len(species_list)
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'API is running',
        'version': '1.0',
        'endpoints': [
            '/api/identify-spider-image (POST)',
            '/api/spider-species (GET)',
            '/api/health (GET)'
        ]
    })

if __name__ == '__main__':
    print("Starting Spider AI API Server...")
    print("\n" + "="*50)
    print("Initializing Model...")
    print("="*50)
    
    # Load spider species classes from dataset
    load_dataset_images()
    
    # Load the trained model (if TensorFlow is available)
    if TENSORFLOW_AVAILABLE:
        if load_model_from_disk():
            print("\n✓ All systems ready!")
        else:
            print("\n⚠ Warning: Model could not be loaded. Please add your model.h5 file.")
    else:
        print("\n⚠ TensorFlow not installed - API will run in demo mode")
        print("  Install with: pip install tensorflow")
    
    print("\n" + "="*50)
    print("Available endpoints:")
    print("="*50)
    print("  POST /api/identify-spider-image - Upload image to identify spider")
    print("  GET /api/spider-species - Get all spider species")
    print("  GET /api/health - Health check")
    print("\nServer running on http://localhost:5000")
    app.run(debug=True, port=5000)
