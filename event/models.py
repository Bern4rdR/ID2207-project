# models.py

class Event:
    def __init__(self, name: str, budget: float = 0, description: str = ""):
        self.name = name
        self.budget = budget
        self.description = description
        self._tasks = []

    def add_task(self, task: "Task"):
        self._tasks.append(task)

    def tasks(self):
        return self._tasks


class Task:
    def __init__(self, name: str, budget: float = 0, description: str = "", assignee: str = None):
        self.name = name
        self.budget = budget
        self.description = description
        self.assignee = assignee
        self.comments = []
        self._approved = False

    @property
    def last_comment(self):
        if len(self.comments):
            return self.comments[-1]
        else:
            return ""

    def add_budget_comment(self, comment: str):
        """Add a budget-related comment to the task."""
        self.comments.append(comment)

    def approve(self):
        """Mark this task as approved."""
        self._approved = True

    def approved(self) -> bool:
        """Return True if the task is approved, else False."""
        return self._approved
