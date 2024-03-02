from django import forms 
from .models import Product, ProductImage, Category
from django.forms import inlineformset_factory

class ProductImageForm(forms.ModelForm):
  image = forms.ImageField(label='Product Image', required=False)

  class Meta:
    model = ProductImage
    fields = ['image']

# to upload multiple image
ProductImageFormSet = inlineformset_factory(
  parent_model=Product, 
  model=ProductImage, 
  form=ProductImageForm, 
  extra=5, 
  can_delete=True
)

class ProductFormBase(forms.ModelForm):
  class Meta:
    model = Product
    fields = ['name', 'description', 'price', 'discount_percentage', 'stock', 'category']

  # to set the choices for category when form is instantiated
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.fields['category'].choices = self.get_all_categories_choices()

  # to build choices for the category dropdown including both parent and child
  def get_category_choices(self, category, level=0):
    choices = [(category.id, '-' * level + category.name)]
    children = category.children.all()
    for child in children:
      choices.extend(self.get_category_choices(child, level + 1))
    return choices

  def get_all_categories_choices(self):
    categories = Category.objects.filter(parent__isnull=True)
    choices = []
    for category in categories:
      choices.extend(self.get_category_choices(category))
    return choices

  def save(self, commit=True):
    product = super().save(commit=False)
    if commit:
      product.save()
    return product


class ProductAddForm(ProductFormBase):
  pass


class ProductUpdateForm(ProductFormBase):
  pass