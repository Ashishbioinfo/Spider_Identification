@echo off
REM Train Spider Model Script for Windows
REM This script ensures the correct Python environment is used

echo ============================================================
echo SPIDER MODEL TRAINER
echo ============================================================

REM Check if Python is available
python --version
if errorlevel 1 (
    echo ERROR: Python not found in PATH
    exit /b 1
)

REM Check if TensorFlow is installed
echo.
echo Checking TensorFlow installation...
python -c "import tensorflow as tf; print('TensorFlow version:', tf.__version__)"
if errorlevel 1 (
    echo ERROR: TensorFlow not installed
    echo Installing TensorFlow...
    pip install tensorflow
)

REM Check dataset
echo.
echo Checking dataset...
python -c "import os; images = len([f for f in os.listdir('dataset/spider_images') if f.lower().endswith(('.jpg','.png','.jpeg'))]); print(f'Images found: {images}')"

REM Run training
echo.
echo ============================================================
echo Starting training...
echo ============================================================
python train_model_fixed.py

if errorlevel 1 (
    echo.
    echo ERROR: Training failed!
    echo.
    echo Try these solutions:
    echo 1. Check that spider images are in: dataset/spider_images/
    echo 2. Install TensorFlow: pip install tensorflow
    echo 3. Run: python train_model_fixed.py
    exit /b 1
)

echo.
echo ============================================================
echo Training complete!
echo Model saved to: model/spider_model.h5
echo ============================================================
