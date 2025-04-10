import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from datetime import datetime

class Notifier:
    def __init__(self):
        # Email configuration would typically come from environment variables
        self.smtp_server = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.environ.get('SMTP_PORT', 587))
        self.sender_email = os.environ.get('SENDER_EMAIL', '')
        self.sender_password = os.environ.get('SENDER_PASSWORD', '')
    
    def send_alert(self, user, subject, message, send_email=True):
        """Send an alert to the user (console and optionally email)"""
        # Always print to console
        print(f"\n[ALERT for {user.username}] {subject}")
        print(f"{message}\n")
        
        # Send email if enabled and configured
        if send_email and self.sender_email and self.sender_password and user.email:
            self._send_email(user.email, subject, message)
            return True
        return False
    
    def _send_email(self, recipient_email, subject, message):
        """Send an email notification"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = recipient_email
            msg['Subject'] = subject
            
            # Add timestamp to the message
            full_message = f"{message}\n\nSent on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            msg.attach(MIMEText(full_message, 'plain'))
            
            # Connect to SMTP server and send email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.sender_email, self.sender_password)
            server.send_message(msg)
            server.quit()
            
            print(f"Email notification sent to {recipient_email}")
            return True
        except Exception as e:
            print(f"Failed to send email: {str(e)}")
            return False
