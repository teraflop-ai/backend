import resend
from typing import Dict

resend.api_key = ""

def send_welcome_mail(
    to_recipient: str,
    from_sender: str = "onboarding@resend.dev",
    subject: str = "Welcome to Teraflop AI",
) -> Dict:
    with open("../backend/src/app/templates/welcome.html", "r") as file:
        html_as_string = file.read()

    params: resend.Emails.SendParams = {
        "from": from_sender,
        "to": [to_recipient],
        "subject": subject,
        "html": html_as_string,
    }

    email: resend.Email = resend.Emails.send(params)
    return email

def send_purchase_confirmation():
    pass

def send_user_deleted_mail():
    pass