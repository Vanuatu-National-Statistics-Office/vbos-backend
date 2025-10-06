from datetime import date
import calendar
from typing import Dict, List


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
        try:
            self.date = date(int(self.year), self.month_name_to_number(), 1)
        except ValueError:
            self.date = None

    def get_property(self, keys: List[str]) -> str:
        value = ""
        for key in keys:
            try:
                value = self.metadata.pop(key)
                break
            except KeyError:
                pass
        return value

    def month_name_to_number(self) -> int:
        month_dict = {
            month.lower(): index
            for index, month in enumerate(calendar.month_name)
            if month
        }
        return month_dict.get(self.month.lower()) or 1
