from flask import flash

class Observer:
    def update(self, task):
        pass

class TaskObserver(Observer):
    def update(self, task):
        flash(f'Task "{task.title}" has been updated!', 'info')  # Mesaj flash