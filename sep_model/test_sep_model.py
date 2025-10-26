from multiprocessing import Queue
import datetime
from message.message import NewEventMessage, StopMessage
from sep_model.sep_model import SepModel
from event.Request import EventRequest
from threading import Thread


def test_new_event():
    """
    Create a SepModel, run its loop in a background thread, send a NewEventMessage
    and a StopMessage, then assert the EventRequest was added to model._requests.
    """
    bgq = Queue()
    outq = Queue()

    model = SepModel(bgq, outq)
    t = Thread(target=model.loop, daemon=True)
    t.start()

    evt_date = datetime.datetime.now() + datetime.timedelta(days=1)
    req = EventRequest("New Event", "Conference", 100, [evt_date])

    bgq.put(NewEventMessage(req))

    # send stop so the loop exits and the background thread can finish
    bgq.put(StopMessage())

    # Wait for loop thread to finish; fail the test if it doesn't
    t.join(timeout=5)
    if t.is_alive():
        raise RuntimeError("SepModel.loop did not exit in time")

    # The request should now be present in the model
    assert any(r.name == "New Event" for r in model._requests), (
        "EventRequest not found in model._requests"
    )
