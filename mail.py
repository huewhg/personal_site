import smtplib
from email.mime.text import MIMEText
import pathlib
password = ""
sender = ""
recipients = []
cwd = pathlib.Path.cwd()

with open( str(cwd.parent) + "/disk/pwd.txt", "r") as p:
    password = p.readline().strip("\n")
with open(str(cwd.parent) + "/disk/mail.txt", "r") as m:
    mail = m.readline().strip("\n")
    sender = mail
with open(str(cwd.parent) + "/disk/bully_recipient.txt", "r") as b:
    mailb = b.readline().strip("\n")
    recipients.append(mailb)

def send_email(
    subject,
    body,
    recipients = recipients,
):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = ", ".join(recipients)
    link = "smtp.seznam.cz"
    port = 465
    
    
    with smtplib.SMTP_SSL(link, port) as smtp_server:
        smtp_server.login(sender, password)
        smtp_server.sendmail(sender, recipients, msg.as_string())
    print("Message sent!")
