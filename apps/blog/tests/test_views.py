from smeuhoverride.tests import BaseTestCase
from django.contrib.contenttypes.models import ContentType
from blog.models import Post


class TestBlog(BaseTestCase):

    def create_post(self):
        return Post.objects.create(title=u"A Neat Title", slug="the-slug",
                                   author=self.me, body="Some content")

    def test_view_post(self):
        self.create_post()
        response = self.client.get("/bob/blog/the-slug")
        self.assertContains(response, "Some content")

    def test_view_source(self):
        self.create_post()
        response = self.client.get("/bob/blog/the-slug/source")
        self.assertContains(response, "Some content")

    def test_blogs_feed(self):
        self.create_post()
        response = self.client.get("/feeds/blogs/")
        self.assertEqual(response.status_code, 200)

    def test_user_blog_feed(self):
        self.create_post()
        response = self.client.get("/{}/blog/feed/".format(self.me.username))
        self.assertEqual(response.status_code, 200)

    def test_comment_post(self):
        post = self.create_post()
        post_type = ContentType.objects.get(app_label="blog", model="post")
        url = "/comments/comment/{}/{}/".format(post_type.pk, post.pk)
        long_comment = "a" * 1001

        response = self.client.post(url, {
            "comment": long_comment,
            "next": "/bob/blog/the-slug",
        })

        self.assertEqual(
            response['location'],
            "http://testserver/bob/blog/the-slug#comment_1"
        )

    def test_comment_post_too_long(self):
        post = self.create_post()
        post_type = ContentType.objects.get(app_label="blog", model="post")
        url = "/comments/comment/{}/{}/".format(post_type.pk, post.pk)
        very_long_comment = "a" * 100001

        with self.settings(DEFAULT_MAX_COMMENT_LENGTH=10):
            response = self.client.post(url, {
                "comment": very_long_comment,
                "next": "/bob/blog/the-slug",
            })
            self.assertContains(response, u"100000 caractères")
