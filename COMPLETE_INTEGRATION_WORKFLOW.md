# Complete Integration Workflow

## Overview Flow

```
Google Colab (Model Training)
    ↓
Export as spider_model.h5
    ↓
Download to local machine
    ↓
Place in model/ folder
    ↓
Run api.py
    ↓
Upload image via API/Frontend
    ↓
API preprocesses image
    ↓
Model makes prediction
    ↓
Return species + confidence
```

---

## Complete Setup Checklist

### Step 1: Google Colab - Export Your Model ✓

**In your Colab notebook (at the end):**

```python
# Your trained model variable (e.g., 'model')
print("Model Architecture:")
model.summary()

# Save the model
print("\nSaving model...")
model.save('spider_model.h5')
print("✓ Model saved as spider_model.h5")

# Download it
from google.colab import files
print("\nDownloading spider_model.h5...")
files.download('spider_model.h5')
print("✓ Download started")
```

### Step 2: Local Machine - Organize Files ✓

Your project structure should look like:

```
spider-ai-app/
├── model/
│   └── spider_model.h5          ← Your downloaded model
├── dataset/
│   ├── spider_images/           ← Must exist with spider images
│   ├── frog_images/
│   └── snail_images/
├── frontend/
│   ├── index.html
│   ├── script.js
│   └── style.css
├── uploads/                     ← Created automatically
├── api.py                       ← Updated API
├── requirements.txt             ← Updated with TensorFlow
├── setup_model.py              ← Helper script
├── test_api.py                 ← Test script
├── COLAB_INTEGRATION_GUIDE.md  ← Detailed guide
└── MODEL_INTEGRATION_SUMMARY.md ← Quick reference
```

### Step 3: Install Dependencies ✓

```bash
pip install -r requirements.txt
```

This installs:
- Flask 2.3.2
- TensorFlow 2.13.0 (your model)
- OpenCV 4.8.0.76 (image processing)
- Other required packages

### Step 4: Start API Server ✓

```bash
python api.py
```

**Expected output:**
```
Starting Spider AI API Server...

==================================================
Initializing Model...
==================================================
Loading dataset images...
Spider species classes: ['Frog', 'Garden Spider', 'Jumping Spider', 'Snail', 'Wolf Spider']
Total classes: 5

✓ Model loaded successfully from model/spider_model.h5
  Model input shape: (None, 224, 224, 3)

✓ All systems ready!

==================================================
Available endpoints:
==================================================
  POST /api/identify-spider-image - Upload image to identify spider
  GET /api/spider-species - Get all spider species
  GET /api/health - Health check

Server running on http://localhost:5000
```

### Step 5: Test the Integration ✓

**Option A: Using the test script**
```bash
python test_api.py
```

**Option B: Using curl**
```bash
# Test with image file
curl -X POST -F "file=@dataset/spider_images/jumping_spider_1.jpg" \
  http://localhost:5000/api/identify-spider-image

# Get available species
curl http://localhost:5000/api/spider-species

# Health check
curl http://localhost:5000/api/health
```

**Option C: Using the web frontend**
1. Open `frontend/index.html` in your browser
2. Upload a spider image
3. See the identification result

---

## API Response Structure

### Success Response (200 OK)
```json
{
  "success": true,
  "species": "Jumping Spider",
  "confidence": 0.9847,
  "all_predictions": [
    {
      "species": "Jumping Spider",
      "confidence": 0.9847
    },
    {
      "species": "Wolf Spider",
      "confidence": 0.0148
    },
    {
      "species": "Garden Spider",
      "confidence": 0.0005
    }
  ],
  "message": "Spider identified successfully"
}
```

### Error Response (4xx/5xx)
```json
{
  "success": false,
  "message": "Detailed error message explaining what went wrong"
}
```

---

## Key Configuration Points

### 1. Image Input Size

Your model expects a specific input size (default: 224×224).

**To check your model's expected size:**
```python
# In Colab
print(model.input_shape)  # Should show (None, height, width, 3)
```

**If different, update api.py:**
```python
# Line ~95
def preprocess_image(image_path, target_size=(224, 224)):  # ← Change this
    # target_size = (256, 256) if your model expects 256×256
    # target_size = (299, 299) if your model expects 299×299
```

### 2. Normalization

Current normalization: **pixel values 0-1** (dividing by 255)

**If your model used different normalization:**
```python
# Current (in api.py, line ~110):
img = img.astype('float32') / 255.0  # Normalize to 0-1

# Alternative - ImageNet normalization:
mean = np.array([0.485, 0.456, 0.406])
std = np.array([0.229, 0.224, 0.225])
img = (img - mean) / std

# Alternative - if Colab used different range:
img = img / 127.5 - 1.0  # Normalize to -1 to 1
```

