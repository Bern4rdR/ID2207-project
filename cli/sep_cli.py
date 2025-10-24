import cmd2
from cmd2 import Cmd
import getpass
from message.message import LoginMessage, LoginResultMessage, NewEventMessage, ViewEventMessage, DecideEventMessage, StopMessage
from threading import Thread

class SepCli(Cmd):
    intro = "Welcome to the SEP Management Application. Type 'login' to begin or '?' for options.\n"
    prompt = "(not logged in) > "
    current_event = None

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
        self.role = None
        self.prompt = "(not logged in) > "

    #
    # HELPER METHODS
    #
    def prompt_for_username(self):
        return self.read_input("Username: ")

    def prompt_for_password(self):
        # getpass masks input
        return getpass.getpass("Password: ")

    def require_login(self):
        if not self.logged_in_user:
            self.poutput("❗ You must be logged in to perform this command. Use 'login'.")
            return False
        return True

    # Event Functions
    def do_newEvent(self, arg):
        if not self.require_login():
            return
        e_name = self.read_input("Event Name: ")
        e_desc = self.read_input("Event Description: ")
        e_budget = self.read_input("Budget: ")
        self._outMsgQueue.put(NewEventMessage(e_name, e_desc, e_budget))
        self.current_event = NewEventMessage(e_name, e_desc, e_budget)

    def do_viewEvent(self, arg):
        if not self.require_login():
            return
        e_name = self.read_input("Event Name: ")
        self._outMsgQueue.put(ViewEventMessage(e_name, "", ""))

    def eventFeedback(self, approve, name):
        self._outMsgQueue.put(DecideEventMessage(name, "", "", self.role, approve))

    def do_approveEvent(self, arg):
        if not self.require_login():
            return
        e_name = self.read_input("Event Name you wish to approve: ")
        self.eventFeedback(True, e_name)

    def do_rejectEvent(self, arg):
        if not self.require_login():
            return
        e_name = self.read_input("Event Name you wish to reject: ")
        self.eventFeedback(False, e_name)
    
    def do_show(self, args):
        self.show_event()

    def show_event(self):
        """
        Display the currently created event in a formatted structure.
        """
        if not self.current_event:
            self.perror("No event created yet. Use 'create_event' first.")
            return

        event = self.current_event
        self.poutput("\n===== EVENT DETAILS =====")
        self.poutput(f"Name:        {event.name}")
        self.poutput(f"Budget:      {event.budget}")
        self.poutput(f"Description:\n{event.description if event.description else '(no description)'}")
        # don't have these in the event yet - should we add?
        # approved_by_display = ", ".join(event.ApprovedBy) if event.ApprovedBy else "(nobody yet)"
        # self.poutput(f"Approved By: {approved_by_display}")
        self.poutput("=========================\n")

    #
    # EXIT
    #
    def do_exit(self, arg):
        """Exit the program."""
        self.poutput("Exiting…")
        return True

    def event_thread(self):
        while True:
            msg = self._inMsgQueue.get()
            print(f"New message {msg}")
            if type(msg) == LoginResultMessage:
                result = msg
                if result.success:
                    self.logged_in_user = result.user
                    self.role = result.role
                    self.prompt = f"({self.logged_in_user} : {self.role}) > "
                    self.poutput(f"✅ Login successful. Welcome, {result.user}!")
                else:
                    self.poutput("❌ Invalid username or password.")
            elif type(msg) == StopMessage:
                break
            elif type(msg) == NewEventMessage:
                self.current_event = msg
                self.show_event()

    def run_ui(self):
        eventT = Thread(target = self.event_thread)
        eventT.start()
        self.cmdloop()
        # clean exit
        self._inMsgQueue.put(StopMessage()) # stop thread, got lazy
        eventT.join()

if __name__ == "__main__":
    cli = SepCli()
    eventT = Thread(target = cli.event_thread)
    cli.cmdloop()
    # clean exit
    cli._inMsgQueue.put(StopMessage()) # stop thread, got lazy
    eventT.join()