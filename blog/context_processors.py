from django.conf import settings
#让模板能拿到站点配置
from .models import SiteSetting

def site_flags(request):
    site=SiteSetting.load()
    return {
        "allow_registration":settings.ALLOW_REGISTRATION,
        "site":site,
    }