from app.models.task import Task

class TaskFactory:
    @staticmethod
    def create_task( title, description):
        return Task(title=title, description=description)
