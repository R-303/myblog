from django.urls import path

from . import  views
#.代表该目录

app_name="blog"

urlpatterns=[
    path("",views.post_list,name="list"),
    path("post/<int:pk>/",views.post_detail,name="detail"),
]

"""
"" 对应首页；
<int:pk> 会匹配 /post/1/ 里的 1，并把它作为 pk 参数传给视图；
name="list" 给路由起名，模板里可以写 {% url 'blog:list' %}。
"""