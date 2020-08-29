import atexit
import sys

from mail.send_mail import send_message

class ExitHooks(object):
    def __init__(self):
        self.exit_code = None
        self.exception = None

    def hook(self):
        self._orig_exit = sys.exit
        sys.exit = self.exit
        sys.excepthook = self.exc_handler

    def exit(self, code=0):
        self.exit_code = code
        self._orig_exit(code)

    def exc_handler(self, exc_type, exc, *args):
        self.exception = exc

def exit_function(hooks, job_name):
    to = "shah.sagar@northeastern.edu"
    sender = "sagar600360@gmail.com"
    subject = ""
    message = ""
    if hooks.exit_code is not None and hooks.exit_code != 0:
        message = "exit by sys.exit(%d)" % hooks.exit_code
        print(message)
        subject = "FAILURE: " + job_name
    elif hooks.exception is not None:
        message = "exit by exception: %s" % hooks.exception
        print(message)
        subject = "FAILURE: " + job_name
    else:
        message = "exit with success"
        subject = "SUCCESS: " + job_name
    send_message(sender, to, subject, message)

def exit_hook(job_name):
    exit_hooks = ExitHooks()
    exit_hooks.hook()
    atexit.register(exit_function, exit_hooks, job_name)
