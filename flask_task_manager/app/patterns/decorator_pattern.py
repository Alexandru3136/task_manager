class TaskDecorator:
    def __init__(self, task):
        self.task = task

    def complete(self):
        self.task.complete()
        print(f"Task {self.task.title} completed.")
