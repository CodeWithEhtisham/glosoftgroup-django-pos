from django.conf.urls import url
from django.contrib.auth.decorators import login_required, permission_required

from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
        url(r'^$', views.users, name='supplier'),
        # url(r'^$', permission_required('userprofile.view_user', login_url='account_login')
        #     (views.users), name='users'),
        url(r'^add/$', permission_required('userprofile.add_user', login_url='account_login')
            (views.user_add), name='supplier-add'),
        url(r'^address/add/(?P<pk>[0-9]+)/$', views.address_add, name='address-add'),
        url(r'^supplier_process/$', views.user_process, name='supplier_process'),
        url(r'^detail/(?P<pk>[0-9]+)/$', views.user_detail, name='supplier-detail'),
        url(r'user_trail/$', views.user_trails, name='user_trail'),
        url(r'^delete/(?P<pk>[0-9]+)/$', views.user_delete, name='supplier-delete'),
        url(r'^delete/contact/(?P<pk>[0-9]+)/$', views.contact_delete, name='contact-delete'),
        url(r'^refresh/contact/(?P<pk>[0-9]+)/$', views.refresh_contact, name='refresh-contact'),
        url(r'^edit/(?P<pk>[0-9]+)/$', views.user_edit, name='supplier-edit'),
        url(r'^supplier_update(?P<pk>[0-9]+)/$', views.user_update, name='supplier-update'),
        url(r'^user_assign_permission/$', views.user_assign_permission, name='user_assign_permission'),
        # url(r'^add/', permission_required('userprofile.add_user', login_url='account_login')(views.user_add)),
        
]

if settings.DEBUG:
    # urlpatterns += [ url(r'^static/(?P<path>.*)$', serve)] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)