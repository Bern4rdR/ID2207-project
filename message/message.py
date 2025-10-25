from uuid import uuid4
from event.Request import EventRequest
from event.models import Event, Task
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
    event: Event
    def __init__(self, ev: Event):
        self.event = ev

class NewEventMessage(Message):
    request: EventRequest
    def __init__(self, er: EventRequest):
        self.request = er

class ViewEventMessage(Message):
    def __init__(self, name):
        self.name = name

class ApproveRequestMessage(NewEventMessage):
    approve: bool
    def __init__(self, er: EventRequest, approved: bool):
        super.__init__(er)
        self.approve = approved

class DecideEventMessage(EventMessage):
    role = None
    decision = None
    def __init__(self, name, descripton, budget, role, decision):
        super.__init__(name, descripton, budget)
        self.role = role
        self.decision = decision