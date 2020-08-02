import logging

from django.shortcuts import render, redirect
from django.template import RequestContext
from django.contrib.admin.views.decorators import staff_member_required

from mezzanine.conf import settings

from quickbooks.models import OAuth_Session
from quickbooks.payments import Payments

@staff_member_required
def authorize(request):
    data = {}
    p = Payments(request)

    if('code' in request.GET):
        p.get_auth_token(request.GET['code'],
                         request.GET['realmId'])

    try:
        p.get_user_info()
    except:
        data['authorize_url'] = p.get_auth_url()

    return render(request, 'quickbooks/authorize.html', data)
