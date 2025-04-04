# Generated by Django 5.1.7 on 2025-03-24 05:10

import shortuuid.django_fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pharmacy', '0005_form_dispensed_by'),
    ]

    operations = [
        migrations.AlterField(
            model_name='form',
            name='form_id',
            field=shortuuid.django_fields.ShortUUIDField(alphabet='0123456789', length=5, max_length=50, prefix='F', unique=True),
        ),
    ]
