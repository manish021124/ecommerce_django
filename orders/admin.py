from django.contrib import admin
from .models import Order, OrderItem

# Register your models here.
# for enabling admin to update status
class OrderAdmin(admin.ModelAdmin):
  actions = ['mark_as_pending', 'mark_as_processing', 'mark_as_shipped', 'mark_as_delivered', 'mark_as_cancelled']

  def mark_as_pending(self, request, queryset):
    queryset.update(status='Pending')

  def mark_as_processing(self, request, queryset):
    queryset.update(status='Processing')

  def mark_as_shipped(self, request, queryset):
    queryset.update(status='Shipped')

  def mark_as_delivered(self, request, queryset):
    queryset.update(status='Delivered')

  def mark_as_cancelled(self, request, queryset):
    queryset.update(status='Cancelled')

  def get_readonly_fields(self, request, obj=None):
    readonly_fields = super().get_readonly_fields(request, obj)
    return readonly_fields + ('status',)

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    if not isinstance(self.readonly_fields, tuple):
      self.readonly_fields = tuple(self.readonly_fields)


admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem)