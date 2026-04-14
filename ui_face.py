import sqlite3
import tkinter as tk
from tkinter import messagebox, filedialog
from tkinter import ttk
from ttkbootstrap import Style
import datetime
from deepface import DeepFace
import cv2
import os
from PIL import Image, ImageTk

# Declare `cap` as a global variable
cap = None

# #Replace with the IP address and port provided by the mobile app
url = "https://192.0.0.4:8080/video"
#  Open a connection to the camera using the URL
# cap = cv2.VideoCapture(url)

# Initialize SQLite database
def initialize_db():
    conn = sqlite3.connect('students.db')
    cursor = conn.cursor()
    
    # Create students table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            student_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            course TEXT NOT NULL,
            image_path TEXT NOT NULL,
            total_attendance INTEGER DEFAULT 0
        )
    ''')
    
    # Create attendance table with course and lecture_name
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            course TEXT NOT NULL,
            lecture_name TEXT NOT NULL,
            date TEXT NOT NULL,
            FOREIGN KEY(student_id) REFERENCES students(student_id)
        )
    ''')
    
    conn.commit()
    conn.close()

# Function to add student to the database with validation
def add_student_to_db(student_id, name, course, image_path):
    if not student_id or not name or not course or not image_path:
        messagebox.showerror("Input Error", "All fields are required.")
        return

    try:
        conn = sqlite3.connect('students.db')
        cursor = conn.cursor()

        # Check if the student_id already exists
        cursor.execute('SELECT student_id FROM students WHERE student_id = ?', (student_id,))
        if cursor.fetchone():
            messagebox.showerror("Error", "Student ID already exists.")
            return

        cursor.execute('INSERT INTO students (student_id, name, course, image_path) VALUES (?, ?, ?, ?)',
                       (student_id, name, course, image_path))
        conn.commit()
        messagebox.showinfo("Success", f"Student {name} added successfully!")
    except sqlite3.Error as e:
        messagebox.showerror("Database Error", f"An error occurred: {e}")
    finally:
        conn.close()

# Function to record attendance
def record_attendance(student_id, course, lecture_name):
    try:
        conn = sqlite3.connect('students.db')
        cursor = conn.cursor()
        date = datetime.datetime.now().strftime("%Y-%m-%d")

        # Check if the student has already been marked for the same course and lecture today
        cursor.execute('''
            SELECT * FROM attendance 
            WHERE student_id = ? AND course = ? AND lecture_name = ? AND date = ?
        ''', (student_id, course, lecture_name, date))
        
        if cursor.fetchone():
            messagebox.showinfo("Info", "Attendance already marked for this course and lecture.")
        else:
            cursor.execute('''
                INSERT INTO attendance (student_id, course, lecture_name, date) 
                VALUES (?, ?, ?, ?)
            ''', (student_id, course, lecture_name, date))
            cursor.execute('UPDATE students SET total_attendance = total_attendance + 1 WHERE student_id = ?', (student_id,))
            conn.commit()
            messagebox.showinfo("Success", f"Attendance marked for student ID: {student_id} in {course} - {lecture_name}")
    except sqlite3.Error as e:
        messagebox.showerror("Database Error", f"An error occurred: {e}")
    finally:
        conn.close()

# Main window
root = tk.Tk()
style = Style(theme='flatly')
root.title("Face Recognition Attendance System")
root.geometry("1000x600")

# Admin Login Screen
def admin_login():
    def validate_login():
        username = username_entry.get()
        password = password_entry.get()
        if username == "a" and password == "a":  # Set your credentials here
            main_dashboard()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")

    login_frame = tk.Frame(root)
    login_frame.pack(pady=100)

    tk.Label(login_frame, text="Admin Login", font=("Arial", 18)).pack(pady=10)
    tk.Label(login_frame, text="Username:").pack()
    username_entry = tk.Entry(login_frame)
    username_entry.pack()

    tk.Label(login_frame, text="Password:").pack()
    password_entry = tk.Entry(login_frame, show='*')
    password_entry.pack()

    ttk.Button(login_frame, text="Login", command=validate_login).pack(pady=20)

