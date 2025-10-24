
class Message:
    name = ""

class StopMessage(Message):
    name="stop"

class LoginMessage(Message):
    _username = ""
    password = ""

    def __init__(self, username, password):
        self._username = username
        self._password = password