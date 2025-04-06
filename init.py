import psycopg2
import subprocess
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import ttk, messagebox
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import socket
SWIPL_PATH = r"C:\Program Files\swipl\bin\swipl.exe"  # Update this path if needed

if not os.path.exists("gpa_calculation.pl"):
    print("Prolog file not found!")


# Database Connection Setup
def connect_db():
    return psycopg2.connect(
        dbname="AI_Database",  # Replace with your database name
        user="postgres",       # Replace with your PostgreSQL username
        password="L3igh-@Ann22",  # Replace with your PostgreSQL password
        host="localhost",      # Replace with your host (e.g., localhost or IP address)
        port="5432"            # Replace with your PostgreSQL port (default is 5432)
    )

# Test database connection
def test_db_connection():
    try:
        conn = connect_db()
        print("Database connection successful!")
        conn.close()
    except Exception as e:
        print(f"Database connection failed: {e}")

# Fetch student name from database
def get_student_name(student_id):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        query = 'SELECT "Student Name" FROM student_master WHERE "Student ID" = %s'
        cursor.execute(query, (student_id,))
        result = cursor.fetchone()
        return result[0] if result else "Unknown Student"
    except Exception as e:
        print(f"Error fetching student name: {e}")
        return "Unknown Student"
    finally:
        cursor.close()
        conn.close()

# Fetch student email from database
def get_student_email(student_id):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        query = 'SELECT "Student Email" FROM student_master WHERE "Student ID" = %s'
        cursor.execute(query, (student_id,))
        result = cursor.fetchone()
        return result[0] if result else "Unknown Student"
    except Exception as e:
        print(f"Error fetching student name: {e}")
        return "Unknown Student"
    finally:
        cursor.close()
        conn.close()

# Gets the information for the calculations
def fetch_student_modules(student_id, year):
    conn = connect_db()
    cursor = conn.cursor()
    # Query to fetch grade points and module credits for the student
    query = """
        SELECT md."Module Code", md."Grade point", mm."Number of Credits", md."semester"
        FROM public.module_details md
        JOIN public.module_master mm ON md."Module Code" = mm."Module Code"
        WHERE md."Student ID" = %s AND md."Year" = %s
        ORDER BY md."semester" ASC;
    """
    cursor.execute(query, (student_id, year))
    records = cursor.fetchall()

    # Organize records into semester-wise lists
    semester_1 = []
    semester_2 = []
    cumulative = []
    for record in records:
        module, grade_point, credits, semester = record
        if semester == 1:
            semester_1.append((grade_point, credits))
            cumulative.append((grade_point, credits))
        elif semester == 2:
            semester_2.append((grade_point, credits))
            cumulative.append((grade_point, credits))

    # Close connection
    cursor.close()
    conn.close()

    print("Semester 1:", semester_1)
    print("Semester 2:", semester_2)
    print("Cumulative:", cumulative)

    return semester_1, semester_2, cumulative

# GPA Calculation function using Prolog
def run_prolog_gpa_calculation(data):
    """
    Calls Prolog to calculate GPA for the given semester data.
    """
    if not data:  # Handle empty data case
        return 0.0
    
    # Get absolute path to the Prolog file
    prolog_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gpa_calculation.pl")
    
    # Convert Python list to Prolog-readable format
    prolog_list = "[" + ", ".join(f"({gp}, {cr})" for gp, cr in data) + "]"

    # Escape the file path for Prolog
    prolog_file_escaped = prolog_file.replace("\\", "/")

    # Construct Prolog query with proper path escaping
    prolog_query = f"consult('{prolog_file_escaped}'), gpa({prolog_list}, GPA), write(GPA), nl."

    # Run Prolog script using subprocess with full path to SWI-Prolog
    try:
        result = subprocess.run(
            [SWIPL_PATH, "-q", "-g", prolog_query, "-t", "halt"],
            capture_output=True,
            text=True,
            check=True  # This will raise an exception if the process fails
        )

        # Debugging: Print Prolog output
        print(f"Prolog query: {prolog_query}")
        print(f"Prolog output: {result.stdout}")
        print(f"Prolog error: {result.stderr}")

        try:
            gpa = float(result.stdout.strip())  # Extract and convert GPA
            return gpa
        except ValueError:
            print("Error: Invalid GPA output from Prolog.")
            return 0.0  # Return 0.0 instead of None for invalid output
    except subprocess.CalledProcessError as e:
        print(f"Prolog execution failed: {e}")
        print(f"Stderr: {e.stderr}")
        return 0.0  # Return 0.0 instead of None for execution errors
    except Exception as e:
        print(f"Unexpected error: {e}")
        return 0.0  # Return 0.0 instead of None for any other errors

