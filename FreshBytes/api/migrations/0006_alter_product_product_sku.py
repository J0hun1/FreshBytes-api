# Generated by Django 5.1.7 on 2025-07-09 07:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0005_alter_product_product_id"),
    ]

    operations = [
        migrations.AlterField(
            model_name="product",
            name="product_sku",
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
