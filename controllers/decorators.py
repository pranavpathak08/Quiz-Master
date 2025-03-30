from flask import session, redirect, url_for, abort
from flask_login import current_user, logout_user
from functools import wraps
from models.models import User

def admin_required(f):
    @wraps(f)
    def decorator_function(*args, **kwargs):
        user_id = session.get("user_id")

        # Check if user is logged in
        if not user_id:
            print("[DEBUG] Unauthorized access. Redirecting to login page.")
            return redirect(url_for("auth.login"))

        # Fetch user from the database
        user = User.query.get(user_id)

        # Check if user exists and is an admin
        if not user or not user.is_admin:
            print("[DEBUG] Non-admin user tried accessing admin dashboard. Logging out.")
            logout_user()  # Logout non-admin users who try to access admin pages
            session.pop("user_id", None)
            session.pop("is_admin", None)
            return redirect(url_for("auth.login"))

        return f(*args, **kwargs)   
    return decorator_function
