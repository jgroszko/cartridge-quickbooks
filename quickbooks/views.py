from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.admin.views.decorators import staff_member_required

from mezzanine.conf import settings

from quickbooks.models import OAuth_Session
from quickbooks.payments import Payments

SESSION_ACCESS_TOKEN = 'qb_oauth_access_token'
SESSION_ACCESS_SECRET = 'qb_oauth_access_secret'

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
        data['charges'] = p.charges()

    else:
        data['authorize_url'] = p.get_auth_url(request.build_absolute_uri())

        request.session[SESSION_ACCESS_TOKEN] = p.access_token
        request.session[SESSION_ACCESS_SECRET] = p.access_secret

    return render_to_response('quickbooks/charges.html',
                              data,
                              context_instance=RequestContext(request))
