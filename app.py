from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from models import User, db, Quiz, Question, Score, Subject, Chapter
from datetime import datetime
from sqlalchemy import or_
from sqlalchemy.orm import joinedload

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quiz.db'
app.secret_key = "your_super_secret_key_here"
db.init_app(app)

with app.app_context():
    db.create_all()

    # Dummy data for subjects
    subjects_data = [
        {"subject_name": "Mathematics", "description": "Study of numbers, shapes, and patterns."},
        {"subject_name": "Science", "description": "Study of the physical and natural world."},
        {"subject_name": "History", "description": "Study of past events."},
    ]

    for subject in subjects_data:
        existing_subject = Subject.query.filter_by(subject_name=subject["subject_name"]).first()
        if not existing_subject:
            new_subject = Subject(subject_name=subject["subject_name"], description=subject["description"])
            db.session.add(new_subject)

    db.session.commit()

    # Dummy data for chapters
    chapters_data = [
        {"chapter_name": "Algebra", "description": "Introduction to algebra.", "subject_id": 1},
        {"chapter_name": "Geometry", "description": "Basics of geometry.", "subject_id": 1},
        {"chapter_name": "Physics", "description": "Fundamentals of physics.", "subject_id": 2},
        {"chapter_name": "Chemistry", "description": "Basics of chemistry.", "subject_id": 2},
        {"chapter_name": "World War II", "description": "Overview of World War II.", "subject_id": 3},
    ]

    for chapter in chapters_data:
        existing_chapter = Chapter.query.filter_by(chapter_name=chapter["chapter_name"]).first()
        if not existing_chapter:
            new_chapter = Chapter(chapter_name=chapter["chapter_name"], description=chapter["description"], subject_id=chapter["subject_id"])
            db.session.add(new_chapter)

    db.session.commit()

    # Dummy data for questions
    questions = [
        {"question_statement": "What is 2+2?", "option1": "4", "option2": "5", "option3": "6", "option4": "7", "correct_answer": "4", "chapter_id": 1},
        {"question_statement": "What is 5+5?", "option1": "10", "option2": "15", "option3": "20", "option4": "25", "correct_answer": "10", "chapter_id": 1},
        {"question_statement": "What is 10+10?", "option1": "20", "option2": "30", "option3": "40", "option4": "50", "correct_answer": "20", "chapter_id": 2},
        {"question_statement": "What is 20+20?", "option1": "40", "option2": "60", "option3": "80", "option4": "100", "correct_answer": "20", "chapter_id": 2},
    ]

    for question in questions:
        existing_question = Question.query.filter_by(question_statement=question["question_statement"]).first()
        if not existing_question:
            new_question = Question(
                question_statement=question["question_statement"],
                option1=question["option1"],
                option2=question["option2"],
                option3=question["option3"],
                option4=question["option4"],
                correct_answer=question["correct_answer"],
                chapter_id=question["chapter_id"]
            )
            db.session.add(new_question)

    db.session.commit()

    # Dummy data for admin user
    admin_email = "admin@example.com"
    admin_password = "admin"

    admin_user = User.query.filter_by(email=admin_email).first()

    if not admin_user:
        admin = User(
            username="admin",
            email=admin_email,
            password=admin_password,
            qualification="Administrator",
            dob=datetime.strptime("2000-01-01", "%Y-%m-%d").date()
        )
        db.session.add(admin)

    db.session.commit()

    # Dummy data for regular user
    user_email = "user@email.com"
    user_password = "user"

    user = User.query.filter_by(email=user_email).first()

    if not user:
        user = User(
            username="user",
            email=user_email,
            password=user_password,
            qualification="User",
            dob=datetime.strptime("2000-01-01", "%Y-%m-%d").date()
        )
        db.session.add(user)

    db.session.commit()

