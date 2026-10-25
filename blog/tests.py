import tempfile

from django.contrib import auth
from django.test import TestCase
from  django.urls import reverse
from unicodedata import category

from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import connection
from django.test.utils import CaptureQueriesContext

# Create your tests here.
"""
花 20 分钟给模型补测试。
测试的作用不是“证明我写对了”，
而是以后改代码时，能立刻发现有没有把原来的功能弄坏。
"""

from django.contrib.auth import get_user_model
#get_user_model()：拿到当前项目使用的用户模型，不直接写死 User，以后换用户模型也不用改测试
from django.db.models.deletion import ProtectedError
#ProtectedError：当 on_delete=PROTECT 阻止删除时，Django 抛出的异常。
from django.test import TestCase
# TestCase：Django 的测试基类，会创建临时测试数据库，跑完自动销毁
from .models import Category,Post,Tag,SiteSetting,Comment,Vote,Attachment
#要测的三个模型
from .views import cached_sidebar_context

#把所有模型测试放在一个类里。测试运行器会自动找到这个类，以及里面所有以 test_ 开头的方法。
class PostModelTests(TestCase):
    def setUp(self):
        self.user=get_user_model().objects.create_user(username="tester")
        self.category=Category.objects.create(name="Python",slug="python")
        self.tag=Tag.objects.create(name="Django",slug="django")

    def create_post(self,**kwargs):
        data={
            "title":"测试文章",
            "slug":"test-post",
            "body":"测试正文",
            "category":self.category,
            "author":self.user,
        }
        data.update(kwargs)
        return Post.objects.create(**data)
    #**data 里的两个星号是 Python 的“字典解包”语法

    def test_published_manager_hides_drafts(self):
        self.create_post(status=Post.Status.DRAFT)
        self.assertEqual(Post.published.count(),0)

    def test_publishing_sets_published_at(self):
        post=self.create_post(status=Post.Status.PUBLISHED)
        self.assertIsNotNone(post.published_at)   #发布时间
        self.assertEqual(Post.published.count(),1)

    def test_category_with_posts_cannot_be_deleted(self):
        self.create_post()
        with self.assertRaises(ProtectedError):
            self.category.delete()


"""
这三个测试分别验证：
1. 草稿不会出现在 Post.published 里；
2. 文章第一次设为已发布时，published_at 会自动填上；
3. 分类下面还有文章时，不能直接删除分类（PROTECT 生效）。
TestCase 会创建一个临时测试数据库，跑完自动销毁，不会动你后台那篇文章。

setUp() 会在每个 test_ 方法运行前执行一次。可以理解成“每次考试前先把文具摆好”：
- 建一个测试用户；
- 建一个 Python 分类；
- 建一个 Django 标签。
每个测试方法之间有事务隔离，一个测试建的数据不会污染下一个测试。

先创建一篇关联到该分类的文章；
然后尝试删除分类；
因为 on_delete=PROTECT，Django 应该抛出 ProtectedError；
assertRaises(ProtectedError) 的意思是“我期望这里抛这个异常”。如果没抛，测试反而失败。




这段当成“测试的骨架”记住
setUp()       准备数据
test_xxx()    做一件事
assert...     检查结果
TestCase      自动建临时数据库、自动隔离

"""

