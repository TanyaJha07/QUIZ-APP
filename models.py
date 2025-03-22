from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

# User Model
class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    qualification = db.Column(db.String(120), nullable=False)
    dob = db.Column(db.Date, nullable=True)

    # Relationship
    scores = db.relationship('Score', backref='user', lazy=True)

    # Password Hashing
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


# Subject Model
class Subject(db.Model):
    __tablename__ = 'subjects'
    
    id = db.Column(db.Integer, primary_key=True)
    subject_name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=True)

    # Relationship with cascade delete
    chapters = db.relationship('Chapter', backref='subject', cascade="all, delete-orphan", lazy=True)

# Chapter Model
# Chapter Model
class Chapter(db.Model):
    __tablename__ = 'chapters'
    
    id = db.Column(db.Integer, primary_key=True)
    chapter_name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)

    # Update the relationships:
    quizzes = db.relationship('Quiz', back_populates='chapter', cascade="all, delete-orphan", lazy=True)
    questions = db.relationship('Question', back_populates='chapter', cascade="all, delete-orphan", lazy=True)

    def serialize(self):
        return {
            'id': self.id,
            'chapter_name': self.chapter_name,
            'description': self.description
        }


# Quiz Model
class Quiz(db.Model):
    __tablename__ = 'quiz'
    
    id = db.Column(db.Integer, primary_key=True)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapters.id'), nullable=False)
    name = db.Column(db.String(225), unique=True, nullable=False)
    date_of_quiz = db.Column(db.Date, nullable=True)
    time_duration = db.Column(db.Integer, nullable=True)
    remarks = db.Column(db.String(255), nullable=True)

    # Relationships
    chapter = db.relationship('Chapter', back_populates='quizzes')
    scores = db.relationship('Score', backref='quiz', lazy=True)

    # Serialization method
    def serialize(self):
        return {
            'id': self.id,
            'chapter_id': self.chapter_id,
            'name': self.name,
            'date_of_quiz': self.date_of_quiz,
            'time_duration': self.time_duration,
            'remarks': self.remarks
        }


# Question Model
class Question(db.Model):
    __tablename__ = 'questions'
    id = db.Column(db.Integer, primary_key=True)
    question_statement = db.Column(db.String, nullable=False)
    option1 = db.Column(db.String, nullable=False)
    option2 = db.Column(db.String, nullable=False)
    option3 = db.Column(db.String, nullable=False)
    option4 = db.Column(db.String, nullable=False)
    correct_answer = db.Column(db.String, nullable=False)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapters.id'), nullable=False)

    # Define relationship with chapter
    chapter = db.relationship("Chapter", back_populates="questions")

    # Serialization method
    def serialize(self):
        return {
            'id': self.id,
            'question_statement': self.question_statement,
            'options': [self.option1, self.option2, self.option3, self.option4],
            'correct_answer': self.correct_answer,
            'chapter_id': self.chapter_id
        }


# Score Model
class Score(db.Model):
    __tablename__ = 'scores'
    
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    time_stamp_of_attempt = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    total_scored = db.Column(db.Integer, nullable=False)
    time_taken = db.Column(db.Integer, nullable=False)
