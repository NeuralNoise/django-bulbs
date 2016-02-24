from rest_framework import filters, routers, viewsets
from rest_framework.permissions import IsAdminUser

from .filters import SpecialCoverageFilter
from .models import SpecialCoverage
from .serializers import SpecialCoverageSerializer


class SpecialCoverageViewSet(viewsets.ModelViewSet):
    serializer_class = SpecialCoverageSerializer
    filter_backends = (
        SpecialCoverageFilter,
        filters.SearchFilter,
        filters.OrderingFilter,)
    boolean_fields = ("promoted",)
    search_fields = (
        "name",
        "description",
        "campaign__campaign_label",
        "campaign__sponsor_name"
    )
    ordering_fields = (
        "name",
        "active",
        "promoted",
        "campaign__campaign_label",
        "campaign__sponsor_name"
    )
    paginate_by = 10
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        return SpecialCoverage.objects.all()

api_v1_router = routers.DefaultRouter()
api_v1_router.register(
    r"special-coverage",
    SpecialCoverageViewSet,
    base_name="special-coverage")
