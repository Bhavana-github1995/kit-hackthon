import sqlite3
from tkinter import *
from tkinter import messagebox
from datetime import datetime, timedelta

# Create or connect to SQLite database
conn = sqlite3.connect('academic_calendar.db')
c = conn.cursor()

# Create tables for users and deadlines if they don't exist
c.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL)
''')

c.execute('''
CREATE TABLE IF NOT EXISTS deadlines (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    event_name TEXT NOT NULL,
    event_date TEXT NOT NULL,
    reminder_time TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id))
''')
conn.commit()

current_user_id = None  # Variable to hold the ID of the logged-in user

# Function to register a new user
def register_user():
    username = username_entry.get()
    password = password_entry.get()

    if not username or not password:
        messagebox.showwarning("Input Error", "Please provide both username and password.")
        return

    try:
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        messagebox.showinfo("Success", "Registration successful! Please log in.")
        username_entry.delete(0, END)
        password_entry.delete(0, END)
    except sqlite3.IntegrityError:
        messagebox.showwarning("Error", "Username already exists.")

# Function to log in an existing user
def login_user():
    global current_user_id
    username = username_entry.get()
    password = password_entry.get()

    c.execute("SELECT id FROM users WHERE username = ? AND password = ?", (username, password))
    user = c.fetchone()

    if user:
        current_user_id = user[0]
        messagebox.showinfo("Success", f"Welcome, {username}!")
        login_frame.pack_forget()  # Hide login screen
        main_frame.pack(fill=BOTH, expand=True)  # Show main app screen
        display_deadlines()
        check_deadlines()  # Check if any deadlines are approaching
    else:
        messagebox.showwarning("Login Failed", "Invalid username or password.")

# Function to add a deadline to the database
def add_deadline():
    event_name = event_entry.get()
    event_date = date_entry.get()
    reminder_time = reminder_entry.get()

    # Validate date format and input
    try:
        datetime.strptime(event_date, '%Y-%m-%d')
        if event_name and reminder_time:
            c.execute("INSERT INTO deadlines (user_id, event_name, event_date, reminder_time) VALUES (?, ?, ?, ?)",
                       (current_user_id, event_name, event_date, reminder_time))
            conn.commit()
            messagebox.showinfo("Success", "Deadline added successfully!")
            event_entry.delete(0, END)
            date_entry.delete(0, END)
            reminder_entry.delete(0, END)
            display_deadlines()
            check_deadlines()  # Check for deadlines right after adding one
        else:
            messagebox.showwarning("Input Error", "Please provide an event name and reminder time.")
    except ValueError:
        messagebox.showwarning("Date Error", "Please enter the date in YYYY-MM-DD format.")

# Function to display all deadlines for the logged-in user
def display_deadlines():
    c.execute("SELECT id, event_name, event_date, reminder_time FROM deadlines WHERE user_id = ? ORDER BY event_date", (current_user_id,))
    deadlines = c.fetchall()

    # Clear the current list in the listbox
    listbox.delete(0, END)

    # Populate the listbox with deadlines
    for deadline in deadlines:
        listbox.insert(END, f"{deadline[1]} - {deadline[2]} (Reminder: {deadline[3]})")

# Function to delete a selected deadline
def delete_deadline():
    selected = listbox.curselection()
    if selected:
        deadline_str = listbox.get(selected)
        # Extracting event_name and event_date from the listbox item
        event_name = deadline_str.split(' - ')[0].strip()
        event_date = deadline_str.split(' - ')[1].split(' (')[0].strip()
        
        # Find the corresponding deadline ID for deletion
        c.execute("DELETE FROM deadlines WHERE user_id = ? AND event_name = ? AND event_date = ?", 
                   (current_user_id, event_name, event_date))
        conn.commit()

        messagebox.showinfo("Deleted", "Deadline deleted successfully!")
        display_deadlines()
        check_deadlines()  # Check for deadlines after deleting one
    else:
        messagebox.showwarning("Selection Error", "Please select a deadline to delete.")

# Function to check if any deadlines are approaching
def check_deadlines():
    today = datetime.today().date()
    upcoming = today + timedelta(days=7)  # Look for deadlines within the next 7 days

    c.execute("SELECT event_name, event_date FROM deadlines WHERE user_id = ? AND event_date BETWEEN ? AND ?", 
               (current_user_id, today, upcoming))
    deadlines = c.fetchall()

    # Clear previous notifications
    notification_label.config(text="")

    if deadlines:
        upcoming_deadlines = "\n".join([f"{d[0]} - {d[1]}" for d in deadlines])
        notification_label.config(text=f"The following deadlines are approaching:\n\n{upcoming_deadlines}")
    else:
        notification_label.config(text="You have no deadlines in the next 7 days.")

# Tkinter GUI setup
root = Tk()
root.title("Academic Calendar with Login")
root.geometry("600x500")

# Change background to a soft pastel pink
root.configure(bg="#FFDDE1")  # Soft pastel pink

# Set a clean modern font for the entire app
font_family = ("Helvetica", 12)

# --- Login Screen --- 
login_frame = Frame(root, bg="#FFDDE1", bd=4, relief="groove")  # 3D Effect on Frame
login_frame.pack(fill=BOTH, expand=True)

Label(login_frame, text="Login / Register", font=("Helvetica", 16, "bold"), bg="#FFDDE1", fg="#4B4453").pack(pady=20)

# Username Entry with 3D effect
Label(login_frame, text="Username", font=font_family, bg="#FFDDE1", fg="#4B4453").pack(pady=5)
username_entry = Entry(login_frame, width=40, font=("Helvetica", 12), bd=4, relief="sunken")  # 3D effect
username_entry.pack(pady=5)

# Password Entry with 3D effect
Label(login_frame, text="Password", font=font_family, bg="#FFDDE1", fg="#4B4453").pack(pady=5)
password_entry = Entry(login_frame, show="*", width=40, font=("Helvetica", 12), bd=4, relief="sunken")  # 3D effect
password_entry.pack(pady=5)

# Login and Register Buttons with 3D effect
Button(login_frame, text="Login", command=login_user, bg="#A6DCEF", fg="#4B4453", font=("Helvetica", 12, "bold"), bd=4, relief="raised", width=15).pack(pady=10)
Button(login_frame, text="Register", command=register_user, bg="#4CAF50", fg="white", font=("Helvetica", 12, "bold"), bd=4, relief="raised", width=15).pack(pady=5)

# --- Main App Screen (after login) --- 
main_frame = Frame(root, bg="#FFDDE1", bd=4, relief="groove")  # 3D Effect on Frame

# Event Entry with 3D effect
Label(main_frame, text="Event Name", font=font_family, bg="#FFDDE1", fg="#4B4453").pack(pady=5)
event_entry = Entry(main_frame, width=40, font=("Helvetica", 12), bd=4, relief="sunken")  # 3D effect
event_entry.pack(pady=5)

# Date Entry with 3D effect
Label(main_frame, text="Event Date (YYYY-MM-DD)", font=font_family, bg="#FFDDE1", fg="#4B4453").pack(pady=5)
date_entry = Entry(main_frame, width=40, font=("Helvetica", 12), bd=4, relief="sunken")  # 3D effect
date_entry.pack(pady=5)

# Reminder Entry with 3D effect
Label(main_frame, text="Reminder Time (e.g., 09:00 AM)", font=font_family, bg="#FFDDE1", fg="#4B4453").pack(pady=5)
reminder_entry = Entry(main_frame, width=40, font=("Helvetica", 12), bd=4, relief="sunken")  # 3D effect
reminder_entry.pack(pady=5)

# Add Deadline Button with 3D effect
Button(main_frame, text="Add Deadline", command=add_deadline, bg="#A6DCEF", fg="#4B4453", font=("Helvetica", 12, "bold"), bd=4, relief="raised", width=20).pack(pady=10)

# Listbox to display deadlines
listbox = Listbox(main_frame, width=60, height=10, font=("Helvetica", 12), bd=4, relief="sunken")
listbox.pack(pady=10)

# Delete Deadline Button with 3D effect
Button(main_frame, text="Delete Selected Deadline", command=delete_deadline, bg="#FF6F61", fg="white", font=("Helvetica", 12, "bold"), bd=4, relief="raised", width=20).pack(pady=10)

# Notification label to display upcoming deadlines
notification_label = Label(main_frame, text="", font=("Helvetica", 12, "bold"), bg="#FFDDE1", fg="#4B4453")
notification_label.pack(pady=10)

# Start the main loop
root.mainloop()

# Close the database connection when the program is closed
conn.close()
