################################################EMAIL SEND###################################################################
In this article, I will share a way to send success or failure mail notification for any python script using Gmail API. Background in programming in Python will be good to grasp the article.
This can be used to set up daily jobs and have notifications sent when the scheduled python scripts run with failure or success.
A sample use case is a python script that runs daily to gather data from different sources to keep a check whether it ran with success or failure.
The first step is to set up sending mail using Gmail API.
Enable the Gmail API ‘https://developers.google.com/gmail/api/quickstart/python’ and save the file credentials.json.
Get the source code from the below local repository and replace the credentials.json obtained in the above step with the repository credentials.json file.
Run the script send_mail.py once to setup Gmail credentials in your root directory by authorizing the app to access Gmail API to send an email uncommenting the test stub with relevant mail addresses.
def send_message(sender, to, subject, plain_msg):
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)
    message = create_message(sender, to, subject, plain_msg)
    send_message_internal(service, "me", message)
#Testing
to = "test_recipient@gmail.com"
sender = "test_sender@gmail.com"
subject = "Test"
message = "Test"
send_message(sender, to, subject, message)
The authorized credentials saved will be referred to by sending any mail now.
The next step is to have a hook around the python sys.exit_code and sys.excepthook. For this refer to the file exit_hooks.py.
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
In the exit_function replace the to and sender with the mail address you want to send notification from and to.
def exit_function(hooks, job_name):
  to = "test_recipient@gmail.com"
  sender = "test_sender@gmail.com"
  subject = ""
  message = ""
  if hooks.exit_code is not None and hooks.exit_code != 0:
    message = "exit by sys.exit(%d)" % hooks.exit_code
    print(message)
    subject = "FAILURE: "+ job_name
  elif hooks.exception is not None:
    message = "exit by exception: %s" % hooks.exception
    print(message)
    subject = "FAILURE: "+ job_name
  else:
    message = "exit with success"
    subject = "SUCCESS: "+ job_name
  send_message(sender, to, subject, message)

def exit_hook(job_name):
    exit_hooks = ExitHooks()
    exit_hooks.hook()
    atexit.register(exit_function, exit_hooks, job_name)
The API exit_hook can now be used importing it in any python script.
exit_hookl(“sample_script”) line of code is to put at the start of any script to enable notification on success or failure exit.
#This is a sample script to test that it sends emails notification of success and failure of job on exit
import sys
from exit_hooks import exit_hook
def main():
  print("Test")
  sys.exit(1)
if __name__ == "__main__":
  exit_hook("sample_script")
  main()
The above sample_script.py when run will send a failure mail notification since exit code 1 is regarded as a failure.
Image for post
sys.exit(0) will send a success notification.
###############################################################################################################################################################

########################################################### Read Emails #######################################################################################
IMAP is an Internet standard protocol used by email clients to retrieve email messages from a mail server. Unlike the POP3 protocol which downloads email and delete them from the server (and then read them offline), with IMAP, the message does not remain on the local computer, it stays on the server.

To get started, we don't have to install anything, all the modules used in this tutorial are the built-in ones:

import imaplib
import email
from email.header import decode_header
import webbrowser
import os

# account credentials
username = "youremailaddress@provider.com"
password = "yourpassword"
We've imported the necessary modules, and then specified the credentials of our email account.

First, we gonna need to connect to the IMAP server:
# create an IMAP4 class with SSL 
imap = imaplib.IMAP4_SSL("imap.gmail.com")
# authenticate
imap.login(username, password)
Since I'm testing this on a gmail account, I've used imap.gmail.com server, check this link that contains list of IMAP servers for most commonly used email providers.

Also, if you're using a Gmail account and the above code raises an error indicating that the credentials are incorrect, make sure you allow less secure apps on your account.

If everything went okey, then you have successfully logged in to your account, let's start getting emails:

