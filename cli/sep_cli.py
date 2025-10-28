import cmd2
from cmd2 import Cmd
import getpass
import datetime

# this did get a bit ridiculous... oops
from message.message import (
    LoginMessage,
    LoginResultMessage,
    NewEventMessage,
    ViewEventMessage,
    DecideEventMessage,
    StopMessage,
    ViewAllRequestMessage,
    RequestListMessage,
    RequestApprovedMessage,
    RequestRejectedMessage,
    ApproveRequestMessage,
    FindWaitingRequestMessage,
    RequestListMessage,
    EventListMessage,
    TaskListMessage,
    UpdateTaskMessage,
    PendingListMessage,
    NewTaskMessage,
    CrewRequestMessage,
)
from threading import Thread
from event.Request import EventRequest  # ✅ import Request object
from event.models import Event, Task
from hr.crew_request import CrewRequest, Department, Role


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

        self.disabled_cmds = [
            "alias",
            "edit",
            "run_script",
            "macro",
            "shell",
            "run_pyscript",
            "py",
            "shortcuts",
            "history",
            "load",
            "save",
            "set",
            "settable",
            "eof",
            "exit",
        ]
        self.hidden_commands.extend(self.disabled_cmds)

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
            self.poutput(
                "❗ You must be logged in to perform this command. Use 'login'."
            )
            return False
        return True

    # ✅ NEW: Create a Request object when creating an Event
    def do_newEvent(self, arg):
        """Create a new Event and corresponding Request."""
        if not self.require_login():
            return

        e_name = self.read_input("Event Name: ")
        e_desc = self.read_input("Event Description: ")
        while True:
            try:
                e_budget = float(self.read_input("Budget: "))
                break
            except:
                self.perror("Budget must be a number > 0")

        # make a Request object
        e_date = None
        while True:
            try:
                date_str = self.read_input("Event Date (YYYY-MM-DD): ")
                e_date = datetime.datetime.strptime(date_str, "%Y-%m-%d")
                break
            except Exception as e:
                self.perror(f"Incorrect date format")

        req = EventRequest(name=e_name, type=e_desc, budget=e_budget, dates=[e_date])
        self.requests.append(req)  # not sure if we need this but maybe
        self.poutput(f"✅ Request created: {req.id}")
        self._outMsgQueue.put(NewEventMessage(req))
        self.current_event = req

    # ✅ NEW: View a Request by ID or name
    def do_viewRequest(self, arg):
        """View details of a Request by ID or type."""
        if not self.require_login():
            return

        query = self.read_input("Enter Request name > ").strip()
        match = None
        for r in self.requests:
            if r.name == query or r.type == query:
                match = r
                break
        if match:
            self.show_event_request(match)
        else:
            self.perror("No matching request found.")

    # ✅ NEW: List all requests - Todo: Update to work with backend
    def do_listRequests(self, arg):
        """List all created Requests."""
        names = [x.name for x in self._requests]
        self.show_list(names, "Request Names:")

    # ✅ NEW: Stub - list requests to approve
    def do_listPendingApprovals(self, arg):
        """List requests pending your approval (stub)."""
        if not self.require_login():
            return
        self._outMsgQueue.put(FindWaitingRequestMessage(self.role))

    def do_approve(self, arg):
        e_name = arg
        if not e_name or e_name == "":
            self.poutput("Require event name to approve")
            return
        self.poutput(f"Event name: {e_name}")
        self._outMsgQueue.put(ApproveRequestMessage(e_name, self.role, True))

    #
    # EVENT SELECTION AND TASK MANAGEMENT - new from my programming partner chatty
    #
    def do_selectEvent(self, arg):
        """Select an event by name to make it the active event."""
        if not self.require_login():
            return
        event_name = arg.strip()
        if not event_name:
            event_name = self.read_input("Event name: ")
        found = False
        for ev in self._events:
            if ev.name == event_name:
                self.current_event = ev
                found = True
                break
        if not found:
            self.perror(f"Could not find event {event_name}")
            return
        self.poutput(f"🎯 Active event set to '{event_name}'")
        self.prompt = self.prompt[:-3] + f" :: {event_name} > "

    def do_addTask(self, arg):
        """Add a task to the currently active event."""
        if not self.require_login():
            return
        if not self.current_event:
            self.perror("❗ No active event selected. Use 'selectEvent' first.")
            return

        t_name = self.read_input("Task Name: ")
        t_budget = self.read_input("Task Budget: ")
        t_assignee = self.read_input("Assignee: ")
        t_desc = self.read_input("Task Description: ")

        try:
            t_budget = float(t_budget)
        except ValueError:
            self.perror("Budget must be a number.")
            return

        nt = Task(t_name, t_budget, t_desc, t_assignee)
        self.current_event.add_task(nt)
        self._outMsgQueue.put(NewTaskMessage(nt))  # ToDo add message here
        self.poutput(f"✅ Added task '{t_name}' to event '{self.current_event}'.")

    # lots of repeated code in these three
    def do_commentTask(self, arg):
        """Add a comment to a task. Usage: commentTask <task_name>"""
        if not self.require_login():
            return
        if not self.current_event:
            self.perror("❗ No active event selected.")
            return

        t_name = arg.strip()
        if not t_name:
            t_name = self.read_input("Task Name: ")
        task: Task = None
        for ts in self.current_event.tasks:
            if ts.name == t_name:
                task = ts
                break
        if task == None:
            self.perror(f"Task {t_name} not found")
            return
        comment = self.read_input("Comment: ")
        task.add_budget_comment(comment)
        self._outMsgQueue.put(
            UpdateTaskMessage(task)
        )  # Todo: task comment message with this task

    def do_updateTaskBudget(self, arg):
        """Update a task's budget. Usage: updateTaskBudget <task_name> <new_value>"""
        if not self.require_login():
            return
        if not self.current_event:
            self.perror("❗ No active event selected.")
            return

        t_name = arg
        new_val = self.read_input("New Budget").strip()
        try:
            new_val = float(new_val)
        except ValueError:
            self.perror("New budget must be a number.")
            return
        task: Task = None
        for ts in self.current_event.tasks:
            if ts.name == t_name:
                task = ts
                break
        if task == None:
            self.perror(f"Task {t_name} not found")
            return
        task.budget = new_val
        self._outMsgQueue.put(UpdateTaskMessage(task))  # ToDo : add message here

    def do_approveTask(self, arg):
        """Approve a task. Usage: approveTask <task_name>"""
        if not self.require_login():
            return
        if not self.current_event:
            self.perror("❗ No active event selected.")
            return

        t_name = arg.strip()
        if not t_name:
            t_name = self.read_input("Task Name: ")
        task: Task = None
        for ts in self.current_event.tasks:
            if ts.name == t_name:
                task = ts
                break
        if task == None:
            self.perror(f"Task {t_name} not found")
            return
        task.approve()
        self._outMsgQueue.put(UpdateTaskMessage(task))  # add message here

    """ These are for display purposes and are used by the event loop mostly"""

    # ROLE-BASED COMMAND CONTROL
    def update_available_commands(self):
        """Enable/disable commands based on role."""
        if not self.role:
            self.hidden_commands = [
                "newEvent",
                "viewRequest",
                "listRequests",
                "listPendingApprovals",
                "addTask",
                "approveTask",
                "commentTask",
                "approve",
                "updateTaskBudget",
                "selectEvent",
                "showTask",
                "viewRequest",
            ]
            return

        # Role-based command visibility using Role enum
        if self.role == Role.Admin:
            self.hidden_commands = []  # Admin sees everything
        elif self.role == Role.CSR:
            self.hidden_commands = [
                "selectEvent",
                "addTask",
                "approve",
                "listPendingApprovals",
                "approveTask",
                "commentTask",
                "showTask",
                "viewRequest",
                "updateTaskBudget",
            ]  # CSR has access to few commands
        elif self.role == Role.Fin:
            self.hidden_commands = [
                "newEvent",
                "addTask",
            ]  # Financial Manager has access to most commands except adding new events/tasks
        elif self.role == Role.HR:
            self.hidden_commands = [
                "listPendingApprovals",
                "approve",
                "approveTask",
                "commentTask",
                "addTask",
                "newEvent",
                "selectEvent",
                "showTask",
                "updateTaskBudget",
                "viewRequest",
                "selectEvent",
                "listRequests",
            ]  # HR has almost no access in the current iteration
        elif self.role == Role.PSR:
            self.hidden_commands = [
                "listPendingApprovals",
                "newEvent",
                "approve",
                "listRequests",
            ]  # PSR can't approve or manage events
        elif self.role == Role.SSR:
            self.hidden_commands = [
                "listPendingApprovals",
                "newEvent",
                "approve",
                "listRequests",
            ]  # SSR can't approve or manage events
        else:
            self.hidden_commands = ["listPendingApprovals"]
        self.hidden_commands.extend(self.disabled_cmds)

    def show_event_request(self, event):
        """
        Display the currently created event in a formatted structure.
        """
        self.poutput("\n===== EVENT DETAILS =====")
        self.poutput(f"Name:        {event.name}")
        self.poutput(f"Budget:      {event.budget}")
        self.poutput(
            f"Description:\n{event.type if event.type else '(no description)'}"
        )
        # don't have these in the event yet - should we add?
        # approved_by_display = ", ".join(event.ApprovedBy) if event.ApprovedBy else "(nobody yet)"
        # self.poutput(f"Approved By: {approved_by_display}")
        self.poutput("=========================\n")

    def show_list(self, things, prompt):
        self.poutput(prompt)
        for thing in things:
            self.poutput(thing)

    def show_approved(self, msg):
        self.poutput(f"Event: {msg.name} approved!")

    def show_rejected(self, msg):
        self.poutput(f"Event: {msg.name} rejected!")

    def do_listEvents(self, arg):
        self.poutput("Events:")
        for ev in self._events:
            self.poutput(ev.name)

    def do_showEvent(self, arg):
        e_name = arg
        try:
            event = [x for x in self._events if x.name == e_name].pop()
        except:
            self.perror("Event not found")
        self.poutput("\n===== EVENT DETAILS =====")
        self.poutput(f"Name:        {event.name}")
        self.poutput(f"Budget:      {event.budget}")
        self.poutput(
            f"Description:\n{event.description if event.description else '(no description)'}"
        )
        # don't have these in the event yet - should we add?
        # approved_by_display = ", ".join(event.ApprovedBy) if event.ApprovedBy else "(nobody yet)"
        # self.poutput(f"Approved By: {approved_by_display}")
        self.poutput("========= Tasks =========\n")
        for ts in event.tasks:
            self.poutput(
                f"Task: {ts.name} :: Budget: {ts.budget} :: {'Approved' if ts.approved else 'Not Approved'}"
            )

    def do_showTask(self, arg):
        """Approve a task. Usage: approveTask <task_name>"""
        if not self.require_login():
            return
        if not self.current_event:
            self.perror("❗ No active event selected.")
            return

        t_name = arg.strip()
        if not t_name:
            t_name = self.read_input("Task Name: ")
        task: Task = None
        for ts in self.current_event.tasks:
            if ts.name == t_name:
                task = ts
                break
        if task == None:
            self.perror(f"Task {t_name} not found")
            return
        self.poutput("\n===== Task DETAILS =====")
        self.poutput(f"Name:        {task.name}")
        self.poutput(f"Budget:      {task.budget}")
        self.poutput(
            f"Description:\n{task.description if task.description else '(no description)'}"
        )
        self.poutput(f"{'Approved' if task.approved else 'Not Approved'}")
        self.poutput("=========== Comments ==========")
        for cm in task.comments:
            self.poutput(cm)

    def do_crewRequest(self, arg):
        """Create a new Request to HR for outsourcing new staff"""

        # Require login
        if not self.require_login():
            return

        # User input and validation
        name = self.read_input("Crew request name: ")
        department = Department.Production                  # TODO: This should be changed so is taken from the user as input or role
        description = self.read_input("Description: ")
        while True:
            try:
                salary = int(self.read_input("Salary: "))
                break
            except:
                self.perror("Salary must be a number > 0 and integer")
        fulltime = True                                     # TODO: This should be a user input

        # Create the object
        hr_req = CrewRequest(name=name, department=department, description=description, salary=salary, fulltime=fulltime)

        self.poutput(f"Crew request created with name: {hr_req.name}\nRequest sent to HR!")
        self._outMsgQueue.put(CrewRequestMessage(hr_req))

    # EVENT HANDLING (existing)
    def event_thread(self):
        while True:
            msg = self._inMsgQueue.get()
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
                self.show_event_request(msg.request)
            elif isinstance(msg, RequestApprovedMessage):
                self.show_approved(msg)
            elif isinstance(msg, RequestRejectedMessage):
                self.show_rejected(msg)
            elif isinstance(msg, RequestListMessage):
                self._requests = msg.requests
            elif isinstance(msg, EventListMessage):
                self._events = msg.events
            elif isinstance(msg, TaskListMessage):
                self._tasks = msg.tasks
            elif isinstance(msg, PendingListMessage):
                self.show_list(msg.names, "Pending Requests: ")

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
