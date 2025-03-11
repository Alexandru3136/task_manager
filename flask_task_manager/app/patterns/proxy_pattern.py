class TaskServiceProxy:
    def __init__(self, task_service):
        self.task_service = task_service

    def add_task(self, task):
        print("Proxy: Checking access before adding task.")
        self.task_service.add_task(task)
