
class LoginManager:
    _users = {}
    def __init__(self, filename='users.txt'):
        self._filename = filename
        with open(filename, 'r') as f:
            for line in f.readlines():
                user = line.split(",")[0].strip()
                password = line.split(",")[1].strip()
                self._users[user] = password

    def login(self, username='', password=''):
        if username == '' or password == '':
            return False
        if username in self._users.keys():
            if self._users[username] == password:
                return True
        return False
