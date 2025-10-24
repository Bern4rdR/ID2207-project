from cli.sep_cli import SepCli
from login.login_manager import LoginManager
from multiprocessing import Process, Queue
from message.message import Message, LoginMessage, StopMessage, LoginResultMessage

# this defines the main backend loop and data structure
# probably should be in a different file but we need 3 refactors per day so...
class SepModel:
    def __init__(self, bgMsgQueue: Queue, outputQueue: Queue):
        self._lm = LoginManager("./login/users.txt")
        self._bgMsgQueue = bgMsgQueue
        self._outputQueue = outputQueue
    
    def loop(self):
        # for user in self._lm._users.keys():
        #     print(user)
        while(True):
            next_msg = self._bgMsgQueue.get()
            if type(next_msg) == LoginMessage:
                # got really lazy with the privacy here
                success, role = self._lm.login(next_msg._username, next_msg._password)
                self._outputQueue.put(LoginResultMessage(success, role)) 
            elif type(next_msg) == StopMessage:
                break
            elif type(next_msg) == Message:
                print(f"Message received with Type Message {next_msg.name}")
            # base case - all messages are type message
            else:
                print(f"Message received without type detected {next_msg.name}")
    
def run_model(qin, qout):
    model = SepModel(qin, qout)
    model.loop()

if __name__ == "__main__":
    print("Start SEP Management Application")
    # interprocess comms
    model_input_queue = Queue()
    model_output_queue = Queue()
    cli = SepCli(model_input_queue, model_output_queue)
    model_process = Process(target=run_model, args=[model_input_queue, model_output_queue])
    model_process.start()
    cli.cmdloop()
    # we will sit in the cli loop until the user exits
    model_input_queue.put(StopMessage())
    model_process.join()