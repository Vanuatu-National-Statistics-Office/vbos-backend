from django.db.models.deletion import ProtectedError
from django.db.utils import IntegrityError
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError

from vbos.datasets.models import (
    Cluster,
    RasterDataset,
    RasterFile,
    TabularDataset,
    VectorDataset,
)


class TestRasterModels(TestCase):
    def setUp(self):
        self.valid_file = SimpleUploadedFile(
            "rainfall.tiff", b"file_content", content_type="image/tiff"
        )
        self.r_1 = RasterFile.objects.create(name="Rainfall COG", file=self.valid_file)
        self.r_2 = RasterFile.objects.create(
            name="Coastline COG", file="raster/coastline.tiff"
        )
        self.dataset = RasterDataset.objects.create(
            name="Rainfall",
            cluster=Cluster.objects.create(name="Environment"),
            file=self.r_1,
        )

    def test_deletion(self):
        # RasterFile can't be deleted if it's associates with a dataset
        with self.assertRaises(ProtectedError):
            self.r_1.delete()

        # name should be unique
        raster = RasterFile(name="Rainfall COG 2", file="raster/coastline.tiff")
        with self.assertRaises(ValidationError):
            raster.full_clean()

        # file path should be unique
        raster = RasterFile(name="Rainfall COG", file="newfile.tif")
        with self.assertRaises(ValidationError):
            raster.full_clean()

        # modify dataset
        self.dataset.file = self.r_2
        self.dataset.save()
        # delete file
        self.r_1.delete()
        self.assertEqual(RasterFile.objects.count(), 1)
        # delete dataset
        self.dataset.delete()
        self.assertEqual(RasterDataset.objects.count(), 0)
        # delete remaining file
        self.r_2.delete()
        self.assertEqual(RasterFile.objects.count(), 0)

        # test file extension validation
        invalid_file = SimpleUploadedFile(
            "test.jpg", b"file_content", content_type="image/jpeg"
        )
        raster = RasterFile(name="Test", file=invalid_file)
        with self.assertRaises(ValidationError):
            raster.full_clean()

        RasterFile.objects.all().delete()

    def test_unique_name_type(self):
        self.cluster = Cluster.objects.create(name="Administrative")
        r_2 = RasterFile.objects.create(
            name="Population Density COG", file="raster/pop.tiff"
        )
        RasterDataset.objects.create(
            name="Population",
            cluster=self.cluster,
            source="Government",
            file=r_2,
        )
        RasterDataset.objects.create(
            name="Population",
            cluster=self.cluster,
            source="Government",
            file=r_2,
            type="estimated_damage",
        )
        with self.assertRaises(IntegrityError):
            RasterDataset.objects.create(
                name="Population",
                cluster=self.cluster,
                source="Government",
                file=r_2,
            )


class TestTabularDatasetModel(TestCase):
    def test_unique_name_type(self):
        self.cluster = Cluster.objects.create(name="Administrative")
        TabularDataset.objects.create(
            name="Population",
            cluster=self.cluster,
            source="Government",
        )
        TabularDataset.objects.create(
            name="Population",
            cluster=self.cluster,
            source="Government",
            type="estimated_damage",
        )
        with self.assertRaises(IntegrityError):
            TabularDataset.objects.create(
                name="Population",
                cluster=self.cluster,
                source="Government",
            )


class TestVectorDatasetModel(TestCase):
    def test_unique_name_type(self):
        self.cluster = Cluster.objects.create(name="Administrative")
        VectorDataset.objects.create(
            name="Population",
            cluster=self.cluster,
            source="Government",
        )
        VectorDataset.objects.create(
            name="Population",
            cluster=self.cluster,
            source="Government",
            type="estimated_damage",
        )
        with self.assertRaises(IntegrityError):
            VectorDataset.objects.create(
                name="Population",
                cluster=self.cluster,
                source="Government",
            )
