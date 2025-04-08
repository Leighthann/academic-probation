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

if not os.path.exists("gpa_calculation.pl"):
    print("Prolog file not found!")


# Database Connection Setup
def connect_db():
    return psycopg2.connect(
        dbname="AI_Database",  # Change as needed
        user="postgres",  # Change as needed
        password="abasi2003",  # Change as needed
        host="localhost",  # Change if using remote server
        port="5432"  # Default PostgreSQL port
    )

# Fetch all student ids from database
def get_all_student_ids():
    try:
        conn = connect_db()  # Assumes you already have a connect_db() function
        cursor = conn.cursor()
        query = 'SELECT "Student ID" FROM student_master ORDER BY "Student ID"'
        cursor.execute(query)
        student_ids = [str(row[0]) for row in cursor.fetchall()]
        return student_ids
    except Exception as e:
        print(f"Error fetching student IDs: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

# Fetch all modules from database
def get_all_modules():
    try:
        conn = connect_db()  # Assumes you already have a connect_db() function
        cursor = conn.cursor()
        query = 'SELECT "module name" FROM module_details ORDER BY "module name"'
        cursor.execute(query)
        student_ids = [str(row[0]) for row in cursor.fetchall()]
        return student_ids
    except Exception as e:
        print(f"Error fetching module names: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

# Fetch student name from database
def get_module_name(module_code):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        query = 'SELECT "Module" FROM module_master WHERE "Module Code" = %s'
        cursor.execute(query, (module_code,))
        result = cursor.fetchone()
        return result[0] if result else "Unknown Module"
    except Exception as e:
        print(f"Error fetching module code: {e}")
        return "Unknown Module"
    finally:
        cursor.close()
        conn.close()

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

# Fetch student details from database
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

# Fetch user_email_credentials
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

# Fetch staff emails from database from database
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

#------------------------------------------------------------------------------------------------------------------

# Gets current GPA default from prolog
def get_current_gpa():
    """
    Calls Prolog to get the current GPA threshold.
    """
    # Construct Prolog query to get the default GPA threshold
    prolog_query = "['gpa_threshold.pl'], default_gpa_threshold(X), write(X), nl."

    # Run Prolog script using subprocess
    result = subprocess.run(
        ["swipl", "-q", "-g", prolog_query, "-t", "halt"],
        capture_output=True,
        text=True
    )

    # Process the result to extract the GPA value from Prolog output
    if result.returncode == 0:
        try:
            # Extract the GPA value from the output (should be in the form of 'X' or 'X\n')
            current_gpa = result.stdout.strip()
            return float(current_gpa)  # Convert to float to return as GPA
        except ValueError:
            return None  # In case parsing fails
    else:
        return None  # In case Prolog query fails

# Function to call Prolog to update the GPA threshold
def update_gpa_threshold(new_threshold):
    """
    Update the GPA threshold by calling Prolog.
    """
    # Prolog query to set the new GPA threshold
    prolog_query = f"set_gpa_threshold({new_threshold})."

    # Run the Prolog script using subprocess
    result = subprocess.run(
        ['swipl', '-s', 'gpa_calculation.pl', '-g', prolog_query, '-t', 'halt'],
        capture_output=True, text=True
    )

    # Check if the result was successful
    if result.returncode == 0:
        print(f"GPA threshold updated to {new_threshold}")
    else:
        print(f"Error updating GPA threshold: {result.stderr}")


#------------------------------------------------------------------------------------------------------------------

# GPA Calculation function using Prolog
def run_prolog_gpa_calculation(data):
    """
    Calls Prolog to calculate GPA for the given semester data.
    """
    # Convert Python list to Prolog-readable format
    prolog_list = "[" + ", ".join(f"({gp}, {cr})" for gp, cr in data) + "]"

    # Construct Prolog query
    prolog_query = f"['gpa_calculation.pl'], gpa({prolog_list}, GPA), write(GPA), nl."

    # Run Prolog script using subprocess
    result = subprocess.run(
        ["swipl", "-q", "-g", prolog_query, "-t", "halt"],
        capture_output=True,
        text=True
    )

    try:
        gpa = float(result.stdout.strip())  # Extract and convert GPA
    except ValueError:
        gpa = None  # Handle errors

    return gpa

# GPA Calculation
def generate_gpa(year_var, results_text, student_id):
    # Get selected year
    selected_year = year_var.get()
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

#------------------------------------------------------------------------------------------------------------------

# Checks if the Cumulative GPA is below the probation threshold
def run_prolog_check_academic_probation(data):
    """
     Calls Prolog to check the status of academic probation.
    """

    # Construct Prolog query
    prolog_query = f"['gpa_calculation.pl'], check_academic_probation({data}, IsProbation), write(IsProbation), nl."

    # Run Prolog script using subprocess
    result = subprocess.run(
        ["swipl", "-q", "-g", prolog_query, "-t", "halt"],
        capture_output=True,
        text=True
    )

    # Process the result to extract 'true' or 'false'
    if "true" in result.stdout.lower():
        return True
    else:
        return False

# Email Sender
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
    login = "8cab6f6319daae"  # Replace with your Mailtrap login
    password = "5127c5ae317e69"  # Replace with your Mailtrap password
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

# Send Probation email if necessary
def check_and_send_email(cumulative_gpa, student_id):
    """Check GPA and automatically send alerts if below threshold"""
    if cumulative_gpa != 0 and run_prolog_check_academic_probation(cumulative_gpa):
        student_email = get_student_email(student_id)
        send_email(student_id, student_email, cumulative_gpa)

#------------------------------------------------------------------------------------------------------------------

# Function to add student data to the database
def add_student(student_id_entry, student_name_entry, email_entry, school_entry, dropdown, password_entry):
    student_id = student_id_entry.get()
    student_name = student_name_entry.get()
    email = email_entry.get()
    school = school_entry.get()
    dropdown_value = dropdown.get()
    password = password_entry.get()

    # Debug output
    print(f"Student ID: '{student_id}'")
    print(f"Student Name: '{student_name}'")
    print(f"Email: '{email}'")
    print(f"School: '{school}'")
    print(f"Programme: '{dropdown_value}'")
    print(f"Password: '{password}'")

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

# Function to add student data to the database
def add_grades(student_id_entry, module_code_entry, module_name_entry, gp_entry, dropdown, year_entry):
    student_id = student_id_entry.get()
    module_code = module_code_entry.get()
    module_name = module_name_entry.get()
    gp = gp_entry.get()
    year = year_entry.get()
    semester = dropdown.get()


    if not student_id or not module_code or not module_name or not gp or not year or not semester :
        messagebox.showwarning("Input Error", "All fields are required!")
        return

    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO module_details ("Module Code", "module name", "semester", "Student ID", "Grade point", "Year")
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (module_code, module_name, semester, student_id, gp, year))
        conn.commit()
        messagebox.showinfo("Success", "Student grade information added successfully!")
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

#------------------------------------------------------------------------------------------------------------------

# Student Dashboard GUI
def show_student_dashboard(student_id):
    root = tk.Tk()
    root.title("Student Dashboard")

    # Welcome message with student name
    tk.Label(root, text=f"Welcome, {get_student_name(student_id)}").pack()

    # Label for year selection
    tk.Label(root, text="Select Year").pack()

    # Dropdown (OptionMenu) for selecting year
    years = ['Choose','2023/2024', '2024/2025']  # Modify based on your needs
    year_var = tk.StringVar()
    year_var.set(years[0])  # Set default selection

    # Function to show the selected year
    def show_selected_year(*args):
        selected_year = year_var.get()
        print(f"Selected Year: {selected_year}")
        year_label.config(text=f"Selected Year: {selected_year}")

    # Bind the dropdown to the show_selected_year function
    year_var.trace('w', show_selected_year)

    # OptionMenu widget
    year_dropdown = tk.OptionMenu(root, year_var, *years)
    year_dropdown.pack()

    # Label to display the selected year
    year_label = tk.Label(root, text=f"Selected Year: {year_var.get()}")
    year_label.pack()

    # Text area to display results
    results_text = tk.Text(root, height=10, width=50)
    results_text.pack()

    # "Generate" button for GPA generation
    generate_button = tk.Button(root, text="Generate", command=lambda: generate_gpa(year_var, results_text, student_id))
    generate_button.pack()

    # Start the Tkinter event loop
    root.mainloop()

# Placeholder function for admin dashboard
def show_admin_dashboard():
    root = tk.Tk()
    root.title("Admin Dashboard")

    def show_add_student_window():
        search_frame.pack_forget()
        student_info_text.pack_forget()
        add_grade_frame.pack_forget()
        update_gpa_frame.pack_forget()
        add_frame.pack(pady=20)

    def show_search_student_window():
        add_frame.pack_forget()
        add_grade_frame.pack_forget()
        update_gpa_frame.pack_forget()
        search_frame.pack(pady=20)
        student_info_text.pack(pady=10)

    def show_add_student_gpa_window():
        add_frame.pack_forget()
        search_frame.pack_forget()
        student_info_text.pack_forget()
        update_gpa_frame.pack_forget()
        add_grade_frame.pack(pady=20)

    def show_update_gpa_window():
        add_frame.pack_forget()
        search_frame.pack_forget()
        student_info_text.pack_forget()
        add_grade_frame.pack_forget()
        update_gpa_frame.pack(pady=20)

    # Toggle buttons
    toggle_frame = tk.Frame(root)
    toggle_frame.pack(pady=10)

    tk.Button(toggle_frame, text="Add Student", command=show_add_student_window).pack(side=tk.LEFT, padx=10)
    tk.Button(toggle_frame, text="Search Student", command=show_search_student_window).pack(side=tk.LEFT, padx=10)
    tk.Button(toggle_frame, text="ADD Student Grades", command=show_add_student_gpa_window).pack(side=tk.LEFT, padx=10)
    tk.Button(toggle_frame, text="Update Default GPA", command=show_update_gpa_window).pack(side=tk.LEFT, padx=10)

    # ---------------------- Window 1: Add Student ----------------------
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

    tk.Button(add_frame, text="Add Student",
              command=lambda: add_student(student_id_entry, student_name_entry, email_entry,
                                          school_entry, dropdown, password_entry)).grid(row=6, columnspan=2, pady=10)

    add_frame.pack(padx=10, pady=10)

    # ---------------------- Window 2: Search Student ----------------------
    search_frame = tk.Frame(root)

    tk.Label(search_frame, text="Search Student Name").grid(row=0, column=0, padx=10, pady=5)
    search_name_entry = tk.Entry(search_frame)
    search_name_entry.grid(row=0, column=1, padx=10, pady=5)

    tk.Button(search_frame, text="Search",
              command=lambda: search_student(search_name_entry, student_info_text)).grid(row=1, columnspan=2, pady=10)

    student_info_text = tk.Text(root, width=50, height=10)

    # ---------------------- Window 3: ADD Grades ----------------------
    add_grade_frame = tk.Frame(root)

    def update_student_name(*args):
        student_id = student_id_entry2.get()
        student_name = get_student_name(student_id)
        student_name_entry2.delete(0, tk.END)  # Clear the existing text
        student_name_entry2.insert(0, student_name)  # Insert the new name

    def update_module_name(*args):
        module_code = module_code_entry.get()
        module_name = get_module_name(module_code)
        module_name_entry.delete(0, tk.END)  # Clear the existing text
        module_name_entry.insert(0, module_name)  # Insert the new name

    tk.Label(add_grade_frame, text="Student ID").grid(row=0, column=0, padx=10, pady=5)
    student_id_entry2 = tk.Entry(add_grade_frame)
    student_id_entry2.grid(row=0, column=1, padx=10, pady=5)

    tk.Label(add_grade_frame, text="Student Name").grid(row=1, column=0, padx=10, pady=5)
    student_name_entry2 = tk.Entry(add_grade_frame)
    student_name_entry2.grid(row=1, column=1, padx=10, pady=5)

    # Trace the 'student_id_entry' field for changes
    student_id_entry2.bind("<KeyRelease>", update_student_name)

    tk.Label(add_grade_frame, text="Module Code").grid(row=3, column=0, padx=10, pady=5)
    module_code_entry = tk.Entry(add_grade_frame)
    module_code_entry.grid(row=3, column=1, padx=10, pady=5)

    tk.Label(add_grade_frame, text="Module Name").grid(row=4, column=0, padx=10, pady=5)
    module_name_entry = tk.Entry(add_grade_frame)
    module_name_entry.grid(row=4, column=1, padx=10, pady=5)

    # Trace the 'student_id_entry' field for changes
    module_code_entry.bind("<KeyRelease>", update_module_name)

    tk.Label(add_grade_frame, text="Semester").grid(row=5, column=0, padx=10, pady=5)
    dropdown2 = ttk.Combobox(add_grade_frame, values=["1", "2", "3"])
    dropdown2.grid(row=5, column=1, padx=10, pady=5)

    tk.Label(add_grade_frame, text="Grade Point").grid(row=6, column=0, padx=10, pady=5)
    gp_entry = tk.Entry(add_grade_frame)
    gp_entry.grid(row=6, column=1, padx=10, pady=5)

    tk.Label(add_grade_frame, text="Year").grid(row=7, column=0, padx=10, pady=5)
    year_entry = tk.Entry(add_grade_frame)
    year_entry.grid(row=7, column=1, padx=10, pady=5)

    # Set default value for the year entry
    year_entry.insert(0, "Format: XXXX/XXXX")  # This sets "2025" as the default value

    tk.Button(add_grade_frame, text="Add Grade",
              command=lambda: add_grades(student_id_entry2, module_code_entry, module_name_entry,
                                          gp_entry, dropdown2, year_entry)).grid(row=8, columnspan=2, pady=10)



    # ---------------------- Window 4: Update GPA Default----------------------
    update_gpa_frame = tk.Frame(root)
    update_gpa_frame.pack(padx=10, pady=10)

    def change_gpa_and_update_label():
        new_gpa = up_gpa_entry.get()
        update_gpa_threshold(new_gpa)  # Step 1: Update GPA

        # Step 2: Wait 500ms before refreshing label
        update_gpa_frame.after(500, lambda: current_gpa_label.config(
            text=f"Current GPA Threshold: {get_current_gpa()}"
        ))

    # Current GPA label (initialized with the current GPA from Prolog)
    current_gpa = get_current_gpa()
    current_gpa_label = tk.Label(update_gpa_frame, text=f"Current GPA Threshold: {current_gpa}")
    current_gpa_label.grid(row=0, columnspan=2, pady=5)

    tk.Label(update_gpa_frame, text="Enter New GPA").grid(row=2, column=0, padx=10, pady=5)
    up_gpa_entry = tk.Entry(update_gpa_frame)
    up_gpa_entry.grid(row=2, column=1, padx=10, pady=5)

    # Use the function with delay
    tk.Button(update_gpa_frame, text="Change Default GPA",
              command=change_gpa_and_update_label).grid(row=3, columnspan=2, pady=10)

    # Start with Add Student window
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
        show_admin_dashboard()
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

if __name__ == "__main__":
    create_gui()
