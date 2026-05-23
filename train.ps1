# Train Spider Model Script for PowerShell
# This script ensures the correct Python environment is used

Write-Host "============================================================"
Write-Host "SPIDER MODEL TRAINER"
Write-Host "============================================================"

# Check if Python is available
Write-Host "`nChecking Python installation..."
python --version
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Python not found in PATH" -ForegroundColor Red
    exit 1
}

# Check if TensorFlow is installed
Write-Host "`nChecking TensorFlow installation..."
python -c "import tensorflow as tf; print('TensorFlow version:', tf.__version__)"
if ($LASTEXITCODE -ne 0) {
    Write-Host "WARNING: TensorFlow installation check failed"
    Write-Host "Installing TensorFlow..." -ForegroundColor Yellow
    pip install tensorflow
}

# Check dataset
Write-Host "`nChecking dataset..."
$imageCount = 0
if (Test-Path "dataset/spider_images") {
    $imageCount = (Get-ChildItem "dataset/spider_images" -Recurse -Include "*.jpg", "*.png", "*.jpeg" | Measure-Object).Count
}
Write-Host "Images found: $imageCount"

if ($imageCount -eq 0) {
    Write-Host "`nWARNING: No spider images found in dataset/spider_images/" -ForegroundColor Yellow
    Write-Host "Add spider images organized by species before training"
}

# Run training
Write-Host "`n============================================================"
Write-Host "Starting training..."
Write-Host "============================================================`n"
python train_model_fixed.py

if ($LASTEXITCODE -ne 0) {
    Write-Host "`nERROR: Training failed!" -ForegroundColor Red
    Write-Host "`nTroubleshooting:" -ForegroundColor Yellow
    Write-Host "1. Check that spider images are in: dataset/spider_images/"
    Write-Host "2. Install TensorFlow: pip install tensorflow"
    Write-Host "3. Run: python train_model_fixed.py"
    exit 1
}

Write-Host "`n============================================================"
Write-Host "Training complete!" -ForegroundColor Green
Write-Host "Model saved to: model/spider_model.h5"
Write-Host "============================================================"
