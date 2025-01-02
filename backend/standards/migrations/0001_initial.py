# Generated by Django 5.1.4 on 2024-12-30 10:42

import django.contrib.postgres.fields
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Standard",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("title", models.CharField(max_length=200)),
                ("description", models.TextField()),
                ("minimum_requirement", models.TextField()),
                (
                    "success_criteria",
                    django.contrib.postgres.fields.ArrayField(
                        base_field=models.CharField(max_length=500),
                        default=list,
                        size=None,
                    ),
                ),
                (
                    "frequency",
                    models.CharField(
                        choices=[
                            ("daily", "Daily"),
                            ("weekly", "Weekly"),
                            ("monthly", "Monthly"),
                            ("custom", "Custom"),
                        ],
                        max_length=20,
                    ),
                ),
                (
                    "specific_days",
                    django.contrib.postgres.fields.ArrayField(
                        base_field=models.IntegerField(
                            choices=[
                                (0, "0"),
                                (1, "1"),
                                (2, "2"),
                                (3, "3"),
                                (4, "4"),
                                (5, "5"),
                                (6, "6"),
                            ]
                        ),
                        blank=True,
                        null=True,
                        size=None,
                    ),
                ),
                ("time_of_day", models.TimeField(blank=True, null=True)),
                ("duration_minutes", models.IntegerField(blank=True, null=True)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "db_table": "standards",
                "ordering": ["category", "title"],
            },
        ),
        migrations.CreateModel(
            name="StandardCategory",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                ("description", models.TextField(blank=True)),
                ("is_default", models.BooleanField(default=False)),
                ("order", models.IntegerField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "db_table": "standard_categories",
                "ordering": ["order", "name"],
            },
        ),
        migrations.CreateModel(
            name="StandardProgress",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("is_completed", models.BooleanField(default=False)),
                ("completion_time", models.DateTimeField(blank=True, null=True)),
                ("notes", models.TextField(blank=True)),
            ],
            options={
                "db_table": "standard_progress",
            },
        ),
    ]