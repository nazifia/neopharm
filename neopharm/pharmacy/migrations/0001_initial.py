# Generated by Django 5.1.7 on 2025-03-23 04:30

import datetime
import django.contrib.auth.models
import django.db.models.deletion
import django.utils.timezone
import shortuuid.django_fields
from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Form',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('buyer_name', models.CharField(blank=True, max_length=255, null=True)),
                ('buyer_address', models.CharField(blank=True, max_length=255, null=True)),
                ('total_amount', models.DecimalField(decimal_places=2, default=Decimal('0.0'), max_digits=10)),
                ('date', models.DateTimeField(default=datetime.datetime.now)),
                ('form_id', shortuuid.django_fields.ShortUUIDField(alphabet='1234567890', length=5, max_length=50, prefix='', unique=True)),
                ('printed', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='LpacemakerDrugs',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('dosage_form', models.CharField(blank=True, choices=[('Tablet', 'Tablet'), ('Capsule', 'Capsule'), ('Cream', 'Cream'), ('Consumable', 'Consumable'), ('Injection', 'Injection'), ('Infusion', 'Infusion'), ('Inhaler', 'Inhaler'), ('Suspension', 'Suspension'), ('Syrup', 'Syrup'), ('Eye-drop', 'Eye-drop'), ('Ear-drop', 'Ear-drop'), ('Eye-ointment', 'Eye-ointment'), ('Rectal', 'Rectal'), ('Vaginal', 'Vaginal')], max_length=200, null=True)),
                ('brand', models.CharField(blank=True, max_length=200, null=True)),
                ('unit', models.CharField(blank=True, choices=[('Amp', 'Amp'), ('Bottle', 'Bottle'), ('Tab', 'Tab'), ('Tin', 'Tin'), ('Caps', 'Caps'), ('Card', 'Card'), ('Carton', 'Carton'), ('Pack', 'Pack'), ('Pcs', 'Pcs'), ('Roll', 'Roll'), ('Vail', 'Vail'), ('1L', '1L'), ('2L', '2L'), ('4L', '4L')], max_length=200, null=True)),
                ('price', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('stock', models.PositiveIntegerField(blank=True, default=0, null=True)),
                ('exp_date', models.DateField(blank=True, null=True)),
            ],
            options={
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='NcapDrugs',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('dosage_form', models.CharField(blank=True, choices=[('Tablet', 'Tablet'), ('Capsule', 'Capsule'), ('Cream', 'Cream'), ('Consumable', 'Consumable'), ('Injection', 'Injection'), ('Infusion', 'Infusion'), ('Inhaler', 'Inhaler'), ('Suspension', 'Suspension'), ('Syrup', 'Syrup'), ('Eye-drop', 'Eye-drop'), ('Ear-drop', 'Ear-drop'), ('Eye-ointment', 'Eye-ointment'), ('Rectal', 'Rectal'), ('Vaginal', 'Vaginal')], max_length=200, null=True)),
                ('brand', models.CharField(blank=True, max_length=200, null=True)),
                ('unit', models.CharField(blank=True, choices=[('Amp', 'Amp'), ('Bottle', 'Bottle'), ('Tab', 'Tab'), ('Tin', 'Tin'), ('Caps', 'Caps'), ('Card', 'Card'), ('Carton', 'Carton'), ('Pack', 'Pack'), ('Pcs', 'Pcs'), ('Roll', 'Roll'), ('Vail', 'Vail'), ('1L', '1L'), ('2L', '2L'), ('4L', '4L')], max_length=200, null=True)),
                ('price', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('stock', models.PositiveIntegerField(blank=True, default=0, null=True)),
                ('exp_date', models.DateField(blank=True, null=True)),
            ],
            options={
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='OncologyPharmacy',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('dosage_form', models.CharField(blank=True, choices=[('Tablet', 'Tablet'), ('Capsule', 'Capsule'), ('Cream', 'Cream'), ('Consumable', 'Consumable'), ('Injection', 'Injection'), ('Infusion', 'Infusion'), ('Inhaler', 'Inhaler'), ('Suspension', 'Suspension'), ('Syrup', 'Syrup'), ('Eye-drop', 'Eye-drop'), ('Ear-drop', 'Ear-drop'), ('Eye-ointment', 'Eye-ointment'), ('Rectal', 'Rectal'), ('Vaginal', 'Vaginal')], max_length=200, null=True)),
                ('brand', models.CharField(blank=True, max_length=200, null=True)),
                ('unit', models.CharField(blank=True, choices=[('Amp', 'Amp'), ('Bottle', 'Bottle'), ('Tab', 'Tab'), ('Tin', 'Tin'), ('Caps', 'Caps'), ('Card', 'Card'), ('Carton', 'Carton'), ('Pack', 'Pack'), ('Pcs', 'Pcs'), ('Roll', 'Roll'), ('Vail', 'Vail'), ('1L', '1L'), ('2L', '2L'), ('4L', '4L')], max_length=200, null=True)),
                ('price', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('stock', models.PositiveIntegerField(blank=True, default=0, null=True)),
                ('exp_date', models.DateField(blank=True, null=True)),
            ],
            options={
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('username', models.CharField(blank=True, max_length=200, null=True)),
                ('mobile', models.CharField(max_length=20, unique=True)),
                ('groups', models.ManyToManyField(blank=True, related_name='pharmacy_user_groups', to='auth.group')),
                ('user_permissions', models.ManyToManyField(blank=True, related_name='pharmacy_user_permissions', to='auth.permission')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(blank=True, max_length=200, null=True)),
                ('user_type', models.CharField(blank=True, choices=[('Admin', 'Admin'), ('Pharmacist', 'Pharmacist'), ('Pharm-Tech', 'Pharm-Tech')], max_length=200, null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='pharmacy.user')),
            ],
        ),
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('brand', models.CharField(blank=True, max_length=200, null=True)),
                ('unit', models.CharField(blank=True, choices=[('Amp', 'Amp'), ('Bottle', 'Bottle'), ('Tab', 'Tab'), ('Tin', 'Tin'), ('Caps', 'Caps'), ('Card', 'Card'), ('Carton', 'Carton'), ('Pack', 'Pack'), ('Pcs', 'Pcs'), ('Roll', 'Roll'), ('Vail', 'Vail'), ('1L', '1L'), ('2L', '2L'), ('4L', '4L')], max_length=200, null=True)),
                ('quantity', models.PositiveIntegerField(default=1)),
                ('price', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('subtotal', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('total', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('cart_id', shortuuid.django_fields.ShortUUIDField(alphabet='1234567890', length=5, max_length=50, prefix='CID: ', unique=True)),
                ('item1', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pharmacy.lpacemakerdrugs')),
                ('item2', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pharmacy.ncapdrugs')),
                ('item3', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pharmacy.oncologypharmacy')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='pharmacy.user')),
            ],
        ),
    ]