#---------------------------------  -----------------------------------------
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        qualification = request.form['qualification']
        dob_string = request.form['dob']

        dob = datetime.strptime(dob_string, "%Y-%m-%d").date()
        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            flash("Email is already registered. Please login or use a different email.", "danger")
            return redirect(url_for('signup'))

        user = User(username=username, email=email, password=password, qualification=qualification, dob=dob)
        db.session.add(user)
        db.session.commit()

        return redirect(url_for('index'))

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()

        if user and user.password == password:
            session['user_id'] = user.id
            session['user_role'] = 'admin' if user.email == "admin@example.com" else 'user'

            flash("Login successful!", "success")

            if session['user_role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('user_dashboard'))
        else:
            flash("Invalid email or password!", "danger")

    return render_template('login.html')

#--------------------------------- Admin Dashboard -----------------------------------------
@app.route('/admin_dashboard', methods=['GET', 'POST'])
def admin_dashboard():
    if "user_id" not in session or session['user_role'] != 'admin':
        flash("Unauthorized access!", "danger")
        return redirect(url_for("login"))

    if request.method == "POST":
        action = request.form.get("action")

        if action == "add_subject":
            subject_name = request.form['subject_name']
            description = request.form['subject_description']

            existing_subject = Subject.query.filter_by(subject_name=subject_name).first()
            if existing_subject:
                flash("Subject already exists!", "warning")
            else:
                new_subject = Subject(subject_name=subject_name, description=description)
                db.session.add(new_subject)
                db.session.commit()
                flash("Subject added successfully!", "success")

        elif action == "add_chapter":
            chapter_name = request.form['chapter_name']
            description = request.form['chapter_description']
            subject_id = request.form.get('subject_id')

            if not subject_id:
                flash("Please select a valid subject!", "warning")
            else:
                new_chapter = Chapter(chapter_name=chapter_name, description=description, subject_id=int(subject_id))
                db.session.add(new_chapter)
                db.session.commit()
                flash("Chapter added successfully!", "success")

        elif action == "add_question":
            question_statement = request.form['question_statement']
            option1 = request.form['option1']
            option2 = request.form['option2']
            option3 = request.form['option3']
            option4 = request.form['option4']
            correct_answer = request.form['correct_answer']
            chapter_id = request.form.get('chapter_id')

            if not chapter_id:
                flash("Please select a valid chapter!", "warning")
            else:
                new_question = Question(
                    question_statement=question_statement,
                    option1=option1,
                    option2=option2,
                    option3=option3,
                    option4=option4,
                    correct_answer=correct_answer,
                    chapter_id=int(chapter_id)
                )
                db.session.add(new_question)
                db.session.commit()
                flash("Question added successfully!", "success")

    subjects = Subject.query.all()
    chapters = Chapter.query.all()
    quiz = Quiz.query.all()

    return render_template("admin_dashboard.html", subjects=subjects, chapters=chapters, quiz=quiz)

#--------------------------------- Routes for User Dashboard -----------------------------------------
@app.route('/user_dashboard')
def user_dashboard():
    if "user_id" not in session or session['user_role'] != 'user':
        flash("Unauthorized access!", "danger")
        return redirect(url_for("login"))

    quiz = Quiz.query.order_by(Quiz.date_of_quiz).all()

    return render_template('user_dashboard.html', quiz=quiz)

#--------------------------------- Routes for Chapter Management -----------------------------------------
@app.route('/chapter/new', methods=['GET', 'POST'])
def create_chapter():
    if "user_id" not in session or session['user_role'] != 'admin':
        flash("Unauthorized access!", "danger")
        return redirect(url_for("login"))

    if request.method == 'POST':
        chapter_name = request.form['chapter_name']
        description = request.form['chapter_description']
        subject_id = request.form['subject_id']

        new_chapter = Chapter(chapter_name=chapter_name, description=description, subject_id=subject_id)
        db.session.add(new_chapter)
        db.session.commit()
        flash("Chapter created successfully!", "success")
        return redirect(url_for('admin_dashboard'))

    return render_template('create_chapter.html')

@app.route('/api/chapters', methods=['GET'])
def get_chapters():
    chapters = Chapter.query.all()
    return jsonify(chapters=[chapter.serialize() for chapter in chapters])

@app.route('/chapter/<int:chapter_id>', methods=['GET', 'PUT'])
def edit_chapter(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)

    if request.method == 'PUT':
        chapter.chapter_name = request.form['chapter_name']
        chapter.description = request.form['chapter_description']
        db.session.commit()
        flash("Chapter updated successfully!", "success")
        return redirect(url_for('admin_dashboard'))

    return render_template('edit_chapter.html', chapter=chapter)

@app.route('/chapter/<int:chapter_id>', methods=['DELETE'])
def delete_chapter(chapter_id):
    if "user_id" not in session or session['user_role'] != 'admin':
        flash("Unauthorized access!", "danger")
        return redirect(url_for("login"))

    chapter = Chapter.query.get_or_404(chapter_id)
    db.session.delete(chapter)
    db.session.commit()
    flash("Chapter deleted successfully!", "success")
    return redirect(url_for('admin_dashboard'))

#--------------------------------- Routes for Subject Management -----------------------------------------
@app.route('/edit_subject/<int:subject_id>', methods=['GET', 'POST'])
def edit_subject(subject_id):
    subject = Subject.query.get_or_404(subject_id)

    if request.method == 'POST':
        subject.subject_name = request.form['subject_name']
        subject.description = request.form['subject_description']
        db.session.commit()
        return redirect(url_for('admin_dashboard'))

    return render_template('edit_subject.html', subject=subject)

@app.route('/delete_subject/<int:subject_id>', methods=['POST'])
def delete_subject(subject_id):
    if "user_id" not in session or session['user_role'] != 'admin':
        flash("Unauthorized access!", "danger")
        return redirect(url_for("login"))

    subject = Subject.query.get_or_404(subject_id)
    Chapter.query.filter_by(subject_id=subject_id).delete()
    db.session.delete(subject)
    db.session.commit()
    flash("Subject deleted successfully!", "success")
    return redirect(url_for('admin_dashboard'))

#--------------------------------- Routes for Quiz Management -----------------------------------------
@app.route('/quiz', methods=['GET'])
def get_quiz():
    quiz = Quiz.query.all()
    return render_template('quiz.html', quiz=quiz)

@app.route('/quiz', methods=['POST'])
def create_quiz():
    if "user_id" not in session or session['user_role'] != 'admin':
        flash("Unauthorized access!", "danger")
        return redirect(url_for("login"))

    chapter_id = request.json.get('chapter_id')  # Get chapter ID
    date_of_quiz_str = request.json.get('date_of_quiz')  # Get date as string
    time_duration = request.json.get('time_duration')
    remarks = request.json.get('remarks')

    if not chapter_id or not date_of_quiz_str or not time_duration:
        return {"error": "Missing required fields"}, 400

    # Convert date_of_quiz from string to date object
    date_of_quiz = datetime.strptime(date_of_quiz_str, "%Y-%m-%d").date()

    # Process the time_duration
    time_duration = time_duration.split(' ')
    time_duration = int(time_duration[0]) * {'minutes': 1, 'hours': 60, 'days': 1440}[time_duration[1]]

    new_quiz = Quiz(chapter_id=chapter_id, date_of_quiz=date_of_quiz, time_duration=time_duration, remarks=remarks)
    db.session.add(new_quiz)
    db.session.commit()

    flash("Quiz created successfully!", "success")
    return redirect(url_for('admin_dashboard'))  # Redirect to admin dashboard

@app.route('/quiz/<int:quiz_id>', methods=['GET'])
def view_quiz(quiz_id):
    quiz = Quiz.query.options(joinedload(Quiz.questions)).get_or_404(quiz_id)
    return render_template('view_quiz.html', quiz=quiz)

@app.route('/quiz/<int:quiz_id>', methods=['PUT'])
def edit_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)

    chapter_id = request.json.get('chapter_id')
    time_duration = request.json.get('time_duration')
    remarks = request.json.get('remarks')

    if chapter_id:
        quiz.chapter_id = chapter_id
    if time_duration:
        quiz.time_duration = time_duration
    if remarks is not None:
        quiz.remarks = remarks

    db.session.commit()

    return {"message": "Quiz updated successfully"}, 200

