import cmd2
from cmd2 import Cmd
import getpass
import datetime
from message.message import (
    LoginMessage, LoginResultMessage, NewEventMessage, ViewEventMessage,
    DecideEventMessage, StopMessage
)
from threading import Thread
from event.Request import EventRequest  # ✅ import Request object

class SepCli(Cmd):
    intro = "Welcome to the SEP Management Application. Type 'login' to begin or '?' for options.\n"
    prompt = "(not logged in) > "
    current_event = None

    def __init__(self, outMsgQueue, inMsgQueue):
        super().__init__()
        self._outMsgQueue = outMsgQueue
        self._inMsgQueue = inMsgQueue
        self.logged_in_user = None
        self.role = None
        self.requests = []  # ✅ local Request list

    # LOGIN
    def do_login(self, arg):
        """Login with a username and password."""
        if self.logged_in_user:
            self.poutput(f"Already logged in as {self.logged_in_user}")
            return

        username = self.prompt_for_username()
        password = self.prompt_for_password()

        self._outMsgQueue.put(LoginMessage(username, password))

    def do_logout(self, arg):
        """Logout the current user."""
        if not self.logged_in_user:
            self.poutput("Not currently logged in.")
            return
        self.poutput(f"Goodbye, {self.logged_in_user}")
        self.logged_in_user = None
        self.role = None
        self.prompt = "(not logged in) > "
        self.update_available_commands()  # ✅ reset command availability

    def prompt_for_username(self):
        return self.read_input("Username: ")

    def prompt_for_password(self):
        return getpass.getpass("Password: ")

    def require_login(self):
        if not self.logged_in_user:
            self.poutput("❗ You must be logged in to perform this command. Use 'login'.")
            return False
        return True

    # ✅ NEW: Create a Request object when creating an Event
    def do_newEvent(self, arg):
        """Create a new Event and corresponding Request."""
        if not self.require_login():
            return

        e_name = self.read_input("Event Name: ")
        e_desc = self.read_input("Event Description: ")
        e_budget = float(self.read_input("Budget: "))

        # make a Request object
        e_date = None
        while True:
            try:
                date_str = self.read_input("Event Date (YYYY-MM-DD): ")
                e_date = datetime.datetime.strptime(date_str, "%Y-%m-%d")
                break
            except Exception as e:
                self.perror(f"Incorrect date format")

        req = EventRequest(type=e_name, budget=e_budget, dates=[e_date])
        self.requests.append(req) # not sure if we need this but maybe
        self.poutput(f"✅ Request created: {req.id}")
        self._outMsgQueue.put(NewEventMessage(req))
        self.current_event = req

    # ✅ NEW: View a Request by ID or name
    def do_viewRequest(self, arg):
        """View details of a Request by ID or type."""
        if not self.require_login():
            return

        query = self.read_input("Enter Request name").strip()
        match = None
        for r in self.requests:
            if r.id == query or r.type == query:
                match = r
                break
        if match:
            self.poutput(f"\n{match}\n")
        else:
            self.perror("No matching request found.")

    # ✅ NEW: List all requests - Todo: Update to work with backend
    def do_listRequests(self, arg):
        """List all created Requests."""
        if not self.require_login():
            return
        if not self.requests:
            self.poutput("No requests created yet.")
            return
        for req in self.requests:
            self.poutput(f"- {req.type} ({req.id}) [{req.status}]")

    # ✅ NEW: Stub - list requests to approve
    def do_listPendingApprovals(self, arg):
        """List requests pending your approval (stub)."""
        if not self.require_login():
            return
        self.poutput("🧩 This feature is not yet implemented (stub).")

    # ROLE-BASED COMMAND CONTROL
    def update_available_commands(self):
        """Enable/disable commands based on role."""
        if not self.role:
            self.hidden_commands = ['newEvent', 'viewRequest', 'listRequests', 'listPendingApprovals']
            return

        if self.role == "Admin":
            self.hidden_commands = []  # admin sees everything
        elif self.role == "Manager":
            self.hidden_commands = ['approveEvent']  # example restriction
        else:
            self.hidden_commands = ['listPendingApprovals']

    # EVENT HANDLING (existing)
    def event_thread(self):
        while True:
            msg = self._inMsgQueue.get()
            print(f"New message {msg}")
            if isinstance(msg, LoginResultMessage):
                result = msg
                if result.success:
                    self.logged_in_user = result.user
                    self.role = result.role
                    self.prompt = f"({self.logged_in_user} : {self.role}) > "
                    self.update_available_commands()  # ✅ apply role
                    self.poutput(f"✅ Login successful. Welcome, {result.user}!")
                else:
                    self.poutput("❌ Invalid username or password.")
            elif isinstance(msg, StopMessage):
                break
            elif isinstance(msg, NewEventMessage):
                self.current_event = msg
                self.show_event()

    def run_ui(self):
        eventT = Thread(target=self.event_thread)
        eventT.start()
        self.cmdloop()
        self._inMsgQueue.put(StopMessage())
        eventT.join()

    def do_exit(self, arg):
        """Exit the program."""
        self.poutput("Exiting…")
        return True
