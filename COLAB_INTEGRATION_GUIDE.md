# Google Colab Model Integration Guide

This guide explains how to integrate your trained Keras/TensorFlow model from Google Colab with the Spider AI application.

## Overview

The updated API now uses a neural network model instead of feature matching. Your `.h5` model file will be loaded on startup and used for spider species classification.

## Step 1: Export Your Model from Google Colab

In your Google Colab notebook, save the model:

```python
# Save the model in .h5 format
model.save('spider_model.h5')

# Then download it
from google.colab import files
files.download('spider_model.h5')
```

## Step 2: Add Model File to Your Project

1. Create a `model` folder in your project root (if it doesn't exist):
   ```
   spider-ai-app/
   ├── model/
   │   └── spider_model.h5
   ├── api.py
   ├── requirements.txt
   └── ...
   ```

2. Place your downloaded `spider_model.h5` file in the `model/` folder

## Step 3: Update Python Dependencies

Install TensorFlow by running:

```bash
pip install -r requirements.txt
```

This will install the required packages including TensorFlow 2.13.0.

## Step 4: Run the API Server

```bash
python api.py
```

The server will:
- Load your spider species classes from the `dataset/` folder structure
- Load your trained model from `model/spider_model.h5`
- Start listening on `http://localhost:5000`

## How It Works

### Image Processing Pipeline

```
User uploads image → Preprocess (resize, normalize) → Model prediction → Return species
```

### Image Preprocessing (Automatic)

The API automatically:
1. Reads the image file
2. Converts BGR (OpenCV format) to RGB
3. Resizes to 224×224 pixels (adjust in code if your model expects different size)
4. Normalizes pixel values to 0-1 range
5. Adds batch dimension for model input

**Note:** If your model expects a different input size, edit the `preprocess_image()` function:

```python
def preprocess_image(image_path, target_size=(224, 224)):  # ← Change this
```

### API Endpoints

#### 1. Identify Spider Image (POST)
```bash
curl -X POST -F "file=@spider_image.jpg" http://localhost:5000/api/identify-spider-image
```

**Response:**
```json
{
  "success": true,
  "species": "Jumping Spider",
  "confidence": 0.95,
  "all_predictions": [
    {"species": "Jumping Spider", "confidence": 0.95},
    {"species": "Wolf Spider", "confidence": 0.04},
    {"species": "Garden Spider", "confidence": 0.01}
  ],
  "message": "Spider identified successfully"
}
```

#### 2. Get Spider Species (GET)
```bash
curl http://localhost:5000/api/spider-species
```

Returns all spider species your model can identify (from dataset folder structure).

#### 3. Health Check (GET)
```bash
curl http://localhost:5000/api/health
```

## Troubleshooting

### Model Not Loading?

**Error:** "Model not loaded. Please ensure the model file exists"

**Solution:**
- Check that `model/spider_model.h5` exists
- Verify the file path is correct
- Check file permissions

### Class Names Not Matching?

**Problem:** Model predictions don't match expected spider species

**Solution:**
The API automatically creates class names from your `dataset/` folder structure:
- Expected format: `species_name_number.extension`
- Example: `jumping_spider_1.jpg`, `wolf_spider_2.jpg`
- The class names are extracted and sorted alphabetically

Ensure your dataset folders have images in this format, or edit `load_dataset_images()` function.

### Different Input Size?

If your model expects input of size 256×256 or other dimensions, modify the preprocess_image function:

```python
# Current (224x224):
def preprocess_image(image_path, target_size=(224, 224)):

# Change to your model's expected size:
def preprocess_image(image_path, target_size=(256, 256)):
```

### Model Input Shape Issues

Check your model's expected input shape:

```python
# In Colab:
print(model.input_shape)  # Should be (None, height, width, 3)
```

If your model uses different preprocessing (e.g., different normalization), edit `preprocess_image()`.

## Advanced: Custom Normalization

If your Colab model used specific preprocessing (e.g., ImageNet normalization):

```python
def preprocess_image(image_path, target_size=(224, 224)):
    # ... existing code ...
    
    # Custom normalization example (ImageNet):
    img = (img - np.array([0.485, 0.456, 0.406])) / np.array([0.229, 0.224, 0.225])
    
    return img
```

## Model File Size Considerations

Large models (>500MB) can be:
- Stored in cloud storage (AWS S3, Google Drive) and downloaded on startup
- Compressed with model quantization
- Split into smaller files and combined on load

For now, keep the model in the local `model/` folder.

## Next Steps

1. ✅ Download model from Colab
2. ✅ Place in `model/spider_model.h5`
3. ✅ Run `pip install -r requirements.txt`
4. ✅ Run `python api.py`
5. ✅ Test with the web frontend in `frontend/index.html`

## Questions?

- Check API logs for detailed error messages
- Verify model was trained with the correct classes matching your dataset
- Ensure image preprocessing in Colab matches the `preprocess_image()` function

---

**Updated API Features:**
- ✨ Uses neural network model instead of feature matching
- ✨ Returns confidence scores for all predictions
- ✨ Automatically loads spider species from dataset structure
- ✨ Handles image preprocessing automatically
