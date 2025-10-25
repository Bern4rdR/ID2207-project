import event.Request as Request
from Request import EventRequest  # inherits from Request abstract class # lmao there is no request abstract class
import event.Status as Status
import datetime
from event.models import Event, Task

SAMPLE_EVENT_REQUEST = EventRequest(
    type="Conference",
    budget=100,
    dates=[datetime.datetime.now() + datetime.timedelta(days=1)],
    preferences=["Quiet", "Enough room for 10 people"],
)
SAMPLE_EVENTS = [SAMPLE_EVENT_REQUEST]


def test_initiate_event_request():
    # TODO: Invalid credentials
    # TODO: Valid credentials

    request = EventRequest(
        type="Conference",
        budget=100,
        dates=[datetime.datetime.now() + datetime.timedelta(days=1)],
        preferences=["Quiet", "Enough room for 10 people"],
    )

    # Required fields
    assert request.id is not None
    assert request.status == Status.Ongoing
    assert request.type == "Conference"
    assert request.budget == 100
    assert request.feedback == []
    assert request.dates != []
    assert request.preferences == ["Quiet", "Enough room for 10 people"]
    # TODO: link to event details

    # Fields validation
    assert not any([d < datetime.datetime.now() for d in request.dates])
    assert request.budget >= 0


def test_view_event_request():
    # Request not found
    assert Request.get(1234567890, SAMPLE_EVENTS) is None

    # Request found
    assert (
        Request.get(SAMPLE_EVENT_REQUEST.id, SAMPLE_EVENTS).id
        == SAMPLE_EVENT_REQUEST.id
    )
    # View event details
    assert len(str(SAMPLE_EVENT_REQUEST)) > 0

    # TODO: Access control


def test_customer_service_desicion():
    # TODO: Invalid credentials
    # TODO: Valid credentials

    # Approval
    SAMPLE_EVENT_REQUEST.approve()
    assert SAMPLE_EVENT_REQUEST.status == Status.Approved
    # Rejection
    SAMPLE_EVENT_REQUEST.reject(reason="Not enough venue capacity")
    assert SAMPLE_EVENT_REQUEST.status == Status.Rejected


def test_financial_manager_feedback():
    # TODO: Invalid credentials
    # TODO: Valid credentials

    # Feedback
    SAMPLE_EVENT_REQUEST.addFeedback("Not financially viable")
    SAMPLE_EVENT_REQUEST.addFeedback("Budget not enough for venue")
    print(SAMPLE_EVENT_REQUEST.feedback)
    assert not any(
        [
            f not in SAMPLE_EVENT_REQUEST.feedback
            for f in ["Not financially viable", "Budget not enough for venue"]
        ]
    )

    # Approval
    SAMPLE_EVENT_REQUEST.approve()
    assert SAMPLE_EVENT_REQUEST.status == Status.Approved
    # Rejection
    SAMPLE_EVENT_REQUEST.reject(reason="Not enough venue capacity")
    assert SAMPLE_EVENT_REQUEST.status == Status.Rejected


def test_admin_manager_desicion():
    # TODO: Invalid credentials
    # TODO: Valid credentials

    # Final Approval
    SAMPLE_EVENT_REQUEST.approve()
    assert SAMPLE_EVENT_REQUEST.status == Status.Approved
    # Final Rejection
    SAMPLE_EVENT_REQUEST.close()
    assert SAMPLE_EVENT_REQUEST.status == Status.Closed


# adding tests for an event class
def test_init_event():
    se = Event(name="testevent")
    assert se != None
    assert se.name == "testevent"

def test_update_event():
    se = Event(name="testevent")
    se.budget = 1000
    se.description = "this is a test"
    assert se.budget == 1000
    assert se.description == "this is a test"

def test_init_task():
    te = Task(name="testtask")
    assert te != None
    assert te.name == "testtask"

def test_update_task():
    te = Task(name="testtask")
    te.budget = 10
    te.description = "test desc"
    te.assignee = "bob"
    assert te.budget == 10
    assert te.description == "test desc"
    assert te.assignee == "bob"

def test_add_task_to_event():
    se = Event(name="testevent")
    te = Task(name="testtask")
    se.add_task(te)
    assert te in se.tasks()