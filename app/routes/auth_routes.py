from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from app.models import Admin, Employee
from app.models import db
from app.forms.login_form import LoginForm
import secrets
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta

auth_bp = Blueprint("auth", __name__)

# Email configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = "your-email@gmail.com"  # Replace with your email
SMTP_PASSWORD = "your-app-password"      # Replace with your app password

def send_reset_email(email, reset_link):
    msg = MIMEMultipart()
    msg['From'] = SMTP_SERVER
    msg['To'] = email
    msg['Subject'] = "Password Reset Request"
    
    body = f"""
    You have requested to reset your password.
    Please click on the following link to reset your password:
    {reset_link}
    
    If you did not request this, please ignore this email.
    """
    
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False

@auth_bp.route("/", methods=["GET", "POST"])
def choose_role():
    """Landing page where user selects Admin or Employee login."""
    if request.method == "POST":
        role = request.form.get("role")
        if role == "Admin":
            return redirect(url_for("auth.admin_login"))
        elif role == "Employee":
            return redirect(url_for("auth.employee_login"))
    return render_template("choose_role.html")

@auth_bp.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    """Admin login route."""
    form = LoginForm()
    if form.validate_on_submit():
        user = Admin.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash("Admin login successful!", "success")
            return redirect(url_for("admin.admin_dashboard"))
        else:
            flash("Invalid credentials!", "danger")
    return render_template("login.html", form=form, role="Admin")

@auth_bp.route("/employee/login", methods=["GET", "POST"])
def employee_login():
    """Employee login route."""
    form = LoginForm()
    if form.validate_on_submit():
        user = Employee.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash("Employee login successful!", "success")
            return redirect(url_for("employee.dashboard"))
        else:
            flash("Invalid credentials!", "danger")
    return render_template("login.html", form=form, role="Employee")

@auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email")
        role = request.form.get("role")
        
        # Find user by email
        user = None
        if role == "Admin":
            user = Admin.query.filter_by(email=email).first()
        elif role == "Employee":
            user = Employee.query.filter_by(email=email).first()
            
        if user:
            # Generate reset token
            token = secrets.token_urlsafe(32)
            user.reset_token = token
            user.reset_token_expiry = datetime.utcnow() + timedelta(hours=1)
            db.session.commit()
            
            # Generate reset link
            reset_link = url_for('auth.reset_password', token=token, _external=True)
            
            # Send reset email
            if send_reset_email(email, reset_link):
                flash("Password reset instructions have been sent to your email.", "success")
            else:
                flash("Error sending reset email. Please try again later.", "danger")
        else:
            # Don't reveal if email exists or not
            flash("If an account exists with this email, you will receive password reset instructions.", "info")
            
        return redirect(url_for('auth.login'))
        
    return render_template("forgot_password.html")

@auth_bp.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    # Check token in both Admin and Employee tables
    user = Admin.query.filter_by(reset_token=token).first()
    if not user:
        user = Employee.query.filter_by(reset_token=token).first()
    
    if not user or not user.reset_token_expiry or user.reset_token_expiry < datetime.utcnow():
        flash("Invalid or expired reset token.", "danger")
        return redirect(url_for('auth.login'))
    
    if request.method == "POST":
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        
        if password != confirm_password:
            flash("Passwords do not match.", "danger")
        else:
            user.set_password(password)
            user.reset_token = None
            user.reset_token_expiry = None
            db.session.commit()
            flash("Your password has been reset successfully.", "success")
            return redirect(url_for('auth.login'))
            
    return render_template("reset_password.html")

@auth_bp.route("/logout")
@login_required
def logout():
    """Logout route."""
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.choose_role"))
