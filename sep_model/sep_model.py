import pickle
from message.message import (
    Message,
    LoginMessage,
    StopMessage,
    LoginResultMessage,
    NewEventMessage,
    ViewEventMessage,
    DecideEventMessage,
    ViewAllRequestMessage,
    RequestListMessage,
    ApproveRequestMessage,
    RequestApprovedMessage,
    RequestRejectedMessage,
    FindWaitingRequestMessage,
    RequestListMessage,
    EventListMessage,
    TaskListMessage,
    UpdateTaskMessage,
    NewTaskMessage,
    PendingListMessage,
    CrewRequestMessage,
    CrewRequestListMessage,
    CrewRequestUpdateMessage,
)
from login.login_manager import LoginManager
from multiprocessing import Queue
from hr.crew_request import Role, Department, CrewRequest
from event.Request import EventRequest
from event.models import Event, Task


# this defines the main backend loop and data structure
# probably should be in a different file but we need 3 refactors per day so...
class SepModel:
    _tasks: list[Task] = []
    _events: list[Event] = []
    _requests: list[EventRequest] = []
    _crewRequests: list[CrewRequest] = []

    def __init__(self, bgMsgQueue: Queue, outputQueue: Queue):
        self._lm = LoginManager("./login/users.txt")
        self._bgMsgQueue = bgMsgQueue
        self._outputQueue = outputQueue

    def save_on_exit(self):
        with open("sep_tasks.pkl", "wb") as f:
            f.truncate(0)
            pickle.dump(self._tasks, f)
        with open("sep_events.pkl", "wb") as f:
            f.truncate(0)
            pickle.dump(self._events, f)
        with open("sep_requests.pkl", "wb") as f:
            f.truncate(0)
            pickle.dump(self._requests, f)

        # TODO: Safe crewRequests on exit

    def load_on_enter(self):
        # yes this is lazy
        try:
            with open("sep_tasks.pkl", "rb") as f:
                self._tasks = pickle.load(f)
            with open("sep_events.pkl", "rb") as f:
                self._events = pickle.load(f)
            with open("sep_requests.pkl", "rb") as f:
                self._requests = pickle.load(f)

            # TODO: Safe crewRequests on exit

        except:
            self._tasks = []
            self._requests = []
        self._outputQueue.put(RequestListMessage(self._requests))
        self._outputQueue.put(EventListMessage(self._events))
        # self._outputQueue.put(TaskListMessage(self._tasks)) # all the tasks are in their events

    def find_event(self, name):
        for event in self._requests:
            if event.name == name:
                return event
        return None

    def send_waiting_requests(self, msg):
        names = []
        if msg.role == Role.CSR:
            names = [x.name for x in self._requests if x.awaiting_CSR]
        elif msg.role == Role.Fin:
            names = [x.name for x in self._requests if x.awaiting_fin]
        elif msg.role == Role.Admin:
            names = [x.name for x in self._requests if x.awaiting_admin]
        self._outputQueue.put(PendingListMessage(names))

    def add_task(self, task: Task):
        for ev in self._events:
            if ev._id == task._event_id:
                ev.add_task(task)
                self._outputQueue.put(EventListMessage(self._events))
                return

    def update_task(self, task: Task):
        for ev in self._events:
            if ev._id == task._event_id:
                for i, ts in enumerate(ev.tasks):
                    if task.name == ts.name:
                        ev.tasks[i] = task
                self._outputQueue.put(EventListMessage(self._events))
                return
    
    def update_crew_request(self, crewRequest: CrewRequest):
        for i, cr in enumerate(self._crewRequests):
            if cr.name == crewRequest.name:
                self._crewRequests[i] = crewRequest
                self._outputQueue.put(CrewRequestListMessage(self._crewRequests))
                return

    # do tasks to check model status
    def admin(self):
        # check if any events Requests are fully approved
        req2 = []
        for i, req in enumerate(self._requests):
            if req.approved:
                ev = Event(req.name, req.budget, req.type)
                ev.add_request(req)
                self._events.append(ev)
            else:
                req2.append(req)
        if len(self._requests) != len(req2):
            self._requests = req2
            self._outputQueue.put(RequestListMessage(self._requests))
            self._outputQueue.put(EventListMessage(self._events))

    # call and response
    def loop(self):
        while True:
            try:
                next_msg = self._bgMsgQueue.get()
                if type(next_msg) is LoginMessage:
                    # got really lazy with the privacy here
                    success, role = self._lm.login(
                        next_msg._username, next_msg._password
                    )
                    self._outputQueue.put(
                        LoginResultMessage(success, role, next_msg._username)
                    )
                elif type(next_msg) is StopMessage:
                    self.save_on_exit()
                    break
                elif type(next_msg) is NewEventMessage:
                    self._requests.append(next_msg.request)
                elif type(next_msg) is ViewEventMessage:
                    ev = [x for x in self._requests if x.name == next_msg.name]
                    if len(ev):
                        self._outputQueue.put(ev[0])
                elif type(next_msg) is ViewAllRequestMessage:
                    names = [x.name for x in self._requests]
                    self._outputQueue.put(RequestListMessage(names))
                elif type(next_msg) is ApproveRequestMessage:
                    event = self.find_event(next_msg.name)
                    if event and next_msg.approve:
                        event.approve(next_msg.role)
                        self._outputQueue.put(RequestApprovedMessage(next_msg.name))
                    elif not next_msg.decision:
                        event.reject()
                        self._outputQueue.put(RequestRejectedMessage(next_msg.name))
                elif type(next_msg) is FindWaitingRequestMessage:
                    self.send_waiting_requests(next_msg)
                elif type(next_msg) is UpdateTaskMessage:
                    self.update_task(next_msg.task)
                elif type(next_msg) is NewTaskMessage:
                    self.add_task(next_msg.task)
                # catch generic messages below, seeing those means there is an issue
                elif type(next_msg) is CrewRequestMessage:
                    self._crewRequests.append(next_msg.crewRequest)
                    self._outputQueue.put(CrewRequestListMessage(self._crewRequests))
                elif type(next_msg) is CrewRequestUpdateMessage:
                    self.update_crew_request(next_msg.crewRequest)
                elif type(next_msg) is Message:
                    print(f"Message received with Type Message {next_msg.name}")
                else:
                    print(
                        f"Model:: Message received without type detected {next_msg.name}"
                    )
            except Exception as e:
                print(f"Error {e}")
            self.admin()


def run_model(qin, qout):
    model = SepModel(qin, qout)
    model.load_on_enter()
    model.loop()
