
from django.db import transaction
from collections import defaultdict
from decimal import Decimal
import json
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.forms import formset_factory
from .models import (
    LpacemakerDrugs,
    NcapDrugs,
    OncologyPharmacy,
    Cart,
    Form,
    FormItem,
)
from .forms import *
from django.contrib import messages
from django.db import transaction
from datetime import datetime, timedelta
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.db.models import Q, F, ExpressionWrapper, Sum, DecimalField
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.db.models.functions import TruncDay
from shortuuid.django_fields import ShortUUIDField
from .forms import UserRegistrationForm
from django.contrib.auth.forms import PasswordChangeForm
from .forms import UserProfileForm, ProfileForm, CustomPasswordChangeForm

# Create your views here.
def is_admin(user):
    return user.is_authenticated and user.is_superuser or user.is_staff



def index(request):
    # If user is already authenticated, redirect to dashboard
    if request.user.is_authenticated:
        return redirect('store:dashboard')

    # Handle login form submission
    if request.method == 'POST':
        mobile = request.POST.get('mobile')
        password = request.POST.get('password')
        next_url = request.POST.get('next') or request.GET.get('next') or 'store:dashboard'

        user = authenticate(request, mobile=mobile, password=password)
        if user is not None:
            login(request, user)
            # Redirect to next URL if it's provided and safe
            if next_url and next_url.startswith('/'):
                return redirect(next_url)
            return redirect('store:dashboard')
        else:
            messages.error(request, 'Invalid mobile number or password')
            # Keep the next parameter in the URL when showing the error
            if next_url:
                return redirect(f'{reverse("store:index")}?next={next_url}')

    return render(request, 'store/index.html')


@login_required
def dashboard(request):
    context = {
        'lpacemaker_count': LpacemakerDrugs.objects.count(),
        'ncap_count': NcapDrugs.objects.count(),
        'oncology_count': OncologyPharmacy.objects.count(),
    }
    return render(request, 'store/dashboard.html', context)


def logout_user(request):
    logout(request)
    return redirect('store:index')





@login_required
def store(request):
    # Get all drugs from different categories
    lpacemaker_drugs = LpacemakerDrugs.objects.all().order_by('name')
    ncap_drugs = NcapDrugs.objects.all().order_by('name')
    oncology_drugs = OncologyPharmacy.objects.all().order_by('name')

    # Calculate statistics for each category
    lpacemaker_stats = {
        'total_items': lpacemaker_drugs.count(),
        'total_stock_value': sum(drug.price * drug.stock for drug in lpacemaker_drugs),
        'low_stock_items': [drug for drug in lpacemaker_drugs if drug.stock < 10]
    }

    ncap_stats = {
        'total_items': ncap_drugs.count(),
        'total_stock_value': sum(drug.price * drug.stock for drug in ncap_drugs),
        'low_stock_items': [drug for drug in ncap_drugs if drug.stock < 10]
    }

    oncology_stats = {
        'total_items': oncology_drugs.count(),
        'total_stock_value': sum(drug.price * drug.stock for drug in oncology_drugs),
        'low_stock_items': [drug for drug in oncology_drugs if drug.stock < 10]
    }

    context = {
        'lpacemaker_drugs': lpacemaker_drugs,
        'ncap_drugs': ncap_drugs,
        'oncology_drugs': oncology_drugs,
        'lpacemaker_stats': lpacemaker_stats,
        'ncap_stats': ncap_stats,
        'oncology_stats': oncology_stats,
    }

    return render(request, 'store/store.html', context)



@login_required
@user_passes_test(is_admin)
def add_item(request):
    if request.method == 'POST':
        store_type = request.POST.get('store_type')

        # Select the appropriate form based on store type
        form_classes = {
            'lpacemaker': LpacemakerDrugsForm,
            'ncap': NcapDrugsForm,
            'oncology': OncologyPharmacyForm
        }

        FormClass = form_classes.get(store_type)
        if not FormClass:
            messages.error(request, 'Invalid store type selected')
            return redirect('store:add_item')

        form = FormClass(request.POST)
        if form.is_valid():
            item = form.save()
            messages.success(request, f'Item added successfully to {store_type.upper()} store')
            return redirect('store:store')
        else:
            messages.error(request, 'Error creating item')
    else:
        form = None  # Form will be selected based on store type

    context = {
        'form': form,
        'dosage_forms': DOSAGE_FORM,
        'units': UNIT,
    }

    if request.headers.get('HX-Request'):
        return render(request, 'partials/add_item_modal.html', context)
    return render(request, 'store/add_item.html', context)



