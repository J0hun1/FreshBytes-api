# Generated by Django 5.1.7 on 2025-06-19 07:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0024_remove_subcategory_sub_category_name"),
    ]

    operations = [
        migrations.DeleteModel(
            name="SubCategory",
        ),
    ]
