from .models import User
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from mailqueue.models import MailerMessage
from django.conf import settings

def detectUser(user):
    if user.role == User.Vendor:
        redirectUrl = 'vendorDashboard'
    if user.role == User.CUSTOMER:
        redirectUrl = 'custDashboard'
    if user.role == None and user.is_superuser:
        redirectUrl = '/admin'

    return redirectUrl

def send_verification_email(request, user, mail_subject, email_template):
    from_email = settings.DEFAULT_FROM_EMAIL
    current_site = get_current_site(request)
    message = render_to_string(email_template, {
        'user': user,
        'domain': current_site,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': default_token_generator.make_token(user)
    })
    to_email = user.email

    # Use MailerMessage to queue the email
    mail = MailerMessage()
    mail.subject = mail_subject
    mail.to_address = to_email
    mail.from_address = from_email
    mail.content = message
    mail.content_subtype = "html"  # Set content type to HTML
    mail.save()  # Save the email to the queue

def send_notification(mail_subject, mail_template, context):
    from_email = settings.DEFAULT_FROM_EMAIL
    message = render_to_string(mail_template, context)
    to_email = context['to_email']

    # Handle single or multiple recipients
    if isinstance(to_email, str):
        to_email = [to_email]

    # Use MailerMessage to queue the email
    for email in to_email:
        mail = MailerMessage()
        mail.subject = mail_subject
        mail.to_address = email
        mail.from_address = from_email
        mail.content = message
        mail.content_subtype = "html"  # Set content type to HTML
        mail.save()  # Save the email to the queue