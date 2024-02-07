# to add additional variables to the context that is passed in templates
# they can then be accessed directly in templates without views
# to provide common data across multiple templates

from .models import Category

def categories(request):
  categories = Category.objects.filter(parent__isnull=True)
  return {'categories': categories}