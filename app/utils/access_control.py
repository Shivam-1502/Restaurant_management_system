from functools import wraps
from flask import redirect, url_for, flash
from flask_login import current_user

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != "Admin":
            flash("Access restricted to Admins only.", "danger")
            return redirect(url_for("auth.choose_role"))
        return f(*args, **kwargs)
    return decorated_function

def employee_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for("auth.employee_login"))
        if current_user.role != "Employee":
            flash("Access restricted to Employees only.", "danger")
            return redirect(url_for("auth.choose_role"))
        return f(*args, **kwargs)
    return decorated_function
