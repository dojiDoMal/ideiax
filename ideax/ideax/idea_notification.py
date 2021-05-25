from django.core.mail import send_mail, EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from notifications.signals import notify
from .enums import Parameters
from .models import Follow

def message_menager(context, notification_type):
    stackholders = ["author", "coauthor", "mentionade", "follower"]
    for stackholder in stackholders:
        message_handle_stackholders(context, notification_type, stackholder)

def message_handle_stackholders(context, notification_type, stackholder):
    recipients = obtain_mail_destiny(context)
    email_key = "email_{0}".format(stackholder)
    notify_key = "notify_{0}".format(stackholder)

    settings = notification_type.value

    idea = context["idea"]
    if "idea_related" in context.keys():
        description = settings['description'].format(idea.id, context["idea_related"].id)
    else:
        description = settings['description'].format(idea.id)
        author_description = settings['author_description'].format(idea.id)

    #notify
    if settings[stackholder] == "11" or settings[stackholder] == "01":
        for recipient in recipients[notify_key]:
            notify.send(context["user"],
                icon_class=settings['icon_class'],
                recipient=recipient,
                description=description,
                target=idea,
                actor=context["user"].get_username(),
                verb=settings['verb'])

    #email
    if settings[stackholder] == "11" or settings[stackholder] == "10":

        for index in range(len(recipients[notify_key])):
            user = recipients[notify_key][index]
            
            mail_context = { 'name': user.first_name,
                'message_pre': settings['message']['message_pre'],
                'message_midle' : settings['message']['message_midle'],
                'message_pos': settings['message']['message_pos'],
                'site': Parameters.ADDRESS_ALIAS.value,
                'url_idea': settings['url'].format(idea.id),
                'id': idea.id,
                'name_author': "{0} {1}".format(idea.author.user.first_name.upper(), idea.author.user.last_name.upper() ) }
            
            if "idea_related" in context.keys():
                mail_context["url_related"] = settings['url'].format(idea.id)
                mail_context["id_related"] = context["idea_related"].id
            
            if "new_phase" in context.keys():
                mail_context['message_pos'] = mail_context['message_pos'].format(context["new_phase"])
            
            send_html_email([recipients[email_key][index]],
               settings['subject'].format(idea.id),
               settings['email_template'],
               mail_context,
               Parameters.EMAIL_FROM.value + " <" + Parameters.EMAIL_HOST_USER.value  + "@dataprev.gov.br>")

def send_html_email(to_list, subject, template_name, context, sender=settings.DEFAULT_FROM_EMAIL):
    msg_html = render_to_string(template_name, context)
    for destiny in to_list:
        msg = EmailMessage(subject=subject, body=msg_html, from_email=sender, to=[destiny])
        msg.content_subtype = "html"  # Main content is now text/html
        msg.send()

def obtain_mail_destiny(context):

    result = {}
    idea = context["idea"]

    result["email_author"] = [format_address(idea.author.user)]
    result["email_coauthor"] = []
    result["email_follower"] = []
    result["email_mentionade"] = []

    result["notify_author"] = [idea.author.user]
    result["notify_coauthor"] = []
    result["notify_follower"] = []
    result["notify_mentionade"] = []
    
    for coauthor in idea.authors.all():
        if coauthor.user not in result["notify_author"]:
            result["email_coauthor"].append(format_address(coauthor.user))
            result["notify_coauthor"].append(coauthor.user)
    
    for item in Follow.objects.filter(idea=idea, active=True):
        result["email_follower"].append(format_address(item.user.user))
        result["notify_follower"].append(item.user.user)

    if "user_mentions" in context.keys():
        for item in context["user_mentions"]:
            result["email_mentionade"].append(format_address(item))
            result["notify_mentionade"].append(item)
    
    if "idea_related" in context.keys():
        for related_author in context["idea_related"].authors.all():
            if related_author.user not in result["notify_author"] and related_author.user not in result["notify_coauthor"] and related_author.user not in result["notify_follower"] and related_author.user not in result["notify_mentionade"]:
                result["notify_author"].append(related_author.user)
                result["email_author"].append(format_address(related_author.user))

    return result

def format_address(user):
    return "{0} {1} <{2}>".format(user.first_name, user.last_name, user.email)  