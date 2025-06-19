from django.contrib import admin

# Register your models here.
from .models import Product, Category, User, Seller

admin.site.register(Product)
admin.site.register(Category)
admin.site.register(User)
admin.site.register(Seller)