@login_required
def search_item(request):
    if not request.user.is_authenticated:
        return redirect('store:index')

    query = request.GET.get('search', '').strip()
    if query:
        # Search across all drug models
        lpacemaker_results = LpacemakerDrugs.objects.filter(
            Q(name__icontains=query) | Q(brand__icontains=query)
        )
        ncap_results = NcapDrugs.objects.filter(
            Q(name__icontains=query) | Q(brand__icontains=query)
        )
        oncology_results = OncologyPharmacy.objects.filter(
            Q(name__icontains=query) | Q(brand__icontains=query)
        )

        context = {
            'lpacemaker_items': lpacemaker_results,
            'ncap_items': ncap_results,
            'oncology_items': oncology_results,
        }
    else:
        context = {
            'lpacemaker_items': LpacemakerDrugs.objects.all(),
            'ncap_items': NcapDrugs.objects.all(),
            'oncology_items': OncologyPharmacy.objects.all(),
        }
    return render(request, 'partials/search_item.html', context)


@login_required
def dispense(request):
    if not request.user.is_authenticated:
        return redirect('store:index')

    query = request.GET.get('search', '').strip()
    category = request.GET.get('category', 'all')

    results = {
        'lpacemaker_items': [],
        'ncap_items': [],
        'oncology_items': []
    }

    if query or category != 'all':
        search_filter = Q(name__icontains=query) | Q(brand__icontains=query)

        if category in ['all', 'lpacemaker']:
            results['lpacemaker_items'] = LpacemakerDrugs.objects.filter(
                search_filter, stock__gt=0
            )

        if category in ['all', 'ncap']:
            results['ncap_items'] = NcapDrugs.objects.filter(
                search_filter, stock__gt=0
            )

        if category in ['all', 'oncology']:
            results['oncology_items'] = OncologyPharmacy.objects.filter(
                search_filter, stock__gt=0
            )

    context = {
        'results': results,
        'query': query,
        'category': category
    }

    if request.headers.get('HX-Request'):
        return render(request, 'partials/dispense_results.html', context)
    return render(request, 'store/dispense.html', context)


@login_required
def cart(request):
    if not request.user.is_authenticated:
        return redirect('store:index')

    cart_items = Cart.objects.filter(user=request.user)
    total_price = sum(item.subtotal for item in cart_items)
    final_total = total_price  # Since we removed discounts

    return render(request, 'store/cart.html', {
        'cart_items': cart_items,
        'total_price': total_price,
        'final_total': final_total
    })


@login_required
@require_POST
def add_to_cart(request, pk, drug_type):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)

    drug_models = {
        'lpacemaker': LpacemakerDrugs,
        'ncap': NcapDrugs,
        'oncology': OncologyPharmacy
    }

    DrugModel = drug_models.get(drug_type)
    if not DrugModel:
        return JsonResponse({'error': 'Invalid drug type'}, status=400)

    try:
        drug = get_object_or_404(DrugModel, id=pk)
        quantity = int(request.POST.get('quantity', 1))
        unit = request.POST.get('unit')

        if quantity <= 0:
            messages.error(request, 'Quantity must be greater than zero')
            return redirect('store:dispense')

        if quantity > drug.stock:
            messages.error(request, f'Not enough stock. Available: {drug.stock}')
            return redirect('store:dispense')

        with transaction.atomic():
            # Create or update cart item
            cart_kwargs = {
                'user': request.user,
                f'{drug_type}_drug': drug,
                'unit': unit,
                'price': drug.price
            }

            cart_item, created = Cart.objects.get_or_create(
                user=request.user,
                **{f'{drug_type}_drug': drug},
                defaults=cart_kwargs
            )

            if not created:
                cart_item.quantity += quantity
                cart_item.save()
            else:
                cart_item.quantity = quantity
                cart_item.save()

            # Update stock quantity
            drug.stock -= quantity
            drug.save()

            messages.success(request, f'Added {quantity} {unit} of {drug.name} to cart')
            return redirect('store:cart')

    except Exception as e:
        messages.error(request, f'Error adding to cart: {str(e)}')
        return redirect('store:dispense')



