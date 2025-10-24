from uuid import uuid4
#literally stealing this from the senior engineers at my last job
# part of the UI, don't need tests

class Message:
    name = ""
    role = "user"
    def setRole(self, role):
        self.role = role

class StopMessage(Message):
    name="stop"

class LoginMessage(Message):
    _username = ""
    _password = ""
    def __init__(self, username, password):
        self._username = username
        self._password = password

class LoginResultMessage(Message):
    success = False
    role = ""
    def __init__(self, success, role):
        self.success = success
        self.role = role

class EventMessage(Message):
    id = None
    budget = None
    description = None
    def __init__(self, name, description, budget):
        self.name = name
        self.id = uuid4()
        self.description = description
        self.budget = budget

class NewEventMessage(EventMessage):
    pass

class ViewEventMessage(EventMessage):
    pass

class DecideEventMessage(EventMessage):
    role = None
    decision = None
    def __init__(self, name, descripton, budget, role, decision):
        super.__init__(name, descripton, budget)
        self.role = role
        self.decision = decision