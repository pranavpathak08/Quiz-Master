from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required
from controllers.decorators import admin_required
from datetime import datetime, time
from models.models import db, Subject, Chapter, Quiz, Question, User, Scores

admin_blueprint = Blueprint("admin", __name__)

@admin_blueprint.route("/dashboard")
@admin_required
def admin_dashboard():
    return render_template("admin_dashboard.html")

#CRUD routes for managing subjects

# View subjects
@admin_blueprint.route("/subjects")
@admin_required
def manage_subjects():
    subjects = Subject.query.all()
    return render_template("admin/admin_subject.html", subjects=subjects)

# Add subject
@admin_blueprint.route("/subjects/add", methods=["GET", "POST"])
@admin_required
def add_subject():
    if request.method == "POST":
        name = request.form["name"].strip()
        description = request.form["description"].strip()

        if not name:
            print("Subject name cannot be empty")
            return redirect(url_for("admin.add_subject"))
        
        if Subject.query.filter_by(name=name).first():
            print("Subject with this name already exists")
            return redirect(url_for("admin.add_subject"))

        new_subject = Subject(name=name, description=description)
        db.session.add(new_subject)
        db.session.commit()
        print(f"✅ {new_subject.name} Subject added successfully")

        return redirect(url_for("admin.manage_subjects"))

    return render_template("admin/add_subject.html")

#Edit Subject
@admin_blueprint.route("/subjects/edit/<int:id>", methods=["GET", "POST"])
@admin_required
def edit_subject(id):
    subject = Subject.query.get_or_404(id)

    if request.method == "POST":
        new_name = request.form["name"].strip()
        new_description = request.form["description"].strip()

        if not new_name:
            print("⚠ Subject name cannot be empty.")
            return redirect(url_for("admin.edit_subject", id=id))

        existing_subject = Subject.query.filter_by(name=new_name).filter(Subject.id!=id).first()
        if existing_subject:
            print("⚠ Subject with this name already exists.")
            return redirect(url_for("admin.edit_subject", id=id))

        subject.name = new_name
        subject.description = new_description

        db.session.commit()
        print("✅ Subject updated successfully")
        return redirect(url_for("admin.manage_subjects"))

    return render_template("admin/edit_subject.html", subject=subject)

#Delete Subject
@admin_blueprint.route("/subjects/delete/<int:id>", methods=["POST"])
@admin_required
def delete_subject(id):
    subject = Subject.query.get_or_404(id)
    db.session.delete(subject)
    db.session.commit()

    print(f"✅ Subject {subject.name} deleted successfully.")
    return redirect(url_for("admin.manage_subjects"))


#CRUD routes for managing chapters

