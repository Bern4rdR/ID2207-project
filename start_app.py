from cli.sep_cli import SepCli
from login.login_manager import LoginManager
from multiprocessing import Process, Queue
from message.message import Message, LoginMessage, StopMessage, LoginResultMessage, NewEventMessage, ViewEventMessage, DecideEventMessage
import pickle

# this defines the main backend loop and data structure
# probably should be in a different file but we need 3 refactors per day so...
class SepModel:
    _tasks = []
    _events = []
    def __init__(self, bgMsgQueue: Queue, outputQueue: Queue):
        self._lm = LoginManager("./login/users.txt")
        self._bgMsgQueue = bgMsgQueue
        self._outputQueue = outputQueue

    def save_on_exit(self):
        with open("sep_tasks.pkl", 'wb') as f:
            f.truncate(0)
            pickle.dump(self._tasks, f)
        with open("sep_events.pkl", 'wb') as f:
            f.truncate(0)
            pickle.dump(self._events, f)    

    def load_on_enter(self):
        # yes this is lazy
        try: 
            with open("sep_tasks.pkl", 'rb') as f:
                self._tasks = pickle.load(f)
            with open("sep_events.pkl", 'rb') as f:
                self._events = pickle.load(f)
        except:
            self._tasks = []
            self._events = []

    def loop(self):
        # for user in self._lm._users.keys():
        #     print(user)
        while(True):
            next_msg = self._bgMsgQueue.get()
            if type(next_msg) == LoginMessage:
                # got really lazy with the privacy here
                success, role = self._lm.login(next_msg._username, next_msg._password)
                self._outputQueue.put(LoginResultMessage(success, role, next_msg._username)) 
            elif type(next_msg) == StopMessage:
                self.save_on_exit()
                break
            elif type(next_msg) == NewEventMessage:
                self._events.append(next_msg)
            elif type(next_msg) == ViewEventMessage:
                ev = [x for x in self._events if x.name == next_msg.name]
                if len(ev):
                    self._outputQueue.put(ev[0])
            elif type(next_msg) == Message:
                print(f"Message received with Type Message {next_msg.name}")
            # base case - all messages are type message
            else:
                print(f"Message received without type detected {next_msg.name}")
    
def run_model(qin, qout):
    model = SepModel(qin, qout)
    model.load_on_enter()
    model.loop()

if __name__ == "__main__":
    print("Start SEP Management Application")
    # interprocess comms
    model_input_queue = Queue()
    model_output_queue = Queue()
    cli = SepCli(model_input_queue, model_output_queue)
    model_process = Process(target=run_model, args=[model_input_queue, model_output_queue])
    model_process.start()
    cli.run_ui()
    # we will sit in the cli loop until the user exits
    model_input_queue.put(StopMessage())
    model_process.join()