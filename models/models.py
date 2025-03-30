from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    full_name = db.Column(db.String(150))
    qualification = db.Column(db.String(150))
    dob = db.Column(db.String(20))
    is_admin = db.Column(db.Boolean, default=False)

    scores = db.relationship("Scores", back_populates="user", overlaps="user_scores,scores")

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Subject {self.name}>"

class Chapter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id', ondelete="CASCADE"), nullable=False)

    __table_args__ = (db.UniqueConstraint("name", "subject_id", name="uq_chapter_name_subject"),)

    subject = db.relationship("Subject", backref=db.backref("chapters", cascade="all, delete-orphan"))

class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    chapter_id = db.Column(db.Integer, db.ForeignKey("chapter.id", ondelete="CASCADE"), nullable=False)
    date = db.Column(db.Date, nullable=False)
    duration = db.Column(db.Time, nullable=False)

    chapter = db.relationship("Chapter", backref=db.backref("quizzes", cascade="all, delete-orphan"))
    scores = db.relationship("Scores", back_populates="quiz", lazy=True, cascade="all, delete-orphan", overlaps="quiz_scores,scores")

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey("quiz.id", ondelete="CASCADE"), nullable=False)
    question_statement = db.Column(db.Text, nullable=False)
    option1 = db.Column(db.String(255), nullable=False)
    option2 = db.Column(db.String(255), nullable=False)
    option3 = db.Column(db.String(255), nullable=False)
    option4 = db.Column(db.String(255), nullable=False)
    correct_option = db.Column(db.Integer, nullable=False)  

    quiz = db.relationship("Quiz", backref=db.backref("questions", cascade="all, delete-orphan"))


class Scores(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)  
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  
    time_stamp_of_attempt = db.Column(db.DateTime, default=datetime.utcnow)
    total_scored = db.Column(db.Integer, nullable=False)

    quiz = db.relationship("Quiz", back_populates="scores", overlaps="quiz_scores,scores")  
    user = db.relationship("User", back_populates="scores", overlaps="user_scores,scores")



