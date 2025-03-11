from app import db
from app.models.task import Task
from app.patterns.observer_pattern import TaskObserver

class TaskService:
    def __init__(self):
        self.observer = TaskObserver()

    def add_task(self, task):
        db.session.add(task)
        db.session.commit()
        self.observer.update(task)

    def get_all_tasks(self):
        return Task.query.all()

    def get_task_by_id(self, task_id):
        return Task.query.get(task_id)

    def update_task(self, task):
        db.session.commit()
        self.observer.update(task)

    def delete_task(self, task_id):
        task = self.get_task_by_id(task_id)
        if task:
            db.session.delete(task)
            db.session.commit()
            self.observer.update(task)