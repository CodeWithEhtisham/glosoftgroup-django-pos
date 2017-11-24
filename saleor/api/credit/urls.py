from django.conf.urls import url

from .views import (    
    CreditCreateAPIView,
    CreditListAPIView,
    CreditorsListAPIView,
    CreditUpdateAPIView,    
    )


urlpatterns = [
    url(r'^$', CreditListAPIView.as_view(), name='list-credit'),
    url(r'^search-credit/$', CreditorsListAPIView.as_view(), name='search-credit'),
    url(r'^update-credit/(?P<pk>[0-9]+)/$', CreditUpdateAPIView.as_view(), name='update-credit'),
    url(r'^create-credit/$', CreditCreateAPIView.as_view(), name='create-credit'),
    
]

