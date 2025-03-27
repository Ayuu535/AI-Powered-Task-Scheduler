import os
import logging
from datetime import datetime
from flask import Flask, render_template, redirect, url_for, flash, request, jsonify, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

# Configure database (SQLite for local development)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///taskmaster.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Define SQLite models
class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    tasks = db.relationship('Task', backref='owner', lazy='dynamic', cascade="all, delete-orphan")
    
    # Required for Flask-Login
    @property
    def is_active(self):
        return True
    
    @property
    def is_authenticated(self):
        return True
    
    @property
    def is_anonymous(self):
        return False
    
    def get_id(self):
        return str(self.id)

class Task(db.Model):
    __tablename__ = 'task'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    deadline = db.Column(db.DateTime, nullable=False)
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

# Configure login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Import forms and utility functions
from forms import LoginForm, RegisterForm, TaskForm, ProfileForm
from utils import sort_tasks_by_edf

# Create tables
with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('tasks'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        
        # Find user by username
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('tasks'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data
        
        # Check if username already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists. Please choose another one.', 'danger')
            return render_template('register.html', form=form)
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered. Please use another one.', 'danger')
            return render_template('register.html', form=form)
        
        # Create new user
        user = User(username=username, email=email)
        user.password_hash = generate_password_hash(password)
        
        # Add to database
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/tasks', methods=['GET', 'POST'])
@login_required
def tasks():
    form = TaskForm()
    if form.validate_on_submit():
        title = form.title.data
        description = form.description.data
        deadline_str = form.deadline.data
        
        # Convert string to datetime
        deadline = datetime.strptime(deadline_str, '%Y-%m-%dT%H:%M')
        
        # Create new task
        task = Task(user_id=current_user.id, title=title, 
                    description=description, deadline=deadline)
        
        # Add to database
        db.session.add(task)
        db.session.commit()
        
        flash('Task added successfully!', 'success')
        return redirect(url_for('tasks'))
    
    # Get all tasks for current user
    user_tasks = Task.query.filter_by(user_id=current_user.id).all()
    
    # Sort tasks using EDF algorithm
    sorted_tasks = sort_tasks_by_edf(user_tasks)
    
    # Group tasks by status (incomplete first, then completed)
    incomplete_tasks = [task for task in sorted_tasks if not task.completed]
    completed_tasks = [task for task in sorted_tasks if task.completed]
    
    return render_template('tasks.html', form=form, 
                          incomplete_tasks=incomplete_tasks, 
                          completed_tasks=completed_tasks)

@app.route('/tasks/<int:task_id>/complete', methods=['POST'])
@login_required
def complete_task(task_id):
    task = Task.query.get(task_id)
    
    if not task:
        flash('Task not found', 'danger')
        return redirect(url_for('tasks'))
    
    if task.user_id != current_user.id:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('tasks'))
    
    task.completed = not task.completed
    db.session.commit()
    
    if task.completed:
        flash('Task marked as completed!', 'success')
    else:
        flash('Task marked as incomplete!', 'info')
    
    return redirect(url_for('tasks'))

@app.route('/tasks/<int:task_id>/delete', methods=['POST'])
@login_required
def delete_task(task_id):
    task = Task.query.get(task_id)
    
    if not task:
        flash('Task not found', 'danger')
        return redirect(url_for('tasks'))
    
    if task.user_id != current_user.id:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('tasks'))
    
    db.session.delete(task)
    db.session.commit()
    
    flash('Task deleted successfully!', 'success')
    return redirect(url_for('tasks'))

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm()
    
    if request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    
    if form.validate_on_submit():
        user = User.query.get(current_user.id)
        
        # Check if username is changed and if it exists
        if form.username.data != user.username:
            existing_user = User.query.filter_by(username=form.username.data).first()
            if existing_user and existing_user.id != user.id:
                flash('Username already exists. Please choose another one.', 'danger')
                return render_template('profile.html', form=form)
            user.username = form.username.data
        
        # Check if email is changed and if it exists
        if form.email.data != user.email:
            existing_user = User.query.filter_by(email=form.email.data).first()
            if existing_user and existing_user.id != user.id:
                flash('Email already registered. Please use another one.', 'danger')
                return render_template('profile.html', form=form)
            user.email = form.email.data
        
        # Update password if provided
        if form.password.data:
            user.password_hash = generate_password_hash(form.password.data)
        
        # Save changes to database
        db.session.commit()
        
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile'))
    
    # Count user's tasks
    user_tasks = Task.query.filter_by(user_id=current_user.id).all()
    total_tasks = len(user_tasks)
    completed_tasks = len([task for task in user_tasks if task.completed])
    
    return render_template('profile.html', form=form, 
                          total_tasks=total_tasks, 
                          completed_tasks=completed_tasks)

@app.route('/tasks/filter', methods=['GET'])
@login_required
def filter_tasks():
    filter_type = request.args.get('type', 'all')
    
    # Base query for current user's tasks
    query = Task.query.filter_by(user_id=current_user.id)
    
    if filter_type == 'completed':
        filtered_tasks = query.filter_by(completed=True).all()
    elif filter_type == 'incomplete':
        filtered_tasks = query.filter_by(completed=False).all()
    elif filter_type == 'upcoming':
        now = datetime.now()
        filtered_tasks = query.filter_by(completed=False).filter(Task.deadline > now).all()
    elif filter_type == 'overdue':
        now = datetime.now()
        filtered_tasks = query.filter_by(completed=False).filter(Task.deadline < now).all()
    else:  # 'all'
        filtered_tasks = query.all()
    
    # Sort tasks using EDF algorithm
    sorted_tasks = sort_tasks_by_edf(filtered_tasks)
    
    # Convert tasks to dictionaries for JSON response
    tasks_list = []
    for task in sorted_tasks:
        tasks_list.append({
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'deadline': task.deadline.strftime('%Y-%m-%d %H:%M'),
            'completed': task.completed
        })
    
    return jsonify({'tasks': tasks_list})