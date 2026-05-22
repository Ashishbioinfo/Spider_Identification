#!/usr/bin/env python3
"""
Helper script to download model from Google Drive and setup the model folder.
Usage: python setup_model.py
"""

import os
import sys
from pathlib import Path

def create_model_folder():
    """Create the model folder if it doesn't exist"""
    model_dir = Path('model')
    model_dir.mkdir(exist_ok=True)
    print(f"✓ Model folder ready: {model_dir.absolute()}")
    return model_dir

def check_model_file():
    """Check if model file exists"""
    model_path = Path('model/spider_model.h5')
    if model_path.exists():
        size_mb = model_path.stat().st_size / (1024 * 1024)
        print(f"✓ Model found: {model_path.absolute()} ({size_mb:.1f} MB)")
        return True
    else:
        print(f"⚠ Model not found at: {model_path.absolute()}")
        return False

def download_from_google_drive(file_id, output_path):
    """Download file from Google Drive"""
    try:
        import gdown
        print(f"Downloading model from Google Drive...")
        gdown.download(f'https://drive.google.com/uc?id={file_id}', output_path, quiet=False)
        print(f"✓ Model downloaded to {output_path}")
        return True
    except ImportError:
        print("⚠ gdown not installed. Run: pip install gdown")
        return False
    except Exception as e:
        print(f"✗ Error downloading: {e}")
        return False

def manual_setup_instructions():
    """Print manual setup instructions"""
    print("\n" + "="*60)
    print("MANUAL SETUP INSTRUCTIONS")
    print("="*60)
    print("\n1. In Google Colab, export your model:")
    print("   model.save('spider_model.h5')")
    print("\n2. Download the model:")
    print("   from google.colab import files")
    print("   files.download('spider_model.h5')")
    print("\n3. Place the file in the 'model' folder:")
    print(f"   {os.path.abspath('model/spider_model.h5')}")
    print("\n4. Run the API:")
    print("   python api.py")
    print("="*60 + "\n")

def main():
    print("Spider AI - Model Setup Helper\n")
    
    # Create model folder
    create_model_folder()
    
    # Check if model exists
    if check_model_file():
        print("\n✓ Setup complete! Ready to run the API.")
        print("  Run: python api.py")
        return True
    
    # Offer download options
    print("\n" + "-"*60)
    print("Options to add your model:")
    print("-"*60)
    print("1. Download from Google Drive (requires file ID)")
    print("2. Manual download (Colab → download → move to model/)")
    print("3. Skip (add manually later)")
    
    choice = input("\nSelect option (1-3): ").strip()
    
    if choice == "1":
        file_id = input("Enter Google Drive file ID: ").strip()
        if file_id:
            download_from_google_drive(file_id, 'model/spider_model.h5')
    elif choice == "2":
        manual_setup_instructions()
    
    # Final check
    if check_model_file():
        print("\n✓ Model setup complete!")
        print("  Run: python api.py")
        return True
    else:
        print("\n⚠ Model still not found.")
        manual_setup_instructions()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
