from django.db import models
from django.contrib.auth.models import AbstractUser

class SubscriptionPlan(models.Model):
    PLAN_CHOICES = [
        ('Free for 7 Days', 'Free for 7 Days'),
        ('Monthly', 'Monthly'),
        ('Quarterly', 'Quarterly'),
        ('Six Months', 'Six Months'),
        ('Yearly', 'Yearly'),
    ]
    name = models.CharField(blank=True, null=True)
    plan_type = models.CharField(max_length=20,choices=PLAN_CHOICES,unique=True)
    price = models.FloatField(default=1)
    description = models.TextField(blank=True, null=True)
    number_of_sub_dairy = models.CharField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_plan_type_display()} - ₹{self.price}"

class User(AbstractUser):
    Role = (
        ('SuperAdmin','SuperAdmin'),
        ('Admin','Admin'),
        ('Customer','Customer'),
        ('Manager','Manager'),
    )
    
    mobile = models.CharField(max_length=12)
    address = models.CharField(max_length=1000,null =True,blank=True)
    role = models.CharField(max_length=12,choices=Role,default='Admin')
    is_active = models.BooleanField(default=True)
    profile_image = models.ImageField(upload_to='profile_images/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} <==> {self.role}"
from django.utils import timezone

    
class MainDairy(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    current_plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE,related_name='main_dairy',null=True,blank=True)
    expiry_date = models.DateTimeField(null=True, blank=True)

    def is_plan_expired(self):
        return not self.current_plan or (self.expiry_date and self.expiry_date < timezone.now())
    def __str__(self):
        return self.name


class BuySubscriptionPlan(models.Model):
    main_dairy = models.ForeignKey(MainDairy, on_delete=models.CASCADE, related_name='purchases', null=True, blank=True)
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.SET_NULL, related_name='purchases', null=True, blank=True)
    razorpay_order_id = models.CharField(max_length=255, null=True, blank=True)
    razorpay_payment_id = models.CharField(max_length=255, null=True, blank=True)
    amount = models.FloatField(default=0.0)
    is_active = models.BooleanField(default=False)
    expiry_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.plan} - ₹{self.amount}"


class Dairy(models.Model):
    TYPE = (
        ('Main','Main'),
        ('Branch','Branch'),
    )
    main_dairy = models.ForeignKey(MainDairy, on_delete=models.CASCADE,related_name='main_dairy',null=True,blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE,related_name='dairy')  #Admin or Manager
    role = models.CharField(max_length=12,choices=TYPE,default='Main')
    name = models.CharField(max_length=255)
    is_main = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class DairyUserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,related_name='dairy_profile')
    dairy = models.ForeignKey(Dairy, on_delete=models.CASCADE,related_name='dairy_profile')
    def __str__(self):
        return self.user.username
    
class MilkType(models.Model):
    dairy = models.ForeignKey(Dairy, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    price_per_litre = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return self.name


class MilkCollection(models.Model):
    TYPE = (
        ('Sale','Sale'),
        ('Purchase','Purchase'),
    )
    dairy = models.ForeignKey(Dairy, on_delete=models.CASCADE)
    milk_type = models.CharField(max_length=100)
    quantity = models.FloatField()
    type = models.CharField(max_length=12,choices=TYPE,default='Sale')
    collection_date = models.DateField(auto_now_add=True)
    userprofile = models.ForeignKey(DairyUserProfile, on_delete=models.CASCADE,null=True,blank=True)
    is_paid = models.BooleanField(default=False)
    amount = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    payment_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.dairy.name} ({self.quantity}L)"


class MilkStock(models.Model):
    dairy = models.ForeignKey(Dairy, on_delete=models.CASCADE)
    milk_type = models.CharField(max_length=100)  # Cow, Buffalo, etc.
    quantity = models.FloatField(null=True,blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.dairy.name} - {self.milk_type}"



class PaymentHistory(models.Model):
    collection = models.ForeignKey(MilkCollection, on_delete=models.CASCADE, related_name='payment_history')
    payment_date = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    status = models.CharField(max_length=12, choices=[('Paid', 'Paid'), ('Unpaid', 'Unpaid')], default='Unpaid')

    def __str__(self):
        return f"{self.collection.dairy.name} - {self.status} - ₹{self.amount} on {self.payment_date}"



# # 4. Order (for placing scheduled milk orders)
# class Order(models.Model):
#     customer = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE)
#     milk_type = models.ForeignKey(MilkType, on_delete=models.CASCADE)
#     quantity_litre = models.DecimalField(max_digits=5, decimal_places=2)
#     schedule_date = models.DateField()
#     created_at = models.DateTimeField(auto_now_add=True)

#     STATUS_CHOICES = (
#         ('Pending', 'Pending'),
#         ('Delivered', 'Delivered'),
#         ('Cancelled', 'Cancelled'),
#     )
#     status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')

#     def __str__(self):
#         return f"{self.customer.user.username} - {self.schedule_date}"

# # 5. Payment Record
# class Payment(models.Model):
#     customer = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE)
#     order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True)
#     amount = models.DecimalField(max_digits=8, decimal_places=2)
#     payment_date = models.DateTimeField(auto_now_add=True)
#     method = models.CharField(max_length=50, default='Cash')  # or 'Online'

#     def __str__(self):
#         return f"{self.customer.user.username} - ₹{self.amount}"




