from multiprocessing import Queue
import datetime
from message.message import NewEventMessage, ViewAllRequestMessage, StopMessage
from sep_model.sep_model import SepModel
from event.Request import EventRequest
from threading import Thread


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
    _new_event(model, bgq)

    assert len(model._requests) == 1


def test_view_all_requests():
    bgq = Queue()
    outq = Queue()

    model = SepModel(bgq, outq)
    _new_event(model, bgq)

    _send_command(model, bgq, ViewAllRequestMessage())
    assert outq.get() is not None


def test_approve_request():
    pass

def test_find_event():
    pass

def test_send_waiting_requests():
    pass

def test_add_task():
    pass

def test_update_task():
    pass

def test_view_event():
    pass

def test_find_waiting_request():
    pass

test_view_all_requests()