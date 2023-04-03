from urllib import parse


def generate_message(group):
    message = f"""
    
    ****** POWERED BY www.PubPubs.Pub ******
    *** Visit www.pubpubs.pub/group/{group.uuid}/ to join this group if you were forwarded this message ***
    *** If you already have joined, uou can delete your link to this group there too, or set up a SNOOZE period ***
    """
    return message  # '%0D'.join(message.splitlines())


def compose_email_link(subject, message, field_txt, email_list):
    email_link = "mailto:?subject=" + encode(subject) + \
                 "&body=" + encode(message) + \
                 f"&{field_txt}={','.join(email_list)}"
    return email_link


from urllib import parse


def encode(_str):
    return parse.quote(_str, safe='~()*!\'')
