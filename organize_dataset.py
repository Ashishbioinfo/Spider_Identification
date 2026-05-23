import os
import shutil

# Define the target dataset directory relative to this script
TARGET_DIR = os.path.join("dataset", "spider_images")

# Allowed extensions from your Flask app
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}

def organize_images():
    if not os.path.exists(TARGET_DIR):
        print(f"❌ Could not find directory: {os.path.abspath(TARGET_DIR)}")
        return

    print(f"Scanning: {os.path.abspath(TARGET_DIR)}\n")
    
    # Track metrics
    moved_count = 0
    folders_removed = 0

    # Read items inside dataset/spider_images
    for item in os.listdir(TARGET_DIR):
        item_path = os.path.join(TARGET_DIR, item)
        
        # If it's a subfolder (like 'Black Widow'), process it
        if os.path.isdir(item_path):
            folder_name = item
            # Create a clean prefix using underscores instead of spaces
            species_prefix = folder_name.replace(" ", "_")
            
            print(f"Processing folder: '{folder_name}' -> Prefix: '{species_prefix}'")
            
            # Counter for renaming images sequentially
            count = 1
            
            # Loop through files inside the subfolder
            for filename in os.listdir(item_path):
                ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
                
                if ext in ALLOWED_EXTENSIONS:
                    old_file_path = os.path.join(item_path, filename)
                    
                    # Generate the new filename (e.g., Black_Widow_1.jpg)
                    new_filename = f"{species_prefix}_{count}.{ext}"
                    new_file_path = os.path.join(TARGET_DIR, new_filename)
                    
                    # If a file with that name somehow exists, increment until it doesn't
                    while os.path.exists(new_file_path):
                        count += 1
                        new_filename = f"{species_prefix}_{count}.{ext}"
                        new_file_path = os.path.join(TARGET_DIR, new_filename)
                    
                    # Move and rename the file
                    shutil.move(old_file_path, new_file_path)
                    print(f"  └─ Moved & Renamed: {filename} -> {new_filename}")
                    
                    count += 1
                    moved_count += 1
            
            # Clean up the subfolder now that it's empty
            try:
                os.rmdir(item_path)
                print(f"  ✓ Cleaned up empty folder: {folder_name}\n")
                folders_removed += 1
            except OSError:
                print(f"  ⚠️ Could not remove folder '{folder_name}' (it might still contain non-image files).\n")

    print("=" * 40)
    print("🎉 Organization Complete!")
    print(f"Total images organized: {moved_count}")
    print(f"Empty folders removed: {folders_removed}")
    print("=" * 40)

if __name__ == "__main__":
    organize_images()