# Checks if the Cumulative GPA is below the probation threshold
def run_prolog_check_academic_probation(gpa):
    """
    Calls Prolog to check the status of academic probation.
    """
    # Get absolute path to the Prolog file
    prolog_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gpa_calculation.pl")
    
    # Escape the file path for Prolog
    prolog_file_escaped = prolog_file.replace("\\", "/")

    # Construct Prolog query
    prolog_query = f"consult('{prolog_file_escaped}'), check_academic_probation({gpa}), write('true'), nl."

    try:
        # Run Prolog script using subprocess with full path to SWI-Prolog
        result = subprocess.run(
            [SWIPL_PATH, "-q", "-g", prolog_query, "-t", "halt"],
            capture_output=True,
            text=True,
            check=True
        )
        return "true" in result.stdout.lower()
    except Exception as e:
        print(f"Error checking academic probation: {e}")
        return False

def get_student_details(student_id):
    """Get student's programme and school information"""
    conn = connect_db()
    cursor = conn.cursor()
    try:
        query = 'SELECT "Programme", "School" FROM student_master WHERE "Student ID" = %s'
        cursor.execute(query, (student_id,))
        result = cursor.fetchone()
        return result if result else (None, None)
    except Exception as e:
        print(f"Error fetching student details: {e}")
        return None, None
    finally:
        cursor.close()
        conn.close()

def get_staff_emails(student_id, programme, school):
    """Get emails for specific advisor, programme director, and faculty admin"""
    conn = connect_db()
    cursor = conn.cursor()
    try:
        # Get the specific advisor ID for this student
        advisor_query = """
            SELECT t.email 
            FROM teacher_master t
            JOIN Advisors a ON t."Teacher ID" = a."Academic Advisor"
            WHERE a."Student ID" = %s
        """
        cursor.execute(advisor_query, (student_id,))
        advisor_email = cursor.fetchone()

        # Get programme director and faculty admin
        staff_query = """
            SELECT "email", "Position" 
            FROM teacher_master 
            WHERE ("programme" = %s OR 
                  LOWER("programme") = LOWER(%s) OR
                  "programme" = %s)
            AND "Position" IN ('Programme director', 'Faculty Administrator')
        """
        cursor.execute(staff_query, (programme, programme, school))
        results = cursor.fetchall()
        
        # Organize emails by role
        staff_emails = {
            'advisor': advisor_email[0] if advisor_email else None,
            'director': None,
            'admin': None
        }
        
        for email, position in results:
            if position == 'Programme director':
                staff_emails['director'] = email
            elif position == 'Faculty Administrator':
                staff_emails['admin'] = email
                
        return staff_emails
    except Exception as e:
        print(f"Error fetching staff emails: {e}")
        return None
    finally:
        cursor.close()
        conn.close()

def get_user_email_credentials(user_id):
    """Get email and password for the authenticated user"""
    conn = connect_db()
    cursor = conn.cursor()
    try:
        # First check teacher_master
        query = """
            SELECT "email", "Password"
            FROM teacher_master
            WHERE "Teacher ID" = %s
        """
        cursor.execute(query, (user_id,))
        result = cursor.fetchone()
        
        if result:
            return result[0], result[1]
            
        # If not found in teacher_master, check admin_master
        query = """
            SELECT "Admin Email", "Password"
            FROM admin_master
            WHERE "Admin ID" = %s
        """
        cursor.execute(query, (user_id,))
        result = cursor.fetchone()
        
        if result:
            return result[0], result[1]

        # If not found in admin_master, check student_master
        query = """
            SELECT "Student Email", "Password"
            FROM student_master
            WHERE "Student ID" = %s
        """
        cursor.execute(query, (user_id,))
        result = cursor.fetchone()
        
        return result if result else (None, None)
    except Exception as e:
        print(f"Error fetching user email credentials: {e}")
        return None, None
    finally:
        cursor.close()
        conn.close()

