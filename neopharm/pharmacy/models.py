from django.db import models
from django.dispatch import receiver
from django.utils import timezone
from django.utils.timezone import now
from django.db.models.signals import post_save
from django.contrib.auth.models import AbstractUser, Group, Permission
from shortuuid.django_fields import ShortUUIDField
from datetime import datetime
from decimal import Decimal
from django.conf import settings


# Create your models here.
DOSAGE_FORM = [
    ('Tablet', 'Tablet'),
    ('Capsule', 'Capsule'),
    ('Cream', 'Cream'),
    ('Consumable', 'Consumable'),
    ('Injection', 'Injection'),
    ('Infusion', 'Infusion'),
    ('Inhaler', 'Inhaler'),
    ('Suspension', 'Suspension'),
    ('Syrup', 'Syrup'),
    ('Eye-drop', 'Eye-drop'),
    ('Ear-drop', 'Ear-drop'),
    ('Eye-ointment', 'Eye-ointment'),
    ('Rectal', 'Rectal'),
    ('Vaginal', 'Vaginal'),
]


UNIT = [
    ('Amp', 'Amp'),
    ('Bottle', 'Bottle'),
    ('Tab', 'Tab'),
    ('Tin', 'Tin'),
    ('Caps', 'Caps'),
    ('Card', 'Card'),
    ('Carton', 'Carton'),
    ('Pack', 'Pack'),
    ('Pcs', 'Pcs'),
    ('Roll', 'Roll'),
    ('Vail', 'Vail'),
    ('1L', '1L'),
    ('2L', '2L'),
    ('4L', '4L'),
]




USER_TYPE = [
    ('Admin', 'Admin'),
    ('Pharmacist', 'Pharmacist'),
    ('Pharm-Tech', 'Pharm-Tech'),
]

# Create your models here.
class User(AbstractUser):
    groups = models.ManyToManyField(Group, related_name="pharmacy_user_groups", blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name="pharmacy_user_permissions", blank=True)
    username = models.CharField(max_length=200, null=True, blank=True)
    mobile = models.CharField(max_length=20, unique=True)
    
    USERNAME_FIELD = 'mobile'
    REQUIRED_FIELDS = ['username']
    
    def __str__(self):
        return self.username if self.username else self.mobile



@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()



class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # image = models.ImageField(upload_to='uploads/images/', blank=True, null=True)
    full_name = models.CharField(max_length=200, blank=True, null=True)
    user_type = models.CharField(max_length=200, choices=USER_TYPE, blank=True, null=True)
    
    def __str__(self):
        return f'{self.user.username} {self.user_type}'





class LpacemakerDrugs(models.Model):
    name = models.CharField(max_length=200)
    dosage_form = models.CharField(max_length=200, choices=DOSAGE_FORM, blank=True, null=True)
    brand = models.CharField(max_length=200, blank=True, null=True)
    unit = models.CharField(max_length=200, choices=UNIT, blank=True, null=True)
    # cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    # markup = models.DecimalField(max_digits=6, decimal_places=2, default=0, choices=MARKUP_CHOICES)
    stock = models.PositiveIntegerField(default=0, null=True, blank=True)
    # low_stock_threshold = models.PositiveIntegerField(default=0, null=True, blank=True)
    exp_date = models.DateField(null=True, blank=True)    
    
    class Meta:
        ordering = ('name',)
    
    def __str__(self):
        return f'{self.name} {self.brand} {self.unit} {self.price} {self.stock} {self.exp_date}'



class NcapDrugs(models.Model):
    name = models.CharField(max_length=200)
    dosage_form = models.CharField(max_length=200, choices=DOSAGE_FORM, blank=True, null=True)
    brand = models.CharField(max_length=200, blank=True, null=True)
    unit = models.CharField(max_length=200, choices=UNIT, blank=True, null=True)
    # cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    # markup = models.DecimalField(max_digits=6, decimal_places=2, default=0, choices=MARKUP_CHOICES)
    stock = models.PositiveIntegerField(default=0, null=True, blank=True)
    # low_stock_threshold = models.PositiveIntegerField(default=0, null=True, blank=True)
    exp_date = models.DateField(null=True, blank=True)    
    
    class Meta:
        ordering = ('name',)
    
    def __str__(self):
        return f'{self.name} {self.unit} {self.price} {self.stock} {self.exp_date}'
    
    

class OncologyPharmacy(models.Model):
    name = models.CharField(max_length=200)
    dosage_form = models.CharField(max_length=200, choices=DOSAGE_FORM, blank=True, null=True)
    brand = models.CharField(max_length=200, blank=True, null=True)
    unit = models.CharField(max_length=200, choices=UNIT, blank=True, null=True)
    # cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    # markup = models.DecimalField(max_digits=6, decimal_places=2, default=0, choices=MARKUP_CHOICES)
    stock = models.PositiveIntegerField(default=0, null=True, blank=True)
    # low_stock_threshold = models.PositiveIntegerField(default=0, null=True, blank=True)
    exp_date = models.DateField(null=True, blank=True)    
    
    class Meta:
        ordering = ('name',)
    
    def __str__(self):
        return f'{self.name} {self.brand} {self.unit} {self.price} {self.stock} {self.exp_date}'



class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    form = models.ForeignKey('Form', on_delete=models.CASCADE, null=True, blank=True, related_name='cart_items')
    lpacemaker_drug = models.ForeignKey(LpacemakerDrugs, on_delete=models.CASCADE, null=True, blank=True)
    ncap_drug = models.ForeignKey(NcapDrugs, on_delete=models.CASCADE, null=True, blank=True)
    oncology_drug = models.ForeignKey(OncologyPharmacy, on_delete=models.CASCADE, null=True, blank=True)
    brand = models.CharField(max_length=200, blank=True, null=True)
    unit = models.CharField(max_length=200, choices=UNIT, blank=True, null=True)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    cart_id = ShortUUIDField(unique=True, length=5, max_length=50, prefix='CID: ', alphabet='1234567890')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.cart_id} {self.user}'
    
    @property
    def get_item(self):
        """Returns the active drug item"""
        return self.lpacemaker_drug or self.ncap_drug or self.oncology_drug
    
    @property
    def calculate_subtotal(self):
        item = self.get_item
        if item:
            return item.price * self.quantity
        return Decimal('0')
    
    def save(self, *args, **kwargs):
        self.subtotal = self.calculate_subtotal
        super().save(*args, **kwargs)

    def get_drug_type(self):
        """Returns the type of drug in the cart item"""
        if self.lpacemaker_drug:
            return 'lpacemaker'
        elif self.ncap_drug:
            return 'ncap'
        elif self.oncology_drug:
            return 'oncology'
        return None


class Form(models.Model):
    form_id = ShortUUIDField(
        length=5,
        max_length=50,
        prefix="F",
        alphabet="0123456789",
        unique=True
    )
    buyer_name = models.CharField(max_length=255, null=True, blank=True)
    hospital_no = models.CharField(max_length=100, null=True, blank=True)
    ncap_no = models.CharField(max_length=100, null=True, blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    dispensed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table = 'pharmacy_form'

    def __str__(self):
        return f"Form {self.form_id} - {self.buyer_name}"
