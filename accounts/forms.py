from django import forms
from django.forms import inlineformset_factory
from .models import Invoice, InvoiceItem

class InvoiceForm(forms.ModelForm):
    """Form for creating and editing invoices"""
    class Meta:
        model = Invoice
        fields = [
            'invoice_number', 'date', 'due_date', 'bill_to', 'ship_to',
            'payment_terms', 'po_number', 'notes', 'terms', 'tax',
            'shipping', 'discount', 'amount_paid'
        ]
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'bill_to': forms.Textarea(attrs={'rows': 3}),
            'ship_to': forms.Textarea(attrs={'rows': 3}),
            'notes': forms.Textarea(attrs={'rows': 3}),
            'terms': forms.Textarea(attrs={'rows': 3}),
        }

class InvoiceItemForm(forms.ModelForm):
    """Form for invoice line items"""
    class Meta:
        model = InvoiceItem
        fields = ['description', 'quantity', 'rate']
        widgets = {
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control item-quantity'}),
            'rate': forms.NumberInput(attrs={'class': 'form-control item-rate'}),
        }

# Create a formset for invoice items
InvoiceItemFormSet = inlineformset_factory(
    Invoice, 
    InvoiceItem,
    form=InvoiceItemForm,
    extra=1,  # Number of empty forms to display
    can_delete=True  # Allow removing items
)