def send_email(student_id, student_email, cumulative_gpa):
    """
    Sends academic probation alert emails to student and all relevant staff members.
    """
    # Get student details
    programme, school = get_student_details(student_id)
    if not programme or not school:
        print(f"Error: Could not find programme/school details for student {student_id}")
        return

    # Get advisor email from Advisors table
    conn = connect_db()
    cursor = conn.cursor()
    try:
        # Get advisor's email
        advisor_query = """
            SELECT t.email 
            FROM teacher_master t
            JOIN Advisors a ON t."Teacher ID" = a."Academic Advisor"
            WHERE a."Student ID" = %s
        """
        cursor.execute(advisor_query, (student_id,))
        advisor_email = cursor.fetchone()

        # Get programme director's email
        director_query = """
            SELECT email 
            FROM teacher_master 
            WHERE "Position" = 'Programme director' 
            AND "programme" = %s
        """
        cursor.execute(director_query, (programme,))
        director_email = cursor.fetchone()

        # Get faculty administrator's email
        admin_query = """
            SELECT email 
            FROM teacher_master 
            WHERE "Position" = 'Faculty Administrator' 
            AND "programme" = %s
        """
        cursor.execute(admin_query, (school,))
        admin_email = cursor.fetchone()

    except Exception as e:
        print(f"Error fetching staff emails: {e}")
        return
    finally:
        cursor.close()
        conn.close()

    # Email configuration
    smtp_server = "sandbox.smtp.mailtrap.io"
    login = "6b62548d11cd6f"  # Replace with your Mailtrap login
    password = "5bfe83beba4bf9"  # Replace with your Mailtrap password
    port = 2525

    # Create message
    msg = MIMEMultipart()
    sender = "noreply@utech.edu.jm"
    msg['From'] = sender
    msg['Subject'] = "Academic Probation Alert"

    # Email body with HTML formatting
    html = f"""
    <html>
      <body>
        <h2>ACADEMIC PROBATION ALERT</h2>
        <p>This is an automated notification that the following student is on academic probation:</p>
        <table style="border-collapse: collapse; width: 100%; border: 1px solid #ddd;">
          <tr>
            <td style="padding: 8px; border: 1px solid #ddd;"><strong>Student ID:</strong></td>
            <td style="padding: 8px; border: 1px solid #ddd;">{student_id}</td>
          </tr>
          <tr>
            <td style="padding: 8px; border: 1px solid #ddd;"><strong>Student Name:</strong></td>
            <td style="padding: 8px; border: 1px solid #ddd;">{get_student_name(student_id)}</td>
          </tr>
          <tr>
            <td style="padding: 8px; border: 1px solid #ddd;"><strong>Programme:</strong></td>
            <td style="padding: 8px; border: 1px solid #ddd;">{programme}</td>
          </tr>
          <tr>
            <td style="padding: 8px; border: 1px solid #ddd;"><strong>School:</strong></td>
            <td style="padding: 8px; border: 1px solid #ddd;">{school}</td>
          </tr>
          <tr>
            <td style="padding: 8px; border: 1px solid #ddd;"><strong>Cumulative GPA:</strong></td>
            <td style="padding: 8px; border: 1px solid #ddd;">{cumulative_gpa:.2f}</td>
          </tr>
        </table>
        <p>This student's GPA has fallen below or is equal to the minimum required GPA threshold.</p>
        <p><strong>Immediate academic counseling and support is recommended.</strong></p>
        <br>
        <p><em>This is an automated message from the UTech Academic Management System.</em></p>
      </body>
    </html>
    """

    # Add HTML content
    msg.attach(MIMEText(html, 'html'))

    try:
        # Create SMTP session
        server = smtplib.SMTP(smtp_server, port)
        server.starttls()
        server.login(login, password)

        # Send to student
        msg['To'] = student_email
        server.send_message(msg)
        print(f"Alert sent to student: {student_email}")

        # Send to advisor
        if advisor_email:
            msg.replace_header('To', advisor_email[0])
            server.send_message(msg)
            print(f"Alert sent to advisor: {advisor_email[0]}")

        # Send to programme director
        if director_email:
            msg.replace_header('To', director_email[0])
            server.send_message(msg)
            print(f"Alert sent to programme director: {director_email[0]}")

        # Send to faculty administrator
        if admin_email:
            msg.replace_header('To', admin_email[0])
            server.send_message(msg)
            print(f"Alert sent to faculty administrator: {admin_email[0]}")

        server.quit()
        print(f"Academic probation alerts sent successfully for student {student_id}")
    except (socket.gaierror, ConnectionRefusedError):
        error_msg = 'Failed to connect to the server. Bad connection settings?'
        print(error_msg)
        messagebox.showerror("Error", error_msg)
    except smtplib.SMTPServerDisconnected:
        error_msg = 'Failed to connect to the server. Wrong user/password?'
        print(error_msg)
        messagebox.showerror("Error", error_msg)
    except smtplib.SMTPException as e:
        error_msg = f'SMTP error occurred: {str(e)}'
        print(error_msg)
        messagebox.showerror("Error", error_msg)
    except Exception as e:
        error_msg = f'An error occurred: {str(e)}'
        print(error_msg)
        messagebox.showerror("Error", error_msg)

