import pickle

from quiz_bot import EMAILS, get_emails


def save_emails(emails: list):
    with open(EMAILS, "wb") as emails_file:
        pickle.dump(emails, emails_file)


def run():
    email = input("Enter email to use: ")
    verification_code_email = input(
        "Enter email from where to fetch the verification code (this is used if you entered an alias email for the first input) (leave empty to use the same email): "
    )
    password = input("Enter email password: ")

    if not verification_code_email:
        verification_code_email = email

    email_vars = [email, verification_code_email, password]

    emails = get_emails()
    emails.append(email_vars)
    save_emails(emails)


if __name__ == "__main__":
    run()
