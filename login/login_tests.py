from login.login_manager import LoginManager
from message.message import Message

def test_login_manager_init():
    lm = LoginManager("users.txt")
    assert lm != None

def test_login_manager_no_file():
    lm = LoginManager()
    assert lm !=None

def test_login_empty():
    lm = LoginManager()
    success, _a = lm.login()
    assert not success

def test_login_correct():
    lm = LoginManager()
    success, _a = lm.login("vivienne", "password")
    assert success

def test_login_wrong_username():
    lm = LoginManager()
    success, _a = lm.login("vivie", "password")
    assert not success

def test_login_no_username():
    lm = LoginManager()
    success, _a = lm.login("", "password")
    assert not success

def test_login_no_password():
    lm = LoginManager()
    success, _a = lm.login("vivienne", "")
    assert not success

def test_login_wrong_password():
    lm = LoginManager()
    success, _a = lm.login("vivienne", "pass")
    assert not success

def test_role_required_success():
    lm = LoginManager()
    msg = Message()
    msg.setRole("admin")
    assert lm.role_required("admin", msg)

def test_role_required_fail():
    lm = LoginManager()
    msg = Message()
    msg.setRole("user")
    assert not lm.role_required("admin", msg)