from django.urls import path
from . import views
#from django.contrib.auth import views as auth_views

urlpatterns = [
    #path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
   
    path('', views.dashboard, name='dashboard'),
    path('invoice/new/', views.new_invoice, name='new_invoice'),
    #path('invoice/save/', views.save_invoice, name='save_invoice'),
   
    #path('invoice/template/', views.create_invoice, name='invoice_template'),
    path('create-invoice/', views.create_invoice, name='create_invoice'),
    path('save-invoice/', views.save_invoice, name='save_invoice'),
    path('invoice/<int:id>/', views.view_invoice, name='view_invoice'),
    path('edit-invoice/<int:invoice_id>/', views.edit_invoice, name='edit_invoice'),
    path('invoice/delete/<int:id>/', views.delete_invoice, name='delete_invoice'),
    


]



