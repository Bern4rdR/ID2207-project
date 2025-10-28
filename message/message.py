from uuid import uuid4
from event.Request import EventRequest
from event.models import Event, Task
from hr.crew_request import CrewRequest
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

class ViewAllRequestMessage(Message):
    pass

class EventMessage(Message):
    event: Event
    name: str
    def __init__(self, ev: Event):
        self.event = ev
        self.name = ev.name

class NewEventMessage(Message):
    request: EventRequest
    name: str
    def __init__(self, er: EventRequest):
        self.request = er
        self.name = er.name

class ViewEventMessage(Message):
    def __init__(self, name):
        self.name = name

class ApproveRequestMessage(Message):
    approve: bool
    def __init__(self, name: str, role, approved: bool):
        self.approve = approved
        self.name = name
        self.role = role

class DecideEventMessage(NewEventMessage):
    role = None
    decision = None
    def __init__(self, name, descripton, budget, role, decision):
        super.__init__(name, descripton, budget)
        self.role = role
        self.decision = decision

class RequestApprovedMessage(Message):
    def __init__(self, name):
        self.name = name

class RequestRejectedMessage(RequestApprovedMessage):
    pass

class FindWaitingRequestMessage(Message):
    def __init__(self, role):
        self.role = role

class EventListMessage(Message):
    events: list[Event]
    def __init__(self, events):
        self.events = events

class TaskListMessage(Message):
    tasks: list[Task]
    def __init__(self, tasks):
        self.tasks = tasks

class RequestListMessage(Message):
    requests: list[EventRequest]
    def __init__(self, ers):
        self.requests = ers

# messages to support modifying and creating tasks
class TaskMessage(Message):
    task: Task
    def __init__(self, task):
        self.task = task

class NewTaskMessage(TaskMessage):
    pass

class UpdateTaskMessage(TaskMessage):
    pass

class PendingListMessage(Message):
    names: list[str]
    def __init__(self, names):
        self.names = names

class CrewRequestMessage(Message):
    crewRequest: CrewRequest
    name: str
    def __init__(self, cr: CrewRequest):
        self.crewRequest = cr
        self.name = cr.name