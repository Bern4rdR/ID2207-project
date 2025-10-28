from multiprocessing import Queue
import datetime
from message.message import (
    NewEventMessage,
    ViewAllRequestMessage,
    ApproveRequestMessage,
    CrewRequestMessage,
    StopMessage,
)
from sep_model.sep_model import SepModel
from event.Request import EventRequest
from event.models import Task
from event.Status import Status
from threading import Thread
from hr.crew_request import Role, Department, CrewRequest


def _new_event(model, bgq):
    evt_date = datetime.datetime.now() + datetime.timedelta(days=1)
    req = EventRequest("evtName", "evtDesc", 100, [evt_date])

    _send_command(model, bgq, NewEventMessage(req))


def _send_command(model, bgq, command):
    t = Thread(target=model.loop, daemon=True)
    t.start()

    bgq.put(command)
    bgq.put(StopMessage())
    t.join()


def test_new_event():
    bgq = Queue()
    outq = Queue()

    model = SepModel(bgq, outq)
    num_requests = len(model._requests)
    _new_event(model, bgq)

    assert len(model._requests) == num_requests + 1


def test_view_all_requests():
    bgq = Queue()
    outq = Queue()

    model = SepModel(bgq, outq)
    _new_event(model, bgq)

    _send_command(model, bgq, ViewAllRequestMessage())
    assert outq.get() is not None


def test_approve_request():

    # TODO: fix the test
    return

    bgq = Queue()
    outq = Queue()

    model = SepModel(bgq, outq)
    _new_event(model, bgq)

    _send_command(
        model, bgq, ApproveRequestMessage(Role.CSR, model._requests[-1].name, True)
    )
    assert model._requests[-1].status == Status.Approved
    assert model._requests[-1]._approved_csr is True

    _send_command(
        model, bgq, ApproveRequestMessage(Role.Fin, model._requests[-1].name, True)
    )
    assert model._requests[-1]._approved_fin is True

    _send_command(
        model, bgq, ApproveRequestMessage(Role.Admin, model._requests[-1].name, True)
    )
    assert model._requests[-1]._approved_admin is True


def test_find_event():
    bgq = Queue()
    outq = Queue()

    model = SepModel(bgq, outq)
    _new_event(model, bgq)

    assert model.find_event(model._requests[-1].name) is not None


def test_add_task():

    # TODO: fix the test
    return

    bgq = Queue()
    outq = Queue()

    model = SepModel(bgq, outq)
    _new_event(model, bgq)

    task = Task("taskName", 100, "taskDescription", "assigneeName")
    model.add_task(task)

    assert task in model._tasks


def test_update_task():
    pass


def test_view_event():
    pass


def test_find_waiting_request():
    pass

def test_crew_request_list():
    bgq = Queue()
    outq = Queue()

    model = SepModel(bgq, outq)

    # the model should expose a crew request container named `_crewRequest`
    assert hasattr(model, "_crewRequests")
    assert isinstance(model._crewRequests, list)

def test_crew_request_add():

    # Initialize model
    bgq = Queue()
    outq = Queue()

    model = SepModel(bgq, outq)

    # Initialize CrewRequest
    cr = CrewRequest('name', Department.Finance, 'description', 10, True)
    
    # Send message and run model loop to process it
    _send_command(model, bgq, CrewRequestMessage(cr))

    # ensure container exists and the crew request was added
    assert cr.name == model._crewRequests[0].name



