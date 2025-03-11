from datetime import datetime
from flask import Blueprint, request, jsonify, render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from app.models.task import Task
from app.models.user import User
from app.services.task_service import TaskService
from app.patterns.command_pattern import AddTaskCommand
from app import db

task_bp = Blueprint('task_bp', __name__)
task_service = TaskService()

@task_bp.route('/')
def index():
    if not current_user.is_authenticated:
        return redirect(url_for('user_bp.login'))
    return redirect(url_for('task_bp.dashboard'))  # Redirecționează corect

@task_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'admin':
        return redirect(url_for('user_bp.admin_dashboard'))
    else:
        return redirect(url_for('user_bp.user_dashboard'))


@task_bp.route('/complete_task/<int:task_id>')
@login_required
def complete_task(task_id):
    task = Task.query.get(task_id)
    if task.user_id != current_user.id and current_user.role != 'admin':
        flash('Access denied')
        return redirect(url_for('task_bp.dashboard'))

    task.completed = True
    db.session.commit()
    flash('Task marked as completed')
    return redirect(url_for('task_bp.dashboard'))

#@task_bp.route('/upload/<int:task_id>', methods=['GET', 'POST'])
#@login_required
#def upload(task_id):
 #   task = Task.query.get(task_id)
  #  if task.user_id != current_user.id and current_user.role != 'admin':
   #     flash('Access denied')
    #    return redirect(url_for('task_bp.dashboard'))
#
 #   if request.method == 'POST':
  #      if 'file' not in request.files or request.files['file'].filename == '':
   #         flash('No file part or no selected file')
    #        return redirect(request.url)
     #   file = request.files['file']
      #  filename = secure_filename(file.filename)
       # file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        #file.save(file_path)
        #task.file_url = file_path
        #db.session.commit()
        #flash('File uploaded')
        #return redirect(url_for('task_bp.dashboard'))

    #return render_template('upload.html', task=task)
#

@task_bp.route('/new_task', methods=['GET', 'POST'])
@login_required
def new_task():
    users = User.query.all()  # Obține toți utilizatorii din baza de date
    if request.method == 'POST':
        data = request.form
        new_task = Task(
            title=data.get('title'),
            description=data.get('description', ''),
            due_date=datetime.strptime(data.get('due_date'), '%Y-%m-%d').date() if data.get('due_date') else None,
            user_id=int(data.get('user_id'))  # Asigură-te că user_id este convertit la întreg
        )
        db.session.add(new_task)
        db.session.commit()
        flash('Task added successfully', 'success')
        return redirect(url_for('task_bp.dashboard'))

    return render_template('index.html', users=users)

@task_bp.route('/tasks', methods=['GET'])
def get_tasks():
    tasks = task_service.get_all_tasks()
    return jsonify([task.title for task in tasks])

@task_bp.route('/tasks', methods=['POST'])
@login_required
def add_task():
    data = request.json
    task = Task(
        title=data['title'],
        description=data.get('description', ''),
        user_id=data['user_id'],
        due_date=datetime.strptime(data['due_date'], '%Y-%m-%d').date() if data.get('due_date') else None
    )
    command = AddTaskCommand(task_service, task)
    command.execute()
    flash(f'Task "{task.title}" has been added!', 'success')
    return jsonify({"message": "Task added"}), 201

@task_bp.route('/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    task = task_service.get_task_by_id(task_id)
    if task:
        return render_template('task.html', task=task)
    else:
        return jsonify({"message": "Task not found"}), 404

@task_bp.route('/tasks/<int:task_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    task = task_service.get_task_by_id(task_id)
    if not task:
        flash('Task not found')
        return redirect(url_for('task_bp.dashboard'))

    if request.method == 'POST':
        data = request.form
        task.title = data['title']
        task.description = data.get('description', '')

        due_date_str = data.get('due_date')
        if due_date_str:
            task.due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()

        task.priority = data.get('priority')
        task_service.update_task(task)
        flash('Task updated successfully')
        return redirect(url_for('task_bp.dashboard'))

    return render_template('edit_task.html', task=task)

@task_bp.route('/tasks/<int:task_id>/delete', methods=['POST'])
@login_required
def delete_task(task_id):
    task = task_service.get_task_by_id(task_id)
    if not task:
        flash('Task not found', 'danger')
        return redirect(url_for('task_bp.dashboard'))

    if task.user_id != current_user.id and current_user.role != 'admin':
        flash('Access denied', 'danger')
        return redirect(url_for('task_bp.dashboard'))

    task_service.delete_task(task_id)
    flash('Task deleted successfully', 'success')
    return redirect(url_for('task_bp.dashboard'))