from multiprocessing import Queue
import time
import datetime
from message.message import (
    NewEventMessage,
    ViewAllRequestMessage,
    ViewEventMessage,
    ApproveRequestMessage,
    CrewRequestMessage,
    CrewRequestUpdateMessage,
    StopMessage,
)
from sep_model.sep_model import SepModel
from event.Request import EventRequest
from event.models import Task, Event
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


# def test_approve_request():

#     bgq = Queue()
#     outq = Queue()

#     model = SepModel(bgq, outq)
#     _new_event(model, bgq)

#     _send_command(
#         model, bgq, ApproveRequestMessage(model._requests[-1].name, Role.CSR, True)
#     )
#     assert model._requests[-1].status == Status.Approved
#     assert model._requests[-1]._approved_csr is True
    
#     _send_command(
#         model, bgq, ApproveRequestMessage(Role.Fin, model._requests[-1].name, True)
#     )
#     assert model._requests[-1]._approved_fin is True

#     _send_command(
#         model, bgq, ApproveRequestMessage(Role.Admin, model._requests[-1].name, True)
#     )
#     assert model._requests[-1]._approved_admin is True


def test_find_event():
    bgq = Queue()
    outq = Queue()

    model = SepModel(bgq, outq)
    _new_event(model, bgq)

    assert model.find_event(model._requests[-1].name) is not None


def test_add_task():

    bgq = Queue()
    outq = Queue()

    model = SepModel(bgq, outq)

    # create an Event so add_task has somewhere to attach the Task
    ev = Event("evtName", 100, "Conference")
    model._events.append(ev)

    # create Task and assign it to the event by id
    task = Task("taskName", 100, "taskDescription", "assigneeName")
    task._event_id = ev._id

    model.add_task(task)

    # verify the task was added to the event's tasks
    assert any(t.name == task.name for t in ev.tasks)


def test_update_task():
    bgq = Queue()
    outq = Queue()

    model = SepModel(bgq, outq)

    # create an Event so add_task has somewhere to attach the Task
    ev = Event("evtName", 100, "Conference")
    model._events.append(ev)

    # create Task and assign it to the event by id
    task = Task("taskName", 100, "taskDescription", "assigneeName")
    task._event_id = ev._id

    model.add_task(task)

    # verify the task was added to the event's tasks
    assert any(t.name == task.name for t in ev.tasks)

    # Update task
    task.budget = 900
    model.update_task(task)

    for t in model._tasks:
        if t._event_id == ev._id:
            assert t.budget == 900


def test_view_event():
    bgq = Queue()
    outq = Queue()

    model = SepModel(bgq, outq)

    # create an Event and add it to the model so the view can find it
    ev = Event("evtName", 100, "Conference")
    model._events.append(ev)

    # request view of the event via the model loop
    _send_command(model, bgq, ViewEventMessage(ev.name))

    # the model should put a response on outq
    resp = outq.get(timeout=1)
    assert resp is not None

    # support a few response shapes: direct Event, message with .event, or object with .name
    if isinstance(resp, Event):
        assert resp.name == ev.name
    elif hasattr(resp, "event") and hasattr(resp.event, "name"):
        assert resp.event.name == ev.name
    elif hasattr(resp, "name"):
        assert resp.name == ev.name
    else:
        pytest.fail("Unexpected response type from view event")

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


def test_crew_request_update():

    # Initialize model
    bgq = Queue()
    outq = Queue()

    model = SepModel(bgq, outq)

    t = Thread(target=model.loop, daemon=True)
    t.start()

    # Initialize CrewRequest
    cr = CrewRequest('name', Department.Finance, 'description', 10, True)
    
    # Send message and run model loop to process it
    bgq.put(CrewRequestMessage(cr))

    # ensure container exists and the crew request was added
    assert cr.name == model._crewRequests[0].name

    # Update
    cr.salary = 100
    bgq.put(CrewRequestUpdateMessage(cr))

    # Validate change
    time.sleep(0.1)                                     # Wait to update the model. Shouldn't be done this way
    assert model._crewRequests[0].salary == 100

    # Terminate model
    bgq.put(StopMessage())
    t.join()


def test_crew_request_comment():

    # Initialize model
    bgq = Queue()
    outq = Queue()

    model = SepModel(bgq, outq)

    t = Thread(target=model.loop, daemon=True)
    t.start()

    # Initialize CrewRequest
    cr = CrewRequest('name', Department.Finance, 'description', 10, True)
    
    # Send message and run model loop to process it
    bgq.put(CrewRequestMessage(cr))

    # ensure container exists and the crew request was added
    assert cr.name == model._crewRequests[0].name

    # Comment
    cr.add_comment("asdf")
    bgq.put(CrewRequestUpdateMessage(cr))

    # Validate change
    time.sleep(0.1)                                     # Wait to update the model. Shouldn't be done this way
    assert model._crewRequests[0].get_comments()[0] == "asdf"

    # Terminate model
    bgq.put(StopMessage())
    t.join()