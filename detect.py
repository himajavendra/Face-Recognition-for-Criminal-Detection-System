import os
import shutil
import sqlite3
import winsound
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, Label, LabelFrame
from PIL import Image, ImageTk
from deepface import DeepFace

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

class CriminalApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Criminal Detection System")
        self.root.geometry('1350x720')
        self.root.configure(bg=THEME['bg'])
        self.root.state("zoomed")

        self.db_path = "images"
        self.model_name = "ArcFace"
        self.detector = "retinaface"
        self.temp_image = "temp/1.png"

        self.setup_ui()

    def setup_ui(self):
        tk.Label(self.root, text="Criminal Detection System", bg=THEME['header_bg'], fg='white',
                 font=("Arial", 20, "bold"), height=2).pack(fill="x")

        tk.Label(self.root, text="1. Select an image\n2. Click 'Detect Face' to find matches",
                 bg=THEME['bg'], fg=THEME['text_dark'], font=("Arial", 14)).place(x=80, y=80)

        self.photo_label = tk.Label(self.root, bg=THEME['bg'], bd=2, relief='groove')
        self.photo_label.place(x=80, y=140, width=400, height=400)

        tk.Button(self.root, text="Select Photo", font=("Arial", 12), width=20, bg=THEME['button_bg'],
                  fg='white', command=self.load_image).place(x=180, y=560)

        tk.Button(self.root, text="Detect Face", font=("Arial", 12), width=20, bg=THEME['accent'],
                  fg='white', command=self.view_matches).place(x=180, y=610)

        self.tree = ttk.Treeview(self.root, columns=("ID", "Name", "Crime", "Nationality"), show='headings')
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120)
        self.tree.place(x=600, y=140, width=750, height=200)

        self.tree.tag_configure('strong', background=THEME['success'])
        self.tree.bind("<Double-1>", self.on_double_click)

        # Criminal Details Frame (not placed initially)
        self.details_frame = LabelFrame(self.root, text="Criminal Details", font=("Arial", 12, "bold"),
                                        bg=THEME['bg'], fg=THEME['text_light'], bd=2)
        
        # Image inside details frame
        self.criminal_face_label = Label(self.details_frame, bg=THEME['bg'])
        self.criminal_face_label.place(x=10, y=10, width=200, height=260)

        # Labels for details
        self.detail_labels = {}
        fields = ["Name", "Father", "Mother", "Gender", "Religion", "Blood Group", "Body Mark", "Nationality", "Crime"]
        for i, field in enumerate(fields):
            label = Label(self.details_frame, text=f"{field}:", font=("Arial", 11), bg=THEME['bg'], fg=THEME['text_light'], anchor="w")
            label.place(x=220, y=10 + (i * 28))

            value = Label(self.details_frame, text="", font=("Arial", 11, "bold"), bg=THEME['bg'], fg="white", anchor="w")
            value.place(x=350, y=10 + (i * 28), width=370)

            self.detail_labels[field] = value

        tk.Button(self.root, text="Exit", width=10, font=("Arial", 10), bg=THEME['button_bg'], fg='white',
                  command=self.root.quit).place(x=1180, y=600)

    def load_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg *.jpeg *.png")])
        if file_path:
            if not os.path.exists("temp"):
                os.makedirs("temp")
            shutil.copy(file_path, self.temp_image)
            img = Image.open(self.temp_image).resize((400, 400), Image.LANCZOS)
            self.photo = ImageTk.PhotoImage(img)
            self.photo_label.configure(image=self.photo)
            self.details_frame.place_forget()  # Hide details on new image load

    def view_matches(self):
        self.tree.delete(*self.tree.get_children())
        self.details_frame.place_forget()  # Hide details on new detection
        try:
            result = DeepFace.find(img_path=self.temp_image, db_path=self.db_path,
                                   model_name=self.model_name, detector_backend=self.detector,
                                   enforce_detection=False)

            if result[0].empty:
                messagebox.showinfo("No Match", "No matching criminal found.")
                return

            for _, row in result[0].iterrows():
                confidence = max(0, min(100, round((1 - row["distance"]) * 100, 2)))
                filename = os.path.basename(row["identity"])
                criminal_id = filename.split('.')[1]

                conn = sqlite3.connect("criminal.db")
                cur = conn.cursor()
                cur.execute("SELECT ID, name, crime, nationality FROM people WHERE ID=?", (criminal_id,))
                db_row = cur.fetchone()
                conn.close()

                if db_row:
                    self.tree.insert("", tk.END, values=(db_row[0], db_row[1], db_row[2], db_row[3]), tags=('strong',))
                    winsound.PlaySound("SystemExclamation", winsound.SND_ALIAS)

        except Exception as e:
            messagebox.showerror("Error", f"Detection failed: {str(e)}")

    def on_double_click(self, event):
        selected_item = self.tree.identify_row(event.y)
        if selected_item:
            item_values = self.tree.item(selected_item, "values")
            if item_values:
                criminal_id = item_values[0]
                self.show_criminal_details(criminal_id)

    def show_criminal_details(self, criminal_id):
        try:
            # Show the frame now
            self.details_frame.place(x=600, y=360, width=750, height=320)

            conn = sqlite3.connect("criminal.db")
            cur = conn.cursor()
            cur.execute("SELECT * FROM people WHERE ID=?", (criminal_id,))
            row = cur.fetchone()
            conn.close()

            if not row:
                print(f"[INFO] No data found for ID: {criminal_id}")
                return

            # Show criminal image
            image_path = None
            for ext in [".png", ".jpg"]:
                image_filename = f"user.{criminal_id}{ext}"
                test_path = os.path.join(self.db_path, image_filename)
                print(f"[DEBUG] Looking for image at: {test_path}")
                if os.path.exists(test_path):
                    image_path = test_path
                    break

            if image_path:
                img = Image.open(image_path).resize((200, 260), Image.LANCZOS)
                self.criminal_photo = ImageTk.PhotoImage(img)
                self.criminal_face_label.configure(image=self.criminal_photo, text="")
                self.criminal_face_label.image = self.criminal_photo
            else:
                print(f"[WARNING] Image not found: {image_path}")
                self.criminal_face_label.configure(image='', text="No Image Found", fg="white")

            # Update labels
            details_map = {
                "Name": row[1],
                "Father": row[3],
                "Mother": row[4],
                "Gender": row[2],
                "Religion": row[5],
                "Blood Group": row[6],
                "Body Mark": row[7],
                "Nationality": row[8],
                "Crime": row[9]
            }
            for field, label in self.detail_labels.items():
                label.config(text=details_map.get(field, "N/A"))

        except Exception as e:
            print(f"[ERROR] Exception in show_criminal_details: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = CriminalApp(root)
    root.mainloop()
