from datetime import date
from django.test import TestCase

from vbos.datasets.utils import CSVRow, GeoJSONProperties


class TestGeoJSONProperties(TestCase):
    def setUp(self):
        self.p1 = GeoJSONProperties(
            {
                "name": "Area 1",
                "ref": "12NC",
                "Province": "Torba",
                "Area Council": "East Gaua",
                "Attribute": "High School",
                "extra": "value",
            }
        )

    def test_class_attributes(self):
        assert self.p1.properties == {"extra": "value"}
        assert self.p1.attribute == "High School"
        assert self.p1.name == "Area 1"
        assert self.p1.ref == "12NC"
        assert self.p1.province == "Torba"
        assert self.p1.area_council == "East Gaua"


class TestCsvRow(TestCase):
    def setUp(self):
        self.r1 = CSVRow(
            {
                "value": "154",
                "year": "2023",
                "month": "March",
                "Province": "Torba",
                "Area Council": "East Gaua",
                "Attribute": "High School",
                "something": "yes",
            }
        )
        self.r2 = CSVRow(
            {
                "value": "154.2",
                "year": "2022",
                "Province": "TAFEA",
                "Area Council": "Futuna",
                "Attribute": "High School",
                "something": "no",
                "k": "v",
            }
        )

    def test_class_attributes(self):
        assert self.r1.metadata == {"something": "yes"}
        assert self.r1.attribute == "High School"
        assert self.r1.date == date(2023, 3, 1)
        assert self.r1.province == "Torba"
        assert self.r1.area_council == "East Gaua"
        assert self.r1.value == "154"

        assert self.r2.metadata == {"something": "no", "k": "v"}
        assert self.r2.attribute == "High School"
        assert self.r2.date == date(2022, 1, 1)
        assert self.r2.province == "TAFEA"
        assert self.r2.area_council == "Futuna"
        assert self.r2.value == "154.2"
