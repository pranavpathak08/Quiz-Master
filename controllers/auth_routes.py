from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from models.models import db, User

auth_blueprint = Blueprint("auth", __name__)

# User registration route
@auth_blueprint.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        full_name = request.form["full_name"]
        username = request.form["username"]
        email = request.form["email"]
        qualification = request.form["qualification"]
        dob = request.form["dob"]
        password = request.form["password"]

        # Convert DOB from string to date format
        try:
            dob = datetime.strptime(dob, "%Y-%m-%d").date()
        except ValueError:
            print("Invalid Date Format! Use YYYY-MM-DD.")
            return redirect(url_for("auth.register"))

        # Check if user already exists
        if User.query.filter_by(email=email).first():
            print("Email already registered")
            return redirect(url_for("auth.register"))

        hashed_password = generate_password_hash(password, method="pbkdf2:sha256")
        new_user = User(full_name=full_name, username=username, email=email, qualification=qualification, dob=dob, password=hashed_password)

        db.session.add(new_user)
        db.session.commit()

        print("Registration successful! You can now log in.")
        return redirect(url_for("auth.login"))
    
    return render_template("register.html")


# User login route
@auth_blueprint.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            print(f"✅ Login Successful for: {user.email}")
            login_user(user, remember=True)  # Logs in user via Flask-Login
            session["user_id"] = user.id  # Store user ID
            session["is_admin"] = user.is_admin  # Store admin status
            
            # Redirect based on role
            next_page = request.args.get("next")
            if next_page:
                return redirect(next_page)
            return redirect(url_for("admin.admin_dashboard") if user.is_admin else url_for("user.user_dashboard"))
        
        print("❌ Invalid Credentials")
        return render_template("login.html")  # Stay on login page

    return render_template("login.html")

# User logout route
@auth_blueprint.route("/logout")
def logout():
    session.pop("user_id", None)
    session.pop("is_admin", None)
    logout_user()
    print("🔴 User logged out")
    return redirect(url_for("auth.login"))