# View Chapter
@admin_blueprint.route("/subjects/<int:subject_id>/chapters")
@admin_required
def manage_chapters(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    return render_template("admin/admin_chapters.html", subject=subject, chapters=subject.chapters)

# Add Chapter
@admin_blueprint.route("/subjects/<int:subject_id>/chapters/add", methods=["GET", "POST"])
@admin_required
def add_chapter(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    if request.method == "POST":
        name = request.form["name"].strip()
        description = request.form["description"].strip()

        if not name:
            print("⚠ Chapter name cannot be empty.")
            return redirect(url_for("admin.add_chapter", subject_id=subject_id))

        existing_chapter = Chapter.query.filter_by(name=name, subject_id=subject_id).first()
        if existing_chapter:
            print("⚠ A chapter with this name already exists under this subject.")
            return redirect(url_for("admin.add_chapter", subject_id=subject_id))

        new_chapter = Chapter(name=name, description=description, subject_id=subject_id)
        db.session.add(new_chapter)
        db.session.commit()

        print(f"✅ {new_chapter.name} Chapter added successfully.")
        return redirect(url_for("admin.manage_chapters", subject_id=subject_id))

    return render_template("admin/add_chapter.html", subject=subject)

# Edit Chapter
@admin_blueprint.route("/chapters/edit/<int:id>", methods=["GET", "POST"])
@admin_required
def edit_chapter(id):
    chapter = Chapter.query.get_or_404(id)

    if request.method == "POST":
        new_name = request.form["name"].strip()
        new_description = request.form["description"].strip()

        if not new_name:
            print("⚠ Chapter cannot be empty")
            return redirect(url_for("admin.edit_chapter", id=id))

        existing_chapter = Chapter.query.filter_by(name=new_name, subject_id=chapter.subject_id).filter(Chapter.id!=id).first()
        if existing_chapter:
            print("⚠ A chapter with this name already exists under this subject.")
            return redirect(url_for("admin.edit_chapter", id=id))

        chapter.name = new_name
        chapter.description = new_description

        db.session.commit()
        print("✅ Chapter updated successfully.")
        return redirect(url_for("admin.manage_chapters", subject_id=chapter.subject_id))

    return render_template("admin/edit_chapter.html", chapter=chapter)

# Delete Chapter
@admin_blueprint.route("/chapters/delete/<int:id>", methods=["POST"])
@admin_required
def delete_chapter(id):
    chapter = Chapter.query.get_or_404(id)
    subject_id = chapter.subject_id
    db.session.delete(chapter)
    db.session.commit()

    print(f"✅ {chapter.name} Chapter deleted successfully.")
    return redirect(url_for("admin.manage_chapters", subject_id=subject_id))
        

# CRUD routes for managing quizzes

# View all quizzes in manage quizzes option
@admin_blueprint.route("/quizzes")
@admin_required
def manage_quizzes_all():
    quizzes = (
        db.session.query(
            Quiz.id, Quiz.name, Quiz.date, Quiz.description, Quiz.duration,
            Chapter.name.label("chapter_name"), Subject.name.label("subject_name")
        )
        .select_from(Quiz)
        .join(Chapter, Quiz.chapter_id == Chapter.id)
        .join(Subject, Chapter.subject_id == Subject.id)
        .all()
    )
    return render_template("admin/manage_quizzes.html", quizzes=quizzes)

@admin_blueprint.route("/quizzes/select_chapter")
@admin_required
def select_chapter_for_quiz():
    chapters = Chapter.query.join(Subject).add_columns(
        Chapter.id, Chapter.name, Subject.name.label("subject_name")
    ).all()
    return render_template("admin/select_chapter.html", chapters=chapters)

# View Quizzes under a chapter
@admin_blueprint.route("/chapters/<int:chapter_id>/quizzes")
@admin_required
def manage_quizzes(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)
    return render_template("admin/admin_quizzes.html", chapter=chapter, quizzes=chapter.quizzes)

# Add Quiz
@admin_blueprint.route("/chapters/<int:chapter_id>/quizzes/add", methods=["GET", "POST"])
@admin_required
def add_quiz(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)

    if request.method == "POST":
        name = request.form["name"].strip()
        description = request.form["description"].strip()
        date_str = request.form["date"].strip()
        duration_str = request.form["duration"].strip()

        if not name or not date_str or not duration_str:
            print("⚠ Quiz name, date, and duration are required.")
            return redirect(url_for("admin.add_quiz", chapter_id=chapter_id))

        # ✅ Convert date string to Python `date` object
        try:
            date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            print("⚠ Invalid date format. Please use YYYY-MM-DD.")
            return redirect(url_for("admin.add_quiz", chapter_id=chapter_id))

        # ✅ Convert duration string (hh:mm) to Python `time` object
        try:
            duration = datetime.strptime(duration_str, "%H:%M").time()
        except ValueError:
            print("⚠ Invalid duration format. Please use HH:MM (e.g., 02:00).")
            return redirect(url_for("admin.add_quiz", chapter_id=chapter_id))

        existing_quiz = Quiz.query.filter_by(name=name, chapter_id=chapter_id).first()
        if existing_quiz:
            print("⚠ A quiz with this name already exists in this chapter.")
            return redirect(url_for("admin.add_quiz", chapter_id=chapter_id))

        new_quiz = Quiz(name=name, description=description, date=date, duration=duration, chapter_id=chapter_id)
        db.session.add(new_quiz)
        db.session.commit()

        print(f"✅ Quiz {new_quiz.name} added successfully.")
        return redirect(url_for("admin.manage_quizzes", chapter_id=chapter_id))

    return render_template("admin/add_quiz.html", chapter=chapter)

# Edit Quiz
@admin_blueprint.route("/quizzes/edit/<int:id>", methods=["GET", "POST"])
@admin_required
def edit_quiz(id):
    quiz = Quiz.query.get_or_404(id)

    if request.method == "POST":
        new_name = request.form["name"].strip()
        new_description = request.form["description"].strip()
        date_str = request.form["date"].strip()
        duration_str = request.form["duration"].strip()

        if not new_name or not date_str or not duration_str:
            print("⚠ Quiz name, date, and duration are required.")
            return redirect(url_for("admin.edit_quiz", id=id))

        # ✅ Convert date string to Python `date` object
        try:
            new_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            print("⚠ Invalid date format. Please use YYYY-MM-DD.")
            return redirect(url_for("admin.edit_quiz", id=id))

        # ✅ Convert duration string (hh:mm) to Python `time` object
        try:
            new_duration = datetime.strptime(duration_str, "%H:%M").time()
        except ValueError:
            print("⚠ Invalid duration format. Please use HH:MM (e.g., 02:00).")
            return redirect(url_for("admin.edit_quiz", id=id))

        # Check if a quiz with the same name exists (excluding the current quiz)
        existing_quiz = Quiz.query.filter(Quiz.name == new_name, Quiz.chapter_id == quiz.chapter_id, Quiz.id != id).first()
        if existing_quiz:
            print("⚠ A quiz with this name already exists in this chapter.")
            return redirect(url_for("admin.edit_quiz", id=id))

        # ✅ Update quiz details
        quiz.name = new_name
        quiz.description = new_description
        quiz.date = new_date
        quiz.duration = new_duration

        db.session.commit()
        print("✅ Quiz updated successfully.")
        return redirect(url_for("admin.manage_quizzes", chapter_id=quiz.chapter_id))

    return render_template("admin/edit_quiz.html", quiz=quiz)

# Delete Quiz
@admin_blueprint.route("/quizzes/delete/<int:id>", methods=["POST"])
@admin_required
def delete_quiz(id):
    quiz = Quiz.query.get_or_404(id)
    chapter_id = quiz.chapter_id
    db.session.delete(quiz)
    db.session.commit()

    print(f"✅ Quiz {quiz.name} deleted successfully.")
    return redirect(url_for("admin.manage_quizzes", chapter_id=chapter_id))


# CRUD Routes for managing questions

# View questions
@admin_blueprint.route("/quizzes/<int:quiz_id>/questions")
@admin_required
def manage_questions(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    return render_template("admin/manage_questions.html", quiz=quiz, questions=questions)

# Add questions
@admin_blueprint.route("/quizzes/<int:quiz_id>/questions/add", methods=["GET", "POST"])
@admin_required
def add_question(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)

    if request.method == "POST":
        question_statement = request.form["question_statement"].strip()
        option1 = request.form["option1"].strip()
        option2 = request.form["option2"].strip()
        option3 = request.form["option3"].strip()
        option4 = request.form["option4"].strip()
        correct_option = request.form["correct_option"].strip()

        # Validation: Ensure all fields are filled
        if not question_statement or not option1 or not option2 or not option3 or not option4 or not correct_option:
            print("⚠ All fields are required.")
            return redirect(url_for("admin.add_question", quiz_id=quiz_id))

        # Ensure correct_option is a valid number (1-4)
        if correct_option not in ["1", "2", "3", "4"]:
            print("⚠ Correct option must be 1, 2, 3, or 4.")
            return redirect(url_for("admin.add_question", quiz_id=quiz_id))

        # Create new question
        new_question = Question(
            quiz_id=quiz.id,
            question_statement=question_statement,
            option1=option1,
            option2=option2,
            option3=option3,
            option4=option4,
            correct_option=int(correct_option)  # Convert to integer
        )

        db.session.add(new_question)
        db.session.commit()

        print(f"✅ Question added successfully")
        return redirect(url_for("admin.manage_questions", quiz_id=quiz_id))

    return render_template("admin/add_question.html", quiz=quiz)


# Edit questions
@admin_blueprint.route("/questions/<int:question_id>/edit", methods=["GET", "POST"])
@admin_required
def edit_question(question_id):
    question = Question.query.get_or_404(question_id)

    if request.method == "POST":
        question_statement = request.form["question_statement"].strip()
        option1 = request.form["option1"].strip()
        option2 = request.form["option2"].strip()
        option3 = request.form["option3"].strip()
        option4 = request.form["option4"].strip()
        correct_option = request.form["correct_option"].strip()

        # Validation: Ensure all fields are filled
        if not question_statement or not option1 or not option2 or not option3 or not option4 or not correct_option:
            print("⚠ All fields are required.")
            return redirect(url_for("admin.edit_question", question_id=question.id))

        # Ensure correct_option is a valid number (1-4)
        if correct_option not in ["1", "2", "3", "4"]:
            print("⚠ Correct option must be 1, 2, 3, or 4.")
            return redirect(url_for("admin.edit_question", question_id=question.id))

        # Update question fields
        question.question_statement = question_statement
        question.option1 = option1
        question.option2 = option2
        question.option3 = option3
        question.option4 = option4
        question.correct_option = int(correct_option)  

        db.session.commit()
        print(f"✅ Question updated successfully")
        return redirect(url_for("admin.manage_questions", quiz_id=question.quiz_id))

    return render_template("admin/edit_question.html", question=question)

# Delete Question

@admin_blueprint.route("/questions/<int:question_id>/delete", methods=["POST"])
@admin_required
def delete_question(question_id):
    question = Question.query.get_or_404(question_id)
    quiz_id = question.quiz_id  

    db.session.delete(question)
    db.session.commit()

    print(f"✅ Question deleted successfully")
    return redirect(url_for("admin.manage_questions", quiz_id=quiz_id))


# Manage Users
@admin_blueprint.route("/users", methods=["GET", "POST"])
@admin_required
def manage_users():
    search_query = request.args.get("search", "").strip()  # Get search input

    if search_query:
        users = User.query.filter(User.username.ilike(f"%{search_query}%")).all()
    else:
        users = User.query.all()

    return render_template("admin/manage_users.html", users=users, search_query=search_query)


@admin_blueprint.route("/users/<int:user_id>/delete", methods=["POST"])
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)

    # Delete all related scores before deleting the user
    Scores.query.filter_by(user_id=user.id).delete()

    db.session.delete(user)
    db.session.commit()

    print(f"✅ User {user.username} deleted successfully")
    return redirect(url_for("admin.manage_users"))












