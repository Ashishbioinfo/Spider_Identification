# Spider AI Identification System

## Setup Instructions

### 1. Adding Your Own Spider Images

Place your spider images in the `dataset/spider_images/` folder with the following naming convention:

**Naming Format:** `species_name_number.extension`

**Examples:**
- `jumping_spider_1.jpg`
- `jumping_spider_2.jpg`
- `wolf_spider_1.jpg`
- `orb_weaver_1.png`
- `huntsman_spider_1.jpg`

### 2. Folder Structure

```
spider-ai-app/
├── frontend/
│   ├── index.html
│   ├── spider.html
│   ├── script.js
│   └── style.css
├── dataset/
│   └── spider_images/           ← Add your images here
│       ├── jumping_spider_1.jpg
│       ├── wolf_spider_1.jpg
│       ├── orb_weaver_1.jpg
│       └── ... (more images)
├── api.py                        ← Backend server
├── requirements.txt
└── README.md
```

### 3. Installation & Running

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the API server:**
   ```bash
   python api.py
   ```

3. **Open the frontend:**
   - Open `frontend/index.html` in your browser
   - Navigate to the Spider Identification page
   - Upload a spider image for identification

### 4. How It Works

- The API loads all images from `dataset/spider_images/` at startup
- Species name is extracted from the filename (e.g., `jumping_spider` → `Jumping Spider`)
- When you upload an image, it's compared against all dataset images using OpenCV feature matching
- The system returns the best matching species with confidence score

### 5. Supported Image Formats

- `.jpg` / `.jpeg`
- `.png`
- `.gif`
- `.bmp`

### 6. Tips for Best Results

- Use clear, well-lit photos of spiders
- Include multiple images per species from different angles
- Ensure at least 500x500 pixel resolution for better feature matching
- More reference images = better accuracy

---

**API Endpoints:**
- `POST /api/identify-spider-image` - Upload image to identify spider
- `GET /api/spider-species` - Get all spider species in database
- `GET /api/health` - Health check