### 3. Class Order

The API maps class indices to species names from the `dataset/` folder.

**Class assignment order:**
1. List all images in `dataset/spider_images/` folder
2. Extract species names from filenames
3. Sort alphabetically
4. Index 0 = first species, Index 1 = second, etc.

**Example:**
```
Files: garden_spider_1.jpg, jumping_spider_2.jpg, wolf_spider_1.jpg

Classes after sorting:
  Index 0: "Garden Spider"
  Index 1: "Jumping Spider"  
  Index 2: "Wolf Spider"
```

---

## Troubleshooting Common Issues

### Issue 1: "Model not loaded"
```
Error: Model not loaded. Please ensure the model file exists
```

**Solution:**
```bash
# Check file exists
ls -la model/spider_model.h5  # Linux/Mac
dir model\spider_model.h5     # Windows

# If missing, re-download from Google Colab
# File must be named exactly: spider_model.h5
# Location must be: project_root/model/spider_model.h5
```

### Issue 2: "Class shape mismatch"
```
Error: Model predictions have 3 classes but found 5 in dataset
```

**Solution:**
Make sure your training data matches your dataset folder:
- If model was trained on 3 classes (spider, frog, snail)
- But dataset folder has 5 folders
- Your model will have 3 output classes, not 5

**Fix:** Either:
- Train model with all dataset classes
- Remove unused class folders from dataset/
- Manually specify classes in api.py

### Issue 3: "Wrong input size"
```
Error: Incompatible shape [1, 224, 224, 3] vs [1, 256, 256, 3]
```

**Solution:**
Check model's expected input:
```python
# In api.py, change target_size to match your model
def preprocess_image(image_path, target_size=(256, 256)):  # Change 224 to 256
```

### Issue 4: "No module named tensorflow"
```
ModuleNotFoundError: No module named 'tensorflow'
```

**Solution:**
```bash
# Install TensorFlow
pip install tensorflow==2.13.0

# Or reinstall all requirements
pip install -r requirements.txt --upgrade
```

### Issue 5: "Low confidence scores"
```
Problem: Model always returns low confidence (e.g., 0.2 confidence)
```

**Possible causes:**
1. Model not properly trained
2. Wrong preprocessing (normalization mismatch)
3. Image size mismatch
4. Input colors (RGB vs BGR) issue

**Check:**
```python
# In Colab, verify preprocessing matches:
# 1. Image size during training
# 2. Normalization method during training
# 3. Color space (RGB or BGR)

# Then update api.py to match exactly
```

---

## Advanced: Custom Model Variations

### Using PyTorch Model

If you trained with PyTorch instead:

```python
# Instead of Keras loading:
import torch

MODEL = torch.load('model/spider_model.pth')
MODEL.eval()

# Then use in predictions:
import torchvision.transforms as transforms
transform = transforms.Compose([...])
img_tensor = transform(processed_image)
predictions = MODEL(img_tensor)
```

### Using SavedModel Format

If exported as SavedModel:

```python
# Instead of:
MODEL = keras.models.load_model(MODEL_PATH)

# Use:
MODEL = keras.models.load_model(MODEL_PATH)  # Still works
# Or
loaded = tf.saved_model.load(MODEL_PATH)
infer = loaded.signatures["serving_default"]
```

---

## Performance Notes

- **Model Load Time**: Depends on model size (typically 2-10 seconds)
- **Prediction Time**: ~0.1-0.5 seconds per image
- **Memory Usage**: Depends on model (usually 100-500 MB)

For large models (>1GB), consider:
- Model quantization (reduce size 4x)
- Model pruning (remove unnecessary layers)
- Storing on cloud and downloading on demand

---

## Next Steps After Integration

1. ✅ Integrate Colab model with API (you're here!)
2. 📊 Monitor prediction accuracy with test images
3. 🔄 Fine-tune preprocessing if needed
4. 🚀 Deploy to production (Heroku, AWS, Google Cloud, etc.)
5. 📱 Add mobile support
6. 🎨 Enhance frontend UI

---

## Support & Questions

- **API not starting?** Check error logs in terminal
- **Model loading failed?** Verify file path and format
- **Wrong predictions?** Check preprocessing matches training
- **Need more help?** See `COLAB_INTEGRATION_GUIDE.md`

---

**Last Updated:** 2026-05-09
**Integration Status:** ✅ Complete and Ready
