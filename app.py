from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_mysqldb import MySQL
import MySQLdb.cursors
from datetime import datetime, timedelta


app = Flask(__name__)
app.secret_key = 'your_secret_key'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'intpt_easms'

mysql = MySQL(app)

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        try:
            # Check employee table first
            cursor.execute("SELECT * FROM employees WHERE username = %s AND password = %s", (username, password))
            employee = cursor.fetchone()

            # Check admin table
            cursor.execute("SELECT * FROM admin_accounts WHERE username = %s AND password = %s", (username, password))
            admin = cursor.fetchone()

            if employee:
                session['user_id'] = employee['employee_id']
                session['user_type'] = 'employee' 
                return redirect(url_for('dashboard', employee_id=employee['employee_id']))
                
            elif admin:
                session['admin_id'] = admin['admin_id']
                session['user_type'] = 'admin' 
                return redirect(url_for('admin_dashboard', admin_id=admin['admin_id']))
                
            else:
                flash('Invalid username or password', 'danger')
                return redirect(url_for('home'))
                
        except Exception as e:
            flash(f'Database error: {str(e)}', 'danger')
            return redirect(url_for('home'))
        finally:
            cursor.close()
            
    return render_template('login.html')

@app.route('/dashboard/<int:employee_id>')
def dashboard(employee_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    # Fetch employee personal data
    cursor.execute("""
        SELECT first_name, last_name, position, birthdate, contact_number, address 
        FROM employees 
        WHERE employee_id = %s
    """, (employee_id,))
    employee_data = cursor.fetchone()
    
    # Fetch payroll data for summary
    cursor.execute("""
        SELECT total_hours, net_salary 
        FROM payroll 
        WHERE employee_id = %s
    """, (employee_id,))
    payroll_data = cursor.fetchone()
    
    cursor.close()
    
    # Check if employee exists
    if not employee_data:
        return "Employee not found", 404
    
    template_data = {
        'employee_id': employee_id,
        'first_name': employee_data['first_name'],
        'position': employee_data['position'],
        'birthdate': employee_data['birthdate'].strftime('%Y-%m-%d') if employee_data['birthdate'] else 'N/A',
        'contact_number': employee_data['contact_number'],
        'address': employee_data['address'],
        'achieved_hours': payroll_data['total_hours'] if payroll_data else 'N/A',
        'achieved_net_salary': f"₱{payroll_data['net_salary']:,.2f}" if payroll_data else 'N/A'
    }
    
    return render_template('Employee_Dashboard.html', **template_data)

@app.route('/attendance/<int:employee_id>')
def attendance(employee_id):
    # Security check to ensure the logged-in user can only access their own attendance
    if 'user_id' not in session or session['user_id'] != employee_id:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('home'))
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    # Fetch employee data
    cursor.execute("""
        SELECT first_name, last_name 
        FROM employees 
        WHERE employee_id = %s
    """, (employee_id,))
    employee_data = cursor.fetchone()
    
    # Fetch attendance logs for this employee
    cursor.execute("""
        SELECT attendance_id, date_in, date_out, time_in, time_out, hours_worked, hours_overtime
        FROM attendance_logs 
        WHERE employee_id = %s 
        ORDER BY date_in DESC, time_in DESC
    """, (employee_id,))
    attendance_logs = cursor.fetchall()
    
    # Get total work hours and overtime hours from payroll table
    cursor.execute("""
        SELECT total_hours, total_overtime_hours
        FROM payroll
        WHERE employee_id = %s
    """, (employee_id,))
    payroll_totals = cursor.fetchone()
    
    cursor.close()
    
    if not employee_data:
        return "Employee not found", 404
    
    # Process attendance logs to ensure proper formatting
    processed_logs = []
    for log in attendance_logs:
        processed_log = dict(log)
        
        # Format dates properly
        if processed_log['date_in']:
            processed_log['date_in_formatted'] = processed_log['date_in'].strftime('%Y-%m-%d') if hasattr(processed_log['date_in'], 'strftime') else str(processed_log['date_in'])
        else:
            processed_log['date_in_formatted'] = 'N/A'
            
        if processed_log['date_out']:
            processed_log['date_out_formatted'] = processed_log['date_out'].strftime('%Y-%m-%d') if hasattr(processed_log['date_out'], 'strftime') else str(processed_log['date_out'])
        else:
            processed_log['date_out_formatted'] = 'N/A'
        
        # Format times properly
        if processed_log['time_in']:
            processed_log['time_in_formatted'] = processed_log['time_in'].strftime('%H:%M:%S') if hasattr(processed_log['time_in'], 'strftime') else str(processed_log['time_in'])
        else:
            processed_log['time_in_formatted'] = 'N/A'
            
        if processed_log['time_out']:
            processed_log['time_out_formatted'] = processed_log['time_out'].strftime('%H:%M:%S') if hasattr(processed_log['time_out'], 'strftime') else str(processed_log['time_out'])
        else:
            processed_log['time_out_formatted'] = 'N/A'
        
        # Format hours as decimal numbers (not datetime objects)
        processed_log['hours_worked_formatted'] = f"{float(processed_log['hours_worked']):.2f}" if processed_log['hours_worked'] is not None else "0.00"
        processed_log['hours_overtime_formatted'] = f"{float(processed_log['hours_overtime']):.2f}" if processed_log['hours_overtime'] is not None else "0.00"
        
        processed_logs.append(processed_log)
    
    template_data = {
        'employee_id': employee_id,
        'employee_name': f"{employee_data['first_name']} {employee_data['last_name']}",
        'attendance_logs': processed_logs,
        'total_work_hours': float(payroll_totals['total_hours']) if payroll_totals and payroll_totals['total_hours'] else 0.0,
        'total_overtime_hours': float(payroll_totals['total_overtime_hours']) if payroll_totals and payroll_totals['total_overtime_hours'] else 0.0
    }
    
    return render_template('Employee_Attendance.html', **template_data)

