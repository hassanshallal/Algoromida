import requests

# Important webhook related tokens and verifications
FB_API_URL = 'https://graph.facebook.com/v2.6/me/messages'
VERIFY_TOKEN = 'BtdlRsV5l9TeXx/OHmZ1ff/69NfQqNSzKS57mK/RGzE='
PAGE_ACCESS_TOKEN = 'EAAEvMG9mZAREBAPxmyfQoBq36WVTdqHSEZBhMcM81UbCZBy0185p3XKJ9WgmBiX9ppqO8UkaeL8ZAL4qlEJnJkgDogMhf1SnmOExQ2fEW0jg3CrWZAouf3LZC7ZB8naCF4JZCaxCN631JCPjUuHqZCAW2lkEcY7kNQxkMcVVj3NDUlAZDZD'


def verify_webhook(req):
    if req.args.get("hub.verify_token") == VERIFY_TOKEN:
        return req.args.get("hub.challenge")
    else:
        return "incorrect"


def is_user_message(message):
    """Check if the message is a message from the user"""
    return (message.get('message') and
            message['message'].get('text') and
            not message['message'].get("is_echo"))


def send_message(recipient_id, text):
    """Send a response to Facebook"""
    payload = {
        'message': {
            'text': text
        },
        'recipient': {
            'id': recipient_id
        },
        'notification_type': 'regular'
    }
    auth = {
        'access_token': PAGE_ACCESS_TOKEN
    }
    # The issue is in the next line!
    # response = requests.post(FB_API_URL, params=auth, data=payload)
    response = requests.post(FB_API_URL, params=auth, json=payload)
    result = response.json()
    return result
