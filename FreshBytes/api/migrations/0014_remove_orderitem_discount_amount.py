# Generated by Django 5.1.7 on 2025-07-18 05:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0013_remove_order_discount_amount_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="orderitem",
            name="discount_amount",
        ),
    ]
