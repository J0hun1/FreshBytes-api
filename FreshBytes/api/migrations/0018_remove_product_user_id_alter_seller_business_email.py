# Generated by Django 5.1.7 on 2025-06-19 03:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0017_alter_seller_business_email"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="product",
            name="user_id",
        ),
        migrations.AlterField(
            model_name="seller",
            name="business_email",
            field=models.EmailField(max_length=254, unique=True),
        ),
    ]
