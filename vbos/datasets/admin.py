import csv
import json
from io import TextIOWrapper

from django.contrib.gis import admin
from django.contrib import messages
from django.contrib.gis.geos.geometry import GEOSGeometry
from django.shortcuts import render, redirect, reverse
from django.urls import path

from vbos.datasets.utils import CSVRow, GeoJSONProperties

from .models import (
    AreaCouncil,
    Cluster,
    Province,
    RasterDataset,
    RasterFile,
    TabularDataset,
    TabularItem,
    VectorDataset,
    VectorItem,
)
from .forms import CSVUploadForm, GeoJSONUploadForm


@admin.register(Cluster)
class ClusterAdmin(admin.ModelAdmin):
    list_display = ["id", "name"]


@admin.register(RasterFile)
class RasterFileAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "created", "file"]


@admin.register(RasterDataset)
class RasterDatasetAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "cluster", "type", "updated", "file"]
    list_filter = ["cluster", "type"]


@admin.register(VectorDataset)
class VectorDatasetAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "cluster", "type", "updated"]
    list_filter = ["cluster", "type"]


@admin.register(VectorItem)
class VectorItemAdmin(admin.GISModelAdmin):
    list_display = ["id", "dataset", "name", "attribute", "province", "area_council"]
    list_filter = ["dataset", "province", "area_council"]

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "upload-file/",
                self.admin_site.admin_view(self.import_file),
                name="datasets_vectoritem_import_file",
            ),
        ]
        return custom_urls + urls

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context["upload_file"] = reverse("admin:datasets_vectoritem_import_file")
        return super().changelist_view(request, extra_context=extra_context)

    def import_file(self, request):
        if request.method == "POST":
            form = GeoJSONUploadForm(request.POST, request.FILES)
            if form.is_valid():
                uploaded_file = request.FILES["file"]

                # Check if the file is a CSV
                if not uploaded_file.name.endswith(".geojson"):
                    messages.error(request, "Please upload a GeoJSON file")
                    return redirect("admin:datasets_vectoritem_import_file")

                try:
                    decoded_file = TextIOWrapper(uploaded_file.file, encoding="utf-8")
                    geojson_content = json.loads(decoded_file.read())

                    created_count = 0
                    error_count = 0

                    for item in geojson_content["features"]:
                        metadata = GeoJSONProperties(item["properties"])
                        try:
                            VectorItem.objects.create(
                                dataset=form.cleaned_data["dataset"],
                                metadata=metadata.properties,
                                name=metadata.name,
                                ref=metadata.ref,
                                attribute=metadata.attribute,
                                province=Province.objects.filter(
                                    name__iexact=metadata.province
                                ).first(),
                                area_council=AreaCouncil.objects.filter(
                                    name__iexact=metadata.area_council
                                ).first(),
                                geometry=GEOSGeometry(json.dumps(item["geometry"])),
                            )
                            created_count += 1
                        except Exception as e:
                            print(e)
                            error_count += 1

                    if created_count > 0:
                        messages.success(
                            request, f"Successfully created {created_count} new records"
                        )

                    if error_count > 0:
                        messages.warning(
                            request, f"Failed to create {error_count} items."
                        )

                except Exception as e:
                    messages.error(request, f"Error processing GeoJSON: {str(e)}")

                return redirect("admin:datasets_vectoritem_import_file")
        else:
            form = GeoJSONUploadForm()

        context = {
            "form": form,
            "opts": self.model._meta,
            "title": "Import GeoJSON File",
        }
        return render(request, "admin/file_upload.html", context)


@admin.register(TabularDataset)
class TabularDatasetAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "cluster", "type", "updated"]
    list_filter = ["cluster", "type"]


@admin.register(TabularItem)
class TabularItemAdmin(admin.GISModelAdmin):
    list_display = ["id", "dataset", "province", "area_council", "attribute", "value"]
    list_filter = ["dataset", "province", "area_council"]

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "upload-file/",
                self.admin_site.admin_view(self.import_file),
                name="datasets_tabularitem_import_file",
            ),
        ]
        return custom_urls + urls

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context["upload_file"] = reverse("admin:datasets_tabularitem_import_file")
        return super().changelist_view(request, extra_context=extra_context)

    def import_file(self, request):
        if request.method == "POST":
            form = CSVUploadForm(request.POST, request.FILES)
            if form.is_valid():
                uploaded_file = request.FILES["file"]

                # Check if the file is a CSV
                if not uploaded_file.name.endswith(".csv"):
                    messages.error(request, "Please upload a CSV file")
                    return redirect("admin:datasets_tabularitem_import_file")

                try:
                    # Read and process the CSV
                    decoded_file = TextIOWrapper(uploaded_file.file, encoding="utf-8")
                    reader = csv.DictReader(decoded_file)

                    created_count = 0
                    error_count = 0

                    for row in reader:  # start=2 to account for header row
                        try:
                            csv_row = CSVRow(row)
                            TabularItem.objects.create(
                                dataset=form.cleaned_data["dataset"],
                                metadata=csv_row.metadata,
                                attribute=csv_row.attribute,
                                value=csv_row.value,
                                date=csv_row.date,
                                province=Province.objects.filter(
                                    name__iexact=csv_row.province
                                ).first(),
                                area_council=AreaCouncil.objects.filter(
                                    name__iexact=csv_row.area_council
                                ).first(),
                            )
                            created_count += 1
                        except Exception as e:
                            print(e)
                            error_count += 1

                    if created_count > 0:
                        messages.success(
                            request, f"Successfully created {created_count} new records"
                        )

                    if error_count > 0:
                        messages.warning(
                            request, f"Failed to create {error_count} items."
                        )

                except Exception as e:
                    messages.error(request, f"Error processing CSV: {str(e)}")

                return redirect("admin:datasets_tabularitem_import_file")
        else:
            form = CSVUploadForm()

        context = {
            "form": form,
            "opts": self.model._meta,
            "title": "Import CSV File",
        }
        return render(request, "admin/file_upload.html", context)