# Main Dashboard
def main_dashboard():
    for widget in root.winfo_children():
        widget.destroy()

    dashboard_frame = tk.Frame(root)
    dashboard_frame.pack(pady=20)

    tk.Label(dashboard_frame, text="Dashboard", font=("Arial", 18)).pack(pady=10)
    ttk.Button(dashboard_frame, text="Add Student", width=20, command=add_student).pack(pady=5)
    ttk.Button(dashboard_frame, text="Remove Student", width=20, command=remove_student).pack(pady=5)
    ttk.Button(dashboard_frame, text="Mark Attendance", width=20, command=mark_attendance).pack(pady=5)
    ttk.Button(dashboard_frame, text="View Attendance", width=20, command=view_attendance).pack(pady=5)
    ttk.Button(dashboard_frame, text="Generate Attendance Report", width=20, command=generate_report).pack(pady=5)
    ttk.Button(dashboard_frame, text="Logout", width=20, command=logout).pack(pady=5)

# Function to add a student with validation to check if the face is already present
def add_student():
    global cap  # Make sure cap is recognized globally
    cap = None  # Initialize cap to None

    for widget in root.winfo_children():
        widget.destroy()

    add_frame = tk.Frame(root)
    add_frame.pack(pady=50)

    tk.Label(add_frame, text="Add Student", font=("Arial", 18)).pack(pady=10)
    
    tk.Label(add_frame, text="Student ID:").pack()
    student_id_entry = tk.Entry(add_frame)
    student_id_entry.pack()
    
    invalid_id_label = tk.Label(add_frame, text="", fg='red')
    invalid_id_label.pack(pady=(0, 1))

    tk.Label(add_frame, text="Name:").pack()
    student_name_entry = tk.Entry(add_frame)
    student_name_entry.pack()

    tk.Label(add_frame, text="Course:").pack()
    course_var = tk.StringVar()
    course_options = ttk.Combobox(add_frame, textvariable=course_var, state="readonly")
    course_options['values'] = ("BCA", "BSc", "BBA")
    course_options.pack()

    # Initialize the Capture Image button as disabled
    capture_btn = ttk.Button(add_frame, text="Capture Image", command=lambda: capture_image(student_id_entry.get(), student_name_entry.get(), course_var.get()))
    capture_btn.config(state='disabled')
    capture_btn.pack(pady=5)
    
    ttk.Button(add_frame, text="Go Back", command=main_dashboard).pack(pady=5)

    # Function to for validationns 
    
    def check_fields():
        student_id = student_id_entry.get()
        student_name = student_name_entry.get()
        course = course_var.get()

        # Check if all fields are filled
        if student_id and student_name and course and " " not in student_id:
            capture_btn.config(state='normal')  # Enable button if all conditions are met
        else:
            capture_btn.config(state='disabled')  # Disable button if any condition fails

        # Show a warning message if the Student ID contains spaces
        if " " in student_id:
            student_id_entry.config(fg='red')# Highlight the Student ID field in red
            invalid_id_label.config(fg='red')
            invalid_id_label.config(text="Invalid ID: No spaces allowed")  
        else:
            student_id_entry.config(fg='black')  # Revert to normal color if no spaces
            invalid_id_label.config(text="")  
        
    # Attach event listeners to the input fields
    student_id_entry.bind("<KeyRelease>", lambda event: check_fields())
    student_name_entry.bind("<KeyRelease>", lambda event: check_fields())
    course_options.bind("<<ComboboxSelected>>", lambda event: check_fields())

