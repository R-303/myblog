"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include,path
from django.conf import settings
from django.conf.urls.static import static
from health import health

urlpatterns = [
    path("healthz/",health,name="health"),
    path('admin/', admin.site.urls),
    path("",include("blog.urls")),
]

# include("blog.urls") 的意思是：除了 /admin/，其他路径都交给 blog 应用继续匹配。

if settings.DEBUG:
    urlpatterns +=static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )
# 这只用于开发环境。生产环境由 Nginx 提供媒体文件。