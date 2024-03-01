from django import forms 
from .models import Product, ProductImage, Category

class ProductFormBase(forms.ModelForm):
  image = forms.ImageField(label='Product Image', required=False)

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
      image = self.cleaned_data.get('image')
      if image:
        ProductImage.objects.create(product=product, image=image)
    return product


class ProductAddForm(ProductFormBase):
  pass


class ProductUpdateForm(ProductFormBase):
  def save(self, commit=True):
    product = super().save(commit=False)
    if commit:
      product.save()
      image = self.cleaned_data.get('image')
      if image:
        product_image = ProductImage.objects.filter(product=product).first()
        if product_image:
          product_image.image = image
          product_image.save()
        else:
          ProductImage.objects.create(product=product, image=image)
    return product