class Command:
    def execute(self):
        pass

class AddTaskCommand(Command):
    def __init__(self, task_service, task):
        self.task_service = task_service
        self.task = task

    def execute(self):
        self.task_service.add_task(self.task)