def check_and_send_email(cumulative_gpa, student_id):
    """Check GPA and automatically send alerts if below threshold"""
    if run_prolog_check_academic_probation(cumulative_gpa):
        student_email = get_student_email(student_id)
        send_email(student_id, student_email, cumulative_gpa)

# GPA Calculation
def generate_gpa(year_var, results_text, student_id, sender_id):
    """Calculate and display GPA, with sender_id for email notifications"""
    # Get selected year
    selected_year = year_var.get()
    if selected_year == 'Choose':
        messagebox.showwarning("Input Error", "Please select a year!")
        return

    print(f"Selected Year: {selected_year}")

    # Display loading message
    results_text.insert(tk.END, f"GPA calculation for {selected_year} is in progress...\n\n")

    # Fetch semester data
    semester_1_data, semester_2_data, cumulative_data = fetch_student_modules(student_id, selected_year)

    # Get GPA results from Prolog
    gpa_sem1 = run_prolog_gpa_calculation(semester_1_data)
    gpa_sem2 = run_prolog_gpa_calculation(semester_2_data)
    cumulative_gpa = run_prolog_gpa_calculation(cumulative_data)

    # Display the results
    results_text.insert(tk.END, f"Semester 1 GPA: {gpa_sem1:.2f}\n")
    results_text.insert(tk.END, f"Semester 2 GPA: {gpa_sem2:.2f}\n")
    results_text.insert(tk.END, f"Cumulative GPA: {cumulative_gpa:.2f}\n")
    results_text.insert(tk.END, f"Email: {get_student_email(student_id)}\n")

    # If GPA is below the threshold, send an email
    check_and_send_email(cumulative_gpa, student_id)

# Student Dashboard GUI
def show_student_dashboard(student_id):
    root = tk.Tk()
    root.title("Student Dashboard")

    # Welcome message with student name
    tk.Label(root, text=f"Welcome, {get_student_name(student_id)}").pack()

    # Label for year selection
    tk.Label(root, text="Select Year").pack()

    # Dropdown (OptionMenu) for selecting year
    years = ['Choose','2023/2024', '2024/2025']
    year_var = tk.StringVar()
    year_var.set(years[0])

    def show_selected_year(*args):
        selected_year = year_var.get()
        print(f"Selected Year: {selected_year}")
        year_label.config(text=f"Selected Year: {selected_year}")

    year_var.trace('w', show_selected_year)
    year_dropdown = tk.OptionMenu(root, year_var, *years)
    year_dropdown.pack()
    year_label = tk.Label(root, text=f"Selected Year: {year_var.get()}")
    year_label.pack()

    results_text = tk.Text(root, height=10, width=50)
    results_text.pack()

    # For students, they can only check their own GPA
    generate_button = tk.Button(root, text="Generate", 
                              command=lambda: generate_gpa(year_var, results_text, student_id, student_id))
    generate_button.pack()

    root.mainloop()

