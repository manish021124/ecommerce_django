from django.contrib import admin
from .models import Category, Product, ProductImage

# Register your models here.
class CategoryAdmin(admin.ModelAdmin):
  list_display = ("name", "parent")


class ProductAdmin(admin.ModelAdmin):
  list_display = ("name", "price", "discount_percentage", "stock", "store")


admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(ProductImage)