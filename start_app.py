from cli.sep_cli import SepCli
from login.login_manager import LoginManager
from multiprocessing import Process, Queue
from message.message import Message, LoginMessage, StopMessage, LoginResultMessage, NewEventMessage, ViewEventMessage, DecideEventMessage
from sep_model.sep_model import run_model


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