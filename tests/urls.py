from bulbs.content.views import ContentListView

from django.conf.urls import patterns, url, include


urlpatterns = patterns("",
    url(r"^content_list_one\.html", ContentListView.as_view(template_name="testapp/content_list.html")),
    url(r"^videos/", include("bulbs.videos.urls"))
)
