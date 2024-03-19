
from datetime import datetime
import os.path
import os
import smtplib
from email.message import EmailMessage
from os.path import basename
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

To= 'dave.pierre23@outlook.com'

def sendMessageWithAttachment(file_path,subject):
    EMAIL_ADDRESS = "soccermsndave@gmail.com"
    EMAIL_PASSWORD ="wyezzrtstndpuxvt"
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = EMAIL_ADDRESS
    msg['To'] =To
    path=file_path
    with open(path, "rb") as fil:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(fil.read())
        
    part.add_header(
        "Content-Disposition",
        f"attachment; filename= 'attachment.txt'",
    )
    part['Content-Disposition'] = 'attachment; filename="%s"' % basename(path)
    msg.attach(part)

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)