from django.shortcuts import get_object_or_404, render

from .models import Post

def post_list(request):
    posts=Post.published.all()
    return render(request,"blog/post_list.html",{"posts":posts})


def post_detail(request,pk):
    post=get_object_or_404(Post.published,pk=pk)
    return render(request,"blog/post_detail.html",{"post":post})

"""
两个视图分别做两件事：
- post_list：查出所有已发布文章，交给列表模板；
- post_detail：按主键查一篇文章，找不到就返回 404。
这里用 Post.published 而不是 Post.objects，
所以草稿不会出现在前台。

"""
