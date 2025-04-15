from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    path('', views.index, name='index'),
    path('store/', views.store, name='store'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dispense/', views.dispense, name='dispense'),
    path('cart/', views.cart, name='cart'),
    path('receipt/', views.receipt, name='receipt'),
    path('receipt/<str:receipt_id>/', views.receipt_detail, name='receipt_detail'),
    path('logout/', views.logout_user, name='logout_user'),
    path('add-item/', views.add_item, name='add_item'),
    path('edit-item/<str:drug_type>/<int:pk>/', views.edit_item, name='edit_item'),
    path('delete-item/<str:drug_type>/<int:pk>/', views.delete_item, name='delete_item'),

    # Cart management
    path('cart/clear/', views.clear_cart, name='clear_cart'),

    # Separate return item URLs for each drug type
    path('return/lpacemaker/<int:pk>/', views.return_lpacemaker_item, name='return_lpacemaker_item'),
    path('return/ncap/<int:pk>/', views.return_ncap_item, name='return_ncap_item'),
    path('return/oncology/<int:pk>/', views.return_oncology_item, name='return_oncology_item'),

    # HTMX endpoints
    path('quick-dispense/<str:drug_type>/<int:pk>/', views.quick_dispense, name='quick_dispense'),
    path('add-to-cart/<str:drug_type>/<int:pk>/', views.add_to_cart, name='add_to_cart'),
    path('update-cart/<int:pk>/', views.update_cart, name='update_cart'),
    path('remove-from-cart/<int:pk>/', views.remove_from_cart, name='remove_from_cart'),
    path('search/', views.search_item, name='search_items'),
    path('register/', views.register_user, name='register'),
    path('profile/', views.profile, name='profile'),
    path('forms/', views.form_list, name='forms'),
    path('forms/<str:form_id>/', views.view_form, name='view_form'),
    path('forms/<str:form_id>/edit/', views.edit_form, name='edit_form'),
    path('forms/<str:form_id>/items/add/', views.add_form_item, name='add_form_item'),
    path('forms/<str:form_id>/items/<int:item_id>/edit/', views.edit_form_item, name='edit_form_item'),
    path('forms/<str:form_id>/items/<int:item_id>/remove/', views.remove_form_item, name='remove_form_item'),
]
