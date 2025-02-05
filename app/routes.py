import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from flask_login import login_user, logout_user, login_required, current_user
from . import db, bcrypt
from datetime import datetime, timedelta
import pytz
import pandas as pd
from .models import Admin, Employee, Attendance, Report

from flask import send_file, flash, redirect, url_for


# Create a Blueprint
main = Blueprint('main', __name__)


# Define UK Timezone
UK_TIMEZONE = pytz.timezone('Europe/London')

def get_uk_time():
    """Returns the current time in the UK timezone"""
    return datetime.now(pytz.utc).astimezone(UK_TIMEZONE)


### ---------- HOME & AUTHENTICATION ROUTES ---------- ###

@main.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('main.login'))

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = Admin.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('main.dashboard'))
        else:
            flash('Invalid username or password.', 'danger')

    return render_template('login.html')

@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('main.login'))

@main.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

### ---------- EMPLOYEE MANAGEMENT ROUTES ---------- ###

@main.route('/add_employee', methods=['GET', 'POST'])
@login_required
def add_employee():
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        dob = request.form.get('dob')
        joining_date = request.form.get('joining_date')
        brp = request.form.get('brp')
        address = request.form.get('address')

        new_employee = Employee(
            first_name=first_name,
            last_name=last_name,
            dob=dob,
            joining_date=joining_date,
            brp=brp,
            address=address
        )
        db.session.add(new_employee)
        db.session.commit()

        flash('Employee added successfully!', 'success')
        return redirect(url_for('main.dashboard'))

    return render_template('add_employee.html')

@main.route('/list_employees')
@login_required
def list_employees():
    employees = Employee.query.all()
    return render_template('list_employees.html', employees=employees)

@main.route('/edit_employee/<int:employee_id>', methods=['GET', 'POST'])
@login_required
def edit_employee(employee_id):
    employee = Employee.query.get_or_404(employee_id)

    if request.method == 'POST':
        employee.first_name = request.form.get('first_name')
        employee.last_name = request.form.get('last_name')
        employee.dob = request.form.get('dob')
        employee.joining_date = request.form.get('joining_date')
        employee.brp = request.form.get('brp')
        employee.address = request.form.get('address')

        db.session.commit()
        flash(f'Employee {employee.first_name} {employee.last_name} updated successfully!', 'success')
        return redirect(url_for('main.list_employees'))

    return render_template('edit_employee.html', employee=employee)

@main.route('/delete_employee/<int:employee_id>', methods=['POST'])
@login_required
def delete_employee(employee_id):
    employee = Employee.query.get_or_404(employee_id)

    # Delete related attendance records before deleting the employee
    Attendance.query.filter_by(employee_id=employee.id).delete()

    # Now delete the employee
    db.session.delete(employee)
    
    try:
        db.session.commit()
        flash('Employee deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting employee: {str(e)}', 'danger')

    return redirect(url_for('main.list_employees'))


### ---------- ATTENDANCE ROUTES ---------- ###

@main.route('/attendance', methods=['GET', 'POST'])
@login_required
def attendance():
    if request.method == 'POST':
        employee_id = request.form.get('employee_id')
        action = request.form.get('action')
        custom_time = request.form.get('custom_time')

        if custom_time:
            action_time = datetime.strptime(custom_time, '%Y-%m-%dT%H:%M')
            action_time = UK_TIMEZONE.localize(action_time)
        else:
            action_time = datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(UK_TIMEZONE)

        employee = Employee.query.get_or_404(employee_id)

        if action == 'clock_in':
            last_record = Attendance.query.filter_by(employee_id=employee_id, clock_out=None).first()

            if last_record:
                flash(f'{employee.first_name} {employee.last_name} is already clocked in! Please clock out first.', 'warning')
            else:
                break_duration = Attendance.calculate_break_time(employee_id, action_time)
                new_record = Attendance(employee_id=employee_id, clock_in=action_time, break_time=break_duration)
                db.session.add(new_record)
                db.session.commit()
                flash(f'{employee.first_name} {employee.last_name} clocked in at {action_time.strftime("%Y-%m-%d %H:%M:%S")}', 'success')

        elif action == 'clock_out':
            record = Attendance.query.filter_by(employee_id=employee_id, clock_out=None).first()

            if record is None:
                flash(f'Error: No active clock-in record found for {employee.first_name} {employee.last_name}!', 'danger')
            else:
                record.clock_out = action_time
                record.total_work_hours = record.clock_out - record.clock_in - record.break_time
                db.session.commit()
                flash(f'{employee.first_name} {employee.last_name} clocked out at {action_time.strftime("%Y-%m-%d %H:%M:%S")}', 'success')

        return redirect(url_for('main.attendance'))

    employees = Employee.query.all()
    return render_template('attendance.html', employees=employees)

