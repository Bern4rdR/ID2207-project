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
    user = ""
    def __init__(self, success, role, user):
        self.success = success
        self.role = role
        self.user = user

"""
@Bernard, since you wrote the event class please look over these and change them however you want. We could just have it hold an event 
instead of the event details. Then the CLI has to do event validation, which is fine. 
It is probably better if it just holds an event, with some message specific metadata (like role and user who just sent an approval or whatever)
"""
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