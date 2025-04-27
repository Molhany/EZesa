from django import forms
from .models import User, Energy
from decimal import Decimal

from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from .models import User

from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from .models import User

        
from django import forms
from .models import Feedback

from django import forms
from .models import SmartDevice


class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('meter_number', 'first_name', 'surname', 'address', 'is_staff')

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ('meter_number', 'first_name', 'surname', 'address', 'password', 'is_active', 'is_staff', 'is_superuser')

    def clean_password(self):
        return self.initial["password"]







class SignUpForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['first_name', 'surname', 'meter_number', 'address', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password != password_confirm:
            raise forms.ValidationError("Passwords do not match.")

        return cleaned_data

class LoginForm(forms.Form):
    login_option = forms.ChoiceField(choices=[('meter_number', 'Meter Number'), ('surname', 'Surname')], widget=forms.RadioSelect)
    login = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

class ProfileForm(forms.ModelForm):
    current_password = forms.CharField(widget=forms.PasswordInput, required=False, label="Current Password")
    new_password = forms.CharField(widget=forms.PasswordInput, required=False, label="New Password")
    confirm_password = forms.CharField(widget=forms.PasswordInput, required=False, label="Confirm New Password")

    class Meta:
        model = User
        fields = ['first_name', 'surname', 'address']

    def clean(self):
        cleaned_data = super().clean()
        current_password = cleaned_data.get("current_password")
        new_password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")

        if new_password or confirm_password:
            if new_password != confirm_password:
                raise forms.ValidationError("New passwords do not match.")

            if not self.instance.check_password(current_password):
                raise forms.ValidationError("Current password is incorrect.")

        return cleaned_data
    
    


class EnergyPurchaseForm(forms.ModelForm):
    amount_spent = forms.DecimalField(max_digits=10, decimal_places=2, label="Amount ($)")
    payment_option = forms.ChoiceField(choices=[('bank', 'Bank'), ('mobile', 'Mobile Network')], label="Payment Option")

    class Meta:
        model = Energy
        fields = ['amount_spent', 'payment_option']

    def save(self, user, commit=True):
        instance = super().save(commit=False)
        # Check if there is a bill associated with the user
        bill = user.bill_set.first()
        if bill:
            tariff_rate = Decimal(bill.tariff_rate)
        else:
            tariff_rate = Decimal('0.12')  # Default tariff rate if no bill is found

        # Calculate energy to be purchased based on amount spent and tariff rate
        instance.amount_kwh = self.cleaned_data['amount_spent'] / tariff_rate
        instance.user = user
        if commit:
            instance.save()
        return instance

class EnergyRechargeForm(forms.ModelForm):
    voucher_code = forms.CharField(max_length=20, label="Voucher Code")
    amount_spent = forms.DecimalField(max_digits=10, decimal_places=2, label="Amount Spent ($)")

    class Meta:
        model = Energy
        fields = ['voucher_code', 'amount_spent']

    def save(self, user, commit=True):
        instance = super().save(commit=False)
        # Check if there is a bill associated with the user
        bill = user.bill_set.first()
        if bill:
            tariff_rate = Decimal(bill.tariff_rate)
        else:
            tariff_rate =Decimal('0.12')  # Default tariff rate if no bill is found

        # Calculate energy to be recharged based on amount spent and tariff rate
        instance.amount_kwh = self.cleaned_data['amount_spent'] / tariff_rate
        instance.user = user
        if commit:
            instance.save()
        return instance

class EnergyTransferForm(forms.ModelForm):
    recipient_meter_number = forms.CharField(max_length=15, label="Recipient Meter Number")
    amount_kwh = forms.DecimalField(max_digits=10, decimal_places=2, label="Amount of Energy to Transfer (kWh)")

    class Meta:
        model = Energy
        fields = ['recipient_meter_number', 'amount_kwh']

    def clean_recipient_meter_number(self):
        meter_number = self.cleaned_data['recipient_meter_number']
        try:
            recipient = User.objects.get(meter_number=meter_number)
        except User.DoesNotExist:
            raise forms.ValidationError("The recipient meter number is invalid.")
        return meter_number

    def save(self, commit=True):
        instance = super().save(commit=False)
        recipient = User.objects.get(meter_number=self.cleaned_data['recipient_meter_number'])
        instance.transferred_to = recipient
        if commit:
            instance.save()
        return instance
    
        
class ContactForm(forms.Form):
    subject = forms.CharField(max_length=100)
    message = forms.CharField(widget=forms.Textarea)
    email = forms.EmailField()
    
class SettingsForm(forms.ModelForm):
    notify_usage_limit = forms.BooleanField(required=False, label="Notify when usage exceeds limit")
    usage_limit_value = forms.DecimalField(required=False, max_digits=10, decimal_places=2, label="Usage Limit Value (kWh)")

    class Meta:
        model = User
        fields = ['notify_usage_limit', 'usage_limit_value']
        
        


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['feedback_type', 'feedback_text', 'rating']
        widgets = {
            'feedback_type': forms.Select(choices=[
                ('Chatbot', 'Chatbot'),
                ('Energy Tips', 'Energy Tips'),
                ('Service', 'Service')
            ]),
            'rating': forms.RadioSelect(choices=[
                (1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')
            ])
        }
        
        
        

class SmartDeviceForm(forms.ModelForm):
    class Meta:
        model = SmartDevice
        fields = ['device_name', 'device_type']