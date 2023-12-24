import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formatdate, make_msgid
from post_caldav_events.output.message import message
from post_caldav_events.helper.datetime import date, now

def send_newsletter(config:dict, query_start, query_end, events:dict, recipientcli, format):
    with smtplib.SMTP_SSL(config['mail']['server'], config['mail']['smtp_port'] , context=ssl.create_default_context()) as smtp:
        smtp.ehlo()
        smtp.set_debuglevel(1)
        smtp.login(config['mail']['account'], config['mail']['password']) 
        mail = MIMEMultipart("alternative")
        mail.add_header('subject', f"{config['mail']['newsletter']['subject']} {date(query_start)} - {date(query_end)}")
        mail.add_header('from', config['mail']['sender'])
        mail.add_header('date', formatdate(localtime=True))
        mail.add_header('Message-ID', make_msgid())
        mail.add_header('Return-Path', 'noreply-bewegungskalender@systemli.org')
        mail.attach(MIMEText(message(config, events, query_start, query_end, format), "html"))
        if recipientcli is not None: #Override config recipients
            mail["to"] = recipientcli
            smtp.sendmail(config['mail']['sender'], recipientcli, mail.as_string())
            print(recipientcli)
        else:
            for recipient in config['mail']['newsletter']['recipients']:
                mail["to"] = recipient
                smtp.sendmail(config['mail']['sender'], recipient, mail.as_string())
                print(recipient)
        smtp.quit()