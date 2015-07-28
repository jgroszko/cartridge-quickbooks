import json, uuid, logging

from quickbooks.models import OAuth_Session
from mezzanine.conf import settings

from rauth import OAuth1Service, OAuth1Session

SERVICE_NAME = "QuickBooks Payments API"

REQUEST_TOKEN_URL = "https://oauth.intuit.com/oauth/v1/get_request_token"
ACCESS_TOKEN_URL = "https://oauth.intuit.com/oauth/v1/get_access_token"
AUTHORIZE_URL = "https://appcenter.intuit.com/connect/begin"
RECONNECT_URL = "https://appcenter.intuit.com/api/v1/connection/reconnect"

if settings.DEBUG:
    BASE_URL = "https://sandbox.api.intuit.com/quickbooks/v4/payments"
else:
    BASE_URL = "https://api.intuit.com/quickbooks/v4/payments"

CHARGES_URL = BASE_URL + "/charges/"

logger = logging.getLogger(__name__)

class Payments:
    def __init__(self, access_token=None, access_secret=None):
        self.service = OAuth1Service(
            name=SERVICE_NAME,
            consumer_key=settings.QUICKBOOKS_CONSUMER_KEY,
            consumer_secret=settings.QUICKBOOKS_CONSUMER_SECRET,
            request_token_url=REQUEST_TOKEN_URL,
            access_token_url=ACCESS_TOKEN_URL,
            authorize_url=AUTHORIZE_URL,
            base_url=BASE_URL)

        self.access_token = access_token
        self.access_secret = access_secret

        if(OAuth_Session.objects.count() == 1):
            session_info = OAuth_Session.objects.get()

            self.company_id = session_info.company_id

            self.session = self.service.get_session((session_info.access_key,
                                                     session_info.access_secret))

    def get_auth_url(self, callback_url):
        params = {
            'oauth_callback': callback_url
        }

        self.access_token, self.access_secret = self.service.get_request_token(params=params)

        return self.service.get_authorize_url(self.access_token)

    def get_auth_session(self, verifier, realm):
        data = {
            'oauth_verifier': verifier
        }

        self.session = self.service.get_auth_session(self.access_token,
                                                     self.access_secret,
                                                     data=data)

        oas = None
        if(OAuth_Session.objects.count() == 1):
            oas = OAuth_Session.objects.get()
        else:
            oas = OAuth_Session.objects.create()

        oas.access_key = self.session.access_token
        oas.access_secret = self.session.access_token_secret
        oas.company_id = realm
        oas.save()

        return self.session

    def charges(self):
        response = self.session.request("GET",
                                    CHARGES_URL)

        if(not response.ok):
            raise Exception(response.reason)

        return response.json()

    def charge(self, charge_data):
        response = self.session.request("POST",
                                        CHARGES_URL[:-1],
                                        header_auth=True,
                                        headers={
                                            'Content-Type': 'application/json',
                                            'Request-Id': str(uuid.uuid1()),
                                            'Company-Id': self.company_id
                                        },
                                        data=json.dumps(charge_data))

        if(not response.ok):
            raise Exception(response.content)

        return response.json()

    def reconnect(self):
        response = self.session.request("GET",
                                        RECONNECT_URL,
                                        header_auth=True,
                                        headers={
                                            'Content-Type': 'application/json',
                                            'Request-Id': str(uuid.uuid1()),
                                            'Company-Id': self.company_id
                                        },
                                        data=None)

        if(not response.ok):
            raise Exception(response.content)

        response_data = response.json()

        if('ErrorCode' in response_data):
            if(response_data['ErrorCode'] == 212):
                logger.info("Attempted to renew API token outside of window\n%s" % response.content)
            else:
                raise Exception(response.content)
        else:
            oas = OAuth_Session.objects.get()
            oas.access_key = response_data['OAuthToken']
            oas.access_secret = response_data['OAuthTokenSecret']
            oas.save()

            logger.info("Successfully reconnect API token" % response.content)
