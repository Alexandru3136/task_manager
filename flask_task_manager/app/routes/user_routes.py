import os
from datetime import datetime
from flask import Blueprint, jsonify, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from app.models.user import User
from app.models.task import Task
from app import db, login_manager
from app.services.user_service import UserService
from flask import current_app

user_bp = Blueprint('user_bp', __name__)
user_service = UserService()

def redirect_based_on_role(user):
    print(f"User role: {user.role}")  # Debugging
    if user.role == 'admin':
        return redirect(url_for('user_bp.admin_dashboard'))
    return redirect(url_for('user_bp.user_dashboard'))

@user_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'], method='pbkdf2:sha256')
        role = request.form['role']
        new_user = User(username=username, email=email, password=password, role=role)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('user_bp.login'))
    return render_template('register.html')

@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        print(f"Already logged in: {current_user.username}, role: {current_user.role}")  # Debugging
        logout_user()  # Logout utilizatorul vechi înainte de login nou
        flash("You were logged out automatically.", "info")

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user:
            print(f"Found user: {user.username}, role: {user.role}")  # Debugging

        if user and check_password_hash(user.password, password):
            print(f"Logging in user: {user.username}, role: {user.role}")  # Debugging
            logout_user()  # Siguranță suplimentară pentru a reseta sesiunea
            login_user(user)
            return redirect_based_on_role(user)
        else:
            flash("Invalid credentials", "error")

    return render_template('login.html')


@user_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('user_bp.login'))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@user_bp.route('/users', methods=['GET'])
@login_required
def get_users():
    if current_user.role != 'admin':
        flash("Access denied", "error")
        return redirect(url_for('user_bp.user_dashboard'))
    users = user_service.get_all_users()
    return jsonify([user.username for user in users])

@user_bp.route('/users', methods=['POST'])
@login_required
def add_user():
    if current_user.role != 'admin':
        flash("Access denied", "error")
        return redirect(url_for('user_bp.user_dashboard'))
    data = request.json
    user = User(username=data['username'], email=data['email'])
    user_service.add_user(user)
    flash("User added", "info")
    return jsonify({"message": "User added"}), 201

@user_bp.route('/admin/dashboard', methods=['GET'])
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        flash(f'Acces interzis pentru utilizatorul {current_user.username} cu rolul {current_user.role}', "error")
        return redirect(url_for('user_bp.user_dashboard'))

    total_tasks = Task.query.count()
    completed_tasks = Task.query.filter_by(completed=True).count()
    total_users = User.query.filter_by(role='user').count()

    recent_tasks = Task.query.order_by(Task.id.desc()).limit(5).all()
    current_year = datetime.now().year

    return render_template('admin_dashboard.html',
                           total_tasks=total_tasks,
                           completed_tasks=completed_tasks,
                           total_users=total_users,
                           recent_tasks=recent_tasks,
                           current_year=current_year)

@user_bp.route('/admin/tasks/new', methods=['POST'])
@login_required
def create_task():
    if current_user.role != 'admin':
        flash('Access denied', "error")
        return redirect(url_for('user_bp.user_dashboard'))
    title = request.form['title']
    description = request.form['description']
    due_date_str = request.form['due_date']
    due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date() if due_date_str else None
    user_id = request.form['user_id']
    new_task = Task(title=title, description=description, due_date=due_date, user_id=user_id)
    db.session.add(new_task)
    db.session.commit()
    flash('Task created successfully', "info")
    return redirect(url_for('user_bp.admin_dashboard'))

@user_bp.route('/admin/tasks/<int:task_id>/edit', methods=['POST'])
@login_required
def edit_task(task_id):
    if current_user.role != 'admin':
        flash('Access denied', "error")
        return redirect(url_for('user_bp.user_dashboard'))
    task = Task.query.get(task_id)
    task.title = request.form['title']
    task.description = request.form['description']
    due_date_str = request.form['due_date']
    task.due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date() if due_date_str else None
    task.user_id = request.form['user_id']
    db.session.commit()
    flash('Task updated successfully', "info")
    return redirect(url_for('user_bp.admin_dashboard'))

@user_bp.route('/admin/manage_users')
@login_required
def manage_users():
    if current_user.role != 'admin':
        flash('Acces interzis', "error")
        return redirect(url_for('user_bp.user_dashboard'))
    users = User.query.all()
    return render_template('manage_users.html', users=users)

@user_bp.route('/user/dashboard', methods=['GET'])
@login_required
def user_dashboard():
    tasks = current_user.tasks
    return render_template('user_dashboard.html', tasks=tasks)


@user_bp.route('/user/tasks/<int:task_id>/confirm', methods=['POST'])
@login_required
def confirm_task(task_id):
    task = Task.query.get(task_id)

    if not task or task.user_id != current_user.id:
        flash("Access denied or task not found", "error")
        return redirect(url_for('user_bp.user_dashboard'))

    confirmation_link = request.form.get('confirmation_link')

    if not confirmation_link:
        flash("Please provide a confirmation link!", "warning")
        return redirect(url_for('user_bp.user_dashboard'))

    # Salvăm link-ul și marcăm task-ul ca „completed”
    task.confirmation_link = confirmation_link
    task.completed = True  # Asigură-te că ai acest câmp în modelul `Task`
    db.session.commit()

    flash("Task confirmed successfully!", "success")
    return redirect(url_for('user_bp.user_dashboard'))

@user_bp.route('/user/tasks/<int:task_id>/upload', methods=['POST'])
@login_required
def upload_file(task_id):
    task = Task.query.get(task_id)
    if task.user_id != current_user.id:
        flash('Access denied', "error")
        return redirect(url_for('user_bp.user_dashboard'))
    if 'file' not in request.files or request.files['file'].filename == '':
        flash('No file part or no selected file', "error")
        return redirect(request.url)
    file = request.files['file']
    filename = secure_filename(file.filename)
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)
    task.file_url = file_path
    db.session.commit()
    flash('File uploaded', "info")
    return redirect(url_for('user_bp.user_dashboard'))
