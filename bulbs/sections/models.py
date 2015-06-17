from django.conf import settings
from django.db import models
from django.db.models.signals import pre_delete
from django.template.defaultfilters import slugify

from bulbs.content.custom_search import custom_search_model
from bulbs.content.models import Content
from elasticsearch import Elasticsearch
from djbetty import ImageField
from json_field import JSONField


es = Elasticsearch(settings.ES_URLS)


class Section(models.Model):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, blank=True, editable=True, unique=True)
    description = models.TextField(default="", blank=True)
    embed_code = models.TextField(default="", blank=True)
    section_logo = ImageField(null=True, blank=True)
    twitter_handle = models.CharField(max_length=255, blank=True)
    promoted = models.BooleanField(default=False)
    query = JSONField(default={}, blank=True)

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        """Saving ensures that the slug, if not set, is set to the slugified name."""

        if not self.slug:
            self.slug = slugify(self.name)

        if self.query and self.query != {}:
            self._save_percolator()

        return super(Section, self).save(*args, **kwargs)

    def _save_percolator(self):
        """saves the query field as an elasticsearch percolator
        """
        index = Content.search_objects.mapping.index
        query_filter = self.get_content().to_dict()

        q = {}

        if "query" in query_filter:
            q = {"query": query_filter.get("query", {})}
        else:
            return

        es.index(
            index=index,
            doc_type=".percolator",
            body=q,
            id=self.es_id
        )

    def _delete_percolator(self):
        index = Content.search_objects.mapping.index
        es.delete(index=index, doc_type=".percolator", id=self.es_id, refresh=True, ignore=404)

    def get_content(self):
        """performs es search and gets content objects
        """
        if "query" in self.query:
            q = self.query["query"]
        else:
            q = self.query
        search = custom_search_model(Content, q, field_map={
            "tag": "tags.slug",
            "content-type": "_type",
            })
        return search

    @property
    def es_id(self):
        return "section.{}".format(self.id)

    @property
    def contents(self):
        """Caches the results of the get_content method    
        """
        if not hasattr(self, "_content"):
            self._content = self.get_content()
        return self._content


def remove_percolator(sender, instance, *args, **kwargs):
    instance._delete_percolator()

pre_delete.connect(remove_percolator, sender=Section)