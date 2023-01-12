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

from charged.utils import create_email_message, is_onion
from django.conf import settings
import os
import grpc


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
    

    macaroon_hex = "0201036C6E6402AC01030A101AC081C5147FE0CC8E704EAA8DFDCC9B1201301A0F0A07616464726573731204726561641A0C0A04696E666F1204726561641A100A08696E766F696365731204726561641A100A086D616361726F6F6E1204726561641A0F0A076D6573736167651204726561641A100A086F6666636861696E1204726561641A0F0A076F6E636861696E1204726561641A0D0A0570656572731204726561641A0E0A067369676E65721204726561640000062061235C2ED71BD5CA46BDEABB840735B0BAD2D23A32075F1F5718F7B1A54C6F4B"
    tls_cert= ""
    host = "" # The onion address
    port = ""

    def metadata_callback(context, callback):
        # for more info see grpc docs
        callback([('macaroon', macaroon_hex)], None)
    
    # Due to updated ECDSA generated tls.cert we need to let gprc know that
    # we need to use that cipher suite otherwise there will be a handshake
    # error when we communicate with the lnd rpc server.
    os.environ["GRPC_SSL_CIPHER_SUITES"] = 'HIGH+ECDSA'

    # build ssl credentials using the cert the same as before
    cert_creds = grpc.ssl_channel_credentials(tls_cert)

    # build meta data credentials
    auth_creds = grpc.metadata_call_credentials(metadata_callback)
    
    # combine the cert credentials and the macaroon auth credentials
    # such that every call is properly encrypted and authenticated
    combined_creds = grpc.composite_channel_credentials(cert_creds, auth_creds)
    



    print(f'Attempting to open a gRPC channel with the ONION address "{host}:{port}".')
    cert_cn = 'localhost' # or parse it out of the cert data
    proxy_address = getattr(settings, 'CHARGED_LND_HTTP_PROXY')
    options = (('grpc.ssl_target_name_override', cert_cn,),('grpc.http_proxy', proxy_address),)
    return grpc.secure_channel('{}:{}'.format(host, port), combined_creds, options)
