import os
import cv2
import sqlite3
import winsound
import threading
import tkinter as tk
from tkinter import ttk, messagebox, Label, LabelFrame
from PIL import Image, ImageTk
import face_recognition

# ------------------ THEME -------------------
THEME = {
    "bg": "#1A1A40",
    "header_bg": "#2F4F4F",
    "button_bg": "#36454F",
    "accent": "#B22222",
    "success": "#2ECC71",
    "text_dark": "white",
    "text_light": "#FAFAFA",
    "hover": "#0D1B2A"
}

class SurveillanceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Criminal Surveillance System")
        self.root.geometry("1350x720")
        self.root.configure(bg=THEME["bg"])
        self.root.state("zoomed")

        self.db_path = "criminal.db"
        self.image_dir = "images"
        self.video_running = False
        self.detected_ids = set()

        self.known_face_encodings = []
        self.known_face_ids = []

        self.load_known_faces()
        self.setup_ui()

    def load_known_faces(self):
        """Load all faces from images and map to ID."""
        for filename in os.listdir(self.image_dir):
            if filename.startswith("user.") and filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                try:
                    id_str = filename.split('.')[1]
                    face_id = int(id_str)
                    path = os.path.join(self.image_dir, filename)
                    image = face_recognition.load_image_file(path)
                    encodings = face_recognition.face_encodings(image)

                    if encodings:
                        self.known_face_encodings.append(encodings[0])
                        self.known_face_ids.append(face_id)
                    else:
                        print(f"[WARNING] No face found in {filename}. Skipping.")

                except Exception as e:
                    print(f"[ERROR] Failed to process {filename}: {e}")

    def setup_ui(self):
        """Setup the main UI elements."""
        tk.Label(self.root, text="Criminal Surveillance System", bg=THEME['header_bg'], fg='white',
                 font=("Arial", 24, "bold"), height=2).pack(fill="x")

        self.video_label = Label(self.root, bg="black")
        self.video_label.place(x=50, y=100, width=800, height=600)

        tk.Button(self.root, text="Start Surveillance", font=("Arial", 14, "bold"), bg=THEME["accent"],
                  fg="white", command=self.toggle_surveillance).place(x=300, y=720)

        tk.Button(self.root, text="Exit", width=10, font=("Arial", 12), bg=THEME['button_bg'], fg='white',
                  command=self.root.quit).place(x=1180, y=720)

        # Treeview to show detected criminals
        self.tree = ttk.Treeview(self.root, columns=("ID", "Name", "Crime", "Nationality"), show='headings')
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120)
        self.tree.place(x=900, y=100, width=450, height=300)

        style = ttk.Style()
        style.configure("Treeview", background=THEME['bg'], fieldbackground=THEME['bg'], foreground='white')
        style.configure("Treeview.Heading", background=THEME['header_bg'], foreground='white', font=("Arial", 11, "bold"))

        self.tree.tag_configure('strong', background=THEME['success'])
        self.tree.bind("<Double-1>", self.on_double_click)

        # Frame for full criminal details (Initially hidden)
        self.details_frame = LabelFrame(self.root, text="Criminal Details", font=("Arial", 14, "bold"),
                                        bg=THEME["bg"], fg=THEME["text_light"], bd=2)
        self.details_frame.place(x=900, y=420, width=450, height=280)
        self.details_frame.place_forget()  # Hide initially

        self.criminal_face_label = Label(self.details_frame, bg=THEME["bg"])
        self.criminal_face_label.place(x=10, y=10, width=180, height=250)

        self.detail_labels = {}
        fields = ["Name", "Father", "Mother", "Gender", "Religion", "Blood Group", "Body Mark", "Nationality", "Crime"]
        for i, field in enumerate(fields):
            label = Label(self.details_frame, text=f"{field}:", font=("Arial", 11, "bold"),
                          bg=THEME["bg"], fg=THEME["text_light"], anchor="w")
            label.place(x=200, y=10 + (i * 28))

            value = Label(self.details_frame, text="", font=("Arial", 11),
                          bg=THEME["bg"], fg="white", anchor="w")
            value.place(x=310, y=10 + (i * 28), width=130)
            self.detail_labels[field] = value

    def toggle_surveillance(self):
        if not self.video_running:
            self.video_running = True
            self.detected_ids.clear()
            threading.Thread(target=self.surveillance_loop, daemon=True).start()
        else:
            self.video_running = False

    def surveillance_loop(self):
        cap = cv2.VideoCapture(0)

        while self.video_running:
            ret, frame = cap.read()
            if not ret:
                break

            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

            for face_encoding in face_encodings:
                matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding, tolerance=0.5)
                criminal_id = None

                if True in matches:
                    match_index = matches.index(True)
                    criminal_id = self.known_face_ids[match_index]

                    if criminal_id not in self.detected_ids:
                        self.detected_ids.add(criminal_id)
                        self.display_matched_criminal(criminal_id)

            # Show frame on GUI
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img_pil = Image.fromarray(rgb_frame).resize((800, 600), Image.LANCZOS)
            photo = ImageTk.PhotoImage(img_pil)
            self.video_label.configure(image=photo)
            self.video_label.image = photo

        cap.release()
        self.video_label.config(image='')

    def display_matched_criminal(self, criminal_id):
        try:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            cur.execute("SELECT ID, name, crime, nationality FROM people WHERE ID=?", (criminal_id,))
            db_row = cur.fetchone()
            conn.close()

            if db_row:
                self.tree.insert("", tk.END, values=(db_row[0], db_row[1], db_row[2], db_row[3]), tags=('strong',))
                winsound.PlaySound("SystemExclamation", winsound.SND_ALIAS)
                self.show_criminal_details(criminal_id)

        except Exception as e:
            print(f"[ERROR] Error displaying matched criminal: {e}")

    def on_double_click(self, event):
        selected_item = self.tree.identify_row(event.y)
        if selected_item:
            item_values = self.tree.item(selected_item, "values")
            if item_values:
                criminal_id = item_values[0]
                self.show_criminal_details(criminal_id)

    def show_criminal_details(self, criminal_id):
        try:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            cur.execute("SELECT * FROM people WHERE ID=?", (criminal_id,))
            row = cur.fetchone()
            conn.close()

            if not row:
                print(f"[INFO] No data found for ID: {criminal_id}")
                return

            # Load image correctly
            image_path = None
            for ext in [".jpg", ".jpeg", ".png"]:
                image_filename = f"user.{criminal_id}{ext}"
                test_path = os.path.join(self.image_dir, image_filename)
                if os.path.exists(test_path):
                    image_path = test_path
                    break

            if image_path:
                img = Image.open(image_path).resize((180, 250), Image.LANCZOS)
                self.criminal_photo = ImageTk.PhotoImage(img)
                self.criminal_face_label.configure(image=self.criminal_photo, text="")
                self.criminal_face_label.image = self.criminal_photo
            else:
                self.criminal_face_label.configure(image='', text="No Image", fg="white")

            # Fill the details
            details_map = {
                "Name": row[1],
                "Gender": row[2],
                "Father": row[3],
                "Mother": row[4],
                "Religion": row[5],
                "Blood Group": row[6],
                "Body Mark": row[7],
                "Nationality": row[8],
                "Crime": row[9]
            }
            for field, label in self.detail_labels.items():
                label.config(text=details_map.get(field, "N/A"))

            # Show the details frame when a match is found
            self.details_frame.place(x=900, y=420, width=450, height=280)

        except Exception as e:
            print(f"[ERROR] Exception in show_criminal_details: {e}")

# ------------ RUN APP -------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = SurveillanceApp(root)
    root.mainloop()
