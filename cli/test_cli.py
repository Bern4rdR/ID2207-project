import sys
import datetime
from io import StringIO
from multiprocessing import Queue
from threading import Thread

from cli.sep_cli import SepCli
from message.message import LoginResultMessage, StopMessage


def _tmp_event_thread(cli):
    t = Thread(target=cli.event_thread, daemon=True)
    t.start()
    t.join()


def _login(role="Manager"):
    cli = SepCli(Queue(), Queue())
    cli.logged_in_user = "user"
    cli.role = role
    return cli


def _add_event(
    monkeypatch,
    cli,
    name="evtName",
    description="evtDescription",
    budget=100,
    date=(datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%Y-%m-%d"),
):
    _fake_input(monkeypatch, name, description, str(budget), date)
    cli.do_newEvent("")


def _fake_input(monkeypatch, *inputs):
    monkeypatch.setattr(sys, "stdin", StringIO("\n".join(inputs) + "\n"))


def test_login():
    # invalid user
    outq = Queue()
    inq = Queue()
    cli = SepCli(outq, inq)

    inq.put(LoginResultMessage(False, "", ""))
    inq.put(StopMessage())

    _tmp_event_thread(cli)

    assert cli.logged_in_user is None
    assert cli.role is None
    assert "(not logged in)" in cli.prompt

    # valid user
    outq = Queue()
    inq = Queue()
    cli = SepCli(outq, inq)

    inq.put(LoginResultMessage(True, "Manager", "validUser"))
    inq.put(StopMessage())

    _tmp_event_thread(cli)

    assert cli.logged_in_user == "validUser"
    assert cli.role == "Manager"
    assert "validUser" in cli.prompt and "Manager" in cli.prompt


def test_logout():
    outq = Queue()
    inq = Queue()
    cli = SepCli(outq, inq)

    inq.put(LoginResultMessage(False, "Manager", "user"))
    inq.put(StopMessage())

    _tmp_event_thread(cli)

    cli.do_logout("")
    assert cli.logged_in_user is None
    assert cli.role is None
    assert "(not logged in)" in cli.prompt


def test_new_event_request(monkeypatch):
    cli = SepCli(Queue(), Queue())

    # invalid user
    cli.do_newEvent("")
    assert len(cli.requests) == 0

    # valid user
    cli.logged_in_user = "user"
    cli.role = "Manager"

    _add_event(monkeypatch, cli)
    assert len(cli.requests) == 1


def test_unique_event_name(monkeypatch):
    cli = _login()

    _add_event(monkeypatch, cli)
    assert len(cli.requests) == 1

    # duplicate event name
    _add_event(monkeypatch, cli)
    assert len(cli.requests) == 1


def test_view_requests(monkeypatch, capsys):
    cli = _login()

    _add_event(monkeypatch, cli)
    capsys.readouterr()  # discard current output stream

    _fake_input(monkeypatch, "evtName")
    cli.do_viewRequest("")
    out = capsys.readouterr().out
    assert out.lstrip().startswith("===== EVENT DETAILS =====")


def test_list_pending_approvals(monkeypatch, capsys):
    cli = _login()

    _add_event(monkeypatch, cli)
    capsys.readouterr()

    cli.do_listPendingApprovals("")
    out = capsys.readouterr().out
    assert out.lstrip() == "Pending Requests:\nevtName"


def test_approve_removes_event_from_pending(monkeypatch, capsys):
    pass


def test_list_event_requests(monkeypatch, capsys):
    cli = _login()

    _add_event(monkeypatch, cli)
    # TODO: approve request
    capsys.readouterr()  # discard current output stream

    cli.do_listRequests("")
    captured = capsys.readouterr()
    assert captured.out.lstrip().startswith("Events:")

    pass


def test_select_event():
    pass


def test_add_task():
    pass


def test_approve_task():
    pass


def test_comment_task():
    pass


def test_show_task():
    pass


def test_update_task_budget():
    pass
