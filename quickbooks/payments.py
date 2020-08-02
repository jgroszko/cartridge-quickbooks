import json, uuid, logging, requests, datetime

from django.utils import timezone
from quickbooks.models import OAuth_Session
from mezzanine.conf import settings

from intuitlib.client import AuthClient
from intuitlib.enums import Scopes

# from rauth import OAuth1Service, OAuth1Session

# SERVICE_NAME = "QuickBooks Payments API"

# REQUEST_TOKEN_URL = "https://oauth.intuit.com/oauth/v1/get_request_token"
# ACCESS_TOKEN_URL = "https://oauth.intuit.com/oauth/v1/get_access_token"
# AUTHORIZE_URL = "https://appcenter.intuit.com/connect/begin"
# RECONNECT_URL = "https://appcenter.intuit.com/api/v1/connection/reconnect"

if settings.DEBUG:
    BASE_URL = "https://sandbox.api.intuit.com/quickbooks/v4/payments"
else:
    BASE_URL = "https://api.intuit.com/quickbooks/v4/payments"

CHARGES_URL = BASE_URL + "/charges"
CHARGES_REFUND_URL_FORMAT = BASE_URL + "/charges/%s/refunds"

logger = logging.getLogger(__name__)

class Payments:
    def __init__(self, request=None):
        callback_url = ''
        if request is not None:
            callback_url = request.build_absolute_uri(request.path).replace('http:','https:')

        self.auth_client = AuthClient(
            settings.QUICKBOOKS_CLIENT_ID,
            settings.QUICKBOOKS_CLIENT_SECRET,
            callback_url,
            'sandbox' if settings.DEBUG else 'production',
        )

        if(OAuth_Session.objects.count() == 1):
            session_info = OAuth_Session.objects.get()

            if(session_info.updated < timezone.now() - datetime.timedelta(hours=1)):
                if(session_info.updated < timezone.now() - datetime.timedelta(days=1)):
                    logger.info('Refresh token has expired')
                    return
                else:
                    logger.info('Get fresh access token')
                    self.refresh()
            else:
                logger.info('Re-use access token')
                self.auth_client.access_token = session_info.access_token
                self.auth_client.refresh_token = session_info.refresh_token

    def is_authorized(self):
        return hasattr(self.auth_client, 'access_token') and self.auth_client.access_token is not None

    def get_auth_url(self):
        return self.auth_client.get_authorization_url([Scopes.PAYMENT, Scopes.OPENID])

    def get_auth_token(self, auth_code, realm_id):
        self.auth_client.get_bearer_token(auth_code, realm_id=realm_id)

        oas = None
        if(OAuth_Session.objects.count() == 1):
            oas = OAuth_Session.objects.get()
        else:
            oas = OAuth_Session.objects.create()

        oas.access_token = self.auth_client.access_token
        oas.refresh_token = self.auth_client.refresh_token
        oas.company_id = self.auth_client.realm_id
        oas.save()

        return self.auth_client.access_token

    def refresh(self):
        try:
            self.auth_client.refresh(refresh_token=self.auth_client.refresh_token)

            session_info = OAuth_Session.objects.get()
            session_info.access_token = self.auth_client.faccess_token
            session_info.refresh_token = self.auth_client.refresh_token

            session_info.save()

            logger.info('Refresh success')
        
        except:
            logger.exception('Refresh failed')

    def headers(self):
        return {
            'Authorization': 'Bearer {0}'.format(self.auth_client.access_token),
            'Accepts': 'application/json',
            'Content-Type': 'application/json;charset=utf-8',
            'request-Id': str(uuid.uuid4())
        }

    def get_request(self, url):
        response = requests.get(url, headers=self.headers())
        return response

    def post_request(self, url, data):
        response = requests.post(url, headers=self.headers(), data=data)

        if(not response.ok):
            print('Charge Failed, ', response.content)

        return response

    def get_user_info(self):
        request = self.auth_client.get_user_info(access_token=self.auth_client.access_token)

    def charge_create(self, charge_data):
        self.get_user_info()

        response = self.post_request(
            CHARGES_URL,
            json.dumps(charge_data)
        )

        if(not response.ok):
            raise Exception(response.content)

        return response.json()
