from tkinter import Tk, Label, Button, messagebox as tmsg
from PIL import Image, ImageTk
from subprocess import call

# Theme Constants
WINDOW_WIDTH = 1350
WINDOW_HEIGHT = 720
BG_COLOR = "#1A1A40"        # Dark background
TITLE_COLOR = "#2F4F4F"     # Slate gray for title bar
BUTTON_BG = "#2ECC71"       # Teal/Green for buttons
BUTTON_ALT_BG = "#B22222"   # Crimson Red for alert-style button
TEXT_LIGHT = "#FAFAFA"
TEXT_DARK = "#333333"
BUTTON_FONT = ("bold", 12)

def register():
    try:
        call([r"myvenv\Scripts\python.exe", "registerGUI.py"])
    except Exception as e:
        tmsg.showerror("Error", f"Failed to open registration window:\n{e}")

def video_surveillance():
    try:
        call([r"myvenv\Scripts\python.exe", "surveillance.py"])
    except Exception as e:
        tmsg.showerror("Error", f"Failed to start video surveillance:\n{e}")

def detect_criminal():
    try:
        call([r"myvenv\Scripts\python.exe", "detect.py"])
    except Exception as e:
        tmsg.showerror("Error", f"Failed to start criminal detection:\n{e}")

def on_closing():
    if tmsg.askokcancel("Exit", "Do you really want to exit?"):
        root.destroy()

root = Tk()
root.geometry(f'{WINDOW_WIDTH}x{WINDOW_HEIGHT}')
root.state("zoomed")
root.title("Face Recognition System for Criminal Detection")
root.configure(bg=BG_COLOR)

# Background image (optional, if image blends with dark theme)


    

   

# Title
Label(root, text="Face Recognition System for Criminal Detection",
      width=82, height=3, font=("bold", 25), anchor="center",
      bg=TITLE_COLOR, fg=TEXT_LIGHT).place(x=0, y=100)

# Buttons
Button(root, text='REGISTER CRIMINAL', width=35, height=3,
       bg=BUTTON_BG, fg=TEXT_DARK, font=BUTTON_FONT, command=register).place(x=420, y=330)

Button(root, text='PHOTO MATCH', width=35, height=3,
       bg=BUTTON_BG, fg=TEXT_DARK, font=BUTTON_FONT, command=detect_criminal).place(x=420, y=410)

Button(root, text='VIDEO SURVEILLANCE', width=35, height=3,
       bg=BUTTON_BG, fg=TEXT_DARK, font=BUTTON_FONT, command=video_surveillance).place(x=420, y=490)

# Side image
try:
    side_image = Image.open("image1.jpg").resize((380, 380), Image.LANCZOS)
    side_photo = ImageTk.PhotoImage(side_image)
    Label(root, image=side_photo, width=380, height=380, bg=BG_COLOR).place(x=900, y=270)
except FileNotFoundError:
    tmsg.showwarning("Warning", "Side image not found!")

# Bottom bar (optional, based on your layout)
Label(root, width=230, height=720, anchor="center", bg=TITLE_COLOR).place(x=0, y=700)

root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()
