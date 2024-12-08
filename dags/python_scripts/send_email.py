import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from airflow.models.variable import Variable
import logging

logger = logging.getLogger(__name__)

def get_email_config():
    variables = Variable.get('email_config', deserialize_json=True)
    recipients = Variable.get('email_recipient', deserialize_json=True)
    return variables, recipients

def sendEmail(message, subject):
    email_config, email_recipient = get_email_config()
    email_sender = email_config['EMAIL_SENDER']
    email_password = email_config['EMAIL_PASSWORD']
    email_receiver = email_recipient['EMAIL_RECIPIENT']
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
        logger.info('Email sent successfully')
        return {
            'status': 'success',
            'message': 'Email sent successfully'
        }
    except Exception as e:
        logger.error(e)
        return {
            'status': 'error',
            'message': str(e)
        }