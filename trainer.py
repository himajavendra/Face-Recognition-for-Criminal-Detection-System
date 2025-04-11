import cv2
import os
import numpy as np
from PIL import Image

# Create recognizer and paths
recognizer = cv2.face.LBPHFaceRecognizer_create()
data_path = "dataSet"
save_path = "recognizer/training_data.yml"
os.makedirs("recognizer", exist_ok=True)

def get_images_and_labels(path):
    image_paths = [os.path.join(path, f) for f in os.listdir(path) if f.lower().endswith(('jpg', 'jpeg', 'png'))]
    faces, ids = [], []

    for image_path in image_paths:
        try:
            img = Image.open(image_path).convert('L')  # grayscale
            img_np = np.array(img, 'uint8')

            file_name = os.path.basename(image_path)
            id_str = file_name.split(".")[1]

            if id_str.isdigit():
                ids.append(int(id_str))
                faces.append(img_np)
                print(f"[INFO] Processed {file_name} - ID: {id_str}")
            else:
                print(f"[WARN] Skipping {file_name}: Invalid ID format")
        except Exception as e:
            print(f"[ERROR] Could not process {image_path}: {e}")
    
    return np.array(ids), faces

# Start training
print("[INFO] Loading dataset for training...")
ids, faces = get_images_and_labels(data_path)

if faces:
    recognizer.train(faces, ids)
    recognizer.write(save_path)
    print(f"[SUCCESS] Training complete. Data saved at: {save_path}")
else:
    print("[ERROR] No valid training data found.")

cv2.destroyAllWindows()
