
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
    def __init__(self, success, role):
        self.success = success
        self.role = role