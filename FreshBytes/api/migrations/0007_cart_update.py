from django.db import migrations, models
import uuid

class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_alter_product_product_sku'),
    ]

    operations = [
        migrations.CreateModel(
            name='NewCart',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField('auth.User', on_delete=models.CASCADE, related_name='cart')),
            ],
            options={
                'db_table': 'Cart',
            },
        ),
        migrations.CreateModel(
            name='NewCartItem',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)),
                ('quantity', models.PositiveIntegerField(default=1)),
                ('unit_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('cart', models.ForeignKey('api.NewCart', on_delete=models.CASCADE, related_name='items')),
                ('product', models.ForeignKey('api.Product', on_delete=models.CASCADE)),
            ],
            options={
                'db_table': 'CartItems',
                'unique_together': {('cart', 'product')},
            },
        ),
        migrations.DeleteModel(
            name='CartItem',
        ),
        migrations.DeleteModel(
            name='Cart',
        ),
        migrations.RenameModel(
            old_name='NewCart',
            new_name='Cart',
        ),
        migrations.RenameModel(
            old_name='NewCartItem',
            new_name='CartItem',
        ),
    ] 