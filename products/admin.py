from django.contrib import admin
from .models import Category, Product

# Register your models here.
class CategoryAdmin(admin.ModelAdmin):
  list_display = ("name", "parent")


class ProductAdmin(admin.ModelAdmin):
  list_display = ("name", "price", "discount_percentage", "stock")


admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)