from django.conf.urls import url
from django.contrib.auth.decorators import login_required, permission_required

from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
        url(r'^$', views.sales_reports, name='sales_reports'),
        url(r'^product_reports/$', views.product_reports, name='products_reports'),
        url(r'^purchases_reports/$', views.purchases_reports, name='purchases_reports'),
        url(r'^balancesheet_reports/$', views.balancesheet_reports, name='balancesheet_reports'),
        url(r'^chart/$', views.get_dashboard_data, name='chart'), 
        # url(r'^$', permission_required('userprofile.view_user', login_url='account_login'))     
]

if settings.DEBUG:
    # urlpatterns += [ url(r'^static/(?P<path>.*)$', serve)] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)