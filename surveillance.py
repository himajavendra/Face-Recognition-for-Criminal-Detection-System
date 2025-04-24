import cv2
from deepface import DeepFace
import numpy as np

# Starting camera
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    # Resize the frame (for quicker processing)
    frame_resized = cv2.resize(frame, (640, 480))

    try:
        # Convert frame to RGB for face detection
        detections = DeepFace.extract_faces(frame_resized, detector_backend="mtcnn", enforce_detection=False)
        
        # Iterate over each detected face
        for face_data in detections:
            # Get bounding box coordinates
            x, y, w, h = face_data["facial_area"]["x"], face_data["facial_area"]["y"], face_data["facial_area"]["w"], face_data["facial_area"]["h"]
            # Draw bounding box
            cv2.rectangle(frame_resized, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            # Recognition logic or additional information can go here
            
    except Exception as e:
        print("Error during face detection:", e)
    
    # Show the frame with bounding box
    cv2.imshow("Face Detection", frame_resized)

    # Exit on 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
