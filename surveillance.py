import cv2
import os
import numpy as np
from deepface import DeepFace
from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk
import imutils
import winsound

class App:
    def __init__(self, video_source=0):
        self.window = Tk()
        self.window.title("Criminal Detection with DeepFace")
        self.window.geometry("1350x720")
        self.window.state("zoomed")
        self.window.configure(bg="#0D1B2A")  # Primary dark background

        self.video_source = video_source
        self.vid = MyVideoCapture(self.video_source)

        self.detectedPeople = []
        self.setup_gui()
        self.setup_treeview()
        self.load_criminal_images("images")
        self.update()
        self.window.mainloop()

    def setup_gui(self):
        Label(
            self.window,
            text="Live Criminal Surveillance",
            font=("bold", 22),
            bg="#1A1A40",  # Secondary background
            fg="#FAFAFA"   # Light text
        ).pack(side=TOP, fill=BOTH)

        self.canvas = Canvas(
            self.window,
            height=700,
            width=700,
            bg="#1A1A40"  # Canvas in dark tone
        )
        self.canvas.pack(side=LEFT, fill=BOTH)

    def setup_treeview(self):
        style = ttk.Style()
        style.theme_use("default")

        style.configure("Treeview",
                        background="#2F4F4F",     # Treeview panel color
                        foreground="#FAFAFA",     # Light text
                        rowheight=28,
                        fieldbackground="#2F4F4F",
                        font=("Arial", 11))

        style.configure("Treeview.Heading",
                        background="#0D1B2A",     # Header background
                        foreground="#FAFAFA",     # Header text
                        font=("Arial", 12, "bold"))

        style.map("Treeview",
                  background=[("selected", "#1ABC9C")],  # Teal highlight
                  foreground=[("selected", "#0D1B2A")])

        self.tree = ttk.Treeview(
            self.window,
            column=("ID", "Name", "Crime", "Nationality", "Match %"),
            show='headings'
        )
        self.tree.heading("ID", text="Cr-ID")
        self.tree.column("ID", width=70)
        self.tree.heading("Name", text="NAME")
        self.tree.column("Name", width=200)
        self.tree.heading("Crime", text="CRIME")
        self.tree.column("Crime", width=200)
        self.tree.heading("Nationality", text="NATIONALITY")
        self.tree.column("Nationality", width=120)
        self.tree.heading("Match %", text="MATCH %")
        self.tree.column("Match %", width=100)
        self.tree.place(x=730, y=50)

    def load_criminal_images(self, folder):
        self.criminal_faces = []
        self.criminal_ids = []
        self.criminal_names = []

        for filename in os.listdir(folder):
            path = os.path.join(folder, filename)
            if filename.lower().endswith(('jpg', 'jpeg', 'png')):
                try:
                    face_img = cv2.imread(path)
                    if face_img is not None:
                        id_str = os.path.splitext(filename)[0].split('.')[1]
                        self.criminal_faces.append(face_img)
                        self.criminal_ids.append(id_str)
                        self.criminal_names.append(path)
                except Exception as e:
                    print(f"Skipping {filename}: {e}")

    def update(self):
        ret, frame = self.vid.getframe()
        if ret:
            img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.photo = ImageTk.PhotoImage(image=Image.fromarray(img_rgb))
            self.canvas.create_image(0, 0, image=self.photo, anchor=NW)

            try:
                result = DeepFace.find(
                    img_path=img_rgb,
                    db_path="images",
                    model_name="ArcFace",
                    detector_backend="retinaface",
                    enforce_detection=True,
                    silent=True
                )

                if isinstance(result, list) and len(result) > 0 and not result[0].empty:
                    best_match = result[0].iloc[0]
                    file_path = best_match["identity"]

                    distance = None
                    for key in best_match.keys():
                        if "cosine" in key or "distance" in key:
                            distance = best_match[key]
                            break

                    if distance is not None:
                        match_id = os.path.splitext(os.path.basename(file_path))[0].split('.')[1]
                        confidence = round((1 - distance) * 100, 2)

                        if match_id not in self.detectedPeople:
                            profile = self.get_criminal_profile(match_id)
                            if profile:
                                self.detectedPeople.append(match_id)
                                profile = list(profile)
                                profile.append(f"{confidence}%")
                                self.tree.insert("", "end", values=tuple(profile))
                                winsound.PlaySound("SystemExclamation", winsound.SND_ALIAS)
                else:
                    print("No match found.")

            except Exception as e:
                print(f"Error in recognition: {e}")

        self.window.after(15, self.update)

    def get_criminal_profile(self, criminal_id):
        profile_data = {
            "001": ("001", "John Doe", "Theft", "USA"),
            "002": ("002", "Jane Smith", "Fraud", "UK"),
            "003": ("003", "Ali Khan", "Smuggling", "Pakistan")
        }
        return profile_data.get(criminal_id, None)

class MyVideoCapture:
    def __init__(self, video_source=0):
        self.vid = cv2.VideoCapture(video_source)
        if not self.vid.isOpened():
            raise ValueError("Unable to open video source", video_source)

    def getframe(self):
        if self.vid.isOpened():
            ret, frame = self.vid.read()
            if ret:
                return ret, imutils.resize(frame, height=700)
        return False, None

    def __del__(self):
        if self.vid.isOpened():
            self.vid.release()

if __name__ == "__main__":
    App()
