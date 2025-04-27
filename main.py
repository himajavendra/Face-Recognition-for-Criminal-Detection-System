from tkinter import *
from tkinter import messagebox
import sqlite3
import hashlib
from PIL import Image, ImageTk
import subprocess

class LoginApp:
    def __init__(self, root):
        self.root = root
        self.root.geometry('1350x720')
        self.root.state("zoomed")
        self.root.title("Admin Login")
        self.root.configure(bg="#1A1A40")

        self.fields = {
            "Police ID *": StringVar(),
            "Password *": StringVar(),
        }

        self.setup_ui()

    def setup_ui(self):
        # Title Label
        Label(self.root, text="Welcome to Face Recognition for Criminal Detection System", width=110, height=3,
              font=("bold", 18), bg="#2F4F4F", fg='#FAFAFA').pack(side=TOP, fill=X)

        # Adding an image for Admin Login
        self.add_login_image()

        # Admin Login Frame
        frame = Frame(self.root, bg="#1A1A40")
        frame.place(x=750, y=200)

        # Admin Login Label
        Label(frame, text="Admin Login", font=("bold", 22), bg="#1A1A40", fg='#FAFAFA').grid(row=0, column=0, columnspan=2, pady=(10, 30))

        # Form Fields
        y_position = 1
        for label, var in self.fields.items():
            self.create_label_entry(frame, label, y_position, var)
            y_position += 2

        # Buttons Frame
        btn_frame = Frame(frame, bg="#1A1A40")
        btn_frame.grid(row=y_position, column=0, columnspan=2, pady=(30, 10))

        Button(btn_frame, text='Login', width=15, font=("bold", 12),
               bg='#1ABC9C', fg='black', command=self.login).grid(row=0, column=0, padx=10)

        Button(btn_frame, text='Signup', width=15, font=("bold", 12),
               bg='#FF4C4C', fg='white', command=self.open_signup_page).grid(row=0, column=1, padx=10)

    def add_login_image(self):
        try:
            img = Image.open("image1.jpg")  # Your image path
            img = img.resize((450, 450), Image.LANCZOS)
            img = ImageTk.PhotoImage(img)
            img_label = Label(self.root, image=img, bg="#1A1A40")
            img_label.image = img
            img_label.place(x=100, y=230)
        except Exception as e:
            print("Error loading image:", e)

    def create_label_entry(self, parent, text, row, variable):
        Label(parent, text=text, font=("bold", 14), bg="#1A1A40", fg="#FAFAFA", anchor="w").grid(row=row, column=0, sticky="w", padx=10, pady=(0,5))
        Entry(parent, width=40, textvariable=variable, bg="#ECECEC", fg="#333333", font=("bold", 12),
              show="*" if "Password" in text else "").grid(row=row+1, column=0, padx=10, pady=(0,20))

    def validate_form(self):
        for field in self.fields:
            if not self.fields[field].get():
                return False
        return True

    def login(self):
        if not self.validate_form():
            messagebox.showwarning("Incomplete Form", "Please fill all mandatory (*) fields.")
            return

        police_id = self.fields["Police ID *"].get()
        password = self.fields["Password *"].get()

        if self.verify_login(police_id, password):
            self.root.destroy()  # Close current login window
            subprocess.Popen(["python", "start.py"])  # Open start.py
        else:
            messagebox.showerror("Login Failed", "Invalid Police ID or Password")
    def verify_login(self, police_id, password):
        try:
            conn = sqlite3.connect("admin.db")
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM admin WHERE police_id=?", (police_id,))
            admin = cursor.fetchone()
            conn.close()

            if admin:
                hashed_password = admin[3]
                return hashed_password == hashlib.sha256(password.encode()).hexdigest()
            return False
        except sqlite3.DatabaseError as e:
            print(f"Database error: {e}")
            return False

    def open_signup_page(self):
        self.new_window = Toplevel(self.root)
        SignupApp(self.new_window)

class SignupApp:
    def __init__(self, root):
        self.root = root
        self.root.geometry('1350x720')
        self.root.state("zoomed")
        self.root.title("Signup")
        self.root.configure(bg="#1A1A40")

        self.fields = {
            "Name *": StringVar(),
            "Police ID *": StringVar(),
            "Password *": StringVar(),
            "Confirm Password *": StringVar(),
        }

        self.setup_ui()

    def setup_ui(self):
        Label(self.root, text="Signup for Admin Account", width=110, height=3,
              font=("bold", 18), bg="#2F4F4F", fg='#FAFAFA').pack(side=TOP, fill=X)

        frame = Frame(self.root, bg="#1A1A40")
        frame.place(x=750, y=150)

        Label(frame, text="Signup", font=("bold", 22), bg="#1A1A40", fg='#FAFAFA').grid(row=0, column=0, columnspan=2, pady=(10, 30))

        y_position = 1
        for label, var in self.fields.items():
            self.create_label_entry(frame, label, y_position, var)
            y_position += 2

        btn_frame = Frame(frame, bg="#1A1A40")
        btn_frame.grid(row=y_position, column=0, columnspan=2, pady=(30, 10))

        Button(btn_frame, text='Register', width=15, font=("bold", 12),
               bg='#1ABC9C', fg='black', command=self.register).grid(row=0, column=0, padx=10)

        Button(btn_frame, text='Cancel', width=15, font=("bold", 12),
               bg='#FF4C4C', fg='white', command=self.root.destroy).grid(row=0, column=1, padx=10)

    def create_label_entry(self, parent, text, row, variable):
        Label(parent, text=text, font=("bold", 14), bg="#1A1A40", fg="#FAFAFA", anchor="w").grid(row=row, column=0, sticky="w", padx=10, pady=(0,5))
        Entry(parent, width=40, textvariable=variable, bg="#ECECEC", fg="#333333", font=("bold", 12),
              show="*" if "Password" in text else "").grid(row=row+1, column=0, padx=10, pady=(0,20))

    def register(self):
        name = self.fields["Name *"].get()
        police_id = self.fields["Police ID *"].get()
        password = self.fields["Password *"].get()
        confirm_password = self.fields["Confirm Password *"].get()

        if not (name and police_id and password and confirm_password):
            messagebox.showwarning("Incomplete Form", "Please fill all fields.")
            return

        if password != confirm_password:
            messagebox.showerror("Password Mismatch", "Passwords do not match.")
            return

        try:
            conn = sqlite3.connect("admin.db")
            cursor = conn.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS admin (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    police_id TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL
                )
            """)
            conn.commit()

            hashed_password = hashlib.sha256(password.encode()).hexdigest()

            cursor.execute("INSERT INTO admin (name, police_id, password) VALUES (?, ?, ?)", (name, police_id, hashed_password))
            conn.commit()
            conn.close()

            messagebox.showinfo("Registration Successful", "Account created successfully!")
            self.root.destroy()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Police ID already exists!")
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

if __name__ == "__main__":
    root = Tk()
    app = LoginApp(root)
    root.mainloop()