@login_required
@require_POST
def quick_dispense(request, drug_type, pk):
    if not request.user.is_authenticated:
        return redirect('store:index')

    drug_models = {
        'lpacemaker': LpacemakerDrugs,
        'ncap': NcapDrugs,
        'oncology': OncologyPharmacy
    }

    DrugModel = drug_models.get(drug_type)
    if not DrugModel:
        return HttpResponse("Invalid drug type", status=400)

    try:
        drug = DrugModel.objects.get(pk=pk)
        quantity = int(request.POST.get('quantity', 1))

        if quantity <= 0:
            return HttpResponse("Quantity must be greater than zero", status=400)

        if quantity > drug.stock:
            return HttpResponse(f"Not enough stock. Available: {drug.stock}", status=400)

        cart_kwargs = {
            'user': request.user,
            f'{drug_type}_drug': drug,
            'unit': drug.unit,
            'quantity': quantity,
            'price': drug.price
        }

        cart_item, created = Cart.objects.get_or_create(
            user=request.user,
            **{f'{drug_type}_drug': drug},
            defaults=cart_kwargs
        )

        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        drug.stock -= quantity
        drug.save()

        if request.headers.get('HX-Request'):
            return HttpResponse(
                f'<div class="alert alert-success">Added {quantity} {drug.unit} of {drug.name} to cart</div>',
                status=200
            )
        return redirect('store:dispense')

    except Exception as e:
        return HttpResponse(str(e), status=500)



@login_required
def view_cart(request):
    if request.user.is_authenticated:
        cart_items = Cart.objects.select_related('item').all()
        total_price, total_discount = 0, 0

        if request.method == 'POST':
            # Process each discount form submission
            for cart_item in cart_items:
                # Fetch the discount amount using cart_item.id in the input name
                discount = Decimal(request.POST.get(f'discount_amount-{cart_item.id}', 0))
                cart_item.discount_amount = max(discount, 0)
                cart_item.save()

        # Calculate totals
        for cart_item in cart_items:
            cart_item.subtotal = cart_item.item.price * cart_item.quantity
            total_price += cart_item.subtotal
            # total_discount += cart_item.discount_amount


        final_total = total_price - total_discount

        total_discounted_price = total_price - total_discount
        return render(request, 'store/cart.html', {
            'cart_items': cart_items,
            'total_discount': total_discount,
            'total_price': total_price,
            'total_discounted_price': total_discounted_price,
            'final_total': final_total,
        })
    else:
        return redirect('store:index')



@login_required
@require_POST
def update_cart(request, pk):
    if request.user.is_authenticated:
        cart_item = get_object_or_404(Cart, id=pk, user=request.user)

        if request.method == 'POST':
            try:
                new_quantity = int(request.POST.get('quantity', 0))
                drug = cart_item.get_item

                if new_quantity <= 0:
                    messages.error(request, "Quantity must be greater than zero")
                    return redirect('store:cart')

                quantity_diff = new_quantity - cart_item.quantity

                if quantity_diff > 0 and quantity_diff > drug.stock:
                    messages.error(request, f"Not enough stock. Available: {drug.stock}")
                    return redirect('store:cart')

                with transaction.atomic():
                    # Update stock
                    drug.stock -= quantity_diff
                    drug.save()

                    # Update cart item
                    cart_item.quantity = new_quantity
                    cart_item.save()

                    messages.success(request, f"Cart updated successfully. New quantity: {new_quantity}")

            except ValueError:
                messages.error(request, "Invalid quantity provided")
            except Exception as e:
                messages.error(request, f"Error updating cart: {str(e)}")

        return redirect('store:cart')

    return redirect('store:index')



@login_required
@require_POST
def remove_from_cart(request, pk):
    if request.user.is_authenticated:
        cart_item = get_object_or_404(Cart, id=pk, user=request.user)

        try:
            with transaction.atomic():
                drug = cart_item.get_item
                quantity_returned = cart_item.quantity

                if drug:
                    # Return quantity to stock
                    drug.stock += quantity_returned
                    drug.save()

                    # Create DispensingLog entry for removal
                    # DispensingLog.objects.create(
                    #     user=request.user,
                    #     name=drug.name,
                    #     quantity=quantity_returned,
                    #     amount=drug.price * quantity_returned,
                    #     action='removed'
                    # )

                # Delete cart item
                cart_item.delete()
                messages.success(request, f"{quantity_returned} {drug.unit} of {drug.name} removed from cart")

        except Exception as e:
            messages.error(request, f"Error removing item: {str(e)}")

        return redirect('store:cart')

    return redirect('store:index')


