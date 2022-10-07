import datetime
import email
import imaplib
import pickle
import quopri
import re
from email.header import decode_header
from os import path

from email_utils import get_emails

USED_CODES_FILE = "used_codes.pkl"
NEW_CODES_FILE_PREFIX = "new_codes_"


def save_codes(codes: set):
    with open(USED_CODES_FILE, "wb") as codes_file:
        pickle.dump(codes, codes_file)


def get_codes() -> set:
    if path.isfile(USED_CODES_FILE):
        with open(USED_CODES_FILE, "rb") as codes_file:
            return pickle.load(codes_file)
    else:
        return set()


def save_code(code: str, new_codes: set):
    codes = get_codes()
    if code not in codes:
        codes.add(code)
        save_codes(codes)
        new_codes.add(code)


def find_code(subject, msg, new_codes):
    correct_subject = "hextech chest code"

    if correct_subject in subject.lower():
        print("Prize message found!")
        for part in msg.walk():
            if part.get_content_type() == "text/html":
                payload = part.get_payload()
                payload = quopri.decodestring(str(payload)).decode()
                code = re.findall("(?<=<strong>)(.*?)(?=</strong>)", payload)
                if code:
                    code = code[0]
                    save_code(code, new_codes)
                    print(code)
                else:
                    print("Code not found!")


def handle_junk(imap, new_codes):
    try:
        _, messages = imap.select("Junk")
        messages = int(messages[0])  # this is how many mails you have
    except:
        return

    emails_to_fetch = min(messages, 100)
    # count down as the highest number is latest email
    # this loop is top 5 emails
    for i in range(messages, messages - emails_to_fetch, -1):
        _, msg = imap.fetch(str(i), "(RFC822)")
        for response in msg:
            if isinstance(response, tuple):
                # parse a bytes email into a message object
                msg = email.message_from_bytes(response[1])
                # decode the email subject
                subject, _ = decode_header(msg["Subject"])[0]
                if isinstance(subject, bytes):
                    try:
                        subject = subject.decode()
                    except UnicodeDecodeError:
                        continue
                find_code(subject, msg, new_codes)
    imap.close()


def handle_inbox(imap, new_codes):
    _, messages = imap.select("INBOX")
    messages = int(messages[0])  # this is how many mails you have

    emails_to_fetch = min(messages, 100)
    # count down as the highest number is latest email
    # this loop is top 5 emails
    for i in range(messages, messages - emails_to_fetch, -1):
        _, msg = imap.fetch(str(i), "(RFC822)")
        for response in msg:
            if isinstance(response, tuple):
                # parse a bytes email into a message object
                msg = email.message_from_bytes(response[1])
                # decode the email subject
                subject, _ = decode_header(msg["Subject"])[0]
                if isinstance(subject, bytes):
                    try:
                        subject = subject.decode()
                    except UnicodeDecodeError:
                        continue
                find_code(subject, msg, new_codes)
    imap.close()


def claim_codes(email_address, password, new_codes):
    if "gmail" in email_address:
        imap = imaplib.IMAP4_SSL("imap.gmail.com")
    else:
        imap = imaplib.IMAP4_SSL("outlook.office365.com")

    try:
        imap.login(email_address, password)
    except:
        return

    handle_junk(imap, new_codes)
    handle_inbox(imap, new_codes)

    imap.logout()


def save_new_codes_to_file(new_codes):
    if new_codes:
        timestr = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        with open(f"{NEW_CODES_FILE_PREFIX}{timestr}.txt", "w") as codes_file:
            for code in new_codes:
                codes_file.write(code + "\n")


def run():
    emails = get_emails()
    emails = [(email_addr[0], email_addr[2]) for email_addr in emails]

    new_codes = set()
    for email_addr, password in emails:
        print(email_addr)
        claim_codes(email_addr, password, new_codes)

    save_new_codes_to_file(new_codes)


if __name__ == "__main__":
    run()
