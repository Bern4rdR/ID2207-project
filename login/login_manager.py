from message.message import Message
# adding role counts as a refactor
class LoginManager:
    _users = {}
    def __init__(self, filename='users.txt'):
        self._filename = filename
        with open(filename, 'r') as f:
            for line in f.readlines():
                user = line.split(",")[0].strip()
                password = line.split(",")[1].strip()
                role = line.split(",")[2].strip()
                self._users[user] = {'pw': password, 'role': role}

    def login(self, username='', password=''):
        if username == '' or password == '':
            return False, 'none'
        if username in self._users.keys():
            if self._users[username]['pw'] == password:
                return True, self._users[username]['role']
        return False, 'none'

    def role_required(self, role, msg: Message):
        return msg.role == role