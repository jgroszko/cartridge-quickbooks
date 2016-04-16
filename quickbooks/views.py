from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.admin.views.decorators import staff_member_required

from mezzanine.conf import settings

from quickbooks.models import OAuth_Session
from quickbooks.payments import Payments

SESSION_ACCESS_TOKEN = 'qb_oauth_access_token'
SESSION_ACCESS_SECRET = 'qb_oauth_access_secret'

def _reauthorize(request, payments):
    authorize_url = payments.get_auth_url(request.build_absolute_uri())

    request.session[SESSION_ACCESS_TOKEN] = payments.access_token
    request.session[SESSION_ACCESS_SECRET] = payments.access_secret

    return authorize_url

@staff_member_required
def charges(request):
    data = {}
    p = Payments(
        access_token = request.session.get(SESSION_ACCESS_TOKEN),
        access_secret = request.session.get(SESSION_ACCESS_SECRET))

    if('oauth_verifier' in request.GET):
        p.get_auth_session(request.GET['oauth_verifier'],
                           request.GET['realmId'])

    if(hasattr(p, 'session')):
        try:
            data['charges'] = p.charges()
        except:
            data['authorize_url'] = _reauthorize(request, p)

    else:
        data['authorize_url'] = _reauthorize(request, p)

    return render_to_response('quickbooks/charges.html',
                              data,
                              context_instance=RequestContext(request))
