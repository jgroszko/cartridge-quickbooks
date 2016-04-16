from django.conf.urls import patterns, include, url

from quickbooks.views import charges, charges_refund

urlpatterns = patterns('',
                       url(r'^charges/$', charges, name="quickbooks_charges"),
                       url(r'^charges/refund/([A-Z0-9]{12})$', charges_refund, name="quickbooks_charges_refund")
)

