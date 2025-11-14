import calendar
from datetime import date
from typing import Dict, List

from .models import (
    TYPE_CHOICES,
    AreaCouncil,
    Cluster,
    Province,
    TabularDataset,
    TabularItem,
)


class GeoJSONProperties:
    def __init__(self, properties: Dict):
        self.properties = properties
        self.area_council = self.get_property(
            ["Area Council", "area_council", "area council", "Area council"]
        )
        self.province = self.get_property(["Province", "province"])
        self.name = self.get_property(["Name", "name"])
        self.ref = self.get_property(["ref", "Ref", "REF"])
        self.attribute = self.get_property(["Attribute", "attribute"])

    def get_property(self, keys: List[str]) -> str:
        value = ""
        for key in keys:
            try:
                value = self.properties.pop(key)
                break
            except KeyError:
                pass
        return value


class CSVRow:
    def __init__(self, row: Dict):
        self.metadata = row
        self.area_council = self.get_property(
            ["Area Council", "area_council", "area council", "Area council"]
        )
        self.province = self.get_property(["Province", "province"])
        self.value = self.get_property(["Value", "value", "VALUE"])
        self.attribute = self.get_property(["Attribute", "attribute"])
        self.year = self.get_property(["Year", "year", "YEAR"])
        self.month = self.get_property(["Month", "month", "MONTH"])
        self.cluster = self.get_property(["Cluster", "cluster"])
        self.type = self.get_property(["Type", "type"])
        try:
            self.date = date(int(self.year), self.month_name_to_number(), 1)
        except ValueError:
            self.date = None
        self.remove_keys()

    def get_property(self, keys: List[str]) -> str:
        value = ""
        for key in keys:
            try:
                value = self.metadata.pop(key)
                break
            except KeyError:
                pass
        return value

    def remove_keys(self):
        keys = [
            "Unit",
            "Source",
            "Year Collected",
            "Frequency Collection",
            "Day",
            "Indicator",
        ]
        for key in keys:
            try:
                self.metadata.pop(key)
            except KeyError:
                pass

    def clean_metadata(self):
        empty_keys = [i[0] for i in self.metadata.items() if i[1] == ""]
        for key in empty_keys:
            self.metadata.pop(key)

    def month_name_to_number(self) -> int:
        month_dict = {
            month.lower(): index
            for index, month in enumerate(calendar.month_name)
            if month
        }
        return month_dict.get(self.month.lower()) or 1


def group_by_dataset(data):
    result = {}

    for item in data:
        # Create a unique key based on Type, Cluster, and Indicator
        key = (item["Type"], item["Cluster"], item["Indicator"])

        # If this key doesn't exist in result, create a new entry
        if key not in result:
            result[key] = {
                "Type": item["Type"],
                "Cluster": item["Cluster"],
                "Indicator": item["Indicator"],
                "items": [],
            }

        result[key]["items"].append(item)

    # Convert the dictionary values to a list
    return list(result.values())


REVERSE_TYPE_MAPPING = {str(label): value for (value, label) in TYPE_CHOICES.items()}


def get_dataset(row):
    return TabularDataset.objects.get(
        name=row["Indicator"],
        cluster=Cluster.objects.get_or_create(name=row["Cluster"])[0],
        type=REVERSE_TYPE_MAPPING[row["Type"]],
    )


def create_tabular_item(csv_row: CSVRow, dataset: TabularDataset):
    return TabularItem.objects.create(
        dataset=dataset,
        metadata=csv_row.metadata,
        attribute=csv_row.attribute.strip(),
        value=csv_row.value,
        date=csv_row.date,
        province=Province.objects.filter(name__iexact=csv_row.province).first(),
        area_council=AreaCouncil.objects.filter(
            name__iexact=csv_row.area_council
        ).first(),
    )


def clean_redundant_tabular_items(dataset: TabularDataset):
    items = TabularItem.objects.filter(dataset=dataset)
    # If a dataset has items with an Area Council value,
    # remove all items that don't have the Area Council set
    if items.filter(area_council__isnull=False).count() > 0:
        items.filter(area_council__isnull=True).delete()

    # If a dataset has items with a Province value,
    # remove all items that don't have the Province set
    if items.filter(province__isnull=False).count() > 0:
        items.filter(province__isnull=True).delete()
