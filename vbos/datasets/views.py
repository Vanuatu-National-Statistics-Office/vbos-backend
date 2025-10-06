from django.shortcuts import render
import django_filters.rest_framework
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework_gis.pagination import GeoJsonPagination
from rest_framework_gis.filters import InBBoxFilter

from vbos.datasets.filters import (
    RasterDatasetFilter,
    TabularDatasetFilter,
    TabularItemFilter,
    VectorDatasetFilter,
    VectorItemFilter,
)

from .models import (
    AreaCouncil,
    Cluster,
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
    ProvinceSerializer,
    RasterDatasetSerializer,
    TabularDatasetSerializer,
    TabularItemExcelSerializer,
    TabularItemSerializer,
    VectorDatasetSerializer,
    VectorItemSerializer,
)


class ClusterListView(ListAPIView):
    queryset = Cluster.objects.all()
    serializer_class = ClusterSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = StandardResultsSetPagination


class ProvinceListView(ListAPIView):
    queryset = Province.objects.all()
    serializer_class = ProvinceSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = GeoJsonPagination


class AreaCouncilListView(ListAPIView):
    serializer_class = AreaCouncilSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = GeoJsonPagination

    def get_queryset(self):
        return AreaCouncil.objects.filter(
            province__name__iexact=self.kwargs.get("province")
        )


class RasterDatasetListView(ListAPIView):
    queryset = RasterDataset.objects.all()
    serializer_class = RasterDatasetSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filterset_class = RasterDatasetFilter


class RasterDatasetDetailView(RetrieveAPIView):
    queryset = RasterDataset.objects.all()
    serializer_class = RasterDatasetSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class VectorDatasetListView(ListAPIView):
    queryset = VectorDataset.objects.all()
    serializer_class = VectorDatasetSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filterset_class = VectorDatasetFilter


class VectorDatasetDetailView(RetrieveAPIView):
    queryset = VectorDataset.objects.all()
    serializer_class = VectorDatasetSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class VectorDatasetDataView(ListAPIView):
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
        return VectorItem.objects.filter(dataset=self.kwargs.get("pk"))


class TabularDatasetListView(ListAPIView):
    queryset = TabularDataset.objects.all()
    serializer_class = TabularDatasetSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filterset_class = TabularDatasetFilter


class TabularDatasetDetailView(RetrieveAPIView):
    queryset = TabularDataset.objects.all()
    serializer_class = TabularDatasetSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class TabularDatasetDataView(ListAPIView):
    filterset_class = TabularItemFilter
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return TabularItem.objects.filter(dataset=self.kwargs.get("pk"))

    def get_serializer_class(self):
        # Use different serializer for Excel format
        if self.request.query_params.get("format") == "xlsx":
            return TabularItemExcelSerializer
        return TabularItemSerializer
