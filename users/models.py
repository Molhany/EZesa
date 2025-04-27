
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

from django.db import models
from django.contrib.auth.models import User


from django.db.models.signals import post_save
from django.dispatch import receiver

class UserManager(BaseUserManager):
    def create_user(self, first_name, surname, meter_number, address, password=None, **extra_fields):
        if not meter_number:
            raise ValueError('The Meter Number is required')
        user = self.model(
            first_name=first_name,
            surname=surname,
            meter_number=meter_number,
            address=address,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, first_name, surname, meter_number, address, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(first_name, surname, meter_number, address, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=30)
    surname = models.CharField(max_length=30)
    meter_number = models.CharField(max_length=15, unique=True)
    address = models.TextField()

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'meter_number'
    REQUIRED_FIELDS = ['first_name', 'surname', 'address']

    objects = UserManager()

    def __str__(self):
        return self.meter_number

    def has_module_perms(self, app_label):
        return True

    def has_perm(self, perm, obj=None):
        return True

class Bill(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date_issued = models.DateField()
    due_date = models.DateField()
    usage_kwh = models.DecimalField(max_digits=10, decimal_places=2)
    tariff_rate = models.DecimalField(max_digits=5, decimal_places=2)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Bill for {self.user.meter_number} - {self.date_issued}"

class Energy(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    voucher_code = models.CharField(max_length=20)
    date_purchased = models.DateField()
    amount_kwh = models.DecimalField(max_digits=10, decimal_places=2)
    balance_kwh = models.DecimalField(max_digits=10, decimal_places=2)
    transferred_to = models.ForeignKey(User, related_name='received_energy', null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"Energy for {self.user.meter_number} - {self.voucher_code}"
    
    
    
    
    

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for {self.user.meter_number} - {self.message[:20]}"

class SupportTicket(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100)
    message = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[('open', 'Open'), ('closed', 'Closed')], default='open')

    def __str__(self):
        return f"Support Ticket for {self.user.meter_number} - {self.subject[:20]}"

class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=[('bank', 'Bank'), ('mobile', 'Mobile Network')])
    description = models.CharField(max_length=100)

    def __str__(self):
        return f"Payment for {self.user.meter_number} - {self.amount} - {self.date}"

class Tutorial(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    video_file = models.FileField(upload_to='tutorials/videos/')
    date_uploaded = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
    
    
    

class Feedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    feedback_type = models.CharField(max_length=255)  # e.g., "Chatbot", "Energy Tips", "Service"
    feedback_text = models.TextField()
    rating = models.PositiveIntegerField()  # Rating out of 5
    date_submitted = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.feedback_type} - {self.rating}"
    
    
    


    
    
class SmartDevice(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    device_name = models.CharField(max_length=255)
    device_type = models.CharField(max_length=255)
    status = models.CharField(max_length=50, default='off')
    energy_consumption = models.FloatField(default=0.0)  # kWh
    energy_balance = models.FloatField(default=10.0)  # kWh, initial balance
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.device_name
    
    
    



class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.FloatField(default=0.0)  # Energy balance

    def __str__(self):
        return self.user.username

# Signal to create/update profile automatically


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()
    