@app.route('/time_action', methods=['POST'])
def time_action():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'})
    
    employee_id = session['user_id']
    action = request.json.get('action')
    time_value = request.json.get('time')
    date_value = request.json.get('date')
    
    cursor = mysql.connection.cursor()
    
    try:
        if action == 'time_in':
            # Check for existing time-in without time-out
            cursor.execute("""
                SELECT COUNT(*) FROM attendance_logs 
                WHERE employee_id = %s AND time_out IS NULL
            """, (employee_id,))
            if cursor.fetchone()[0] > 0:
                return jsonify({'success': False, 'message': 'Complete your previous time record first'})
            
            # Insert new time-in record
            cursor.execute("""
                INSERT INTO attendance_logs (employee_id, date_in, time_in)
                VALUES (%s, %s, %s)
            """, (employee_id, date_value, time_value))
            
            mysql.connection.commit()
            return jsonify({
                'success': True,
                'message': 'Time in saved successfully',
                'hasActiveTimeIn': True
            })
            
        elif action == 'time_out':
            # Find most recent time-in without time-out
            cursor.execute("""
                SELECT attendance_id, date_in, time_in 
                FROM attendance_logs 
                WHERE employee_id = %s AND time_out IS NULL
                ORDER BY date_in DESC, time_in DESC 
                LIMIT 1
            """, (employee_id,))
            
            record = cursor.fetchone()
            if not record:
                return jsonify({'success': False, 'message': 'No time-in found to pair with time-out'})
            
            attendance_id, date_in, time_in = record
            
            # Calculate duration (even if less than 1 hour)
            time_in_dt = datetime.combine(date_in, time_in)
            time_out_dt = datetime.combine(
                datetime.strptime(date_value, '%Y-%m-%d').date(),
                datetime.strptime(time_value, '%H:%M:%S').time()
            )
            
            # Handle overnight case
            if time_out_dt < time_in_dt:
                time_out_dt += timedelta(days=1)
            
            duration = (time_out_dt - time_in_dt).total_seconds() / 3600
            regular_hours = min(duration, 8.0)
            overtime = max(0, duration - 8.0)
            
            # Update with time-out and calculations
            cursor.execute("""
                UPDATE attendance_logs 
                SET date_out = %s,
                    time_out = %s,
                    hours_worked = %s,
                    hours_overtime = %s
                WHERE attendance_id = %s
            """, (date_value, time_value, regular_hours, overtime, attendance_id))
            
            mysql.connection.commit()
            return jsonify({
                'success': True,
                'message': 'Time out saved successfully',
                'hasActiveTimeIn': False
            })
            
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({'success': False, 'message': str(e)})
    finally:
        cursor.close()

