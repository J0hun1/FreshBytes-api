from django.contrib import admin

# Register your models here.
from .models import Product, Category, User, Seller, SubCategory, Reviews, Promo, Cart, CartItem

admin.site.register(Product)
admin.site.register(Category)
admin.site.register(User)
admin.site.register(Seller)
admin.site.register(SubCategory)
admin.site.register(Reviews)
admin.site.register(Promo)
admin.site.register(Cart)
admin.site.register(CartItem)