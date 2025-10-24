from login.login_manager import LoginManager

def test_login_manager_init():
    lm = LoginManager("users.txt")
    assert lm != None

def test_login_manager_no_file():
    lm = LoginManager()
    assert lm !=None

def test_login_empty():
    lm = LoginManager()
    success = lm.login()
    assert not success

def test_login_correct():
    lm = LoginManager()
    success = lm.login("vivienne", "password")
    assert success

def test_login_wrong_username():
    lm = LoginManager()
    success = lm.login("vivie", "password")
    assert not success

def test_login_no_username():
    lm = LoginManager()
    success = lm.login("", "password")
    assert not success

def test_login_no_password():
    lm = LoginManager()
    success = lm.login("vivienne", "")
    assert not success

def test_login_wrong_password():
    lm = LoginManager()
    success = lm.login("vivienne", "pass")
    assert not success