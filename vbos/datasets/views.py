import django_filters.rest_framework
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_control
from drf_excel.mixins import XLSXFileMixin
from drf_excel.renderers import XLSXRenderer
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework_gis.filters import InBBoxFilter
from rest_framework_gis.pagination import GeoJsonPagination

from vbos.datasets.filters import (
    PMTilesDatasetFilter,
    RasterDatasetFilter,
    TabularDatasetFilter,
    TabularItemFilter,
    VectorDatasetFilter,
    VectorItemFilter,
)

from .models import (
    AreaCouncil,
    Cluster,
    PMTilesDataset,
    Province,
    RasterDataset,
    TabularDataset,
    TabularItem,
    VectorDataset,
    VectorItem,
)
from .pagination import StandardResultsSetPagination
from .serializers import (
    AreaCouncilSerializer,
    ClusterSerializer,
    PMTilesDatasetSerializer,
    ProvinceSerializer,
    RasterDatasetSerializer,
    TabularDatasetSerializer,
    TabularItemExcelSerializer,
    TabularItemSerializer,
    VectorDatasetSerializer,
    VectorItemSerializer,
)


class CachedAPIViewMixin:
    """
    Mixin to add cache headers to list and retrieve API views
    """

    @method_decorator(cache_control(public=True, max_age=86400))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @method_decorator(cache_control(public=True, max_age=86400))
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


class ClusterListView(CachedAPIViewMixin, ListAPIView):
    queryset = Cluster.objects.all()
    serializer_class = ClusterSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = StandardResultsSetPagination


class ProvinceListView(CachedAPIViewMixin, ListAPIView):
    queryset = Province.objects.all()
    serializer_class = ProvinceSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = GeoJsonPagination


class AreaCouncilListView(CachedAPIViewMixin, ListAPIView):
    serializer_class = AreaCouncilSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = GeoJsonPagination

    def get_queryset(self):
        return AreaCouncil.objects.filter(
            province__name__iexact=self.kwargs.get("province")
        ).select_related("province")


class RasterDatasetListView(CachedAPIViewMixin, ListAPIView):
    queryset = RasterDataset.objects.all().select_related("cluster")
    serializer_class = RasterDatasetSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filterset_class = RasterDatasetFilter


class RasterDatasetDetailView(CachedAPIViewMixin, RetrieveAPIView):
    queryset = RasterDataset.objects.all()
    serializer_class = RasterDatasetSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class PMTilesDatasetListView(CachedAPIViewMixin, ListAPIView):
    queryset = PMTilesDataset.objects.all().select_related("cluster")
    serializer_class = PMTilesDatasetSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filterset_class = PMTilesDatasetFilter


class PMTilesDatasetDetailView(CachedAPIViewMixin, RetrieveAPIView):
    queryset = PMTilesDataset.objects.all()
    serializer_class = PMTilesDatasetSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class VectorDatasetListView(CachedAPIViewMixin, ListAPIView):
    queryset = VectorDataset.objects.all().select_related("cluster")
    serializer_class = VectorDatasetSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filterset_class = VectorDatasetFilter


class VectorDatasetDetailView(CachedAPIViewMixin, RetrieveAPIView):
    queryset = VectorDataset.objects.all()
    serializer_class = VectorDatasetSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class VectorDatasetDataView(CachedAPIViewMixin, ListAPIView):
    serializer_class = VectorItemSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = GeoJsonPagination
    bbox_filter_field = "geometry"
    filterset_class = VectorItemFilter
    filter_backends = (
        InBBoxFilter,
        django_filters.rest_framework.DjangoFilterBackend,
    )

    def get_queryset(self):
        return VectorItem.objects.filter(dataset=self.kwargs.get("pk")).select_related(
            "province", "area_council"
        )


class TabularDatasetListView(CachedAPIViewMixin, ListAPIView):
    queryset = TabularDataset.objects.all().select_related("cluster")
    serializer_class = TabularDatasetSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filterset_class = TabularDatasetFilter


class TabularDatasetDetailView(CachedAPIViewMixin, RetrieveAPIView):
    queryset = TabularDataset.objects.all()
    serializer_class = TabularDatasetSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class TabularDatasetDataView(CachedAPIViewMixin, ListAPIView):
    filterset_class = TabularItemFilter
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = TabularItemSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return TabularItem.objects.filter(dataset=self.kwargs.get("pk")).select_related(
            "province", "area_council"
        )


class TabularDatasetXSLXDataView(XLSXFileMixin, TabularDatasetDataView):
    serializer_class = TabularItemExcelSerializer
    renderer_classes = (XLSXRenderer,)
    pagination_class = None

    def get_filename(self, request, *args, **kwargs):
        return f"vbos-mis-tabular-{kwargs.get('pk')}.xlsx"
