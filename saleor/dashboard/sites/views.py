from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.http import HttpResponse
from django.utils.translation import ugettext_lazy as _
from django.db import DatabaseError
from django.views.decorators.csrf import csrf_exempt
from .forms import SiteSettingForm
from ..views import staff_member_required
from ...site.models import AuthorizationKey, SiteSettings, Files
from ...site.utils import get_site_settings_from_request
import json
import socket

from structlog import get_logger

logger = get_logger(__name__)


@staff_member_required
# @permission_decorator('site.view_sitesettings')
def index(request):
    settings = get_site_settings_from_request(request)
    return redirect('dashboard:site-update', site_id=settings.pk)


@staff_member_required
# @permission_decorator('site.change_sitesettings')
def update(request, site_id=None):
    site = get_object_or_404(SiteSettings, pk=site_id)
    form = SiteSettingForm(request.POST or None, instance=site)
    authorization_qs = AuthorizationKey.objects.filter(site_settings=site)
    if all([form.is_valid()]):
        site = form.save()

        messages.success(request, _('Updated site %s') % site)
        return redirect('dashboard:site-update', site_id=site.id)
    ip_address, server_ip = get_ip_address()
    ctx = {'site': site, 'form': form, 'ip_address': ip_address}
    return TemplateResponse(request, 'dashboard/sites/detail.html', ctx)


@staff_member_required
# @permission_decorator('site.change_sitesettings')
def update_settings(request, site_id=None):
    if request.method == 'POST':
        site = get_object_or_404(SiteSettings, pk=site_id)
        if request.POST.get('sms_username'):
            site.sms_gateway_username = request.POST.get('sms_username')
            print (site.sms_gateway_username)
        if request.POST.get('sms_api_key'):
            site.sms_gateway_apikey = request.POST.get('sms_api_key')
            print (site.sms_gateway_apikey)
        if request.POST.get('company_name'):
            site.name = request.POST.get('company_name')
        if request.POST.get('wholesale_name'):
            site.wholesale_name = request.POST.get('wholesale_name')
        if request.POST.get('company_email'):
            site.email = request.POST.get('company_email')
        if request.POST.get('show_transfer'):
            site.show_transfer = True
        else:
            site.show_transfer = False
        if request.POST.get('loyalty_point_equiv'):
            site.loyalty_point_equiv = request.POST.get('loyalty_point_equiv')
        if request.POST.get('opening_time'):
            site.opening_time = request.POST.get('opening_time')
        if request.POST.get('closing_time'):
            site.closing_time = request.POST.get('closing_time')
        if request.FILES.get('image'):
            site.image = request.FILES.get('image')
        if request.POST.get('max_credit_date'):
            site.max_credit_date = request.POST.get('max_credit_date')
        site.save()
        return HttpResponse('success')
    return HttpResponse('Invalid method')


@csrf_exempt
def add_sitekeys(request):
    if request.method == 'POST':
        keyfiles = request.POST.get('lic_key').strip()

        if keyfiles:
            try:
                keyfile, check = keyfiles.split('###')

                keyfile = keyfile.replace('\r', '').replace('\n', '')
                check = check.replace('\r', '').replace('\n', '')

            except Exception as e:
                result = json.dumps({'message': 'Invalid License Key', 'status': 500})
                return HttpResponse(result, content_type="application/json")
            try:
                Files.objects.all().delete()
            except DatabaseError or BaseException:
                result = json.dumps({'message': 'Failed to Add license', 'status': 500})
                return HttpResponse(result, content_type="application/json")

            new_key = Files.objects.create(
                file=keyfile,
                check=check
            )
        else:
            logger.info('License Key is empty ')
            result = json.dumps({'message': 'Empty Key license', 'status': 500})
            return HttpResponse(result, content_type="application/json")

        try:
            new_key.save()
        except DatabaseError or  BaseException:
            logger.info('Error when saving ')

        if new_key.id:
            result = json.dumps({'message': 'success', 'status': 200})
            return HttpResponse(result, content_type="application/json")
        return HttpResponse('Error: Not saved')

    return HttpResponse('Invalid request')


def removenewline(data):
    for n, line in enumerate(data):
        if line.startswith("line"):
            data[n] = "\n" + line.strip()
        else:
            data[n] = line.strip()
    return ''.join(data)


def test(request):
    print ('testKeys')
    return HttpResponse('success 123')


def get_ip_address():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))

        ip_address = "http://"+str(s.getsockname()[0])+":8000"
        server_ip = str(s.getsockname()[0])
        s.close()
    except Exception as e:
        ip_address = "http://127.0.0.1:8000"
        server_ip = "http://127.0.0.1"

    return ip_address, server_ip
