# Generated by Django 5.0.1 on 2024-02-08 06:27

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='order_number',
            field=models.CharField(default=django.utils.timezone.now, max_length=20, unique=True),
            preserve_default=False,
        ),
    ]
