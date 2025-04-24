# save_embeddings.py
import os, pickle
from deepface import DeepFace

embeddings = []

for filename in os.listdir("images"):
    if filename.lower().endswith((".jpg", ".jpeg", ".png")):
        path = os.path.join("images", filename)
        try:
            result = DeepFace.represent(img_path=path, model_name="SFace", enforce_detection=False)[0]
            embeddings.append({
                "name": os.path.splitext(filename)[0],
                "embedding": result["embedding"]
            })
        except Exception as e:
            print(f"Error processing {filename}: {e}")

with open("embeddings.pkl", "wb") as f:
    pickle.dump(embeddings, f)

print("✅ Embeddings saved successfully.")
