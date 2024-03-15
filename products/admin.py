from django.contrib import admin
from .models import Category, Product, ProductImage, Review

# Register your models here.
class CategoryAdmin(admin.ModelAdmin):
  list_display = ("name", "parent")


class ProductAdmin(admin.ModelAdmin):
  list_display = ("name", "price", "discount_percentage", "stock", "store", "is_deleted")


class ReviewAdmin(admin.ModelAdmin):
  list_display = ("review_info", "rating", "created_at") 

  def review_info(self, obj):
    return str(obj) # calls the __str__ method of review model
  review_info.short_description = 'Review Info'


admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(ProductImage)
admin.site.register(Review, ReviewAdmin)