@app.route('/quiz/<int:quiz_id>', methods=['POST'])
def delete_quiz(quiz_id):
    if request.form.get('_method') == 'DELETE':
        quiz = Quiz.query.get_or_404(quiz_id)
        db.session.delete(quiz)
        db.session.commit()
        flash("Quiz deleted successfully")
        return redirect(url_for('admin_dashboard'))
    return {"message": "Method not allowed"}, 405

@app.route('/quiz/<int:quiz_id>', methods=['GET'])
def start_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)  # Fetch the quiz by ID or return a 404 error
    questions = Question.query.filter_by(chapter_id=quiz.chapter_id).all()  # Fetch questions related to the quiz

    return render_template('start_quiz.html', quiz=quiz, questions=questions)

#--------------------------------- Other Routes -----------------------------------------
@app.route('/summary')
def summary():
    return render_template('summary.html')

@app.route('/score')
def score():
    return render_template('score.html')

@app.route('/search')
def search():
    if "user_id" not in session or session.get("user_role") != "admin":
        flash("Unauthorized access!", "danger")
        return redirect(url_for("login"))

    query = request.args.get("query", "").strip()
    subjects = []
    chapters = []

    if query:
        subjects = Subject.query.filter(Subject.subject_name.ilike(f"%{query}%")).union(
            Subject.query.filter(Subject.description.ilike(f"%{query}%"))
        ).all()
        chapters = Chapter.query.filter(Chapter.chapter_name.ilike(f"%{query}%")).union(
            Chapter.query.filter(Chapter.description.ilike(f"%{query}%"))
        ).all()

    return render_template("search.html", query=query, subjects=subjects, chapters=chapters)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)