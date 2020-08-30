import imaplib
import email
from email.header import decode_header
import webbrowser
import os
import csv

# account credentials
username = ""
password = ""

# number of top emails to fetch
N = 4

# create an IMAP4 class with SSL, use your email provider's IMAP server
imap = imaplib.IMAP4_SSL("imap.gmail.com")
# authenticate
imap.login(username, password)

# select a mailbox (in this case, the inbox mailbox)
# use imap.list() to get the list of mailboxes
status, messages = imap.select("Test")

# total number of emails
messages = int(messages[0])
def between(value, a, b):
    # Find and validate before-part.
    pos_a = value.find(a)
    if pos_a == -1: return ""
    # Find and validate after part.
    pos_b = value.rfind(b)
    if pos_b == -1: return ""
    # Return middle part.
    adjusted_pos_a = pos_a + len(a)
    if adjusted_pos_a >= pos_b: return ""
    return value[adjusted_pos_a:pos_b]

for i in range(messages-1, messages-1-N, -2):
    # fetch the email message by ID
    res, msg = imap.fetch(str(i), "(RFC822)")
    for response in msg:
        if isinstance(response, tuple):
            # parse a bytes email into a message object
            msg = email.message_from_bytes(response[1])
            #print("===========================+++++++++++++++++++++++++++++++++++++++++++++++=========================")
            #print("message: ", msg)
            #print("=============================+++++++++++++++++++++++++++++++++++===================================")
            # decode the email subject
            subject = decode_header(msg["Subject"])[0][0]
            if isinstance(subject, bytes):
                # if it's a bytes, decode to str
                subject = subject.decode()
            # email sender
            from_ = msg.get("From")
            #print("Subject:", subject)
            #print("From:", from_)
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
                        #print("===================== BODY 1=========================")
                        #print(body)
                        #print("===================== BODY 1=========================")
                    except:
                        pass
                    if content_type == "text/plain" and "attachment" not in content_disposition:
                        # print text/plain emails and skip attachments
                        #print("===================== BODY 2=========================")
                        #print(body)
                        #print("===================== BODY =========================")
                        #print(between(body, "to", "because"))
                        email_id = (between(body, "to", "because"))
                        print("email: ",email_id)
                        if email_id:
                            ofile  = open('data.csv', "a")
                            writer = csv.writer(ofile, delimiter=',')
                            writer.writerow([email_id])
                            ofile.close()
                        #csvfile = "data.csv"
                        #with open(csvfile, "w", newline='') as fp:
                        #    wr = csv.writer(fp, dialect='excel')
                        #    wr.writerow(email_id)
                        #with open("email_data.csv", "a") as fp:
                        #    fp.write(email_id)
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
                    #print("===================== BODY 3=========================")
                    print(body)
                    #print("===================== BODY 3=========================")
            if content_type == "text/html":
                # if it's HTML, create a new HTML file and open it in browser
                #if not os.path.isdir(subject):
                    # make a folder for this email (named after the subject)
                    #os.mkdir(subject)
                filename = f"{subject[:50]}.html"
                filepath = os.path.join(subject, filename)
                # write the file
                
                open(filepath, "w").write(body)
                # open in the default browser
                #webbrowser.open(filepath)
          
            print("="*100)

# close the connection and logout
imap.close()
imap.logout()
