# IMPORTS
import imaplib
from time import sleep
import smtplib
import email
from subprocess import call
import sys
import json
import random


# OPENING THE CONFIGURATION FILE
with open(sys.argv[1]) as configF:
    config = json.load(configF)


# MAIN AUTORESPONDER CLASS
class VacationAutoResponder:

    def __init__(self , config):
        #INITIALISING THE VARIABLES
        self.imap_server = config["imap_servr"]
        self.smtp_server = config["smtp_servr"]
        self.smtp_port = int(config["smtp_port"])
        
        #CONNECTING IMAP AND SMTP CLIENTS TO GMAIL ACCOUNT
        self.mail = imaplib.IMAP4_SSL(self.imap_server)
        self.mail.login(config["username"] , config["password"])
        self.sender = smtplib.SMTP(self.smtp_server , self.smtp_port)
        self.sender.ehlo()
        self.sender.starttls()
        self.sender.ehlo
        self.sender.login(config["username"] , config["password"])


   # FOR SELECTING RANDOM TIME INTERVAL BETWEEN 45 and 120
    def refresh_delay(self):
        rate =  random.randrange(45 , 120)
        return rate

    # CLOSING THE APPLICATION
    def close_application(self):
        self.sender.close()
        self.mail.logout()

    # CHECKING ALL THE UNREPLIED EMAILS
    def checkEmail(self):
        self.mail.select()
        _ , data = self.mail.search(None , '(UNANSWERED)')
        self.mail.close()
        for mail_numbr in data[0].split():
            self.reply(mail_numbr)

    # ADDING THE Replied label to all the answered emails by the bot
    def add_label(self ,mail_numbr):
        self.mail.select(readonly=False)
        self.mail.store(mail_numbr , '+X-GM-LABELS', 'Replied')
        self.mail.store(mail_numbr, '+FLAGS', '\\Answered')
        self.mail.close()
    
    # SENDING THE REPLY USING SMTP CLIENT    
    def send_auto_reply(self , original):
        subject = "Re: " + original.get("Subject")
        header = 'To:' + original['From'] + '\n' + 'From: '+config["name"]+' <'+config["username"]+'>\n' + 'Subject:'+ subject+'\n'
        message = header + '\n' + config["responseMessage"] + '\n\n'
        self.sender.sendmail(config["username"] ,[original['From']] , message)
        log = 'Replied to “%s” for the mail “%s”' % (original['From'],
                                                     original['Subject'])
        print(log)
        try:
            call(['notify-send', log])
        except FileNotFoundError:
            pass

    # REPLY TO SEND
    def reply(self , mail_numbr):
        self.mail.select(readonly=True)
        _ , data = self.mail.fetch(mail_numbr , '(RFC822)')
        self.mail.close()
        self.send_auto_reply(email.message_from_bytes(data[0][1]))
        self.add_label(mail_numbr)

    # THE MAIN RUNNING FUNCTION
    def run(self):
        print("[STARTING] Vacation Autoresponder....")
        try:
            while True:
                self.checkEmail()
                time_ = self.refresh_delay()
                print("[SLEEPING] for {} seconds".format(time_))
                sleep(time_)
        finally:
            self.close_application()






# INSTANTIATING AND RUNNING THE CLASS
vac = VacationAutoResponder(config)
vac.run()


