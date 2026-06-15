import smtplib
from email.mime.text import MIMEText
import pathlib
subject = "Email Subject"
body = "This is the body of the text message"
password = ""
sender = ""
recipients = []
cwd = pathlib.Path.cwd()

with open( str(cwd.parent) + "/disk/pwd.txt", "r") as p:
    password = p.readline()
with open(str(cwd.parent) + "/disk/mail.txt", "r") as m:
    mail = m.readline()
    sender = mail
    recipients.append(sender)


def send_email(
    subject,
    body,
):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = ", ".join(recipients)
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp_server:
        smtp_server.login(sender, password)
        smtp_server.sendmail(sender, recipients, msg.as_string())
    print("Message sent!")
