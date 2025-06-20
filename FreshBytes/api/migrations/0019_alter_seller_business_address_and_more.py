# Generated by Django 5.1.7 on 2025-06-19 03:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0018_remove_product_user_id_alter_seller_business_email"),
    ]

    operations = [
        migrations.AlterField(
            model_name="seller",
            name="business_address",
            field=models.CharField(default="", max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name="seller",
            name="business_email",
            field=models.EmailField(default="", max_length=254, unique=True),
        ),
        migrations.AlterField(
            model_name="seller",
            name="business_name",
            field=models.CharField(default="", max_length=255),
        ),
        migrations.AlterField(
            model_name="seller",
            name="business_phone",
            field=models.IntegerField(default=""),
        ),
    ]
