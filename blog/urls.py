from django.urls import path

from . import  views
#.代表该目录

app_name="blog"

urlpatterns=[
    path("",views.post_list,name="list"),
    path("post/<int:pk>/",views.post_detail,name="detail"),
    path("category/<slug:slug>/",views.category_posts,name="category"),
    path("tag/<slug:slug>/",views.tag_posts,name="tag"),
    path("archive/<int:year>/<int:month>/",views.archive_posts,name="archive"),
    path("post/<int:pk>/comment/",views.add_comment,name="comment"),
    path(
        "post/<int:pk>/vote/<str:value>/",
        views.vote,
        name="vote",
    ),
    path("account/register/",views.register,name="register"),
    path(
        "account/login/",
        views.BlogLoginView.as_view(),
        name="login",
    ),
    path(
        "account/logout/",
        views.BlogLogoutView.as_view(),
        name="logout"
    ),
]

"""
路由文件
"" 对应首页；
<int:pk> 会匹配 /post/1/ 里的 1，并把它作为 pk 参数传给视图；
name="list" 给路由起名，模板里可以写 {% url 'blog:list' %}。

对应地址分别是
/category/python/
/tag/django/
/archive/2026/10/
"""

# Django 6.1 的 LogoutView 只接受 POST，所以下一步导航栏里退出必须用表单。