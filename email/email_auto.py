import imaplib
import email
from email.header import decode_header
import sqlalchemy as db

# Database setup
DATABASE_URL = "sqlite:///emails.db"
engine = db.create_engine(DATABASE_URL)
connection = engine.connect()
metadata = db.MetaData()

emails_table = db.Table('emails', metadata,
                         db.Column('id', db.Integer, primary_key=True),
                         db.Column('subject', db.String),
                         db.Column('body', db.Text))

metadata.create_all(engine)

# IMAP connection
def connect_to_gmail(username, password):
    mail = imaplib.IMAP4_SSL('imap.gmail.com')
    mail.login(username, password)
    return mail

# Fetch unread emails
def fetch_unread_emails(mail):
    mail.select("inbox")  # Select the inbox
    status, messages = mail.search(None, 'UNSEEN')  # Search for all unread emails
    email_ids = messages[0].split()
    return email_ids

# Extract email content
def get_email_content(mail, email_id):
    res, msg = mail.fetch(email_id, '(RFC822)')
    msg = email.message_from_bytes(msg[0][1])
    
    # Decode email subject
    subject, encoding = decode_header(msg['Subject'])[0]
    if isinstance(subject, bytes):
        subject = subject.decode(encoding if encoding else 'utf-8')
    
    # Get email body
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                body = part.get_payload(decode=True).decode()
    else:
        body = msg.get_payload(decode=True).decode()
    
    return subject, body

# Store email data in database
# def store_email(subject, body):
#     query = db.insert(emails_table).values(subject=subject, body=body)
#     connection.execute(query)

# Main function
def main():
    username = 'strikepunchk@gmail.com'  # Replace with your email
    password = 'gfau vzyj pxhg vyfo'       # Replace with your App Password

    mail = connect_to_gmail(username, password)
    email_ids = fetch_unread_emails(mail)
    
    for email_id in email_ids:
        subject, body = get_email_content(mail, email_id)
        if subject and body:
            # store_email(subject, body)
            print(f"Stored email with subject: {subject}")

    mail.logout()

if __name__ == '__main__':
    main()