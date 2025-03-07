from flask import Flask, render_template, request, redirect, url_for, flash, session
from models import User, db, Quiz, Question, Score, Subject, Chapter
from datetime import datetime

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

@app.route('/admin_dashboard')
def admin_dashboard():
    return render_template('admin_dashboard.html')

@app.route('/user_dashboard')   
def user_dashboard():  
    if "user_id" not in session or session['user_role'] != 'user':
        flash("Please login as a user to access this page.", "danger")
        return redirect(url_for("login")) 
    return render_template('user_dashboard.html')

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
def search():   
    return render_template('search.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run(debug=True)