@app.route('/check_active_timein')
def check_active_timein():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'})
    
    employee_id = session['user_id']
    cursor = mysql.connection.cursor()
    
    try:
        # Check if there's any time-in without time-out
        cursor.execute("""
            SELECT COUNT(*) 
            FROM attendance_logs 
            WHERE employee_id = %s AND time_out IS NULL
        """, (employee_id,))
        count = cursor.fetchone()[0]
        
        return jsonify({
            'success': True,
            'hasActiveTimeIn': count > 0
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
    finally:
        cursor.close()

@app.route('/save_attendance', methods=['POST'])
def save_attendance():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'})
    
    employee_id = session['user_id']
    data = request.json
    
    cursor = mysql.connection.cursor()
    
    try:
        # Calculate hours worked
        time_in = datetime.strptime(data['time_in'], '%H:%M:%S').time()
        time_out = datetime.strptime(data['time_out'], '%H:%M:%S').time()
        date_in = datetime.strptime(data['date_in'], '%Y-%m-%d').date()
        date_out = datetime.strptime(data['date_out'], '%Y-%m-%d').date()
        
        time_in_dt = datetime.combine(date_in, time_in)
        time_out_dt = datetime.combine(date_out, time_out)
        
        # Handle overnight case
        if time_out_dt < time_in_dt:
            time_out_dt += timedelta(days=1)
        
        duration = (time_out_dt - time_in_dt).total_seconds() / 3600
        regular_hours = min(duration, 8.0)
        overtime = max(0, duration - 8.0)
        
        # Insert complete record
        cursor.execute("""
            INSERT INTO attendance_logs 
            (employee_id, date_in, time_in, date_out, time_out, hours_worked, hours_overtime)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            employee_id,
            data['date_in'],
            data['time_in'],
            data['date_out'],
            data['time_out'],
            regular_hours,
            overtime
        ))
        
        mysql.connection.commit()
        return jsonify({'success': True, 'message': 'Attendance saved'})
        
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({'success': False, 'message': str(e)})
    finally:
        cursor.close()


@app.route('/salary/<int:employee_id>')
def salary(employee_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    cursor.execute("SELECT last_name, position FROM employees WHERE employee_id = %s", (employee_id,))
    employee_data = cursor.fetchone()

    cursor.execute("SELECT * FROM payroll WHERE employee_id = %s", (employee_id,))
    payroll_data = cursor.fetchone()
    
    if not employee_data or not payroll_data:
        cursor.close()
        return "Employee not found", 404
    
    if payroll_data.get('total_hours') is not None:
        total_work_hours = float(payroll_data['total_hours'])
    else:
        cursor.execute("SELECT COALESCE(SUM(hours_worked), 0) as total FROM attendance_logs WHERE employee_id = %s", (employee_id,))
        total_work_hours = float(cursor.fetchone()['total'])
    
    if payroll_data.get('total_overtime_hours') is not None:
        total_overtime_hours = float(payroll_data['total_overtime_hours'])
    else:
        cursor.execute("SELECT COALESCE(SUM(hours_overtime), 0) as total FROM attendance_logs WHERE employee_id = %s", (employee_id,))
        total_overtime_hours = float(cursor.fetchone()['total'])
    
    # Get pay rates and bonus
    basic_pay_per_hour = float(payroll_data['basic_pay_per_hour'])
    overtime_pay_per_hour = float(payroll_data['overtime_pay_per_hour'])
    bonus = float(payroll_data['bonus'] or 0)
    monthly_basic = float(payroll_data['basic_salary'])
    
    # Calculate Gross Salary for this period
    period_gross = (total_work_hours * basic_pay_per_hour) + (total_overtime_hours * overtime_pay_per_hour)
    
    # Calculate monthly equivalent for tax purposes
    if total_work_hours > 0:
        hours_per_month = 160  # Standard 40 hrs/week * 4 weeks
        monthly_gross = (period_gross / total_work_hours) * hours_per_month
    else:
        monthly_gross = monthly_basic
    
    # ----- DEDUCTION CALCULATIONS -----
    # PAG-IBIG (Fixed)
    pagibig = 200.00 if monthly_gross >= 1000 else 0
    
    # PhilHealth (4% of monthly salary, with min/max)
    if monthly_basic <= 10000:
        philhealth = 400.00
    elif monthly_basic <= 80000:
        philhealth = monthly_basic * 0.04
    else:
        philhealth = 3200.00
    
    # SSS (Based on monthly salary brackets)
    sss_brackets = [
        (0, 4250, 180),
        (4250, 4750, 202.50),
        (4750, 5250, 225),
        (5250, 5750, 247.50),
        (5750, 6250, 270),
        (6250, 6750, 292.50),
        (6750, 7250, 315),
        (7250, 7750, 337.50),
        (7750, 8250, 360),
        (8250, 8750, 382.50),
        (8750, 9250, 405),
        (9250, 9750, 427.50),
        (9750, 10250, 450),
        (10250, 10750, 472.50),
        (10750, 11250, 495),
        (11250, 11750, 517.50),
        (11750, 12250, 540),
        (12250, 12750, 562.50),
        (12750, 13250, 585),
        (13250, 13750, 607.50),
        (13750, 14250, 630),
        (14250, 14750, 652.50),
        (14750, 15250, 675),
        (15250, 15750, 697.50),
        (15750, 16250, 720),
        (16250, 16750, 742.50),
        (16750, 17250, 765),
        (17250, 17750, 787.50),
        (17750, 18250, 810),
        (18250, 18750, 832.50),
        (18750, 19250, 855),
        (19250, 19750, 877.50),
        (19750, 20250, 900),
        (20250, 20750, 922.50),
        (20750, 21250, 945),
        (21250, 21750, 967.50),
        (21750, 22250, 990),
        (22250, 22750, 1012.50),
        (22750, 23250, 1035),
        (23250, 23750, 1057.50),
        (23750, 24250, 1080),
        (24250, 24750, 1102.50),
        (24750, 25250, 1125),
        (25250, 25750, 1147.50),
        (25750, 26250, 1170),
        (26250, 26750, 1192.50),
        (26750, 27250, 1215),
        (27250, 27750, 1237.50),
        (27750, 28250, 1260),
        (28250, 28750, 1282.50),
        (28750, 29250, 1305),
        (29250, 29750, 1327.50),
        (29750, float('inf'), 1350)
    ]
    
    sss = 1350
    for lower, upper, contribution in sss_brackets:
        if lower <= monthly_basic < upper:
            sss = contribution
            break
    
    # Tax Calculation
    if monthly_basic < 20833:
        tax = 0
    elif monthly_basic < 33332 and monthly_basic >= 20833:
        tax = (monthly_basic - 20833) * 0.15
    elif monthly_basic < 66666 and monthly_basic >= 33333:
        tax = 1875 + 0.20 * (monthly_basic - 33333) 
    elif monthly_basic < 166666 and monthly_basic >=66667:
        tax = 8541.80 +  0.25* (monthly_basic - 66667)
    elif monthly_basic < 666666 and monthly_basic >= 166667:
        tax = 33541.80 + 0.30 * (monthly_basic - 166667)
    else:
        tax = 183541.80 +  0.35 *(monthly_basic - 666667)
    
    # Scale tax to current period
    if monthly_basic > 0:
        tax = (tax / monthly_basic) * period_gross
    
    # Total Deductions
    total_deduction = pagibig + philhealth + sss + tax
    
    # Net Salary for this period
    net_salary = (period_gross - total_deduction) + bonus
    
    # Update payroll record
    cursor.execute("""
        UPDATE payroll 
        SET total_hours = %s,
            total_overtime_hours = %s,
            gross_salary = %s,
            pagibig = %s,
            philhealth = %s,
            SSS = %s,
            tax = %s,
            total_deduction = %s,
            net_salary = %s,
            bonus = %s
        WHERE employee_id = %s
    """, (
        total_work_hours,
        total_overtime_hours,
        period_gross,
        pagibig,
        philhealth,
        sss,
        tax,
        total_deduction,
        net_salary,
        bonus,
        employee_id
    ))
    mysql.connection.commit()
    cursor.close()
    
    data = [
        employee_id,
        employee_data['last_name'],
        payroll_data['payroll_id'],
        f"{total_work_hours:.2f}",
        f"{total_overtime_hours:.2f}",
        f"{monthly_basic:.2f}",
        f"{basic_pay_per_hour:.2f}",
        f"{overtime_pay_per_hour:.2f}",
        f"{period_gross:.2f}",
        f"{pagibig:.2f}",
        f"{philhealth:.2f}",
        f"{sss:.2f}",
        f"{tax:.2f}",
        f"{total_deduction:.2f}",
        f"{bonus:.2f}",
        f"{net_salary:.2f}"
    ]
    
    return render_template('Employee_Salary.html', data=data)

    
    #------------ ADMIN DASHBOARD PART----------
@app.route('/admin_dashboard/<int:admin_id>')
def admin_dashboard(admin_id):
    # Add security check
    if 'admin_id' not in session or session['admin_id'] != admin_id:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('home'))
    
    # Get admin info and statistics
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    try:
        # Get admin name
        cursor.execute("SELECT name FROM admin_accounts WHERE admin_id = %s", (admin_id,))
        admin_data = cursor.fetchone()
        
        # Get employee count
        cursor.execute("SELECT COUNT(*) as employee_count FROM employees")
        employee_count = cursor.fetchone()['employee_count']
        
        # Get admin count
        cursor.execute("SELECT COUNT(*) as admin_count FROM admin_accounts")
        admin_count = cursor.fetchone()['admin_count']
        
        # Get current month
        from datetime import datetime
        current_month = datetime.now().strftime('%B %Y')
        
        template_data = {
            'admin_id': admin_id,
            'name': admin_data['name'] if admin_data else 'Administrator',
            'employee_count': employee_count,
            'admin_count': admin_count,
            'current_month': current_month,
            'total_accounts': employee_count + admin_count
        }
        
        return render_template('Admin_Dashboard.html', **template_data)
        
    except Exception as e:
        flash(f'Error loading dashboard: {str(e)}', 'danger')
        return redirect(url_for('home'))
    finally:
        cursor.close()

@app.route('/admin_attendance/<int:admin_id>')
def admin_attendance(admin_id):
    if 'admin_id' not in session or session['admin_id'] != admin_id:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('home'))
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    try:
        # Get all attendance logs with employee information
        cursor.execute("""
            SELECT 
                al.attendance_id,
                al.employee_id,
                e.last_name,
                al.date_in,
                al.time_in,
                al.date_out,
                al.time_out,
                al.hours_worked,
                al.hours_overtime
            FROM attendance_logs al
            JOIN employees e ON al.employee_id = e.employee_id
            ORDER BY al.date_in DESC, al.time_in DESC
        """)
        
        attendance_logs = cursor.fetchall()
        
        # Process attendance logs for proper formatting
        processed_logs = []
        for log in attendance_logs:
            processed_log = dict(log)
            
            # Format dates
            if processed_log['date_in']:
                processed_log['date_in_formatted'] = processed_log['date_in'].strftime('%Y-%m-%d') if hasattr(processed_log['date_in'], 'strftime') else str(processed_log['date_in'])
            else:
                processed_log['date_in_formatted'] = 'N/A'
                
            if processed_log['date_out']:
                processed_log['date_out_formatted'] = processed_log['date_out'].strftime('%Y-%m-%d') if hasattr(processed_log['date_out'], 'strftime') else str(processed_log['date_out'])
            else:
                processed_log['date_out_formatted'] = 'N/A'
            
            # Format times
            if processed_log['time_in']:
                processed_log['time_in_formatted'] = processed_log['time_in'].strftime('%H:%M:%S') if hasattr(processed_log['time_in'], 'strftime') else str(processed_log['time_in'])
            else:
                processed_log['time_in_formatted'] = 'N/A'
                
            if processed_log['time_out']:
                processed_log['time_out_formatted'] = processed_log['time_out'].strftime('%H:%M:%S') if hasattr(processed_log['time_out'], 'strftime') else str(processed_log['time_out'])
            else:
                processed_log['time_out_formatted'] = 'N/A'
            
            # Format hours
            processed_log['hours_worked_formatted'] = f"{float(processed_log['hours_worked']):.2f}" if processed_log['hours_worked'] is not None else "0.00"
            processed_log['hours_overtime_formatted'] = f"{float(processed_log['hours_overtime']):.2f}" if processed_log['hours_overtime'] is not None else "0.00"
            
            processed_logs.append(processed_log)
        
        return render_template('Admin_Attendance.html', 
                             admin_id=admin_id, 
                             attendance_logs=processed_logs)
        
    except Exception as e:
        flash(f'Error loading attendance data: {str(e)}', 'danger')
        return redirect(url_for('admin_dashboard', admin_id=admin_id))
    finally:
        cursor.close()

@app.route('/search_attendance/<int:admin_id>', methods=['POST'])
def search_attendance(admin_id):
    # Security check
    if 'admin_id' not in session or session['admin_id'] != admin_id:
        return jsonify({'success': False, 'message': 'Unauthorized access'})
    
    employee_id = request.json.get('employee_id')
    
    if not employee_id:
        return jsonify({'success': False, 'message': 'Employee ID is required'})
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    try:
        # Search for attendance logs by employee ID
        cursor.execute("""
            SELECT 
                al.attendance_id,
                al.employee_id,
                e.last_name,
                al.date_in,
                al.time_in,
                al.date_out,
                al.time_out,
                al.hours_worked,
                al.hours_overtime
            FROM attendance_logs al
            JOIN employees e ON al.employee_id = e.employee_id
            WHERE al.employee_id = %s
            ORDER BY al.date_in DESC, al.time_in DESC
        """, (employee_id,))
        
        attendance_logs = cursor.fetchall()
        
        if not attendance_logs:
            return jsonify({'success': False, 'message': 'No attendance records found for this employee'})
        
        processed_logs = []
        for log in attendance_logs:
            processed_log = {
                'attendance_id': log['attendance_id'],
                'employee_id': log['employee_id'],
                'last_name': log['last_name'],
                'date_in': log['date_in'].strftime('%Y-%m-%d') if log['date_in'] else 'N/A',
                'time_in': log['time_in'].strftime('%H:%M:%S') if log['time_in'] else 'N/A',
                'date_out': log['date_out'].strftime('%Y-%m-%d') if log['date_out'] else 'N/A',
                'time_out': log['time_out'].strftime('%H:%M:%S') if log['time_out'] else 'N/A',
                'hours_worked': f"{float(log['hours_worked']):.2f}" if log['hours_worked'] is not None else "0.00",
                'hours_overtime': f"{float(log['hours_overtime']):.2f}" if log['hours_overtime'] is not None else "0.00"
            }
            processed_logs.append(processed_log)
        
        return jsonify({'success': True, 'data': processed_logs})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
    finally:
        cursor.close()

@app.route('/manage_attendance/<int:admin_id>', methods=['POST'])
def manage_attendance(admin_id):
    # Security check
    if 'admin_id' not in session or session['admin_id'] != admin_id:
        return jsonify({'success': False, 'message': 'Unauthorized access'})
    
    action = request.json.get('action')
    data = request.json.get('data', {})
    
    cursor = mysql.connection.cursor()
    
    try:
        if action == 'add':
            # Add new attendance record
            cursor.execute("""
                INSERT INTO attendance_logs 
                (employee_id, date_in, time_in, date_out, time_out, hours_worked, hours_overtime)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                data['employee_id'],
                data['date_in'],
                data['time_in'],
                data['date_out'],
                data['time_out'],
                data['hours_worked'],
                data['hours_overtime']
            ))
            
        elif action == 'update':
            # Update existing attendance record
            cursor.execute("""
                UPDATE attendance_logs 
                SET employee_id = %s, date_in = %s, time_in = %s, 
                    date_out = %s, time_out = %s, hours_worked = %s, hours_overtime = %s
                WHERE attendance_id = %s
            """, (
                data['employee_id'],
                data['date_in'],
                data['time_in'],
                data['date_out'],
                data['time_out'],
                data['hours_worked'],
                data['hours_overtime'],
                data['attendance_id']
            ))
            
        elif action == 'delete':
            # Delete attendance record
            cursor.execute("DELETE FROM attendance_logs WHERE attendance_id = %s", (data['attendance_id'],))
        
        mysql.connection.commit()
        return jsonify({'success': True, 'message': f'Attendance record {action}d successfully'})
        
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({'success': False, 'message': str(e)})
    finally:
        cursor.close()

@app.route('/admin_salary/<int:admin_id>')
def admin_salary(admin_id):
    # Security check
    if 'admin_id' not in session or session['admin_id'] != admin_id:
        return redirect(url_for('home'))
    
    return render_template('Admin_Salary.html', admin_id=admin_id)

@app.route('/get_all_payroll/<int:admin_id>')
def get_all_payroll(admin_id):
    # Security check
    if 'admin_id' not in session or session['admin_id'] != admin_id:
        return jsonify({'success': False, 'message': 'Unauthorized access'})
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    try:
        cursor.execute("""
            SELECT 
                p.payroll_id,
                p.employee_id,
                e.last_name,
                p.total_hours,
                p.total_overtime_hours,
                p.basic_salary,
                p.basic_pay_per_hour,
                p.overtime_pay_per_hour,
                p.gross_salary,
                p.pagibig,
                p.philhealth,
                p.SSS,
                p.tax,
                p.total_deduction,
                p.bonus,
                p.net_salary
            FROM payroll p
            JOIN employees e ON p.employee_id = e.employee_id
            ORDER BY p.payroll_id
        """)
        
        payroll_data = cursor.fetchall()
        

        for record in payroll_data:
            for key, value in record.items():
                if hasattr(value, '__float__'): 
                    record[key] = float(value)
        
        return jsonify({'success': True, 'data': payroll_data})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
    finally:
        cursor.close()

@app.route('/search_payroll/<int:admin_id>', methods=['POST'])
def search_payroll(admin_id):
    # Security check
    if 'admin_id' not in session or session['admin_id'] != admin_id:
        return jsonify({'success': False, 'message': 'Unauthorized access'})
    
    employee_id = request.json.get('employee_id')
    
    if not employee_id:
        return jsonify({'success': False, 'message': 'Employee ID is required'})
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    try:
        cursor.execute("""
            SELECT 
                p.payroll_id,
                p.employee_id,
                e.last_name,
                p.total_hours,
                p.total_overtime_hours,
                p.basic_salary,
                p.basic_pay_per_hour,
                p.overtime_pay_per_hour,
                p.gross_salary,
                p.pagibig,
                p.philhealth,
                p.SSS,
                p.tax,
                p.total_deduction,
                p.bonus,
                p.net_salary
            FROM payroll p
            JOIN employees e ON p.employee_id = e.employee_id
            WHERE p.employee_id = %s
        """, (employee_id,))
        
        payroll_record = cursor.fetchone()
        
        if not payroll_record:
            return jsonify({'success': False, 'message': 'No payroll record found for this employee'})
        
        for key, value in payroll_record.items():
            if hasattr(value, '__float__'): 
                payroll_record[key] = float(value)
        
        return jsonify({'success': True, 'data': payroll_record})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
    finally:
        cursor.close()

@app.route('/manage_payroll/<int:admin_id>', methods=['POST'])
def manage_payroll(admin_id):
    # Security check
    if 'admin_id' not in session or session['admin_id'] != admin_id:
        return jsonify({'success': False, 'message': 'Unauthorized access'})
    
    action = request.json.get('action')
    data = request.json.get('data', {})
    
    cursor = mysql.connection.cursor()
    
    try:
        if action == 'add':
            cursor.execute("""
                INSERT INTO payroll 
                (employee_id, total_hours, total_overtime_hours, basic_salary, 
                 basic_pay_per_hour, overtime_pay_per_hour, gross_salary, 
                 pagibig, philhealth, SSS, tax, total_deduction, bonus, net_salary)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                data['employee_id'], 
                float(data.get('total_hours', 0)), 
                float(data.get('total_overtime_hours', 0)),
                float(data.get('basic_salary', 0)), 
                float(data.get('basic_pay_per_hour', 0)), 
                float(data.get('overtime_pay_per_hour', 0)),
                float(data.get('gross_salary', 0)), 
                float(data.get('pagibig', 0)), 
                float(data.get('philhealth', 0)), 
                float(data.get('SSS', 0)),
                float(data.get('tax', 0)), 
                float(data.get('total_deduction', 0)), 
                float(data.get('bonus', 0)), 
                float(data.get('net_salary', 0))
            ))
            
        elif action == 'update':
            cursor.execute("""
                UPDATE payroll 
                SET employee_id = %s, total_hours = %s, total_overtime_hours = %s,
                    basic_salary = %s, basic_pay_per_hour = %s, overtime_pay_per_hour = %s,
                    gross_salary = %s, pagibig = %s, philhealth = %s, SSS = %s,
                    tax = %s, total_deduction = %s, bonus = %s, net_salary = %s
                WHERE payroll_id = %s
            """, (
                data['employee_id'], 
                float(data.get('total_hours', 0)), 
                float(data.get('total_overtime_hours', 0)),
                float(data.get('basic_salary', 0)), 
                float(data.get('basic_pay_per_hour', 0)), 
                float(data.get('overtime_pay_per_hour', 0)),
                float(data.get('gross_salary', 0)), 
                float(data.get('pagibig', 0)), 
                float(data.get('philhealth', 0)), 
                float(data.get('SSS', 0)),
                float(data.get('tax', 0)), 
                float(data.get('total_deduction', 0)), 
                float(data.get('bonus', 0)), 
                float(data.get('net_salary', 0)),
                data['payroll_id']
            ))
            
        elif action == 'delete':
            cursor.execute("DELETE FROM payroll WHERE payroll_id = %s", (data['payroll_id'],))
        
        mysql.connection.commit()
        return jsonify({'success': True, 'message': f'Payroll record {action}d successfully'})
        
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({'success': False, 'message': str(e)})
    finally:
        cursor.close()

@app.route('/get_all_employees/<int:admin_id>')
def get_all_employees(admin_id):
    # Security check
    if 'admin_id' not in session or session['admin_id'] != admin_id:
        return jsonify({'success': False, 'message': 'Unauthorized access'})
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    try:
        cursor.execute("""
            SELECT employee_id, first_name, last_name, position, birthdate, 
                   contact_number, address, username, password
            FROM employees
            ORDER BY employee_id
        """)
        
        employees = cursor.fetchall()
        
        for emp in employees:
            if emp['birthdate']:
                emp['birthdate'] = emp['birthdate'].strftime('%Y-%m-%d')
        
        return jsonify({'success': True, 'data': employees})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
    finally:
        cursor.close()

@app.route('/search_employee/<int:admin_id>', methods=['POST'])
def search_employee(admin_id):
    # Security check
    if 'admin_id' not in session or session['admin_id'] != admin_id:
        return jsonify({'success': False, 'message': 'Unauthorized access'})
    
    employee_id = request.json.get('employee_id')
    
    if not employee_id:
        return jsonify({'success': False, 'message': 'Employee ID is required'})
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    try:
        cursor.execute("""
            SELECT employee_id, first_name, last_name, position, birthdate, 
                   contact_number, address, username, password
            FROM employees
            WHERE employee_id = %s
        """, (employee_id,))
        
        employee = cursor.fetchone()
        
        if not employee:
            return jsonify({'success': False, 'message': 'Employee not found'})
        
        # Format birthdate
        if employee['birthdate']:
            employee['birthdate'] = employee['birthdate'].strftime('%Y-%m-%d')
        
        return jsonify({'success': True, 'data': employee})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
    finally:
        cursor.close()
        
@app.route('/admin_employee_data/<int:admin_id>')
def admin_employee_data(admin_id):
    # Security check
    if 'admin_id' not in session or session['admin_id'] != admin_id:
        return redirect(url_for('home'))
    
    return render_template('Admin_EmployeeData.html', admin_id=admin_id)

@app.route('/manage_employee/<int:admin_id>', methods=['POST'])
def manage_employee(admin_id):
    # Security check
    if 'admin_id' not in session or session['admin_id'] != admin_id:
        return jsonify({'success': False, 'message': 'Unauthorized access'})
    
    action = request.json.get('action')
    data = request.json.get('data', {})
    
    cursor = mysql.connection.cursor()
    
    try:
        if action == 'add':
            cursor.execute("""
                INSERT INTO employees 
                (first_name, last_name, position, birthdate, contact_number, address, username, password)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                data['first_name'], data['last_name'], data['position'],
                data['birthdate'] if data['birthdate'] else None,
                data['contact_number'], data['address'], 
                data['username'], data['password']
            ))
            
        elif action == 'update':
            cursor.execute("""
                UPDATE employees 
                SET first_name = %s, last_name = %s, position = %s, 
                    birthdate = %s, contact_number = %s, address = %s, 
                    username = %s, password = %s
                WHERE employee_id = %s
            """, (
                data['first_name'], data['last_name'], data['position'],
                data['birthdate'] if data['birthdate'] else None,
                data['contact_number'], data['address'], 
                data['username'], data['password'], data['employee_id']
            ))
            
        elif action == 'delete':
            # Check if employee has related records
            cursor.execute("SELECT COUNT(*) FROM attendance_logs WHERE employee_id = %s", (data['employee_id'],))
            attendance_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM payroll WHERE employee_id = %s", (data['employee_id'],))
            payroll_count = cursor.fetchone()[0]
            
            if attendance_count > 0 or payroll_count > 0:
                return jsonify({'success': False, 'message': 'Cannot delete employee with existing attendance or payroll records'})
            
            cursor.execute("DELETE FROM employees WHERE employee_id = %s", (data['employee_id'],))
        
        mysql.connection.commit()
        return jsonify({'success': True, 'message': f'Employee {action}ed successfully'})
        
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({'success': False, 'message': str(e)})
    finally:
        cursor.close()
        
        
if __name__ == '__main__':
    app.run(debug=True)
    
    