@login_required
@require_POST
def clear_cart(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            cart_items = Cart.objects.filter(user=request.user)

            with transaction.atomic():
                for cart_item in cart_items:
                    # Return items to stock
                    drug = cart_item.get_item
                    if drug:
                        drug.stock += cart_item.quantity
                        drug.save()

                # Clear cart items
                cart_items.delete()
                messages.success(request, 'Cart cleared and items returned to stock.')

            if request.headers.get('HX-Request'):
                return render(request, 'partials/cart_items.html', {
                    'cart_items': [],
                    'total_price': 0,
                    'final_total': 0
                })

            return redirect('store:cart')

    return redirect('store:index')


@login_required
def receipt(request):
    if not request.user.is_authenticated:
        return redirect('store:index')

    if request.method != 'POST':
        return redirect('store:cart')

    cart_items = Cart.objects.filter(user=request.user).select_related('lpacemaker_drug', 'ncap_drug', 'oncology_drug')
    if not cart_items.exists():
        messages.warning(request, "No items in the cart.")
        return redirect('store:cart')

    total_price = sum(item.subtotal for item in cart_items)

    try:
        with transaction.atomic():
            # Create form
            form = Form.objects.create(
                total_amount=total_price,
                buyer_name=request.POST.get('buyer_name'),
                hospital_no=request.POST.get('hospital_no'),
                ncap_no=request.POST.get('ncap_no'),
                dispensed_by=request.user
            )

            # Create FormItem records for each cart item
            for cart_item in cart_items:
                drug = None
                drug_type = None

                if cart_item.lpacemaker_drug:
                    drug = cart_item.lpacemaker_drug
                    drug_type = 'LPACEMAKER'
                elif cart_item.ncap_drug:
                    drug = cart_item.ncap_drug
                    drug_type = 'NCAP'
                elif cart_item.oncology_drug:
                    drug = cart_item.oncology_drug
                    drug_type = 'ONCOLOGY'

                if drug:
                    FormItem.objects.create(
                        form=form,
                        drug_name=drug.name,
                        drug_brand=drug.brand,
                        drug_type=drug_type,
                        unit=cart_item.unit,
                        quantity=cart_item.quantity,
                        price=drug.price,
                        subtotal=cart_item.subtotal
                    )

            # Store cart items for context before clearing
            cart_items_for_context = list(cart_items)

            # Clear the cart without returning items to stock
            # since they are being dispensed
            cart_items.delete()
            messages.success(request, 'Form generated successfully and cart cleared.')

            context = {
                'form': form,
                'cart_items': cart_items_for_context,
                'total_price': total_price,
                'user': request.user,
            }

            return render(request, 'store/receipt.html', context)

    except Exception as e:
        print(f"Error processing receipt: {e}")
        messages.error(request, "An error occurred while processing the receipt.")
        return redirect('store:cart')


@login_required
def receipt_detail(request, receipt_id):
    receipt = get_object_or_404(Receipt, receipt_id=receipt_id)
    sales_items = SalesItem.objects.filter(receipt=receipt)

    if request.method == 'POST':
        # Only update buyer_name if there's no customer associated
        if not receipt.customer:
            receipt.buyer_name = request.POST.get('buyer_name', '').strip() or 'WALK-IN CUSTOMER'
        receipt.buyer_address = request.POST.get('buyer_address', '')
        receipt.payment_method = request.POST.get('payment_method', '')
        receipt.save()

    context = {
        'receipt': receipt,
        'sales_items': sales_items,
        'user': request.user,
    }
    return render(request, 'partials/receipt_detail.html', context)


@login_required
@user_passes_test(is_admin)
def return_lpacemaker_item(request, pk):
    try:
        drug = get_object_or_404(LpacemakerDrugs, pk=pk)

        if request.method == "POST":
            return_quantity = int(request.POST.get('return_quantity', 0))
            if return_quantity > 0:
                drug.stock += return_quantity
                drug.save()
                messages.success(request, f'Successfully returned {return_quantity} {drug.unit} of {drug.name}')
                return redirect('store:store')
            else:
                messages.error(request, 'Please enter a valid quantity')

        return render(request, 'store/return_item_modal.html', {
            'drug': drug,
            'drug_type': 'lpacemaker'
        })

    except Exception as e:
        messages.error(request, f'Error processing return: {str(e)}')
        return HttpResponse(str(e), status=400)

@login_required
@user_passes_test(is_admin)
def return_ncap_item(request, pk):
    try:
        drug = get_object_or_404(NcapDrugs, pk=pk)

        if request.method == "POST":
            return_quantity = int(request.POST.get('return_quantity', 0))
            if return_quantity > 0:
                drug.stock += return_quantity
                drug.save()
                messages.success(request, f'Successfully returned {return_quantity} {drug.unit} of {drug.name}')
                return redirect('store:store')
            else:
                messages.error(request, 'Please enter a valid quantity')

        return render(request, 'store/return_item_modal.html', {
            'drug': drug,
            'drug_type': 'ncap'
        })

    except Exception as e:
        messages.error(request, f'Error processing return: {str(e)}')
        return HttpResponse(str(e), status=400)

@login_required
@user_passes_test(is_admin)
def return_oncology_item(request, pk):
    try:
        drug = get_object_or_404(OncologyPharmacy, pk=pk)

        if request.method == "POST":
            return_quantity = int(request.POST.get('return_quantity', 0))
            if return_quantity > 0:
                drug.stock += return_quantity
                drug.save()
                messages.success(request, f'Successfully returned {return_quantity} {drug.unit} of {drug.name}')
                return redirect('store:store')
            else:
                messages.error(request, 'Please enter a valid quantity')

        return render(request, 'store/return_item_modal.html', {
            'drug': drug,
            'drug_type': 'oncology'
        })

    except Exception as e:
        messages.error(request, f'Error processing return: {str(e)}')
        return HttpResponse(str(e), status=400)


@login_required
@user_passes_test(is_admin)
def delete_item(request, drug_type, pk):
    if not request.user.is_authenticated:
        return redirect('store:index')

    drug_models = {
        'lpacemaker': LpacemakerDrugs,
        'ncap': NcapDrugs,
        'oncology': OncologyPharmacy
    }

    DrugModel = drug_models.get(drug_type)
    if not DrugModel:
        messages.error(request, 'Invalid drug type')
        return redirect('store:store')

    try:
        drug = get_object_or_404(DrugModel, pk=pk)
        drug.delete()
        messages.success(request, 'Item deleted successfully')
    except Exception as e:
        messages.error(request, f'Error deleting item: {str(e)}')

    return redirect('store:store')

def get_daily_sales():
    # Fetch daily sales data
    regular_sales = (
        SalesItem.objects
        .annotate(day=TruncDay('sales__date'))
        .values('day')
        .annotate(
            total_sales=Sum(F('price') * F('quantity')),
            total_cost=Sum(F('item__cost') * F('quantity')),
            total_profit=ExpressionWrapper(
                Sum(F('price') * F('quantity')) - Sum(F('item__cost') * F('quantity')),
                output_field=DecimalField()
            )
        )
    )

    wholesale_sales = (
        WholesaleSalesItem.objects
        .annotate(day=TruncDay('sales__date'))
        .values('day')
        .annotate(
            total_sales=Sum(F('price') * F('quantity')),
            total_cost=Sum(F('item__cost') * F('quantity')),
            total_profit=ExpressionWrapper(
                Sum(F('price') * F('quantity')) - sum(F('item__cost') * F('quantity')),
                output_field=DecimalField()
            )
        )
    )

    # Combine results
    combined_sales = defaultdict(lambda: {'total_sales': 0, 'total_cost': 0, 'total_profit': 0})

    for sale in regular_sales:
        day = sale['day']
        combined_sales[day]['total_sales'] += sale['total_sales']
        combined_sales[day]['total_cost'] += sale['total_cost']
        combined_sales[day]['total_profit'] += sale['total_profit']

    for sale in wholesale_sales:
        day = sale['day']
        combined_sales[day]['total_sales'] += sale['total_sales']
        combined_sales[day]['total_cost'] += sale['total_cost']
        combined_sales[day]['total_profit'] += sale['total_profit']

    # Convert combined sales to a sorted list by date in descending order
    sorted_combined_sales = sorted(combined_sales.items(), key=lambda x: x[0], reverse=True)

    return sorted_combined_sales

@login_required
@require_POST
def remove_from_cart(request, pk):
    if not request.user.is_authenticated:
        return redirect('store:index')

    cart_item = get_object_or_404(Cart, id=pk, user=request.user)

    try:
        with transaction.atomic():
            # Return the quantity back to stock
            drug = cart_item.get_item
            if drug:
                drug.stock += cart_item.quantity
                drug.save()

            # Delete the cart item
            cart_item.delete()

            # Calculate new totals
            cart_items = Cart.objects.filter(user=request.user)
            total_price = sum(item.subtotal for item in cart_items)

            if request.headers.get('HX-Request'):
                return JsonResponse({
                    'total_price': float(total_price),
                    'cart_count': cart_items.count(),
                })

            messages.success(request, "Item removed from cart successfully.")

    except Exception as e:
        messages.error(request, f"Error removing item: {str(e)}")

    return redirect('store:cart')

@login_required
@user_passes_test(is_admin)
def edit_item(request, drug_type, pk):
    drug_models = {
        'lpacemaker': LpacemakerDrugs,
        'ncap': NcapDrugs,
        'oncology': OncologyPharmacy
    }

    DrugModel = drug_models.get(drug_type)
    if not DrugModel:
        messages.error(request, 'Invalid drug type')
        return redirect('store:store')

    drug = get_object_or_404(DrugModel, pk=pk)

    if request.method == 'POST':
        form_classes = {
            'lpacemaker': LpacemakerDrugsForm,
            'ncap': NcapDrugsForm,
            'oncology': OncologyPharmacyForm
        }
        FormClass = form_classes.get(drug_type)
        form = FormClass(request.POST, instance=drug)

        if form.is_valid():
            form.save()
            messages.success(request, f'Item updated successfully')
            return redirect('store:store')
    else:
        form_classes = {
            'lpacemaker': LpacemakerDrugsForm,
            'ncap': NcapDrugsForm,
            'oncology': OncologyPharmacyForm
        }
        FormClass = form_classes.get(drug_type)
        form = FormClass(instance=drug)

    context = {
        'form': form,
        'drug': drug,
        'drug_type': drug_type,
        'dosage_forms': DOSAGE_FORM,
        'units': UNIT,
    }

    if request.headers.get('HX-Request'):
        return render(request, 'partials/edit_item_modal.html', context)
    return render(request, 'store/edit_item.html', context)

@login_required
@user_passes_test(is_admin)
def register_user(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_staff = form.cleaned_data.get('is_staff', False)
            user.save()
            messages.success(request, f'User {user.username} has been created successfully!')
            return redirect('store:dashboard')
    else:
        form = UserRegistrationForm()

    return render(request, 'store/register.html', {'form': form})

@login_required
def profile(request):
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'update_profile':
            user_form = UserProfileForm(request.POST, instance=request.user)
            profile_form = ProfileForm(request.POST, instance=request.user.profile)

            if user_form.is_valid() and profile_form.is_valid():
                with transaction.atomic():
                    user_form.save()
                    profile_form.save()
                messages.success(request, 'Your profile has been updated successfully!')
                return redirect('store:profile')

        elif action == 'change_password':
            password_form = CustomPasswordChangeForm(request.user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Your password was successfully updated!')
                return redirect('store:profile')
            else:
                messages.error(request, 'Please correct the error below.')
    else:
        user_form = UserProfileForm(instance=request.user)
        profile_form = ProfileForm(instance=request.user.profile)
        password_form = CustomPasswordChangeForm(request.user)

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'password_form': password_form,
    }
    return render(request, 'store/profile.html', context)

@login_required
def view_form(request, form_id):
    # Get the form with its related items
    form = get_object_or_404(Form, form_id=form_id)

    # Get form items
    form_items = FormItem.objects.filter(form=form)

    # Prepare items for display
    items = []

    for form_item in form_items:
        items.append({
            'name': form_item.drug_name,
            'brand': form_item.drug_brand,
            'unit': form_item.unit,
            'quantity': form_item.quantity,
            'price': form_item.price,
            'subtotal': form_item.subtotal,
            'drug_type': form_item.drug_type
        })

    # If no items were found, display a message
    total_amount = sum(item['subtotal'] for item in items) if items else form.total_amount

    context = {
        'form': form,
        'items': items,
        'total_amount': total_amount
    }

    return render(request, 'store/form_detail.html', context)

@login_required
def form_list(request):
    forms = Form.objects.all().order_by('-date')

    context = {
        'forms': forms,
    }

    if request.headers.get('HX-Request'):
        return render(request, 'partials/form_list.html', context)
    return render(request, 'store/forms.html', context)
