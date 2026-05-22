from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import cv2
import numpy as np
import os
from pathlib import Path
import json
from werkzeug.utils import secure_filename
import time
import xml.etree.ElementTree as ET
from io import StringIO
import math

# Try to import TensorFlow, but continue if it fails
try:
    import tensorflow as tf
    from tensorflow import keras
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False
    print("⚠ TensorFlow not available - model loading disabled")

# Try to import BioPython for NCBI BLAST
try:
    from Bio.Blast import NCBIWWW, NCBIXML
    from Bio import Entrez
    BIOPYTHON_AVAILABLE = True
except ImportError:
    BIOPYTHON_AVAILABLE = False
    print("⚠ BioPython not available - NCBI BLAST disabled")

# Set Entrez email (required by NCBI)
if BIOPYTHON_AVAILABLE:
    Entrez.email = "spider.ai.app@example.com"

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

@app.route('/api/blast-sequence', methods=['POST'])
def blast_sequence():
    """Submit DNA sequence to NCBI BLAST and return top 10 spider species matches"""
    try:
        # Check if BioPython is available
        if not BIOPYTHON_AVAILABLE:
            return jsonify({
                'success': False,
                'message': 'BioPython not installed. Please install with: pip install biopython'
            }), 500
        
        # Get DNA sequence from request
        data = request.get_json()
        if not data or 'sequence' not in data:
            return jsonify({
                'success': False,
                'message': 'No DNA sequence provided'
            }), 400
        
        sequence = data['sequence'].strip()
        
        # Validate sequence
        if not sequence or len(sequence) < 50:
            return jsonify({
                'success': False,
                'message': 'DNA sequence too short (minimum 50 bp)'
            }), 400
        
        # Remove whitespace and validate it contains only ATGCN
        sequence = ''.join(sequence.split())
        valid_bases = set('ATGCNATGCN')
        if not all(base.upper() in valid_bases for base in sequence):
            return jsonify({
                'success': False,
                'message': 'Invalid DNA sequence. Contains non-DNA characters.'
            }), 400
        
        print(f"Submitting {len(sequence)} bp sequence to NCBI BLAST...")
        
        try:
            # Submit sequence to NCBI BLAST (nucleotide database, blastn)
            # Using nucleotide BLAST (blastn) for spider DNA queries
            result_handle = NCBIWWW.qblast(
                "blastn",                    # Program: nucleotide search
                "nt",                        # Database: nucleotide database
                sequence,
                expect=1e-6,                 # E-value threshold
                format_type="XML"
            )
            
            # Parse BLAST results
            blast_results = NCBIXML.read(result_handle)
            
            # Extract top 10 spider matches
            matches = []
            seen_species = set()
            
            for alignment in blast_results.alignments:
                # Extract species name from NCBI description
                description = alignment.title
                
                # Parse description to extract species
                # Format is typically: "gi|...|...|species_name other info"
                parts = description.split('|')
                species_info = parts[-1] if parts else description
                
                # Clean up the species name
                species_name = species_info.strip()
                
                # Filter for spider-related hits
                spider_keywords = ['spider', 'arachnida', 'araneae', 'salticidae', 
                                 'lycosidae', 'araneidae', 'linyphiidae', 'thomisidae']
                is_spider = any(keyword in species_name.lower() for keyword in spider_keywords)
                
                # Get HSP (High Scoring Pair) information
                for hsp in alignment.hsps:
                    # Skip if we've already added this species
                    if species_name in seen_species:
                        continue
                    
                    if len(matches) >= 10:
                        break
                    
                    # Calculate match score (percent identity)
                    identities = hsp.identities
                    align_length = hsp.align_length
                    percent_identity = (identities / align_length * 100) if align_length > 0 else 0
                    
                    # Calculate e-value score (lower is better, convert to confidence)
                    e_value = hsp.expect
                    # Convert e-value to confidence: higher confidence for lower e-values
                    confidence = max(0, min(100, 100 - (math.log10(max(e_value, 1e-180)) + 180)))
                    
                    match = {
                        'species': species_name,
                        'accession': alignment.accession,
                        'description': description,
                        'percent_identity': round(percent_identity, 2),
                        'align_length': align_length,
                        'identities': identities,
                        'e_value': float(e_value),
                        'confidence': round(confidence, 2),
                        'bit_score': round(hsp.bits, 2),
                        'ncbi_url': f"https://www.ncbi.nlm.nih.gov/protein/{alignment.accession}"
                    }
                    
                    matches.append(match)
                    seen_species.add(species_name)
                
                if len(matches) >= 10:
                    break
            
            # If we have fewer than 10 results, it's still valid
            if not matches:
                return jsonify({
                    'success': False,
                    'message': 'No spider sequences found in NCBI BLAST results'
                }), 404
            
            return jsonify({
                'success': True,
                'matches': matches,
                'total_matches': len(matches),
                'sequence_length': len(sequence),
                'message': f'Found {len(matches)} matching spider sequences'
            })
        
        except Exception as blast_error:
            print(f"NCBI BLAST Error: {str(blast_error)}")
            return jsonify({
                'success': False,
                'message': f'NCBI BLAST Error: {str(blast_error)}'
            }), 500
    
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'API is running',
        'version': '1.0',
        'endpoints': [
            '/api/identify-spider-image (POST)',
            '/api/spider-species (GET)',
            '/api/blast-sequence (POST)',
            '/api/health (GET)'
        ]
    })

@app.route('/', methods=['GET'])
def serve_frontend():
    """Serve the frontend index.html"""
    return send_from_directory('frontend', 'index.html')

@app.route('/<path:path>', methods=['GET'])
def serve_static(path):
    """Serve static files from frontend folder"""
    return send_from_directory('frontend', path)

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
    print("  POST /api/blast-sequence - NCBI BLAST DNA sequence analysis")
    print("  GET /api/health - Health check")
    
    # Get port from environment variable (Render provides this)
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV', 'development') == 'development'
    
    print(f"\nServer running on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)
