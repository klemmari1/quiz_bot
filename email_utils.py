import datetime
import email
import imaplib
import pickle
from email.header import decode_header
from os import path

TODAY = datetime.date.today().isoformat()

EMAILS = "emails.pkl"
USED_EMAILS = "used_emails.pkl"


def get_used_emails():
    if path.isfile(USED_EMAILS):
        with open(USED_EMAILS, "rb") as used_emails_file:
            try:
                email_dict = pickle.load(used_emails_file)
            except EOFError:
                email_dict = {}
    else:
        email_dict = {}

    return email_dict


def get_emails():
    emails = []
    if path.isfile(EMAILS):
        with open(EMAILS, "rb") as emails_file:
            emails = pickle.load(emails_file)
    return emails


def get_unused_emails() -> list:
    emails = get_emails()
    if not emails:
        return []
    used_emails = []
    used_emails_dict = get_used_emails()
    if TODAY in used_emails_dict:
        used_emails = used_emails_dict[TODAY]

    emails = [email_addr for email_addr in emails if email_addr[0] not in used_emails]
    return emails


def get_email():
    emails = get_unused_emails()
    if emails:
        return emails[0]
    else:
        return "asd@asd.com", None, None


def save_email(email_addr):
    email_dict = get_used_emails()

    if TODAY not in email_dict:
        email_dict[TODAY] = []
    email_dict[TODAY].append(email_addr)

    with open(USED_EMAILS, "wb") as used_emails_file:
        pickle.dump(email_dict, used_emails_file)


def get_verification_code(email_address, password, code_sender):
    if "gmail" in email_address:
        imap = imaplib.IMAP4_SSL("imap.gmail.com")
    else:
        imap = imaplib.IMAP4_SSL("outlook.office365.com")
    imap.login(email_address, password)

    _, messages = imap.select("INBOX")
    messages = int(messages[0])  # this is how many mails you have

    # count down as the highest number is latest email
    # this loop is top 5 emails
    for i in range(messages, messages - 5, -1):
        _, msg = imap.fetch(str(i), "(RFC822)")
        for response in msg:
            if isinstance(response, tuple):
                # parse a bytes email into a message object
                msg = email.message_from_bytes(response[1])
                # decode the email subject
                subject, _ = decode_header(msg["Subject"])[0]
                sender, _ = decode_header(msg.get("From"))[0]
                if isinstance(subject, bytes):
                    try:
                        subject = subject.decode()
                    except:
                        continue

                if sender == code_sender:
                    break

        if sender == code_sender:
            break

    imap.close()
    imap.logout()

    verification_code = subject.split(" ")[0]
    print(verification_code)
    return verification_code
