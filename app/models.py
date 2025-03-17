from . import db, login_manager
from flask_login import UserMixin
from datetime import datetime, timedelta
import pytz

# Define UK Timezone
UK_TIMEZONE = pytz.timezone('Europe/London')

@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(int(user_id))

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    clock_in = db.Column(db.DateTime(timezone=True), nullable=True)
    clock_out = db.Column(db.DateTime(timezone=True), nullable=True)
    break_time = db.Column(db.Interval, default=timedelta(seconds=0))
    total_work_hours = db.Column(db.Interval, default=timedelta(seconds=0))

    employee = db.relationship('Employee', backref=db.backref('attendance_records', lazy=True))

    UK_TIMEZONE = pytz.timezone('Europe/London')

    def __init__(self, employee_id, clock_in=None, clock_out=None, break_time=None, total_work_hours=None):
        self.employee_id = employee_id
        self.clock_in = clock_in if clock_in else datetime.now(pytz.utc).astimezone(self.UK_TIMEZONE)
        self.clock_out = clock_out
        self.break_time = break_time if break_time else timedelta(seconds=0)
        self.total_work_hours = total_work_hours if total_work_hours else timedelta(seconds=0)


    @staticmethod
    def calculate_break_time(employee_id, clock_in_time):
        """
        Calculate total break time based on previous clock-out time.
        If the break is greater than 5 minutes, count it as break time.
        """
        last_record = Attendance.query.filter(
            Attendance.employee_id == employee_id,
            Attendance.clock_out.isnot(None)  # Correct SQLAlchemy syntax
        ).order_by(Attendance.clock_out.desc()).first()

        if last_record and last_record.clock_out:
            break_duration = clock_in_time - last_record.clock_out
            if break_duration > timedelta(minutes=5):  # Consider as break if >5 minutes
                return break_duration

        return timedelta(seconds=0)

class Admin(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)

class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(150), nullable=False)
    last_name = db.Column(db.String(150), nullable=False)
    dob = db.Column(db.Date, nullable=False)
    joining_date = db.Column(db.Date, nullable=False)
    brp = db.Column(db.String(100), nullable=False)
    address = db.Column(db.Text, nullable=False)

class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    report_type = db.Column(db.String(50), nullable=False)
    file_path = db.Column(db.String(255), nullable=False, unique=True)
    generated_on = db.Column(db.DateTime, default=lambda: datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(UK_TIMEZONE))
