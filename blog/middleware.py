from urllib.parse import urlencode

from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse

class PrivateSiteMiddleware:
    def __init__(self,get_response):
        self.get_response=get_response

    def __call__(self,request):
        if not settings.PRIVATE_SITE or request.user.is_authenticated:
            return self.get_response(request)

        public_prefixes=(
            reverse("blog:login"),
            "/healthz/",
            "/admin/",
            "/static/",
            "/media/",
        )

        if any(
            request.path.startswith(prefix)
            for prefix in public_prefixes
        ):
            return self.get_response(request)

        login_url=reverse("blog:login")
        query=urlencode({"next": request.get_full_path()})
        return redirect(f"{login_url}?{query}")
"""
中间件
它做的事情是：
- 站点是私密的，且用户没登录；
- 除了登录页、健康检查、后台、静态文件和媒体文件，其他地址全部跳转登录页；
- 登录成功后可以回到原来的文章地址。
"""