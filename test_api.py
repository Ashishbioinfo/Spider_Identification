#!/usr/bin/env python3
"""
Test script to verify the model integration is working correctly.
Run this after starting the API server: python test_api.py
"""

import requests
import json
import os
from pathlib import Path

API_URL = "http://localhost:5000"

def test_health():
    """Test health check endpoint"""
    print("\n" + "="*60)
    print("TEST 1: Health Check")
    print("="*60)
    try:
        response = requests.get(f"{API_URL}/api/health")
        print(f"Status: {response.status_code}")
        print(json.dumps(response.json(), indent=2))
        return response.status_code == 200
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_get_species():
    """Test get species endpoint"""
    print("\n" + "="*60)
    print("TEST 2: Get Spider Species")
    print("="*60)
    try:
        response = requests.get(f"{API_URL}/api/spider-species")
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Total species: {data.get('total', 0)}")
        print(f"Species:")
        for species in data.get('species', [])[:5]:  # Show first 5
            print(f"  - {species['name']}")
        if len(data.get('species', [])) > 5:
            print(f"  ... and {len(data['species']) - 5} more")
        return response.status_code == 200
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def find_test_image():
    """Find a test image in the project"""
    # Check dataset folder
    dataset_folders = ['dataset/spider_images', 'dataset/frog_images', 'dataset/snail_images']
    
    for folder in dataset_folders:
        if os.path.exists(folder):
            for file in os.listdir(folder):
                if file.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.gif')):
                    return os.path.join(folder, file)
    
    # Check uploads folder
    if os.path.exists('uploads'):
        for file in os.listdir('uploads'):
            if file.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.gif')):
                return os.path.join('uploads', file)
    
    return None

def test_identify_spider(image_path):
    """Test spider identification endpoint"""
    print("\n" + "="*60)
    print(f"TEST 3: Identify Spider Image")
    print("="*60)
    
    if not os.path.exists(image_path):
        print(f"✗ Image not found: {image_path}")
        return False
    
    try:
        print(f"Using image: {image_path}")
        
        with open(image_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(f"{API_URL}/api/identify-spider-image", files=files)
        
        print(f"Status: {response.status_code}")
        data = response.json()
        
        if data.get('success'):
            print(f"\n✓ Identification Successful!")
            print(f"  Species: {data.get('species')}")
            print(f"  Confidence: {data.get('confidence', 0):.2%}")
            
            # Show all predictions
            if 'all_predictions' in data:
                print(f"\n  All predictions:")
                for pred in data['all_predictions']:
                    print(f"    - {pred['species']}: {pred['confidence']:.2%}")
        else:
            print(f"✗ Identification failed: {data.get('message')}")
        
        print(json.dumps(data, indent=2))
        return response.status_code == 200
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("Spider AI - API Test Suite")
    print(f"Testing: {API_URL}")
    
    results = {}
    
    # Test 1: Health check
    results['health_check'] = test_health()
    
    # Test 2: Get species
    results['get_species'] = test_get_species()
    
    # Test 3: Identify image
    test_image = find_test_image()
    if test_image:
        results['identify_spider'] = test_identify_spider(test_image)
    else:
        print("\n" + "="*60)
        print("TEST 3: Identify Spider Image")
        print("="*60)
        print("⚠ No test image found in dataset or uploads folders")
        results['identify_spider'] = None
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    for test_name, result in results.items():
        if result is True:
            status = "✓ PASSED"
        elif result is False:
            status = "✗ FAILED"
        else:
            status = "⊘ SKIPPED"
        print(f"{test_name:.<40} {status}")
    
    passed = sum(1 for r in results.values() if r is True)
    failed = sum(1 for r in results.values() if r is False)
    skipped = sum(1 for r in results.values() if r is None)
    
    print(f"\nTotal: {passed} passed, {failed} failed, {skipped} skipped")
    
    if failed == 0:
        print("\n✓ All tests passed! API is working correctly.")
        return True
    else:
        print(f"\n✗ {failed} test(s) failed. Check the errors above.")
        return False

if __name__ == "__main__":
    import sys
    
    # Check if requests is installed
    try:
        import requests
    except ImportError:
        print("Error: requests library not installed")
        print("Install it with: pip install requests")
        sys.exit(1)
    
    success = main()
    sys.exit(0 if success else 1)
