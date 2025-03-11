class TaskProcessor:
    @staticmethod
    def process_task(self, task):
        self.validate_task(task)
        self.save_task(task)
        self.notify_user(task)

    @staticmethod
    def validate_task(task):
        print(f"Validating task: {task.title}")

    @staticmethod
    def save_task(task):
        print(f"Saving task: {task.title}")

    @staticmethod
    def notify_user(task):
        print(f"Notifying user about task: {task.title}")
