from django.contrib import auth
from django.test import TestCase
from  django.urls import reverse
from unicodedata import category

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
from .models import Category,Post,Tag,SiteSetting
#要测的三个模型

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

"""
