from django.core import mail
from django.core.mail import EmailMessage
from django.template.loader import get_template


class MailUtil:
    def __init__(self):
        self.connection = mail.get_connection()

    def send_mail(self, messages):
        self.connection.open()
        self.connection.send_messages(messages)
        self.connection.close()

    def send_messages(self, subject, template, context, emails):
        messages = self.generate_messages(subject, template, context, emails)
        self.send_mail(messages)

    def generate_messages(self, subject, template, context, emails):
        messages = []
        template = get_template(template)
        for recipient in emails:
            message_content = template.render(context)
            message = EmailMessage(subject, message_content, to=[recipient])
            message.content_subtype = 'html'
            messages.append(message)

        return messages
