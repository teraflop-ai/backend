import resend
from typing import Dict

resend.api_key = ""

template_path = "path/to/file.html"


def send_mail(
    template_path,
    from_sender: str = "onboarding@resend.dev", 
    to_recipient: str = "delivered@resend.dev", 
    subject: str = "Hello World"
) -> Dict:
    
    with open(template_path, 'r') as file:
        html_as_string = file.read()

    params: resend.Emails.SendParams = {
        "from": from_sender,
        "to": [to_recipient],
        "subject": subject,
        "html": html_as_string,
    }

    email: resend.Email = resend.Emails.send(params)
    return email