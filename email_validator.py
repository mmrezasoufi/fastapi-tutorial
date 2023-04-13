import re


def validate_email(email):
    """
    This function takes an email address as input and returns True if the email is valid,
    and False otherwise.
    """
    # A regular expression for checking the format of an email address
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    # Check if the email matches the regular expression
    if re.match(email_regex, email):
        return True
    else:
        raise Exception('Invalid email address')
