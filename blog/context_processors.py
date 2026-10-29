from django.conf import settings

def site_flags(request):
    return {
        "allow_registration":settings.ALLOW_REGISTRATION,
    }