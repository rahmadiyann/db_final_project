import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def sendEmail(email_file: str = None, email_string: str = None, subject: str = 'Your Music Universe'):
    email_sender = os.getenv('EMAIL_SENDER')
    email_password = os.getenv('EMAIL_PASSWORD')
    email_receiver = os.getenv('EMAIL_RECEIVER')
    if email_file:
        with open(email_file, 'r') as f:
            message = f.read()
    elif email_string:
        message = email_string
    msg = MIMEMultipart()
    msg['From'] = email_sender
    msg['To'] = email_receiver
    msg['Subject'] = subject
    msg.attach(MIMEText(message, 'html'))
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(email_sender, email_password)
        server.sendmail(email_sender, email_receiver, msg.as_string())
        server.quit()
        print('Email sent successfully')
        return {
            'status': 'success',
            'message': 'Email sent successfully'
        }
    except Exception as e:
        print(e)
        return {
            'status': 'error',
            'message': str(e)
        }