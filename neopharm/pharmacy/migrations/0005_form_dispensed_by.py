# Generated by Django 5.1.7 on 2025-03-24 04:35

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pharmacy', '0004_remove_form_buyer_address_remove_form_printed_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='form',
            name='dispensed_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
    ]
