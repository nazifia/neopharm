from . models import *
from django import forms
from django.contrib.auth.forms import UserChangeForm, UserCreationForm, PasswordChangeForm
from .models import LpacemakerDrugs, NcapDrugs, OncologyPharmacy, User, Profile

class LpacemakerDrugsForm(forms.ModelForm):
    class Meta:
        model = LpacemakerDrugs
        fields = ['name', 'dosage_form', 'brand', 'unit', 'price', 'stock', 'exp_date']
        widgets = {
            'exp_date': forms.DateInput(attrs={'type': 'date'}),
        }

class NcapDrugsForm(forms.ModelForm):
    class Meta:
        model = NcapDrugs
        fields = ['name', 'dosage_form', 'brand', 'unit', 'price', 'stock', 'exp_date']
        widgets = {
            'exp_date': forms.DateInput(attrs={'type': 'date'}),
        }

class OncologyPharmacyForm(forms.ModelForm):
    class Meta:
        model = OncologyPharmacy
        fields = ['name', 'dosage_form', 'brand', 'unit', 'price', 'stock', 'exp_date']
        widgets = {
            'exp_date': forms.DateInput(attrs={'type': 'date'}),
        }

class DispenseSearchForm(forms.Form):
    search = forms.CharField(required=False)
    category = forms.ChoiceField(choices=[
        ('all', 'All Categories'),
        ('lpacemaker', 'Lpacemaker Drugs'),
        ('ncap', 'NCAP Drugs'),
        ('oncology', 'Oncology Pharmacy')
    ], required=False)

class EditUserProfileForm(UserChangeForm):

    class Meta:
        model = User
        fields = ['username', 'password', 'first_name', 'last_name']


class addItemForm(forms.ModelForm):
    name = forms.CharField(max_length=200)
    dosage_form = forms.ChoiceField(
        choices=[
            ('Unit', 'Dosage form'),
            ('Tablet', 'Tablet'),
            ('Capsule', 'Capsule'),
            ('Consumable', 'Consumable'),
            ('Cream', 'Cream'),
            ('Syrup', 'Syrup'),
            ('Suspension', 'Suspension'),
            ('Eye-drop', 'Eye-drop'),
            ('Ear-drop', 'Ear-drop'),
            ('Eye-ointment', 'Eye-ointment'),
            ('Nasal', 'Nasal'),
            ('Injection', 'Injection'),
            ('Infusion', 'Infusion'),
            ('Inhaler', 'Inhaler'),
            ('Vaginal', 'Vaginal'),
            ('Rectal', 'Rectal'),
        ],
        widget=forms.Select(attrs={'class': 'form-control mt-3'}),
    )
    brand = forms.CharField(max_length=200)
    unit = forms.CharField(max_length=200)
    cost = forms.DecimalField(max_digits=12, decimal_places=2)
    markup = forms.DecimalField(max_digits=6, decimal_places=2)
    stock = forms.IntegerField()
    exp_date = forms.DateField()

    class Meta:
        model = LpacemakerDrugs
        fields = ('name', 'dosage_form', 'brand', 'unit', 'cost', 'markup', 'stock', 'exp_date')



class dispenseForm(forms.Form):
    q = forms.CharField(min_length=2, label='', widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder':'SEARCH  HERE...'}))



class AddFundsForm(forms.Form):
    amount = forms.DecimalField(max_digits=10, decimal_places=2)



class ReturnItemForm(forms.Form):
    return_quantity = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter quantity to return'
        })
    )
    drug_type = forms.CharField(widget=forms.HiddenInput())
    drug_id = forms.IntegerField(widget=forms.HiddenInput())
    return_reason = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control mb-3', 'rows': 3}),
        required=True,
        label="Reason for Return"
    )

    def clean_return_quantity(self):
        quantity = self.cleaned_data.get('return_quantity')
        if quantity <= 0:
            raise forms.ValidationError("Return quantity must be greater than zero.")
        return quantity

class UserRegistrationForm(UserCreationForm):
    username = forms.CharField(max_length=200, required=True)
    mobile = forms.CharField(max_length=20, required=True)
    is_staff = forms.BooleanField(required=False, label='Staff Status')

    class Meta:
        model = User
        fields = ('username', 'mobile', 'password1', 'password2', 'is_staff')

    def clean_mobile(self):
        mobile = self.cleaned_data.get('mobile')
        if User.objects.filter(mobile=mobile).exists():
            raise forms.ValidationError("This mobile number is already registered.")
        return mobile

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'mobile']


class EditFormForm(forms.ModelForm):
    class Meta:
        model = Form
        fields = ['buyer_name', 'hospital_no', 'ncap_no']
        widgets = {
            'buyer_name': forms.TextInput(attrs={'class': 'form-control'}),
            'hospital_no': forms.TextInput(attrs={'class': 'form-control'}),
            'ncap_no': forms.TextInput(attrs={'class': 'form-control'}),
        }


class FormItemForm(forms.ModelForm):
    class Meta:
        model = FormItem
        fields = ['drug_name', 'drug_brand', 'drug_type', 'unit', 'quantity', 'price']
        widgets = {
            'drug_name': forms.TextInput(attrs={'class': 'form-control'}),
            'drug_brand': forms.TextInput(attrs={'class': 'form-control'}),
            'drug_type': forms.Select(attrs={'class': 'form-control'}, choices=[
                ('LPACEMAKER', 'LPACEMAKER'),
                ('NCAP', 'NCAP'),
                ('ONCOLOGY', 'ONCOLOGY'),
            ]),
            'unit': forms.Select(attrs={'class': 'form-control'}, choices=UNIT),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        quantity = cleaned_data.get('quantity')
        price = cleaned_data.get('price')

        if quantity and price:
            # Calculate subtotal
            cleaned_data['subtotal'] = quantity * price

        return cleaned_data

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['full_name', 'user_type']

class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to all fields
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
