from django.conf.urls import include, url

from quickbooks.views import authorize

urlpatterns = [
                       url(r'^authorize/$', authorize, name="quickbooks_authorize"),
]