# Capture image function (remains the same)
def capture_image(student_id, student_name, course):
    global cap  # Ensure cap is recognized as a global variable
    cap = cv2.VideoCapture(url)  # Initialize the webcam

    def capture_and_save():
        ret, frame = cap.read()
        if not ret:
            messagebox.showerror("Error", "Failed to capture image")
            return

        temp_image_path = "temp_image.jpg"
        cv2.imwrite(temp_image_path, frame)

        # Check if the face already exists in any of the course folders
        img_folder_base = r"D:\\code grams\\aaProject sem5\\code\\img1"
        folders = ["BCA", "BSc", "BBA"]
        match_found = False

        try:
            for folder in folders:
                folder_path = os.path.join(img_folder_base, folder)
                for student_image in os.listdir(folder_path):
                    student_img_path = os.path.join(folder_path, student_image)
                    result = DeepFace.verify(img1_path=temp_image_path, img2_path=student_img_path, model_name="Facenet512")

                    if result['verified']:
                        messagebox.showerror("Error", f"Student already registered in {folder} course!")
                        match_found = True
                        main_dashboard()
                        break
                if match_found:
                    break

            if not match_found:
                # Save the image and add the student to the database
                image_path = f"{img_folder_base}\\{course}\\{student_id}.jpg"
                cv2.imwrite(image_path, frame)  # Save the captured image
                add_student_to_db(student_id, student_name, course, image_path)
                # messagebox.showinfo("Success", "Face detected!")
                main_dashboard()

        except Exception as e:
            messagebox.showerror("Error", f"Face not detected")

        finally:
            os.remove(temp_image_path)  # Remove the temporary image file
            cap.release()

    def update_frame():
        ret, frame = cap.read()
        if ret:
            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(cv2image)
            imgtk = ImageTk.PhotoImage(image=img)
            camera_label.imgtk = imgtk
            camera_label.configure(image=imgtk)
        if cap.isOpened():
            camera_label.after(10, update_frame)

    # Clear the previous interface
    for widget in root.winfo_children():
        widget.destroy()

    # Interface for capturing image
    capture_frame = tk.Frame(root)
    capture_frame.pack(pady=50)

    tk.Label(capture_frame, text="Capturing Image", font=("Arial", 18)).pack(pady=10)
    camera_label = tk.Label(capture_frame)
    camera_label.pack(pady=20)

    ttk.Button(capture_frame, text="Capture Image", command=capture_and_save).pack(pady=20)
    ttk.Button(capture_frame, text="Go Back", command=lambda: (cap.release(), add_student())).pack(pady=5)

    # Start updating the frame
    update_frame()


# Function to remove a student
def remove_student():
    for widget in root.winfo_children():
        widget.destroy()

    remove_frame = tk.Frame(root)
    remove_frame.pack(pady=50)

    tk.Label(remove_frame, text="Remove Student", font=("Arial", 18)).pack(pady=10)
    tk.Label(remove_frame, text="Student ID:").pack()
    student_id_entry = tk.Entry(remove_frame)
    student_id_entry.pack()

    def remove_from_db():
        student_id = student_id_entry.get()

        if not student_id:
            messagebox.showerror("Error", "Please enter a valid Student ID.")
            return

        try:
            conn = sqlite3.connect('students.db')
            cursor = conn.cursor()

            # Retrieve the image path before deleting the student record
            cursor.execute('SELECT image_path FROM students WHERE student_id = ?', (student_id,))
            student = cursor.fetchone()

            if student:
                image_path = student[0]
                if os.path.exists(image_path):
                    os.remove(image_path)  # Delete the image file

            # Delete the student record from the database
            cursor.execute('DELETE FROM students WHERE student_id = ?', (student_id,))
            cursor.execute('DELETE FROM attendance WHERE student_id = ?', (student_id,))
            conn.commit()

            if cursor.rowcount == 0:
                messagebox.showerror("Error", "Student ID not found.")
            else:
                messagebox.showinfo("Success", f"Student {student_id} removed successfully!")              
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}")
        finally:
            conn.close()

    ttk.Button(remove_frame, text="Remove Student", command=remove_from_db).pack(pady=5)
    ttk.Button(remove_frame, text="Go Back", command=main_dashboard).pack(pady=5)

# Function to mark attendance

