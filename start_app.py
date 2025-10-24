from cli.sep_cli import SepCli
from login.login_manager import LoginManager
from multiprocessing import Process, Queue
from message.message import Message, LoginMessage, StopMessage

class SepModel:
    def __init__(self, bgMsgQueue: Queue ):
        self._lm = LoginManager("./login/users.txt")
        self._bgMsgQueue = bgMsgQueue
    
    def loop(self):
        while(True):
            next_msg = self._bgMsgQueue.get()
            if type(next_msg) == LoginMessage:
                # got really lazy with the privacy here
                self._lm.login(next_msg._username, next_msg._password)
            elif type(next_msg) == StopMessage:
                break
            # base case - all messages are type message
            elif type(next_msg) == Message:
                print(f"Message received {next_msg}")

if __name__ == "__main__":
    print("Start SEP Management Application")
    model_input_queue = Queue()
    cli = SepCli()
    model = SepModel(model_input_queue)
    # front_process = Process(target=SepCli.cmdloop)
    model_process = Process(target=model.loop)
    # front_process.start()
    model_process.start()
    cli.cmdloop()
    # we will sit in the cli loop until the user exits
    model_input_queue.put(StopMessage())