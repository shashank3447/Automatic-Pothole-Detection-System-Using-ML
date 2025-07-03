from tkinter import *
import tkinter.filedialog
import tkinter.messagebox as tmsg
from PIL import Image, ImageTk
import cv2
from predictions import detection, draw_bounding_boxes
import time
import os
import RPi.GPIO as GPIO
import smtplib
from email.message import EmailMessage

# Setup GPIO for buzzer
BUZZER_PIN = 16
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUZZER_PIN, GPIO.OUT)

def buzz_for_2_seconds():
    GPIO.output(BUZZER_PIN, GPIO.HIGH)
    time.sleep(2)
    GPIO.output(BUZZER_PIN, GPIO.LOW)

def send_email(image_path):
    try:
        msg = EmailMessage()
        msg["Subject"] = "Pothole Detected"
        msg["From"] = "bharatshingare2601@gmail.com"
        msg["To"] = "bharatshingare03@gmail.com"
        msg.set_content("Pothole detected. See attached image.")

        with open(image_path, "rb") as f:
            file_data = f.read()
            file_name = os.path.basename(image_path)

        msg.add_attachment(file_data, maintype="image", subtype="jpeg", filename=file_name)

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login("bharatshingare2601@gmail.com", "dmev nnqx zync efpj")
            smtp.send_message(msg)

    except Exception as e:
        print("Email sending failed:", e)

def print_path():
    global f
    f = tkinter.filedialog.askopenfilename(
        parent=root,
        initialdir='',
        title='Select file',
        filetypes=[('JPG Image', '*.jpg'), ('MP4 Video', '*.mp4')]
    )

    if f.endswith('.jpg'):
        img1 = cv2.imread(f)
        if img1 is None:
            tmsg.showerror("Error", "Failed to load image.")
            return
        newimg = cv2.cvtColor(img1, cv2.COLOR_BGR2RGB)
        newimg = cv2.resize(newimg, (512, 512))
        img = Image.fromarray(newimg)
        imgtk = ImageTk.PhotoImage(image=img)
        x.imgtk = imgtk
        x.configure(image=imgtk)

    elif f.endswith('.mp4'):
        cap = cv2.VideoCapture(f)
        ret, frame = cap.read()
        cap.release()
        if not ret or frame is None:
            tmsg.showerror("Error", "Failed to load video.")
            return
        newimg = cv2.resize(frame, (512, 512))
        img = Image.fromarray(cv2.cvtColor(newimg, cv2.COLOR_BGR2RGB))
        imgtk = ImageTk.PhotoImage(image=img)
        x.imgtk = imgtk
        x.configure(image=imgtk)

def detect_objects():
    if f.endswith('.jpg'):
        img = cv2.imread(f)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        co_ords = detection(img)
        if co_ords:
            buzz_for_2_seconds()
            timestamp = time.strftime("%Y-%m-%d %H-%M-%S")
            if not os.path.exists("screenshots"):
                os.makedirs("screenshots")
            path = f"screenshots/detected_{timestamp}.jpg"
            cv2.imwrite(path, cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
            send_email(path)
        img_new = draw_bounding_boxes(co_ords, img.copy())
        img_new = cv2.resize(img_new, (512, 512))
        img = Image.fromarray(img_new)
        imgtk = ImageTk.PhotoImage(image=img)
        x.imgtk = imgtk
        x.configure(image=imgtk)

    elif f.endswith('.mp4'):
        cap = cv2.VideoCapture(f)
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            co_ords = detection(frame)
            if co_ords:
                #buzz_for_2_seconds()
                timestamp = time.strftime("%Y-%m-%d %H-%M-%S")
                if not os.path.exists("screenshots"):
                    os.makedirs("screenshots")
                path = f"screenshots/detected_{timestamp}.jpg"
                #cv2.imwrite(path, frame)
                #send_email(path)
            img_new = draw_bounding_boxes(co_ords, frame.copy())
            img_new = cv2.resize(img_new, (512, 512))
            img = Image.fromarray(cv2.cvtColor(img_new, cv2.COLOR_BGR2RGB))
            imgtk = ImageTk.PhotoImage(image=img)
            x.imgtk = imgtk
            x.configure(image=imgtk)
            x.update()

def live_detection():
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        co_ords = detection(frame)
        if co_ords:
            buzz_for_2_seconds()
            timestamp = time.strftime("%Y-%m-%d %H-%M-%S")
            if not os.path.exists("screenshots"):
                os.makedirs("screenshots")
            path = f"screenshots/live_{timestamp}.jpg"
            cv2.imwrite(path, frame)
            send_email(path)
        img_new = draw_bounding_boxes(co_ords, frame.copy())
        img_new = cv2.resize(img_new, (512, 512))
        img = Image.fromarray(cv2.cvtColor(img_new, cv2.COLOR_BGR2RGB))
        imgtk = ImageTk.PhotoImage(image=img)
        x.imgtk = imgtk
        x.configure(image=imgtk)
        x.update()

def login_page():
    login_window = Tk()
    login_window.geometry("800x600")
    login_window.title("Pothole Detection - Login")

    username_label = Label(login_window, text="Username:")
    username_label.pack(pady=5)
    username_entry = Entry(login_window)
    username_entry.pack(pady=5)

    password_label = Label(login_window, text="Password:")
    password_label.pack(pady=5)
    password_entry = Entry(login_window, show="*")
    password_entry.pack(pady=5)

    def validate_login():
        if username_entry.get() == "admin" and password_entry.get() == "admin":
            login_window.destroy()
            root.deiconify()
        else:
            tmsg.showerror("Login Failed", "Invalid username or password")

    login_button = Button(login_window, text="Login", command=validate_login)
    login_button.pack(pady=10)

    login_window.mainloop()

# GUI Layout
root = Tk()
root.geometry("800x800")
root.title("Pothole Detection System")
root.resizable(0, 0)
im = None

MF = Frame(root, bd=8, bg="lightgray", relief=GROOVE)
MF.place(x=0, y=0, height=50, width=800)
menu_label = Label(MF, text="Pothole Detection", font=("times new roman", 20, "bold"), bg="lightgray", fg="black")
menu_label.pack(side=TOP, fill="x")

x = Label(root, image=im)
x.grid(row=1, column=0, padx=5, pady=50)

button_frame = Frame(root)
button_frame.grid(row=2, column=0, columnspan=2, pady=10)

Button(button_frame, text='Select Image/Video', font=("times new roman", 20, "bold"), command=print_path).grid(row=0, column=0, padx=10)
Button(button_frame, text='Detect', font=("times new roman", 20, "bold"), command=detect_objects).grid(row=0, column=1, padx=10)
Button(button_frame, text='Live', font=("times new roman", 20, "bold"), command=live_detection).grid(row=0, column=2, padx=10)

root.withdraw()
login_page()
root.mainloop()