# Function to add student data to the database
def add_student(student_id_entry, student_name_entry, email_entry, school_entry, dropdown, password_entry):
    student_id = student_id_entry.get()
    student_name = student_name_entry.get()
    email = email_entry.get()
    school = school_entry.get()
    dropdown_value = dropdown.get()
    password = password_entry.get()

    if not student_id or not student_name or not email or not password:
        messagebox.showwarning("Input Error", "All fields are required!")
        return

    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO student_master ("Student ID", "Student Name", "Student Email", "School", "Programme", "Password")
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (student_id, student_name, email, school, dropdown_value, password))
        conn.commit()
        messagebox.showinfo("Success", "Student information added successfully!")
    except Exception as e:
        messagebox.showerror("Error", str(e))
    finally:
        conn.close()

# Function to search student by name (partial match)
def search_student(search_name_entry, student_info_text):
    search_name = search_name_entry.get()
    if not search_name:
        messagebox.showwarning("Input Error", "Please enter a name to search!")
        return

    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM student_master WHERE "Student Name" ILIKE %s
        """, ('%' + search_name + '%',))
        students = cursor.fetchall()

        # Clear text area before displaying new results
        student_info_text.delete(1.0, tk.END)

        if students:
            for student in students:
                student_info_text.insert(tk.END,
                                         f"ID: {student[0]}\nName: {student[1]}\nEmail: {student[2]}\nSchool: {student[3]}\nProgramme: {student[4]}\n\n")
        else:
            student_info_text.insert(tk.END, "No matching student found.")
    except Exception as e:
        messagebox.showerror("Error", str(e))
    finally:
        conn.close()

# Placeholder function for admin dashboard
def show_admin_dashboard(admin_id):
    root = tk.Tk()
    root.title("Admin Dashboard")

    def show_add_student_window():
        search_frame.pack_forget()
        add_frame.pack(pady=20)

    def show_search_student_window():
        add_frame.pack_forget()
        search_frame.pack(pady=20)

    # Create main buttons for toggling between windows
    toggle_frame = tk.Frame(root)
    toggle_frame.pack(pady=10)

    add_student_button = tk.Button(toggle_frame, text="Add Student", command=show_add_student_window)
    add_student_button.pack(side=tk.LEFT, padx=10)

    search_student_button = tk.Button(toggle_frame, text="Search Student", command=show_search_student_window)
    search_student_button.pack(side=tk.LEFT, padx=10)

    # Window 1: Add student info
    add_frame = tk.Frame(root)

    tk.Label(add_frame, text="Student ID").grid(row=0, column=0, padx=10, pady=5)
    student_id_entry = tk.Entry(add_frame)
    student_id_entry.grid(row=0, column=1, padx=10, pady=5)

    tk.Label(add_frame, text="Student Name").grid(row=1, column=0, padx=10, pady=5)
    student_name_entry = tk.Entry(add_frame)
    student_name_entry.grid(row=1, column=1, padx=10, pady=5)

    tk.Label(add_frame, text="Email").grid(row=2, column=0, padx=10, pady=5)
    email_entry = tk.Entry(add_frame)
    email_entry.grid(row=2, column=1, padx=10, pady=5)

    tk.Label(add_frame, text="School").grid(row=3, column=0, padx=10, pady=5)
    school_entry = tk.Entry(add_frame)
    school_entry.grid(row=3, column=1, padx=10, pady=5)

    tk.Label(add_frame, text="Programme").grid(row=4, column=0, padx=10, pady=5)
    dropdown = ttk.Combobox(add_frame, values=["Animation", "Chemical engineering", "Computing"])
    dropdown.grid(row=4, column=1, padx=10, pady=5)

    tk.Label(add_frame, text="Password").grid(row=5, column=0, padx=10, pady=5)
    password_entry = tk.Entry(add_frame, show="*")
    password_entry.grid(row=5, column=1, padx=10, pady=5)

    add_button = tk.Button(add_frame, text="Add Student",
                           command=lambda: add_student(student_id_entry, student_name_entry, email_entry,
                                                       school_entry, dropdown, password_entry))
    add_button.grid(row=6, columnspan=2, pady=10)

    # Window 2: Search student
    search_frame = tk.Frame(root)

    tk.Label(search_frame, text="Search Student Name").grid(row=0, column=0, padx=10, pady=5)
    search_name_entry = tk.Entry(search_frame)
    search_name_entry.grid(row=0, column=1, padx=10, pady=5)

    search_button = tk.Button(search_frame, text="Search", command=lambda: search_student(search_name_entry, student_info_text))
    search_button.grid(row=1, columnspan=2, pady=10)

    # Display student info in a text area
    student_info_text = tk.Text(root, width=50, height=10)
    student_info_text.pack(pady=10)

    # Start by showing the Add Student window
    show_add_student_window()

    root.mainloop()

# Login Check Function
def check_login(user_id, password):
    conn = connect_db()
    cursor = conn.cursor()
    student_query = 'SELECT * FROM student_master WHERE "Student ID" = %s AND "Password" = %s'
    cursor.execute(student_query, (user_id, password))
    student_result = cursor.fetchone()
    if student_result:
        messagebox.showinfo("Login Success", "Student login successful!")
        show_student_dashboard(user_id)
        conn.close()
        return
    admin_query = 'SELECT * FROM admin_master WHERE "Admin ID" = %s AND "Password" = %s'
    cursor.execute(admin_query, (user_id, password))
    admin_result = cursor.fetchone()
    conn.close()
    if admin_result:
        messagebox.showinfo("Login Success", "Admin login successful!")
        show_admin_dashboard(user_id)
    else:
        messagebox.showerror("Login Failed", "Invalid credentials!")

# Tkinter GUI Setup
def create_gui():
    root = tk.Tk()
    root.title("Login")
    tk.Label(root, text="User ID").grid(row=0, column=0)
    user_id_entry = tk.Entry(root)
    user_id_entry.grid(row=0, column=1)
    tk.Label(root, text="Password").grid(row=1, column=0)
    password_entry = tk.Entry(root, show="*")
    password_entry.grid(row=1, column=1)

    def login():
        user_id = user_id_entry.get()
        password = password_entry.get()
        check_login(user_id, password)

    tk.Button(root, text="Login", command=login).grid(row=2, columnspan=2)
    root.mainloop()

# Function to view data from a table
def view_table_data(table_name):
    """
    Fetches and displays all records from the specified table with column names.
    """
    try:
        conn = connect_db()
        cursor = conn.cursor()
        query = f'SELECT * FROM {table_name}'
        cursor.execute(query)
        records = cursor.fetchall()

        # Print column names
        column_names = [desc[0] for desc in cursor.description]
        print(f"Table: {table_name}")
        print("-" * 50)

        # Print each record with column names
        for record in records:
            for col_name, value in zip(column_names, record):
                print(f"{col_name}: {value}")
            print("-" * 50)

    except Exception as e:
        print(f"Error fetching data from {table_name}: {e}")
    finally:
        cursor.close()
        conn.close()

def check_all_students_gpa(sender_id):
    """
    Checks all students' GPAs and sends alerts for those below threshold
    """
    conn = connect_db()
    cursor = conn.cursor()
    try:
        # Get all students
        cursor.execute('SELECT "Student ID", "Student Email" FROM student_master')
        students = cursor.fetchall()
        
        current_year = "2023/2024"  # You might want to make this configurable
        
        for student_id, student_email in students:
            # Fetch semester data for the student
            _, _, cumulative_data = fetch_student_modules(student_id, current_year)
            
            # Calculate cumulative GPA
            cumulative_gpa = run_prolog_gpa_calculation(cumulative_data)
            
            # Check if GPA is below threshold and send alerts
            check_and_send_email(cumulative_gpa, student_id)
                
    except Exception as e:
        print(f"Error checking student GPAs: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    test_db_connection()
    
    create_gui()