class PostViewTests(TestCase):
    def setUp(self):
        self.user=get_user_model().objects.create_user(username="viewer")
        self.category=Category.objects.create(name="Python",slug="python")
        self.post=Post.objects.create(
            title="博客的第一页",
            slug="first-page",
            summary="列表和详情已经接通",
            body="这是详情页正文",
            category=self.category,
            author=self.user,
            status=Post.Status.PUBLISHED,
        )
        self.tag=Tag.objects.create(name="Django",slug="django")
        self.post.tags.add(self.tag)

    def test_list_shows_only_published_posts(self):
        Post.objects.create(
            title="不能出现的草稿",
            slug="hidden-draft",
            category=self.category,
            author=self.user,
        )
        response=self.client.get(reverse("blog:list"))
        self.assertContains(response,"博客的第一页")
        self.assertNotContains(response,"不能出现的草稿")

    def test_detail_renders_and_counts_view(self):
        response=self.client.get(reverse("blog:detail",args=[self.post.pk]))
        self.post.refresh_from_db()
        self.assertEqual(response.status_code,200)
        self.assertContains(response,"这是详情页正文")
        self.assertEqual(self.post.views,1)

    def test_draft_detail_returns_404(self):
        draft=Post.objects.create(
            title="草稿",
            slug="draft-post",
            body="草稿正文",
            category=self.category,
            author=self.user,
        )#初始化，构造测试案例
        response=self.client.get(reverse("blog:detail",args=[draft.pk]))
        self.assertEqual(response.status_code,404)   #判断是否相同


    def test_category_page_shows_post(self):
        response=self.client.get(
          reverse("blog:category",args=[self.category.slug])
        )
        self.assertContains(response,self.post.title)
        self.assertContains(response,f"分类：{self.category.name}")

    def test_tag_page_shows_post(self):
        response=self.client.get(
            reverse("blog:tag",args=[self.tag.slug])
        )
        self.assertContains(response,self.post.title)
        self.assertContains(response,"标签：Django")

    def test_archive_page_shows_post(self):
        year=self.post.published_at.year
        month=self.post.published_at.month
        response=self.client.get(
            reverse("blog:archive",args=[year,month])
        )
        self.assertContains(response,self.post.title)
        self.assertContains(response,f"{year} 年 {month} 月归档")
        # 用self.post.published_at.year / month  不写死 2026 和 10，以后换日期测试也不会坏

    def test_list_paginates_posts(self):
        SiteSetting.objects.update_or_create(
            pk=1,
            defaults={"page_size":1},
        )
        Post.objects.create(
            title="第二篇文章",
            slug="second-post",
            body="第二篇正文",
            category=self.category,
            author=self.user,
            status=Post.Status.PUBLISHED,
        )
        response=self.client.get(reverse("blog:list"))
        self.assertEqual(len(response.context["page_obj"]),1)
        self.assertTrue(response.context["page_obj"].has_next())

    def test_sidebar_contains_latest_post_and_category(self):
        response=self.client.get(reverse("blog:list"))
        self.assertIn(self.post,response.context["latest_posts"])
        self.assertIn(self.category,response.context["sidebar_categories"])


    def test_detail_renders_markdown_and_codehilite(self):
        self.post.body="## 标题\n\n```python\nprint('hello')\n```"
        self.post.save()

        response=self.client.get(
            reverse("blog:detail",args=[self.post.pk])
        )

        self.assertContains(response,"<h2>标题</h2>")
        self.assertContains(response,"codehilite")
        self.assertContains(response,"print")

    def test_detail_renders_comment_form(self):
        response=self.client.get(
            reverse("blog:detail",args=[self.post.pk])
        )
        self.assertContains(response,'name="nickname"')
        self.assertContains(response,'name="email"')
        self.assertContains(response,'name="body"')

    def test_comment_can_be_created_and_is_escaped(self):
        response=self.client.post(
            reverse("blog:comment",args=[self.post.pk]),
            {
                "nickname":"小易",
                "email":"yi@example.com",
                "body":"<script>alert(1)</script>这条评论很有用。",
            },
            follow=True,
        )
        self.assertContains(response,"已提交")
        self.assertContains(response,"&lt;script&gt;")
        self.assertNotContains(response,"<script>alert(1)</script>")
        self.assertEqual(self.post.comments.count(),1)

    def test_invalid_comment_is_not_saved(self):
        self.client.post(
            reverse("blog:comment",args=[self.post.pk]),
            {
                "nickname":"",
                "email":"bad-email",
                "body":"",
            },
        )
        self.assertEqual(Comment.objects.count(),0)

    def test_like_can_only_be_voted_once_per_session(self):
        url=reverse("blog:vote",args=[self.post.pk,"like"])

        self.client.post(url)
        self.client.post(url)

        self.post.refresh_from_db()
        self.assertEqual(self.post.likes,1)
        self.assertEqual(Vote.objects.count(),1)

    def test_dislike_increments_dislikes(self):
        self.client.post(
            reverse("blog:vote",args=[self.post.pk,"dislike"])
        )

        self.post.refresh_from_db()
        self.assertEqual(self.post.dislikes,1)

    def test_vote_requires_post(self):
        response=self.client.get(
            reverse("blog:vote",args=[self.post.pk,"like"])
        )
        self.assertEqual(response.status_code,405)
"""
这三个测试验证：
- 首页只显示已发布文章；
- 详情页能渲染，并且浏览量加 1；
- 草稿通过详情 URL 访问时返回 404。

reverse("blog:list") 的作用是：把 URL 名字翻译成真实路径
response 不是“接收创造的数据”，而是服务器返回的响应对象
assertIn(self.post, ...) 检查测试文章确实出现在里面

def test_detail_renders_markdown_and_codehilite(self):
这个测试验证三件事：
- Markdown 标题变成了 HTML 标题；
- 代码块有 .codehilite 容器；
- 代码内容仍然存在。

def test_vote_requires_post(self):
第三个测试验证：直接访问投票 URL（GET）应该被拒绝，投票只能通过表单 POST。
"""

class AuthTests(TestCase):
    def test_register_creates_user_and_logs_in(self):
        response=self.client.post(
            reverse("blog:register"),
            {
                "username":"new_edu_user",
                "email":"new@edu.com",
                "password1":"strong_password_123",
                "password2":"strong_password_123",
            },
            follow=True,
        )

        self.assertEqual(
            get_user_model().objects.filter(username="new_edu_user").count(),
            1,
        )
        self.assertTrue(response.context["user"].is_authenticated)
        self.assertContains(response,"注册成功")

    def test_login_and_logout(self):
        get_user_model().objects.create_user(
            username="alice",
            password="strong-password-123",
        )

        response=self.client.post(
            reverse("blog:login"),
            {
                "username":"alice",
                "password":"strong-password-123",
            },
            follow=True,
        )

        self.assertTrue(response.context["user"].is_authenticated)
        self.assertContains(response,"alice")

        response=self.client.post(
            reverse("blog:logout"),
            follow=True,
        )
        self.assertFalse(response.context["user"].is_authenticated)

    def test_logout_rejects_get(self):
        response=self.client.get(reverse("blog:logout"))
        self.assertEqual(response.status_code,405)
