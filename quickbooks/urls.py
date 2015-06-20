from django.conf.urls import patterns, include, url

from quickbooks.views import charges

urlpatterns = patterns('',
                       url(r'^charges/$', charges, name="quickbooks_charges"),
)

