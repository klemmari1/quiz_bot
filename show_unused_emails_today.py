import pprint

from email_utils import get_unused_emails

emails = get_unused_emails()
pprint.pprint([email[0] for email in emails])
