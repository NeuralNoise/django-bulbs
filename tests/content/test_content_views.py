from datetime import datetime, timedelta

from django.core.urlresolvers import reverse
from django.test import Client
from elastimorphic.tests.base import BaseIndexableTestCase

from bulbs.content.models import Content, ObfuscatedUrlInfo


class TestContentViews(BaseIndexableTestCase):

    def setUp(self):
        super(TestContentViews, self).setUp()

        self.client = Client()
        self.client.login(username="admin", password="secret")

    def test_base_content_detail_view(self):
        """Test basic functionality of base content view, no tokens."""

        # do a "normal" request for a content object through test view using base view
        content = Content.objects.create()
        response = self.client.get(reverse("published", kwargs={"pk": content.id}))

        # test response is valid
        self.assertTrue(response.status_code, 200)
        self.assertTrue(int(response.content), content.id)

    def test_base_content_detail_view_tokenized_url(self):
        """Test that we can get an article via a /unpublished/<token> style url."""

        # create test content and token
        create_date = datetime.now()
        expire_date = create_date + timedelta(days=3)
        content = Content.objects.create()
        obfuscated_url_info = ObfuscatedUrlInfo.objects.create(
            content=content,
            create_date=create_date.isoformat(),
            expire_date=expire_date.isoformat()
        )
        uuid = obfuscated_url_info.url_uuid

        # attempt to get article via token
        response = self.client.get(reverse("unpublished", kwargs={"token": uuid}))

        # check that everything went well and we got the content id back from the view
        self.assertEqual(response.status_code, 200)
        self.assertEqual(int(response.content), content.id)

    def test_base_content_detail_view_tokenized_url_outside_date_window(self):
        """Test that dates work for /unpublished/<token> style urls."""

        # create test content and token
        create_date = datetime.now() + timedelta(days=3)
        expire_date = create_date + timedelta(days=3)
        content = Content.objects.create()
        obfuscated_url_info = ObfuscatedUrlInfo.objects.create(
            content=content,
            create_date=create_date.isoformat(),
            expire_date=expire_date.isoformat()
        )
        uuid = obfuscated_url_info.url_uuid

        # attempt to get article via token
        response = self.client.get(reverse("unpublished", kwargs={"token": uuid}))

        # expect that we got a 404
        self.assertEqual(response.status_code, 404)

    def test_base_content_detail_view_tokenized_url_invalid(self):
        """Test that we get a 404 when token is invalid."""

        # create test content and token
        create_date = datetime.now()
        expire_date = create_date + timedelta(days=3)
        ObfuscatedUrlInfo.objects.create(
            content=Content.objects.create(),
            create_date=create_date.isoformat(),
            expire_date=expire_date.isoformat()
        )

        # use some invalid token
        response = self.client.get(reverse("unpublished", kwargs={"token": 123}))

        # expect that we got a 404
        self.assertEqual(response.status_code, 404)