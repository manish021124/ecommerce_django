from django import forms 
from .models import Product, ProductImage, Category

class ProductAddForm(forms.ModelForm):
  image = forms.ImageField(label='Product Image', required=False)

  class Meta:
    model = Product
    fields = ['name', 'description', 'price', 'discount_percentage', 'stock', 'category']

  def save(self, commit=True):
    product = super().save(commit=False)
    if commit:
      product.save()
      image = self.cleaned_data.get('image')
      if image:
        ProductImage.objects.create(product=product, image=image)
    return product


class ProductUpdateForm(forms.ModelForm):
  image = forms.ImageField(label='Product Image', required=False)

  class Meta:
    model = Product
    fields = ['name', 'description', 'price', 'discount_percentage', 'stock', 'category']

  def save(self, commit=True):
    product = super(ProductUpdateForm, self).save(commit=False)
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