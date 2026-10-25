from django.db import models

# Create your models here.

from django.conf import settings
from django.db import models
from django.utils import timezone

# 模型类就是数据库表的 Python 描述

class Category(models.Model):
    name=models.CharField("名称",max_length=50,unique=True)
    slug=models.SlugField("URL 别名",max_length=60,unique=True)
    created_at=models.DateTimeField("创建时间",auto_now_add=True)

#内部类
    class Meta:
        verbose_name="分类"
        verbose_name_plural=verbose_name
        ordering=["name"]

    def __str__(self):
        return self.name
    # 静态方法


class Tag(models.Model):
    name=models.CharField("名称",max_length=30,unique=True)
    slug=models.SlugField("URL 别名",max_length=40,unique=True)
    created_at=models.DateTimeField("创建时间",auto_now_add=True)

    class Meta:
        verbose_name="标签"
        verbose_name_plural=verbose_name
        ordering=["name"]

    def __str__(self):
        return self.name

#括号里是父类
class PublishedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status=Post.Status.PUBLISHED)
#super调用父类方法

class Post(models.Model):
    class Status(models.TextChoices):
        DRAFT="draft","草稿"
        PUBLISHED="published","已发布"

    title=models.CharField("标题",max_length=120)
    slug=models.SlugField("URL 别名",max_length=140,unique=True)
    summary=models.CharField("摘要",max_length=240,blank=True)
    body=models.TextField("正文")
    category=models.ForeignKey(
        Category,
        verbose_name="分类",
        on_delete=models.PROTECT,
        related_name="posts",
    )
    tags=models.ManyToManyField(
        Tag,
        verbose_name="标签",
        blank=True,
        related_name="posts",
    )
    author=models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="作者",
        on_delete=models.CASCADE,
        related_name="posts",
    )
    status=models.CharField(
        "状态",
        max_length=12,
        choices=Status.choices,
        default=Status.DRAFT,
        db_index=True,
    )

    published_at=models.DateTimeField("发布时间",null=True,blank=True)
    views=models.PositiveIntegerField("浏览量",default=0)
    likes=models.PositiveIntegerField("顶",default=0)
    dislikes=models.PositiveIntegerField("踩",default=0)

    created_at=models.DateTimeField("创建时间",auto_now_add=True)
    updated_at=models.DateTimeField("更新时间",auto_now=True)

    objects=models.Manager()
    published=PublishedManager()

    class Meta:
        verbose_name="文章"
        verbose_name_plural=verbose_name
        ordering=["-published_at","-created_at"]

    def __str__(self):
        return self.title

    def save(self,*args,**kwargs):
        if self.status==self.Status.PUBLISHED and self.published_at is None :
            self.published_at=timezone.now()
        super().save(*args,**kwargs)
    #保存时间

"""
几个关键点，先看一遍：
- CharField 是短文本，必须给 max_length；TextField 是长正文。
- SlugField 是 URL 里用的短标识，比如 first-post。中文标题自动生成的 slug 可能为空，后台里要手动填英文。
- ForeignKey 是“一对多”：一个分类有多篇文章。
- ManyToManyField 是“多对多”：一篇文章可以有多个标签，一个标签也可以属于多篇文章。
- on_delete=models.PROTECT：分类下面还有文章时，不允许删分类。
- on_delete=models.CASCADE：删除作者时，他的文章也会被删除。
- related_name="posts"：以后可以写 category.posts.all()、tag.posts.all()。
- Post.objects 查全部文章，Post.published 只查已发布文章。
- save() 里那段逻辑：第一次把文章设为已发布时，自动填发布时间。
"""

class Comment(models.Model):
    post=models.ForeignKey(
        Post,
        verbose_name="文章",
        on_delete=models.CASCADE,
        related_name="comments",
    )
    nickname=models.CharField("昵称",max_length=30)
    email=models.EmailField("邮箱")
    body=models.TextField("内容",max_length=2000)
    created_at=models.DateTimeField("创建时间",auto_now_add=True)

    class Meta:
        verbose_name="评论"
        verbose_name_plural=verbose_name
        ordering=["created_at"]

    def __str__(self):
        return f"{self.nickname} 评论 《{self.post.title}》"
"""
增加评论类
related_name="comments" 以后可以写 post.comments.all()。
"""

class Vote(models.Model):
    post=models.ForeignKey(
        Post,
        verbose_name="文章",
        on_delete=models.CASCADE,
        related_name="votes",
    )
    session_key=models.CharField(
        "浏览器标识",
        max_length=64,
        db_index=True,
    )
    value=models.SmallIntegerField(
        "票值",
        choices=[(1,"顶"),(-1,"踩")],
    )
    created_at=models.DateTimeField("创建时间",auto_now_add=True)

    class Meta:
        verbose_name="投票"
        verbose_name_plural=verbose_name
        constraints=[
            models.UniqueConstraint(
                fields=["post","session_key"],
                name="unique_post_vote",
            )
        ]

        def __str__(self):
            return f"{self.post.title} - {self.get_value_display()}"
"""
UniqueConstraint 是最后一道保险：同一个浏览器对同一篇文章，数据库层面也只允许一条投票记录。
"""

class SiteSetting(models.Model):
    """  全局站点设置，数据库只保留一行"""

    site_name=models.CharField("站点名称",max_length=80,default="我的博客")
    page_size=models.PositiveSmallIntegerField("每页文章数",default=5)
    updated_at=models.DateTimeField("更新时间",auto_now=True)

    class Meta:
        verbose_name="站点设置"
        verbose_name_plural=verbose_name

    def __str__(self):
        return self.site_name

    def save(self,*args,**kwargs):
# 强制主键为 1，避免后台误建多行全局设置。
        self.pk=1
        super().save(*args,**kwargs)

    @classmethod
    def load(cls):
        return cls.objects.get_or_create(pk=1)[0]


class Attachment(models.Model):
    post=models.ForeignKey(
        Post,
        verbose_name="文章",
        on_delete=models.CASCADE,
        related_name="attachments",
    )
    image=models.ImageField(
        "图片",
        upload_to="blog/attachments/%Y/%m/",
    )
    title=models.CharField("标题",max_length=80,blank=True)
    created_at=models.DateTimeField("创建时间",auto_now_add=True)

    class Meta:
        verbose_name="图片附件",
        verbose_name_plural=verbose_name,
        ordering=["-created_at"]

    def __str__(self):
        return self.title or self.image.name
    