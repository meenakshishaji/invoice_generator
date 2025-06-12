from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import authenticate, login, logout
#from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import IntegrityError
#from django.http import HttpResponse
from django import forms
from django.http import HttpResponseBadRequest
#from django.template.loader import get_template
from datetime import datetime
from .models import Invoice, InvoiceItem, UserProfile
from django.core.files.storage import FileSystemStorage

# Custom forms
class UserSignupForm(forms.Form):
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    terms = forms.BooleanField(required=True)

class UserLoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    remember_me = forms.BooleanField(required=False)



# Login view
def login_view(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            remember_me = form.cleaned_data.get('remember_me')
            
            try:
                user = User.objects.get(email=email)#Attempts to find a User object in the database with the given email.
                user = authenticate(request, username=user.username, password=password)
                
                if user is not None:
                    login(request, user)
                    
                    
                    if not remember_me:
                        request.session.set_expiry(0)  # Session expires when browser closes
                    
                    return redirect('dashboard')
                else:
                    messages.error(request, 'Invalid email or password.')
            except User.DoesNotExist:
                messages.error(request, 'No account found with this email.')
    else:
        form = UserLoginForm()# blank login form 
    
    return render(request, 'accounts/login.html', {'form': form})

# Signup view ----------------
def signup_view(request):
    if request.method == 'POST':
        form = UserSignupForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            
            try:
                # Create user with email as username
                user = User.objects.create_user(
                    username=email,  
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name
                )
                
                
                login(request, user)
                return redirect('dashboard')
            
            except IntegrityError:
                messages.error(request, 'An account with this email already exists.')
    else:
        form = UserSignupForm()
    
    return render(request, 'accounts/signup.html', {'form': form})

# Logout view
def logout_view(request):
    logout(request)
    return redirect('login')

# ------------dashboard------------------------

@login_required
def dashboard(request):
    invoices = Invoice.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'accounts/dashboard.html', {'invoices': invoices})

@login_required
def new_invoice(request):
    if request.method == "POST":
        client = request.POST.get("client")
        invoice_date = request.POST.get("invoice_date")
        due_date = request.POST.get("due_date")
        total_amount = request.POST.get("total_amount")

        Invoice.objects.create(
            user=request.user,
            client=client,
            invoice_date=invoice_date,
            due_date=due_date,
            total_amount=total_amount
        )
        return redirect("dashboard")

    return render(request, "accounts/invoice_template.html")


# ------------save--------------------------


@login_required
def save_invoice(request):
    if request.method != 'POST':
        return HttpResponseBadRequest("Only POST requests allowed.")
    
    invoice_id = request.POST.get('invoice_id')#existing or to create

    if invoice_id:
        invoice = get_object_or_404(Invoice, id=invoice_id, user=request.user)
        invoice.items.all().delete()
    else:
        invoice = Invoice(user=request.user)

    
    invoice.invoice_number  = request.POST.get('invoice_number', '').strip()
    invoice.from_name       = request.POST.get('from_name',    '').strip()
    invoice.bill_to         = request.POST.get('bill_to',      '').strip()
    invoice.ship_to         = request.POST.get('ship_to',      '').strip()
    invoice.payment_terms   = request.POST.get('payment_terms','').strip()
    invoice.po_number       = request.POST.get('po_number',    '').strip()
    invoice.notes           = request.POST.get('notes',        '').strip()
    invoice.terms           = request.POST.get('terms',        '').strip()
    invoice.currency        = request.POST.get('currency',     'USD').strip()

    
    raw_inv_date = request.POST.get('invoice_date', '').strip()
    if raw_inv_date:
        try:
            invoice.invoice_date = datetime.strptime(raw_inv_date, '%Y-%m-%d').date()
        except ValueError:
            return HttpResponseBadRequest("Invalid invoice_date; use YYYY-MM-DD.")
    else:
        invoice.invoice_date = None

    raw_due_date = request.POST.get('due_date', '').strip()
    if raw_due_date:
        try:
            invoice.due_date = datetime.strptime(raw_due_date, '%Y-%m-%d').date()
        except ValueError:
            return HttpResponseBadRequest("Invalid due_date; use YYYY-MM-DD.")
    else:
        invoice.due_date = None

    # Numeric fields
    try:
        invoice.tax_rate    = float(request.POST.get('tax_rate',    0))
    except ValueError:
        invoice.tax_rate    = 0.0

    try:
        invoice.amount_paid = float(request.POST.get('amount_paid', 0))
    except ValueError:
        invoice.amount_paid = 0.0

    
    if 'logo' in request.FILES:
        invoice.logo = request.FILES['logo'] #If a file was uploaded for the logo, it is assigned to the invoice.

    invoice.save()

    # Gets the total number of line items from the form.
    try:
        total_items = int(request.POST.get('total_items', 0))
    except ValueError:
        total_items = 0

