# Employee Attendance and Salary Management System (EASMS)

A web-based employee attendance and salary management project made for our subject **Integrative Programming and Technologies**.  
It uses **Python Flask** for the backend and **MySQL** as the database.

---

## Features

### Employee Side
- Secure login and personalized dashboard  
- Record **Time In** and **Time Out**  
- View attendance logs and total working hours  
- View computed salary and deductions  

### Admin Side
- Secure admin login  
- Dashboard with employee and admin statistics  
- Manage employee attendance records  
- Add, edit, delete, or search attendance logs  
- View and manage payroll details  

---

## How to Run

1. Make sure you have **Python 3.8+** installed.  
2. Install the required dependencies:
   ```bash
   pip install flask flask-mysqldb
   ```
3. Set up your **MySQL database**:
   - Create a database named `intpt_easms`
   - Import the `intpt_easms.sql` file  
4. Open the project folder and update the database credentials in `app.py`:
   ```python
   app.config['MYSQL_HOST'] = 'localhost'
   app.config['MYSQL_USER'] = 'root'
   app.config['MYSQL_PASSWORD'] = ''
   app.config['MYSQL_DB'] = 'intpt_easms'
   ```
5. Run the Flask app:
   ```bash
   python app.py
   ```
6. Open your browser and go to:
   ```
   http://127.0.0.1:5000
   ```

---

## File Structure
```
project-folder/
│
├── app.py
├── intpt_easms.sql
│
├── templates/
│   ├── Admin_Attendance.html
│   ├── Admin_Dashboard.html
│   ├── Admin_EmployeeData.html
│   ├── Admin_Salary.html
│   ├── Employee_Attendance.html
│   ├── Employee_Dashboard.html
│   ├── Employee_Salary.html
│   └── Login.html
    └── images/
       ├── attendance.png
       ├── dashboard.png
       ├── employee.png
       ├── logo_admin.png
       ├── logo_employee.png
       ├── logo_login.png
       ├── logout.png
       └── salary.png
```
