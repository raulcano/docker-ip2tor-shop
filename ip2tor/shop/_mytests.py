##########################
# Open a shell environment in the django container
# Open a python shell for the django project:
#   python3 manage.py shell
# Inside there, import the function to test e.g.:
#   from shop._mytests.py import testmail
# After that, you can call the function directly to check the result
#   testmail()
#
####

from charged.utils import create_email_message
from django.conf import settings

def hello():
    print('hello world')

def testmail():
    # https://www.guerrillamail.com/
    recipients = ['sentinelium@protonmail.com', 'krvuztxo@sharklasers.com']

    print( 'RECIPIENTS: ' + str(recipients))
    print( 'EMAIL_HOST: ' + getattr(settings, 'EMAIL_HOST'))
    print( 'EMAIL_PORT: ' + str(getattr(settings, 'EMAIL_PORT')))
    print( 'EMAIL_HOST_USER: ' + getattr(settings, 'EMAIL_HOST_USER'))
    print( 'EMAIL_HOST_PASSWORD: ' + getattr(settings, 'EMAIL_HOST_PASSWORD'))
    print( 'EMAIL_USE_TLS: ' + str(getattr(settings, 'EMAIL_USE_TLS')))
    print( 'SERVER_EMAIL: ' + getattr(settings, 'SERVER_EMAIL'))
    print( 'DEFAULT_FROM_EMAIL: ' + getattr(settings, 'DEFAULT_FROM_EMAIL'))


    msg = create_email_message(f'[IP2Tor] Testing email',
                                f'Message body is_alive now',
                                recipients=recipients)
    print(msg.send(fail_silently=False))

# Test if we can connect to the LND node using the Tor address it exposes
def grpctor():
    pass