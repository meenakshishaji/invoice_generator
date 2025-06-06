from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
   
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    business_name = models.CharField(max_length=255, blank=True, null=True)
    default_currency = models.CharField(max_length=3, default='USD')
    default_tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    default_payment_terms = models.CharField(max_length=255, blank=True, null=True)
    default_notes = models.TextField(blank=True, null=True)
    default_terms = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
 
    instance.profile.save()

class Invoice(models.Model):
   
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    invoice_number = models.CharField(max_length=50)
    from_name = models.CharField(max_length=255)
    bill_to = models.CharField(max_length=255)
    ship_to = models.CharField(max_length=255, blank=True, null=True)
    invoice_date = models.DateField(null=True, blank=True)

    payment_terms = models.CharField(max_length=255, blank=True, null=True)
    due_date = models.DateField(null=True, blank=True)
    po_number = models.CharField(max_length=50, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    terms = models.TextField(blank=True, null=True)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    currency = models.CharField(max_length=3, default='USD')
    logo = models.ImageField(upload_to='invoice_logos/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    from_name = models.CharField(max_length=100, default="YourCompanyName")

    def __str__(self):
        return f"Invoice #{self.invoice_number} - {self.bill_to}"
    
    @property
    def subtotal(self):
        
        return sum(item.amount for item in self.items.all())
    
    @property
    def tax_amount(self):
       
        return self.subtotal * (self.tax_rate / 100)
    
    @property
    def total(self):
        
        return self.subtotal + self.tax_amount
    
    @property
    def balance_due(self):
      
        return self.total - self.amount_paid


class InvoiceItem(models.Model):
   
    invoice = models.ForeignKey(Invoice, related_name='items', on_delete=models.CASCADE)
    description = models.CharField(max_length=255)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    rate = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    def __str__(self):
        return f"{self.description} - {self.invoice.invoice_number}"
    
    @property
    def amount(self):
        
        return self.quantity * self.rate