import cmd2
from cmd2 import Cmd
import getpass
from message.message import LoginMessage, NewEventMessage, ViewEventMessage, DecideEventMessage


class SepCli(Cmd):
    intro = "Welcome to the SEP Management Application. Type 'login' to begin or '?' for options.\n"
    prompt = "(not logged in) > "

    def __init__(self, outMsgQueue, inMsgQueue):
        super().__init__()
        self._outMsgQueue = outMsgQueue
        self._inMsgQueue = inMsgQueue
        self.logged_in_user = None

    #
    # LOGIN command
    #
    def do_login(self, arg):
        """Login with a username and password."""
        if self.logged_in_user:
            self.poutput(f"Already logged in as {self.logged_in_user}")
            return

        username = self.prompt_for_username()
        password = self.prompt_for_password()

        self._outMsgQueue.put(LoginMessage(username, password))
        # we could make this async eventually, but I got lazy
        result = self._inMsgQueue.get()
        if result.success:
            self.logged_in_user = username
            self.role = result.role
            self.prompt = f"({self.logged_in_user} : {self.role}) > "
            self.poutput(f"✅ Login successful. Welcome, {username}!")
        else:
            self.poutput("❌ Invalid username or password.")

    #
    # PROTECTED COMMAND EXAMPLE
    #
    def do_secret(self, arg):
        """Example of a protected command that requires login."""
        if not self.require_login():
            return
        self.poutput("🤫 This is top secret information only for logged-in users!")

    #
    # LOGOUT
    #
    def do_logout(self, arg):
        """Logout the current user."""
        if not self.logged_in_user:
            self.poutput("Not currently logged in.")
            return
        self.poutput(f"Goodbye, {self.logged_in_user}")
        self.logged_in_user = None
        self.prompt = "(not logged in) > "

    #
    # HELPER METHODS
    #
    def prompt_for_username(self):
        return self.read_input("Username: ")

    def prompt_for_password(self):
        # getpass masks input
        return getpass.getpass("Password: ")

    def authenticate(self, username, password):
        return USERS.get(username) == password

    def require_login(self):
        if not self.logged_in_user:
            self.poutput("❗ You must be logged in to perform this command. Use 'login'.")
            return False
        return True

    # Event Functions
    def do_newEvent(self, arg):
        e_name = self.read_input("Event Name: ")
        e_desc = self.read_input("Event Description: ")
        e_budget = self.read_input("Budget: ")
        self._outMsgQueue.put(NewEventMessage(e_name, e_desc, e_budget))

    def do_viewEvent(self, arg):
        e_name = self.read_input("Event Name: ")
        self._outMsgQueue.put(ViewEventMessage(e_name, "", ""))

    def eventFeedback(self, approve, name):
        self._outMsgQueue.put(DecideEventMessage(name, "", "", self.role, approve))

    def do_approveEvent(self, arg):
        e_name = self.read_input("Event Name you wish to approve: ")
        self.eventFeedback(True, e_name)

    def do_rejectEvent(self, arg):
        e_name = self.read_input("Event Name you wish to reject: ")
        self.eventFeedback(False, e_name)


    #
    # EXIT
    #
    def do_exit(self, arg):
        """Exit the program."""
        self.poutput("Exiting…")
        return True


if __name__ == "__main__":
    cli = SepCli()
    cli.cmdloop()
