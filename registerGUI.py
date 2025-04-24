from tkinter import *
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import sqlite3, shutil, os, pycountry
import cv2
import re

class CriminalRegistrationApp:
    def __init__(self, root):
        self.root = root
        self.root.geometry('1350x720')
        self.root.state("zoomed")
        self.root.title("Criminal Registration")
        self.root.configure(bg="#1A1A40")

        self.filepath = ""
        self.fields = {
            "Full Name *": StringVar(),
            "Father Name": StringVar(),
            "Mother Name": StringVar(),
            "Body Mark": StringVar(),
            "Nationality": StringVar(),
            "Crime *": StringVar(),
            "Gender *": IntVar(),
            "Religion *": StringVar(),
            "Blood Group": StringVar()
        }

        self.setup_ui()

    def setup_ui(self):
        Label(self.root, text="Criminal Registration Form", width=110, height=3,
              font=("bold", 18), bg="#2F4F4F", fg='#FAFAFA').place(x=0, y=0)

        y_position = 130
        for label, var in self.fields.items():
            if label == "Gender *":
                self.create_gender_section(y_position)
            elif label in ["Religion *", "Blood Group", "Nationality"]:
                options = {
                    "Religion *": ["Hindu", "Muslim", "Christian", "Sikh", "Jain", "Others"],
                    "Blood Group": ["A+", "A-", "B+", "B-", "AB+", "O+", "O-", "Not known"],
                    "Nationality": sorted([c.name for c in pycountry.countries])
                }
                self.create_dropdown(var, options[label], f"Select {label.split()[0]}", y_position)
            else:
                self.create_label_entry(label, y_position, var)
            y_position += 50

        Label(self.root, text="Face Image *", width=20, font=("bold", 12), bg="#1A1A40", fg="white").place(x=70, y=y_position)
        OptionMenu(self.root, StringVar(value="Select Option"),
                   "Select from File", "Capture from Webcam",
                   command=self.handle_image_option).place(x=260, y=y_position)
        y_position += 60

        Button(self.root, text='Register', width=15, font=("bold", 10),
               bg='#1ABC9C', height=2, fg='black', command=self.register).place(x=150, y=y_position)

        Button(self.root, text='Back', width=15, font=("bold", 10),
               bg='#FF4C4C', height=2, fg='white', command=self.root.quit).place(x=300, y=y_position)

        self.image_frame = Frame(self.root, width=500, height=500, bg="#F4F4F4", bd=2, relief="solid")
        self.image_frame.place(x=740, y=140)

        self.image_label = Label(self.image_frame, width=500, height=500, bg="#F4F4F4")
        self.image_label.place(x=0, y=0)

    def create_label_entry(self, text, y, variable):
        Label(self.root, text=text, width=20, font=("bold", 12), bg="#1A1A40", fg="#FAFAFA").place(x=70, y=y)
        entry = Entry(self.root, width=50, textvariable=variable, bg="#ECECEC", fg="#333333")
        entry.place(x=260, y=y)
        if text in ["Full Name *", "Father Name", "Mother Name", "Body Mark"]:
            entry.bind("<KeyRelease>", lambda e, var=variable: self.validate_alpha(var))

    def validate_alpha(self, variable):
        value = variable.get()
        if not re.match(r'^[a-zA-Z ]*$', value):
            variable.set(re.sub(r'[^a-zA-Z ]', '', value))

    def create_dropdown(self, variable, options, default, y):
        Label(self.root, text=default, width=20, font=("bold", 12), bg="#1A1A40", fg="#FAFAFA").place(x=70, y=y)
        button = Button(self.root, textvariable=variable, width=40, bg="#3C3C3C", fg="#FAFAFA", relief="raised")
        button.place(x=260, y=y)
        variable.set(default)
        button.bind("<Button-1>", lambda e, v=variable, o=options, b=button: self.open_scrollable_dropdown(v, o, b))

    def open_scrollable_dropdown(self, variable, options, button):
        # Remove existing dropdowns
        for widget in self.root.winfo_children():
            if isinstance(widget, Frame) and hasattr(widget, "is_dropdown"):
                widget.destroy()

        dropdown = Frame(self.root, bg="white", bd=1, relief="solid")
        dropdown.is_dropdown = True

        x = button.winfo_rootx() - self.root.winfo_rootx()
        y = button.winfo_rooty() - self.root.winfo_rooty() + button.winfo_height()
        dropdown.place(x=x, y=y, width=button.winfo_width(), height=150)

        scrollbar = Scrollbar(dropdown)
        scrollbar.pack(side=RIGHT, fill=Y)

        listbox = Listbox(dropdown, yscrollcommand=scrollbar.set, font=("Arial", 11))
        for item in options:
            listbox.insert(END, item)
        listbox.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.config(command=listbox.yview)

        def on_select(event):
            selected = listbox.get(listbox.curselection())
            variable.set(selected)
            dropdown.destroy()

        listbox.bind("<Double-Button-1>", on_select)
        listbox.bind("<Return>", on_select)

    def create_gender_section(self, y):
        Label(self.root, text="Gender *", width=20, font=("bold", 12), bg="#1A1A40", fg="#FAFAFA").place(x=70, y=y)
        Radiobutton(self.root, text="Male", padx=5, variable=self.fields["Gender *"], value=1,
                    bg="#1A1A40", fg="#FAFAFA", selectcolor="#1ABC9C").place(x=260, y=y)
        Radiobutton(self.root, text="Female", padx=20, variable=self.fields["Gender *"], value=2,
                    bg="#1A1A40", fg="#FAFAFA", selectcolor="#1ABC9C").place(x=320, y=y)

    def handle_image_option(self, option):
        if option == "Select from File":
            self.select_image()
        elif option == "Capture from Webcam":
            self.capture_from_camera()

    def select_image(self):
        self.filepath = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
        self.display_selected_image()

    def capture_from_camera(self):
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        if ret:
            if not os.path.exists("temp"): os.makedirs("temp")
            filepath = "temp/captured_image.jpg"
            cv2.imwrite(filepath, frame)
            self.filepath = filepath
            self.display_selected_image()
        cap.release()
        cv2.destroyAllWindows()

    def display_selected_image(self):
        if self.filepath:
            image = Image.open(self.filepath).resize((500, 500), Image.LANCZOS)
            self.photo = ImageTk.PhotoImage(image)
            self.image_label.config(image=self.photo)

    def validate_form(self):
        required_fields = ["Full Name *", "Crime *", "Gender *", "Religion *"]
        for field in required_fields:
            if not self.fields[field].get() or (field == "Gender *" and self.fields[field].get() == 0):
                return False
        return bool(self.filepath)

    def register(self):
        if not self.validate_form():
            messagebox.showwarning("Incomplete Form", "Please fill all mandatory (*) fields and select an image.")
            return

        if messagebox.askquestion("Confirm", "Are you sure you want to register this criminal?") == "yes":
            self.save_to_database()

    def save_to_database(self):
        try:
            conn = sqlite3.connect('criminal.db')
            cursor = conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS People (
                                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                                Name TEXT, Gender TEXT, Father TEXT, Mother TEXT,
                                Religion TEXT, Blood TEXT, Bodymark TEXT,
                                Nationality TEXT, Crime TEXT)''')

            cursor.execute('''INSERT INTO People 
                              (Name, Gender, Father, Mother, Religion, Blood, Bodymark, Nationality, Crime) 
                              VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                           (
                               self.fields["Full Name *"].get(),
                               "Male" if self.fields["Gender *"].get() == 1 else "Female",
                               self.fields["Father Name"].get(),
                               self.fields["Mother Name"].get(),
                               self.fields["Religion *"].get(),
                               self.fields["Blood Group"].get(),
                               self.fields["Body Mark"].get(),
                               self.fields["Nationality"].get(),
                               self.fields["Crime *"].get()
                           ))
            criminal_id = cursor.lastrowid
            conn.commit()

            if not os.path.exists('images'):
                os.makedirs('images')

            ext = os.path.splitext(self.filepath)[1]
            saved_path = f'images/user.{criminal_id}{ext}'
            shutil.copy(self.filepath, saved_path)

            conn.close()
            messagebox.showinfo("Success", "Criminal Registered Successfully")
            self.root.quit()
        except Exception as e:
            messagebox.showerror("Database Error", f"An error occurred: {str(e)}")

if __name__ == "__main__":
    root = Tk()
    app = CriminalRegistrationApp(root)
    root.mainloop()