# 现在测试总数应该从 18 增加到 21。


class SearchTests(TestCase):
    def setUp(self):
        self.user=get_user_model().objects.create_user(
            username="searcher"
        )
        self.category=Category.objects.create(
            name="Python",
            slug="python",
        )
        self.post=Post.objects.create(
            title="Django 搜索测试",
            slug="search-post",
            summary="关于搜索的文章",
            body="这里是 Django 正文。",
            category=self.category,
            author=self.user,
            status=Post.Status.PUBLISHED,
        )

    def test_search_finds_published_post(self):
        response=self.client.get(
            reverse("blog:list"),
            {"q":"Django"},
        )
        self.assertContains(response,"Django 搜索测试")
        self.assertContains(response,"搜索： Django")

    def test_search_does_not_show_draft(self):
        Post.objects.create(
            title="Django 草稿",
            slug="django-draft",
            body="Django 草稿正文",
            category=self.category,
            author=self.user,
        )
        response=self.client.get(
            reverse("blog:list"),
            {"q":"Django"},
        )
        self.assertContains(response,"Django 搜索测试")
        self.assertNotContains(response,"Django 草稿")

    def test_search_pagination_preserves_query(self):
        SiteSetting.objects.update_or_create(
            pk=1,
            defaults={"page_size":1},
        )
        Post.objects.create(
            title="Django 第二篇",
            slug="django-second",
            body="Django 第二篇正文",
            category=self.category,
            author=self.user,
            status=Post.Status.PUBLISHED,
        )

        response=self.client.get(
            reverse("blog:list"),
            {"q":"Django"},
        )

        self.assertEqual(len(response.context["page_obj"]),1)
        self.assertTrue(response.context["page_obj"].has_next())
        self.assertContains(response,"q=Django")


class AdminStatsTests(TestCase):
    def test_changelist_shows_blog_stats(self):
        user=get_user_model().objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="strong-password-123",
        )
        category=Category.objects.create(
            name="Python",
            slug="python",
        )
        Post.objects.create(
            title="已发布文章",
            slug="stats-published",
            body="正文",
            category=category,
            author=user,
            status=Post.Status.PUBLISHED,
            views=4,
        )
        Post.objects.create(
            title="草稿文章",
            slug="stats-draft",
            body="草稿正文",
            category=category,
            author=user,
            views=2,
        )

        self.client.force_login(user)
        response=self.client.get(
            reverse("admin:blog_post_changelist")
        )

        self.assertEqual(response.status_code,200)
        self.assertContains(response,"博客统计")

        stats=response.context["blog_stats"]
        self.assertEqual(stats["total"],2)
        self.assertEqual(stats["published"],1)
        self.assertEqual(stats["draft"],1)
        self.assertEqual(stats["views"],6)
        self.assertEqual(stats["average_views"],3.0)


class AttachmentTests(TestCase):
    def test_attachment_uploads_and_render(self):
        user=get_user_model().objects.create_user(username="uploader")
        category=Category.objects.create(name="Python",slug="python")
        post=Post.objects.create(
            title="带图片的文章",
            slug="post-width-image",
            body="正文",
            category=category,
            author=user,
            status=Post.Status.PUBLISHED,
        )

        png=bytes.fromhex(
            "89504e470d0a1a0a0000000d494844520000000100000001"
            "08060000001f15c4890000000a49444154789c6300010000050001"
        )#这段是一张 1×1 像素 PNG 图片的二进制内容，用十六进制写出来了 它把每两个十六进制字符转成一个字节  png 变量里装的不是哈希值，而是一张真正的 PNG 图片的原始字节

        with tempfile.TemporaryDirectory() as root:
            with self.settings(MDIA_ROOT=root):
                attachment=Attachment.objects.create(
                    post=post,
                    title="结构图",
                    image=SimpleUploadedFile(
                        "diagram.png",
                        png,
                        content_type="image/png",
                    ),
                )

                response=self.client.get(
                    reverse("blog:detail",args=[post.pk])
                )

                self.assertContains(response,"结构图")
                self.assertContains(response,attachment.image.url)

class SidebarCacheTests(TestCase):
    def test_cached_sidebar_reuses_result(self):
        cache.clear()

        with CaptureQueriesContext(connection) as first:
            cached_sidebar_context()

        with CaptureQueriesContext(connection) as second:
            cached_sidebar_context()

        self.assertLess(
            len(second.captured_queries),
            len(first.captured_queries),
        )