#Loops through each item. If the description is empty, it skips that item.
    for i in range(total_items):
        desc = request.POST.get(f'description_{i}', '').strip()
        if not desc:
            continue
        try:
            qty = int(request.POST.get(f'quantity_{i}', 0))
        except ValueError:
            qty = 0
        try:
            rate = float(request.POST.get(f'rate_{i}', 0))
        except ValueError:
            rate = 0.0

        InvoiceItem.objects.create(
            invoice=invoice,
            description=desc,
            quantity=qty,
            rate=rate
        )

    messages.success(request, 'Invoice saved successfully.')

    return redirect('dashboard')


@login_required

def view_invoice(request, id):
    invoice = get_object_or_404(Invoice, id=id)
    items = InvoiceItem.objects.filter(invoice=invoice)
    return render(request, 'accounts/view_invoice.html', {
        'invoice': invoice,
        'items': items,
    })

@login_required
def create_invoice(request):
    if request.method == 'POST':
        total_items = int(request.POST.get('total_items', 1))
        items = []
        for i in range(total_items):
            description = request.POST.get(f'description_{i}', '')
            quantity = request.POST.get(f'quantity_{i}', 0)
            rate = request.POST.get(f'rate_{i}', 0)
            try:
                amount = float(quantity) * float(rate)
            except:
                amount = 0
            items.append({
                'description': description,
                'quantity': quantity,
                'rate': rate,
                'amount': f'{amount:.2f}',
            })

        # Create an Invoice object and fill fields from the form
        invoice = Invoice(user=request.user)
        invoice.invoice_number  = request.POST.get('invoice_number', '').strip()
        invoice.from_name       = request.POST.get('from', '').strip()
        invoice.bill_to         = request.POST.get('bill_to', '').strip()
        invoice.ship_to         = request.POST.get('ship_to', '').strip()
        invoice.payment_terms   = request.POST.get('payment_terms', '').strip()
        invoice.po_number       = request.POST.get('po_number', '').strip()
        invoice.notes           = request.POST.get('notes', '').strip()
        invoice.terms           = request.POST.get('terms', '').strip()
        invoice.currency        = request.POST.get('currency', 'USD').strip()

        
        raw_inv_date = request.POST.get('invoice_date', '').strip()
        if raw_inv_date:
            try:
                invoice.invoice_date = datetime.strptime(raw_inv_date, '%Y-%m-%d').date()
            except ValueError:
                invoice.invoice_date = None
        else:
            invoice.invoice_date = None#Handles invalid formats by setting dates to None.

        raw_due_date = request.POST.get('due_date', '').strip()
        if raw_due_date:
            try:
                invoice.due_date = datetime.strptime(raw_due_date, '%Y-%m-%d').date()
            except ValueError:
                invoice.due_date = None
        else:
            invoice.due_date = None

        # Numeric fields
        try:
            invoice.tax_rate = float(request.POST.get('tax', 0))
        except ValueError:
            invoice.tax_rate = 0.0

        try:
            invoice.amount_paid = float(request.POST.get('amount_paid', 0))
        except ValueError:
            invoice.amount_paid = 0.0

       
        try:
            invoice.discount = float(request.POST.get('discount', 0))
        except ValueError:
            invoice.discount = 0

        try:
            invoice.shipping = float(request.POST.get('shipping', 0))
        except ValueError:
            invoice.shipping = 0

        
       
        # Logo
        logo_file = request.FILES.get('logo')
        logo_url = None
        if logo_file:
            fs = FileSystemStorage()
            filename = fs.save(logo_file.name, logo_file)
            invoice.logo = logo_file  # Save to DB
            logo_url = fs.url(filename)
       
        if not logo_file and 'logo_url' in request.POST:
           logo_url = request.POST.get('logo_url')

       
        subtotal = sum([float(amount) for amount in request.POST.getlist('amount[]')])
        tax_rate = float(request.POST.get('tax_rate') or 0)
        discount = float(request.POST.get('discount') or 0)
        shipping = float(request.POST.get('shipping') or 0)
        amount_paid = float(request.POST.get('amount_paid') or 0)

        
        
        tax_amount = subtotal * (tax_rate / 100)
        total = subtotal + tax_amount + shipping - discount
        balance_due = total - amount_paid

        invoice.subtotal = subtotal
        invoice.tax_rate = tax_rate
        invoice.discount = discount
        invoice.shipping = shipping
        invoice.total = total
        invoice.amount_paid = amount_paid
        invoice.balance_due = balance_due
  

        invoice.save()

        # Save line items
        for i in range(total_items):
            desc = request.POST.get(f'description_{i}', '').strip()
            if not desc:
                continue
            try:
                qty = int(request.POST.get(f'quantity_{i}', 0))
            except ValueError:
                qty = 0
            try:
                rate = float(request.POST.get(f'rate_{i}', 0))
            except ValueError:
                rate = 0.0
            InvoiceItem.objects.create(
                invoice=invoice,
                description=desc,
                quantity=qty,
                rate=rate
            )

        # Render preview with saved invoice
        
        context = {
            'company_name': request.POST.get('company_name'),
            'invoice_number': request.POST.get('invoice_number'),
            'bill_to': request.POST.get('bill_to'),
            'ship_to': request.POST.get('ship_to'),
            'po_number': request.POST.get('po_number'),
            'logo': logo_url,
            'invoice_date': request.POST.get('invoice_date'),
            'due_date': request.POST.get('due_date'),
            'payment_terms': request.POST.get('payment_terms'),
            'from': request.POST.get('from'),
            'quantity_0': request.POST.get('quantity_0'),
            'rate_0': request.POST.get('rate_0'),
            'amount': request.POST.get('amount'),
            'description_0': request.POST.get('description_0'),
            'subtotal': request.POST.get('subtotal'),
            'discount': request.POST.get('discount'),
            'tax': request.POST.get('tax'),
            'shipping': request.POST.get('shipping'),
            'total': request.POST.get('total'),
            'amount_paid': request.POST.get('amount_paid'),
            'balance_due': request.POST.get('balance_due'),
            'item_range': range(total_items),
            'notes': request.POST.get('notes', ''),
            'terms': request.POST.get('terms', ''),
            'items': items,
            'request': request,

        }

        return render(request, 'accounts/create_invoice.html', context)

    return render(request, 'accounts/invoice_template.html')


# ----------------edit--------------------------

@login_required
def edit_invoice(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id, user=request.user)
    items = invoice.items.all()

    context = {
        'invoice': invoice,
        'items': items,
        'logo_url': invoice.logo.url if invoice.logo else None,
        
    }

    return render(request, 'accounts/invoice_template.html', context)


# ----------------delete--------------------------

def delete_invoice(request, id):
    invoice = get_object_or_404(Invoice, id=id)
    if request.method == "POST":
        invoice.delete()
        return redirect('dashboard')