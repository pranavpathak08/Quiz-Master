from flask import Blueprint, render_template, request, url_for, redirect
from flask_login import login_required, current_user
from models.models import Quiz, Scores, Question, db
import datetime


user_blueprint = Blueprint("user", __name__)

# User Dashboard
@user_blueprint.route("/dashboard")
@login_required
def user_dashboard():
    quizzes = Quiz.query.all()
    
    # Fetch past attempts with quiz details
    user_attempts = (
        db.session.query(Scores, Quiz)
        .join(Quiz, Scores.quiz_id == Quiz.id)
        .filter(Scores.user_id == current_user.id)
        .order_by(Scores.id.desc())  # Latest first
        .all()
    )
    
    return render_template("user_dashboard.html", quizzes=quizzes, user_attempts=user_attempts)

@user_blueprint.route("/quiz/<int:quiz_id>/attempt", methods=["GET", "POST"])
@login_required
def attempt_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)

    if request.method == "POST":
        # Strip "q" prefix from keys to match correct_answers
        selected_options = {key[1:]: request.form[key] for key in request.form}  # Removing "q" from "q1", "q2"
        correct_answers = {str(q.id): str(q.correct_option) for q in quiz.questions}

        # Debugging prints
        print(f"Selected Options (Fixed): {selected_options}")
        print(f"Correct Answers: {correct_answers}")

        # Calculate score
        score = sum(1 for q_id in correct_answers if selected_options.get(q_id) == correct_answers[q_id])

        # Save attempt in database
        attempt = Scores(user_id=current_user.id, quiz_id=quiz_id, total_scored=score)
        db.session.add(attempt)
        db.session.commit()

        return redirect(url_for("user.quiz_result", quiz_id=quiz_id, score=score))

    return render_template("user/quiz_attempt.html", quiz=quiz)




@user_blueprint.route("/quiz/<int:quiz_id>/result")
@login_required
def quiz_result(quiz_id):
    attempt = Scores.query.filter_by(user_id=current_user.id, quiz_id=quiz_id).order_by(Scores.id.desc()).first()

    if not attempt:
        print("No attempt found for this quiz.")
        return redirect(url_for("user.user_dashboard"))

    return render_template("user/quiz_result.html", quiz_id=quiz_id, score=attempt.total_scored)

