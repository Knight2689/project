# Generated by Django 5.0.2 on 2024-03-18 04:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0004_alter_imagemodel_product'),
    ]

    operations = [
        migrations.AddField(
            model_name='registered_user',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]