### ---------- ATTENDANCE REPORTS ---------- ###

REPORTS_FOLDER = "reports"
if not os.path.exists(REPORTS_FOLDER):
    os.makedirs(REPORTS_FOLDER)

### ---------- ATTENDANCE REPORT ROUTES ---------- ###
@main.route('/attendance_reports')
@login_required
def attendance_reports():
    reports = Report.query.order_by(Report.generated_on.desc()).all()
    employees = Employee.query.all()  # Fetch all employees for the dropdown
    return render_template('attendance_reports.html', reports=reports, employees=employees)


@main.route('/generate_employee_report', methods=['POST'])
@login_required
def generate_employee_report():
    employee_id = request.form.get('employee_id')
    report_type = request.form.get('report_type')  # 'weekly' or 'monthly'

    if not employee_id or not report_type:
        flash("Please select an employee and report type!", "danger")
        return redirect(url_for('main.attendance_reports'))

    # Fetch employee details
    employee = Employee.query.get_or_404(employee_id)

    # Define report start date
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=7) if report_type == "weekly" else end_date.replace(day=1)

    # Fetch attendance records only for the selected employee
    attendance_records = Attendance.query.filter(
        Attendance.employee_id == employee_id,
        Attendance.clock_in >= start_date,
        Attendance.clock_out != None
    ).all()

    # Convert data to a DataFrame
    data = []
    for record in attendance_records:
        data.append([
            employee.first_name + " " + employee.last_name,
            record.clock_in.strftime('%Y-%m-%d %H:%M:%S'),
            record.clock_out.strftime('%Y-%m-%d %H:%M:%S') if record.clock_out else "Still Clocked In",
            str(record.total_work_hours)
        ])

    if not data:
        flash(f"No attendance records found for {employee.first_name} {employee.last_name}.", "warning")
        return redirect(url_for('main.attendance_reports'))

    df = pd.DataFrame(data, columns=["Employee", "Clock In", "Clock Out", "Total Work Hours"])

    # Ensure reports folder exists
    if not os.path.exists(REPORTS_FOLDER):
        os.makedirs(REPORTS_FOLDER)

    # Generate filename
    filename = f"{employee.first_name}_{employee.last_name}_{report_type}_attendance_{end_date.strftime('%Y%m%d')}.xlsx"
    file_path = os.path.join(REPORTS_FOLDER, filename)

    # Save file
    df.to_excel(file_path, index=False, engine='openpyxl')

    # Save report info in DB
    new_report = Report(report_type=f"{report_type} ({employee.first_name} {employee.last_name})", file_path=file_path)
    db.session.add(new_report)
    db.session.commit()

    flash(f"{report_type.capitalize()} report for {employee.first_name} {employee.last_name} generated!", "success")
    return redirect(url_for('main.attendance_reports'))


@main.route('/download_report/<int:report_id>')
@login_required
def download_report(report_id):
    report = Report.query.get_or_404(report_id)

    # Convert the file path to an absolute path
    absolute_path = os.path.abspath(report.file_path)

    # Check if the file exists before sending
    if not os.path.exists(absolute_path):
        flash("Error: Report file not found!", "danger")
        return redirect(url_for('main.attendance_reports'))

    return send_file(absolute_path, as_attachment=True)


@main.route('/delete_report/<int:report_id>', methods=['POST'])
@login_required
def delete_report(report_id):
    report = Report.query.get_or_404(report_id)

    # Delete the actual file if it exists
    if os.path.exists(report.file_path):
        os.remove(report.file_path)

    db.session.delete(report)
    db.session.commit()
    
    flash("Report deleted successfully!", "success")
    return redirect(url_for('main.attendance_reports'))