# Generated by Django 5.0.1 on 2024-02-10 06:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('carts', '0002_cartitem_discount_pecentage_cartitem_price'),
    ]

    operations = [
        migrations.RenameField(
            model_name='cartitem',
            old_name='discount_pecentage',
            new_name='discount_percentage',
        ),
    ]
