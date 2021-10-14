from add_email import save_emails
from quiz_bot import get_emails

remove_all = input("Remove latest email from the emails list? (y/n): ")

if remove_all == "y":
    emails = get_emails()
    del emails[-1]
    save_emails(emails)