# Function to mark attendance
def mark_attendance():
    global cap
    cap = cv2.VideoCapture(url)  # Initialize the webcam

    # Function to capture and mark attendance with course and lecture_name
    def capture_image_for_attendance():
        global cap
        ret, frame = cap.read()
        if not ret:
            messagebox.showerror("Error", "Failed to capture image")
            return

        # Save the captured image temporarily
        captured_image_path = "captured_image.jpg"
        cv2.imwrite(captured_image_path, frame)

        course = course_var.get()
        lecture_name = lecture_var.get()

        if not course or not lecture_name:
            messagebox.showerror("Error", "Please select a course and enter a lecture name.")
            return

        try:
            conn = sqlite3.connect('students.db')
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM students WHERE course = ?', (course,))
            students = cursor.fetchall()

            found_match = False
            for student in students:
                try:
                    result = DeepFace.verify(img1_path=captured_image_path, img2_path=student[3], enforce_detection=False)
                    if result["verified"]:
                        # Mark attendance with course and lecture_name
                        record_attendance(student[0], course, lecture_name)
                        found_match = True
                        break
                except Exception as e:
                    continue  # Handle face verification errors silently

            if not found_match:
                messagebox.showerror("Error", "No matching face found for the selected course.")
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}")
        finally:
            conn.close()
            
        # Release the webcam resource
        cap.release()
        mark_attendance()

    # UI for course and lecture selection
    for widget in root.winfo_children():
        widget.destroy()

    attendance_frame = tk.Frame(root)
    attendance_frame.pack(pady=50)

    tk.Label(attendance_frame, text="Mark Attendance", font=("Arial", 18)).pack(pady=10)

    tk.Label(attendance_frame, text="Select Course:").pack()
    course_var = tk.StringVar()
    course_options = ttk.Combobox(attendance_frame, textvariable=course_var, state="readonly")
    course_options['values'] = ("BCA", "BSc", "BBA")
    course_options.pack()

    tk.Label(attendance_frame, text="Select Lecture:").pack()
    lecture_var = tk.StringVar()
    lecture_options = ttk.Combobox(attendance_frame, textvariable=lecture_var, state="readonly")
    lecture_options.pack()

    def update_lecture_options(event):
        course = course_var.get()
        lectures = {
            "BCA": ["C Programming", "Operating System", "DBMS", "Web Technologies"],
            "BSc": ["Computer Network", "Java", "Software Engineering", "Mathematical Foundation"],
            "BBA": ["Human Resources", "Accounting", "Principle of Management", "Marketing"]
        }
        lecture_options['values'] = lectures.get(course, [])
        lecture_var.set("")  # Clear the selected lecture

    course_options.bind("<<ComboboxSelected>>", update_lecture_options)

    camera_label = tk.Label(attendance_frame)
    camera_label.pack(pady=20)

    def update_frame():
        ret, frame = cap.read()
        if ret:
            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(cv2image)
            imgtk = ImageTk.PhotoImage(image=img)
            camera_label.imgtk = imgtk
            camera_label.configure(image=imgtk)
        if cap.isOpened():
            camera_label.after(10, update_frame)

    ttk.Button(attendance_frame, text="Capture and Mark Attendance", command=capture_image_for_attendance).pack(pady=20)
    ttk.Button(attendance_frame, text="Go Back", command=lambda: (cap.release(), main_dashboard())).pack(pady=5)

    update_frame()

# Function to view attendance
def view_attendance():
    for widget in root.winfo_children():
        widget.destroy()

    view_frame = tk.Frame(root)
    view_frame.pack(pady=50)

    tk.Label(view_frame, text="View Attendance", font=("Arial", 18)).pack(pady=10)

    tree = ttk.Treeview(view_frame, columns=('ID', 'Name', 'Course', 'Attendance'), show='headings')
    tree.heading('ID', text='Student ID')
    tree.heading('Name', text='Name')
    tree.heading('Course', text='Course')
    tree.heading('Attendance', text='Total Attendance')
    tree.pack()

    try:
        conn = sqlite3.connect('students.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM students')
        students = cursor.fetchall()

        for student in students:
            tree.insert('', tk.END, values=(student[0], student[1], student[2], student[4]))

    except sqlite3.Error as e:
        messagebox.showerror("Database Error", f"An error occurred: {e}")
    finally:
        conn.close()

    ttk.Button(view_frame, text="Go Back", command=main_dashboard).pack(pady=5)

# Function to generate attendance report
def generate_report():
    # Implementation for generating report (e.g., export data to CSV or PDF)
    pass

# Function to log out with confirmation
def logout():
    global cap  # Ensure `cap` is recognized

    # Ask for confirmation before logging out
    confirm = messagebox.askyesno("Logout", "Are you sure you want to log out?")
    
    if confirm:  # If the user confirms
        if cap and cap.isOpened():
            cap.release()  # Release the webcam resource
        for widget in root.winfo_children():
            widget.destroy()
        admin_login()  # Redirect to admin login screen

# Initialize the database
initialize_db()

# Start the application
admin_login()
root.mainloop()


