from enum import Enum

class Department(Enum):
    Production = 1
    HR = 2
    Finance = 3

class CrewRequest:
    def __init__(self, name, department=None, description="", salary=0, fulltime=True):
        self.name = name
        self.department = department
        self.description = description
        self.salary = salary
        self.fulltime = fulltime
        self.comments = []
        self.approved = False
    
    @property
    def last_comment(self):
        if len(self.comments):
            return self.comments[-1]
        else:
            return ""

    def add_comment(self, comment: str):
        self.comments.append(comment)

    def get_comments(self):
        return self.comments

    def approve(self):
        self.approved = True
