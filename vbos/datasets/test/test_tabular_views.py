from datetime import date
from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse

from ..models import AreaCouncil, Cluster, Province, TabularDataset, TabularItem
from ...users.test.factories import UserFactory


class TestTabularDatasetListDetailViews(APITestCase):
    def setUp(self):
        self.user = UserFactory()
        self.dataset_1 = TabularDataset.objects.create(
            name="Population",
            cluster=Cluster.objects.create(name="Administrative"),
            source="Government",
        )
        self.dataset_2 = TabularDataset.objects.create(
            name="Prices",
            cluster=Cluster.objects.create(name="Statistics"),
            source="Government",
            type="estimated_damage",
            unit="Vatu (VUV)"
        )
        self.url = reverse("datasets:tabular-list")

    def test_tabular_datasets_list(self):
        req = self.client.get(self.url)
        assert req.status_code == status.HTTP_200_OK
        assert req.data.get("count") == 2
        assert req.data.get("results")[0]["name"] == "Population"
        assert req.data.get("results")[1]["name"] == "Prices"
        assert req.data.get("results")[0]["source"] == "Government"
        assert req.data.get("results")[1]["source"] == "Government"
        assert req.data.get("results")[0]["cluster"] == "Administrative"
        assert req.data.get("results")[1]["cluster"] == "Statistics"
        assert req.data.get("results")[0]["type"] == "baseline"
        assert req.data.get("results")[1]["type"] == "estimated_damage"
        assert req.data.get("results")[1]["unit"] == "Vatu (VUV)"

    def test_raster_datasets_list_filter(self):
        req = self.client.get(self.url, {"cluster": "transportation"})
        assert req.status_code == status.HTTP_400_BAD_REQUEST

        req = self.client.get(self.url, {"cluster": "administrative"})
        assert req.status_code == status.HTTP_200_OK
        assert req.data.get("count") == 1

        req = self.client.get(self.url, {"cluster": "statistics"})
        assert req.status_code == status.HTTP_200_OK
        assert req.data.get("count") == 1

    def test_tabular_datasets_detail(self):
        url = reverse("datasets:tabular-detail", args=[self.dataset_1.id])
        req = self.client.get(url)
        assert req.status_code == status.HTTP_200_OK
        assert req.data.get("name") == "Population"
        assert req.data.get("created")
        assert req.data.get("updated")


class TestTabularDatasetDataView(APITestCase):
    def setUp(self):
        self.cluster = Cluster.objects.create(name="Other")
        self.user = UserFactory()
        self.dataset_1 = TabularDataset.objects.create(
            name="Population", cluster=self.cluster
        )
        self.dataset_2 = TabularDataset.objects.create(
            name="Employment", cluster=self.cluster
        )
        self.item = TabularItem.objects.create(
            dataset=self.dataset_1,
            date=date(2025, 1, 1),
            province=Province.objects.get(name="TORBA"),
            attribute="Population",
            value=13874,
        )
        TabularItem.objects.create(
            dataset=self.dataset_1,
            date=date(2025, 1, 1),
            province=Province.objects.get(name="TAFEA"),
            attribute="Population",
            value=1230,
        )
        TabularItem.objects.create(
            dataset=self.dataset_1,
            date=date(2025, 1, 1),
            province=Province.objects.get(name="PENAMA"),
            area_council=AreaCouncil.objects.get(name="North Maewo"),
            attribute="Population",
            value=5682,
        )
        TabularItem.objects.create(
            dataset=self.dataset_2,
            date=date(2025, 1, 1),
            attribute="Employed Population",
            value=0.93,
            province=Province.objects.get(name="TORBA"),
            area_council=AreaCouncil.objects.get(name="East Gaua"),
            metadata={"additional_value": "test"},
        )
        TabularItem.objects.create(
            dataset=self.dataset_2,
            date=date(2025, 2, 1),
            attribute="Employed Population",
            value=0.9,
            province=Province.objects.get(name="TORBA"),
            area_council=AreaCouncil.objects.get(name="East Gaua"),
        )
        TabularItem.objects.create(
            dataset=self.dataset_2,
            date=date(2025, 3, 1),
            attribute="Employed Population",
            value=0.91,
            province=Province.objects.get(name="TORBA"),
            area_council=AreaCouncil.objects.get(name="East Gaua"),
        )
        TabularItem.objects.create(
            dataset=self.dataset_2,
            date=date(2025, 4, 1),
            attribute="Employed Population",
            value=0.95,
            province=Province.objects.get(name="TORBA"),
            area_council=AreaCouncil.objects.get(name="East Gaua"),
        )
        self.url = reverse("datasets:tabular-data", args=[self.dataset_1.id])

    def test_tabular_datasets_data(self):
        req = self.client.get(self.url)
        assert req.status_code == status.HTTP_200_OK
        assert req.data.get("count") == 3
        assert len(req.data.get("results")) == 3
        assert req.data.get("results")[0]["province"] == "TORBA"
        assert req.data.get("results")[0]["value"] == 13874
        assert req.data.get("results")[0]["date"] == "2025-01-01"
        assert req.data.get("results")[0]["attribute"] == "Population"
        assert req.data.get("results")[2]["province"] == "PENAMA"
        assert req.data.get("results")[2]["area_council"] == "North Maewo"
        assert req.data.get("results")[2]["value"] == 5682
        assert req.data.get("results")[2]["date"] == "2025-01-01"
        assert req.data.get("results")[2]["attribute"] == "Population"

        # fetch second dataset's data
        url = reverse("datasets:tabular-data", args=[self.dataset_2.id])
        req = self.client.get(url)
        assert req.status_code == status.HTTP_200_OK
        assert req.data.get("count") == 4
        assert len(req.data.get("results")) == 4
        assert req.data.get("results")[0]["province"] == "TORBA"
        assert req.data.get("results")[0]["area_council"] == "East Gaua"
        assert req.data.get("results")[0]["value"] == 0.93
        assert req.data.get("results")[0]["date"] == "2025-01-01"
        assert req.data.get("results")[0]["attribute"] == "Employed Population"
        assert req.data.get("results")[0]["additional_value"] == "test"

    def test_filter_data(self):
        url = reverse("datasets:tabular-data", args=[self.dataset_2.id])
        req = self.client.get(url, {"date_after": "2025-01-01"})
        assert req.status_code == status.HTTP_200_OK
        assert req.data.get("count") == 4

        req = self.client.get(url, {"date_after": "2025-03-01"})
        assert req.status_code == status.HTTP_200_OK
        assert req.data.get("count") == 2

        req = self.client.get(url, {"date_before": "2024-12-01"})
        assert req.status_code == status.HTTP_200_OK
        assert req.data.get("count") == 0

        req = self.client.get(url, {"province": "torba"})
        assert req.status_code == status.HTTP_200_OK
        assert req.data.get("count") == 4

        req = self.client.get(url, {"province": "south"})
        assert req.status_code == status.HTTP_400_BAD_REQUEST

        req = self.client.get(url, {"area_council": "North Maewo"})
        assert req.status_code == status.HTTP_200_OK
        assert req.data.get("count") == 0

        req = self.client.get(url, {"area_council": "East Gaua"})
        assert req.status_code == status.HTTP_200_OK
        assert req.data.get("count") == 4

        req = self.client.get(url, {"attribute": "population"})
        assert req.status_code == status.HTTP_200_OK
        assert req.data.get("count") == 4