status, messages = imap.select("INBOX")
# number of top emails to fetch
N = 3
# total number of emails
messages = int(messages[0])
We've used imap.select() method, which selects a mailbox (Inbox, spam, etc.), we've chose INBOX folder, you can use imap.list() method to see the available mailboxes.
messages variable contains number of total messages in that folder (inbox folder), and status is just a message that indicates whether we received the message successfully. We then converted messages into an integer so we can make a for loop.

N variable is the number of top email messages you want to retrieve, I'm gonna use 3 for now, let's loop over each email message, extract everything we need and finish our code:

for i in range(messages, messages-N, -1):
    # fetch the email message by ID
    res, msg = imap.fetch(str(i), "(RFC822)")
    for response in msg:
        if isinstance(response, tuple):
            # parse a bytes email into a message object
            msg = email.message_from_bytes(response[1])
            # decode the email subject
            subject = decode_header(msg["Subject"])[0][0]
            if isinstance(subject, bytes):
                # if it's a bytes, decode to str
                subject = subject.decode()
            # email sender
            from_ = msg.get("From")
            print("Subject:", subject)
            print("From:", from_)
            # if the email message is multipart
            if msg.is_multipart():
                # iterate over email parts
                for part in msg.walk():
                    # extract content type of email
                    content_type = part.get_content_type()
                    content_disposition = str(part.get("Content-Disposition"))
                    try:
                        # get the email body
                        body = part.get_payload(decode=True).decode()
                    except:
                        pass
                    if content_type == "text/plain" and "attachment" not in content_disposition:
                        # print text/plain emails and skip attachments
                        print(body)
                    elif "attachment" in content_disposition:
                        # download attachment
                        filename = part.get_filename()
                        if filename:
                            if not os.path.isdir(subject):
                                # make a folder for this email (named after the subject)
                                os.mkdir(subject)
                            filepath = os.path.join(subject, filename)
                            # download attachment and save it
                            open(filepath, "wb").write(part.get_payload(decode=True))
            else:
                # extract content type of email
                content_type = msg.get_content_type()
                # get the email body
                body = msg.get_payload(decode=True).decode()
                if content_type == "text/plain":
                    # print only text email parts
                    print(body)
            if content_type == "text/html":
                # if it's HTML, create a new HTML file and open it in browser
                if not os.path.isdir(subject):
                    # make a folder for this email (named after the subject)
                    os.mkdir(subject)
                filename = f"{subject[:50]}.html"
                filepath = os.path.join(subject, filename)
                # write the file
                open(filepath, "w").write(body)
                # open in the default browser
                webbrowser.open(filepath)
            print("="*100)
imap.close()
imap.logout()
A lot to cover here, the first thing to notice is we've used range(messages, messages-N, -1), which means going from the top to the bottom, the newest email messages got the highest id number, the first email message has an ID of 1, so that's the main reason, if you want to extract the oldest email addresses, you can change it to something like range(N).

Second, we used the imap.fetch() method, which fetches the email message by ID using the standard format specified in RFC 822.

After that, we parse the bytes returned by the fetch() method to a proper Message object, and used decode_header() function from email.header module to decode the subject of the email address to human readable unicode.
After we print the email sender and the subject, we want to extract the body message. We look if the email message is multipart, which means it contains multiple parts. For instance, an email message can contain the text/html content and text/plain parts, which means it has the HTML version and plain text version of the message.

It can also contain file attachments, we detect that by the Content-Disposition header, so we download it under a new folder created for each email message named after the subject.

The msg object, which is email module's Message object, has many other fields to extract, in this example, we used only From and the Subject, write msg.keys() and see available fields to extract, you can for instance, get the date of when the message was sent using msg["Date"].

After I ran the code for my test gmail account, I got this output:

Subject: Thanks for Subscribing to our Newsletter !
From: sagar600360@gmail.com
====================================================================================================
Subject: An email with a photo as an attachment
From: Python Code <sagar600360@gmail.com>
Get the photo now!

====================================================================================================
Subject: A Test message with attachment
From: Python Code <sagar600360@gmail.com>
There you have it!

====================================================================================================
