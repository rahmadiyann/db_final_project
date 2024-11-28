import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
import json
import boto3
import os

def get_email_config():
    """
    Retrieve email configuration from S3
    Returns dict containing SMTP configuration
    """
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
        )
        response = s3_client.get_object(
            Bucket='db-final-project-spotipy',  # Replace with your bucket name
            Key='config/email_config.json'
        )
        config_str = response['Body'].read().decode('utf-8')
        return json.loads(config_str)
    except Exception as e:
        logging.error(f"Failed to retrieve email config from S3: {str(e)}")
        raise

def send_email(recipient_email: str, message: str, subject: str = "Notification"):
    """
    Send an email using SMTP
    
    Args:
        recipient_email (str): Email address of the recipient
        message (str): Content of the email message
        subject (str): Subject line of the email (defaults to "Notification")
    """
    try:
        # Get email configuration from S3
        email_config = get_email_config()
        smtp_server = email_config.get("smtp_server")
        smtp_port = email_config.get("smtp_port")
        sender_email = email_config.get("sender_email")
        sender_password = email_config.get("sender_password")

        # Create message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject

        # Add message body
        msg.attach(MIMEText(message, 'plain'))

        # Create SMTP session
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)

        logging.info(f"Successfully sent email to {recipient_email}")
    except Exception as e:
        logging.error(f"Failed to send email to {recipient_email}: {str(e)}")
        raise


print(get_email_config())