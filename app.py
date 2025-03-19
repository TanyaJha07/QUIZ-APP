from flask import Flask, render_template, request, redirect, url_for, flash, session
from models import User, db, Quiz, Question, Score, Subject, Chapter
from datetime import datetime
from sqlalchemy import or_


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quiz.db'
app.secret_key = "your_super_secret_key_here" 
db.init_app(app)  

with app.app_context():
    db.create_all() 

    admin_email = "admin@example.com"
    admin_password = "aaaaa" 

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

# app.app_context().push()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    print("Signup route accessed!")
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
            
            # Check if subject already exists
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

            if not subject_id:  # Ensure subject_id is not None or empty
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

            if not chapter_id:  # Ensure chapter_id is valid
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

    # Fetch all subjects & chapters for dropdowns
    subjects = Subject.query.all()
    chapters = Chapter.query.all()

    return render_template("admin_dashboard.html", subjects=subjects, chapters=chapters)

@app.route('/edit_subject/<int:subject_id>', methods=['GET', 'POST'])
def edit_subject(subject_id):
    subject = Subject.query.get_or_404(subject_id)

    if request.method == 'POST':
        subject.subject_name = request.form['subject_name']
        subject.description = request.form['subject_description']
        db.session.commit()
        return redirect(url_for('admin_dashboard'))

    return render_template('edit_subject.html', subject=subject)

@app.route('/edit_chapter/<int:chapter_id>', methods=['GET', 'POST'])
def edit_chapter(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)

    if request.method == 'POST':
        chapter.chapter_name = request.form['chapter_name']
        chapter.description = request.form['chapter_description']
        db.session.commit()
        return redirect(url_for('admin_dashboard'))

    return render_template('edit_chapter.html', chapter=chapter)

@app.route('/delete_subject/<int:subject_id>', methods=['POST'])
def delete_subject(subject_id):
    if "user_id" not in session or session['user_role'] != 'admin':
        flash("Unauthorized access!", "danger")
        return redirect(url_for("login"))

    subject = Subject.query.get_or_404(subject_id)
    
    # Ensure all related chapters are deleted first
    Chapter.query.filter_by(subject_id=subject_id).delete()
    
    db.session.delete(subject)
    db.session.commit()
    flash("Subject deleted successfully!", "success")
    return redirect(url_for('admin_dashboard'))

@app.route('/delete_chapter/<int:chapter_id>', methods=['POST'])
def delete_chapter(chapter_id):
    if "user_id" not in session or session['user_role'] != 'admin':
        flash("Unauthorized access!", "danger")
        return redirect(url_for("login"))

    chapter = Chapter.query.get_or_404(chapter_id)
    db.session.delete(chapter)
    db.session.commit()
    flash("Chapter deleted successfully!", "success")
    return redirect(url_for('admin_dashboard'))

@app.route('/add_question', methods=['GET', 'POST'])
def add_question():
    if "user_id" not in session or session['user_role'] != 'admin':
        flash("Unauthorized access!", "danger")
        return redirect(url_for("login"))

    if request.method == 'POST':
        question_statement = request.form.get('question_statement')
        option1 = request.form.get('option1')
        option2 = request.form.get('option2')
        option3 = request.form.get('option3')
        option4 = request.form.get('option4')
        correct_answer = request.form.get('correct_answer')
        quiz_id = request.form.get('quiz_id')  # Select quiz, not chapter

        # Validate required fields
        if not (question_statement and option1 and option2 and option3 and option4 and correct_answer and quiz_id):
            flash("All fields are required!", "danger")
            return redirect(url_for("add_question"))

        # Create new question
        new_question = Question(
            question_statement=question_statement,
            option1=option1,
            option2=option2,
            option3=option3,
            option4=option4,
            correct_answer=correct_answer,
            quiz_id=int(quiz_id)  # Ensure it's an integer
        )
        db.session.add(new_question)
        db.session.commit()
        flash("Question added successfully!", "success")
        return redirect(url_for('admin_dashboard'))

    quizzes = Quiz.query.all()  # Fetch quizzes instead of chapters
    return render_template('add_question.html', quizzes=quizzes)


@app.route('/user_dashboard')
def user_dashboard():
    if "user_id" not in session or session.get("user_role") != "user":
        flash("Please login as a user to access this page.", "danger")
        return redirect(url_for("login"))
    
    subjects = Subject.query.all()
    return render_template('user_dashboard.html', subjects=subjects)

@app.route('/quiz')
def quiz():
    return render_template('quiz.html')

@app.route('/summary')
def summary():   
    return render_template('summary.html')

@app.route('/score')   
def score():   
    return render_template('score.html')

@app.route('/search')
@app.route('/search')
def search():
    # Ensure only admin can access the search page
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
