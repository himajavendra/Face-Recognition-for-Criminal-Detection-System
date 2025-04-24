import cv2
import os
import sqlite3
from deepface import DeepFace

# Paths
DB_PATH = "criminal.db"
FACE_FOLDER = "images/"

# Connect to SQLite database
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Open webcam
cap = cv2.VideoCapture(0)
print("[INFO] Starting webcam... Press 'q' to quit.")

def get_criminal_details(name):
    cursor.execute("SELECT * FROM People WHERE Name = ?", (name,))
    result = cursor.fetchone()
    if result:
        return {
            "ID": result[0],
            "Name": result[1],
            "Gender": result[2],
            "Father": result[3],
            "Mother": result[4],
            "Religion": result[5],
            "Blood Group": result[6],
            "Identification Mark": result[7],
            "Nationality": result[8],
            "Crime": result[9]
        }
    return None

while True:
    ret, frame = cap.read()
    if not ret:
        break

    try:
        # Detect and compare face
        results = DeepFace.find(img_path=frame, db_path=FACE_FOLDER, enforce_detection=False)

        if len(results) > 0 and len(results[0]) > 0:
            identity_path = results[0].iloc[0]["identity"]
            name = os.path.splitext(os.path.basename(identity_path))[0]

            # Fetch full details
            details = get_criminal_details(name)
            if details:
                # Display details on frame
                cv2.putText(frame, f"Name: {details['Name']}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,255,0), 2)
                cv2.putText(frame, f"Crime: {details['Crime']}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,255), 2)
                cv2.putText(frame, f"Nationality: {details['Nationality']}", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,0), 2)
            else:
                cv2.putText(frame, "Match found, but no DB details", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,255), 2)

        else:
            cv2.putText(frame, "No Match Detected", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,255), 2)

    except Exception as e:
        print(f"[ERROR] {e}")

    cv2.imshow("Criminal Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
conn.close()
