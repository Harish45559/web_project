from . import db, login_manager
from flask_login import UserMixin
from datetime import datetime, timedelta
import pytz  # Import pytz for timezone conversion
from . import bcrypt
from flask_sqlalchemy import SQLAlchemy

@login_manager.user_loader
def load_user(user_id):
    admin = Admin.query.get(int(user_id))
    if admin:
        return admin
    return Employee.query.get(int(user_id))


# Define UK Timezone
UK_TIMEZONE = pytz.timezone('Europe/London')

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    clock_in = db.Column(db.DateTime, nullable=True)
    clock_out = db.Column(db.DateTime, nullable=True)
    total_work_hours = db.Column(db.Interval, nullable=True)
    break_time = db.Column(db.Interval, nullable=True)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)

    employee = db.relationship('Employee', backref=db.backref('attendance_records', lazy=True))

    def __init__(self, employee_id, clock_in=None, clock_out=None, break_time=None, latitude=None, longitude=None):
        self.employee_id = employee_id
        self.clock_in = self.get_uk_time(clock_in)
        self.clock_out = self.get_uk_time(clock_out) if clock_out else None
        self.break_time = break_time if break_time else timedelta(seconds=0)
        self.total_work_hours = timedelta(seconds=0)
        self.latitude = latitude
        self.longitude = longitude

    @staticmethod
    def get_uk_time(dt):
        """Ensures the datetime is stored in UK timezone."""
        if dt is None:
            dt = datetime.utcnow()  # Get current UTC time
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=pytz.utc)  # Assign UTC timezone
        return dt.astimezone(UK_TIMEZONE)  # Convert to UK Time

    def calculate_total_work_hours(self):
        """Calculates total work hours even if the shift crosses midnight."""
        if self.clock_in and self.clock_out:
            # If clock_out is before clock_in, shift spans across midnight
            if self.clock_out < self.clock_in:
                self.clock_out += timedelta(days=1)

            work_duration = self.clock_out - self.clock_in
            return work_duration - self.break_time
        return timedelta(seconds=0)

    @staticmethod
    def calculate_break_time(employee_id, clock_in_time):
        """Calculates break time but ensures it remains within the same shift day."""
        last_record = (
            Attendance.query.filter(Attendance.employee_id == employee_id, Attendance.clock_out.isnot(None))
            .order_by(Attendance.clock_out.desc())
            .first()
        )

        if last_record and last_record.clock_out:
            break_duration = clock_in_time - last_record.clock_out

            # If the previous shift ended past midnight, adjust break time to stay within the workday
            if break_duration < timedelta():
                break_duration += timedelta(days=1)

            if break_duration > timedelta(minutes=5):  # Consider break only if > 5 min
                return break_duration
        return timedelta(seconds=0)

class Admin(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)

    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)

class Employee(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(150), nullable=False)
    last_name = db.Column(db.String(150), nullable=False)
    dob = db.Column(db.Date, nullable=False)
    joining_date = db.Column(db.Date, nullable=False)
    brp = db.Column(db.String(100), nullable=False)
    address = db.Column(db.Text, nullable=False)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(50), nullable=False, default="employee")

    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)
class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    report_type = db.Column(db.String(50), nullable=False)
    file_path = db.Column(db.String(255), nullable=False, unique=True)
    generated_on = db.Column(db.DateTime, default=lambda: datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(UK_TIMEZONE))
