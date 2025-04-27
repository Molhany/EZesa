
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as auth_logout
from django.contrib import messages
from django.http import JsonResponse
from .forms import SignUpForm, LoginForm, ProfileForm, EnergyPurchaseForm, EnergyRechargeForm, EnergyTransferForm, ContactForm, SettingsForm, SmartDeviceForm
from .models import User, Bill, Energy, Notification, Payment, Tutorial, SmartDevice, Profile
import datetime
import random
from decimal import Decimal

import matplotlib.pyplot as plt
import io
import urllib, base64
from django.shortcuts import render
from .models import Energy

from .data_preprocessing import preprocess_energy_data
from .machine_learning import train_energy_model, predict_energy_usage
import pandas as pd


import matplotlib.pyplot as plt
import io
import urllib, base64
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Energy
from .data_preprocessing import preprocess_energy_data
from .recommendations import generate_recommendations
from .machine_learning import train_energy_model, predict_energy_usage
from .anomaly_detection import detect_anomalies

from django.http import HttpResponse
from .data_preprocessing import preprocess_energy_data


from django.urls import reverse
from django.http import HttpResponseRedirect

from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone


from django.db.models import Prefetch





def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            messages.success(request, "Registration successful. Please log in.")
            return redirect('login')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            login_option = form.cleaned_data['login_option']
            login_value = form.cleaned_data['login']
            password = form.cleaned_data['password']
            if login_option == 'meter_number':
                try:
                    user = User.objects.get(meter_number=login_value)
                except User.DoesNotExist:
                    user = None
            else:
                try:
                    user = User.objects.get(surname=login_value)
                except User.DoesNotExist:
                    user = None

            if user is not None and user.check_password(password):
                auth_login(request, user)
                messages.success(request, "Login successful. Proceed.")
                return redirect('dashboard')
            else:
                form.add_error(None, "Invalid login credentials.")
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})




@login_required
def dashboard(request):
    user = request.user
    bills = Bill.objects.filter(user=user).order_by('-date_issued')
    latest_bill = bills.first() if bills.exists() else None
    total_energy_usage = sum(bill.usage_kwh for bill in bills)
    energy_transactions = Energy.objects.filter(user=user).order_by('-date_purchased')
    energy_balance = sum(e.balance_kwh for e in energy_transactions) if energy_transactions.exists() else 0

    # Calculate energy status color and notification
    if energy_balance > 30:
        energy_status = 'green'
    elif 15 < energy_balance <= 30:
        energy_status = 'orange'
    else:
        energy_status = 'red'
        messages.warning(request, "You need to recharge or purchase energy.")

    # Estimate days left of kWh (Assuming average daily usage)
    avg_daily_usage = total_energy_usage / max(len(bills), 1) if total_energy_usage > 0 else 1
    days_left = energy_balance / avg_daily_usage if avg_daily_usage else 0

    context = {
        'username': user.first_name,
        'latest_bill': latest_bill,
        'total_energy_usage': total_energy_usage,
        'energy_balance': energy_balance,
        'energy_status': energy_status,
        'days_left': days_left,
        'recent_activities': energy_transactions[:5],  # Displaying recent 5 energy transactions as activities
        'notifications': Notification.objects.filter(user=user, is_read=False),
    }

    return render(request, 'dashboard.html', context)

@login_required
def profile(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            user = form.save(commit=False)
            new_password = form.cleaned_data.get('new_password')
            if new_password:
                user.set_password(new_password)
                update_session_auth_hash(request, user)  # Keep the user logged in after password change
            user.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('profile')
    else:
        form = ProfileForm(instance=request.user)
    return render(request, 'profile.html', {'form': form})




@login_required
def bill_list(request):
    bills = Bill.objects.filter(user=request.user).order_by('-date_issued')
    return render(request, 'bill_list.html', {'bills': bills})

@login_required
def bill_detail(request, bill_id):
    bill = get_object_or_404(Bill, id=bill_id, user=request.user)
    return render(request, 'bill_detail.html', {'bill': bill})



@login_required
def purchase_energy(request):
    if request.method == 'POST':
        form = EnergyPurchaseForm(request.POST)
        if form.is_valid():
            energy = form.save(user=request.user, commit=False)
            energy.date_purchased = datetime.date.today()
            energy.balance_kwh = energy.amount_kwh
            energy.save()

            # Log the payment transaction
            Payment.objects.create(
                user=request.user,
                amount=form.cleaned_data['amount_spent'],
                payment_method=form.cleaned_data['payment_option'],
                description=f"Purchased {energy.amount_kwh} kWh of energy."
            )

            Notification.objects.create(user=request.user, message=f"Energy purchased: {energy.amount_kwh} kWh")
            messages.success(request, "Energy purchased successfully.")
            return redirect('energy_history')
    else:
        form = EnergyPurchaseForm()
    return render(request, 'purchase_energy.html', {'form': form})

@login_required
def recharge_energy(request):
    if request.method == 'POST':
        form = EnergyRechargeForm(request.POST)
        if form.is_valid():
            energy = form.save(user=request.user, commit=False)
            energy.date_purchased = datetime.date.today()
            energy.balance_kwh = energy.amount_kwh
            energy.save()
            Notification.objects.create(user=request.user, message=f"Energy recharged: {energy.amount_kwh} kWh")
            messages.success(request, "Energy recharged successfully.")
            return redirect('energy_history')
    else:
        form = EnergyRechargeForm()
    return render(request, 'recharge_energy.html', {'form': form})





@login_required
def energy_history(request):
    energy_transactions = Energy.objects.filter(user=request.user).order_by('-date_purchased')
    return render(request, 'energy_history.html', {'energy_transactions': energy_transactions})



@login_required
def transfer_energy(request):
    if request.method == 'POST':
        form = EnergyTransferForm(request.POST)
        if form.is_valid():
            transferred_to_meter_number = form.cleaned_data['recipient_meter_number']
            amount_kwh = form.cleaned_data['amount_kwh']

            if amount_kwh <= 0:
                form.add_error('amount_kwh', "Cannot transfer negative or zero energy.")
            else:
                sender_energy = Energy.objects.filter(user=request.user).order_by('-date_purchased').first()
                if sender_energy:
                    current_balance = sum(e.balance_kwh for e in Energy.objects.filter(user=request.user))

                    if current_balance < amount_kwh:
                        form.add_error(None, "Insufficient balance to complete the transfer.")
                    elif current_balance <= 15:
                        form.add_error(None, "Your balance is too low to transfer energy. Please recharge or purchase more energy.")
                    else:
                        sender_energy.balance_kwh -= amount_kwh
                        sender_energy.save()

                        recipient = User.objects.get(meter_number=transferred_to_meter_number)
                        recipient_energy, created = Energy.objects.get_or_create(user=recipient, voucher_code='Transfer', defaults={'date_purchased': datetime.date.today(), 'amount_kwh': 0, 'balance_kwh': 0})
                        recipient_energy.balance_kwh += amount_kwh
                        recipient_energy.amount_kwh += amount_kwh
                        recipient_energy.save()

                        Notification.objects.create(user=request.user, message=f"Transferred {amount_kwh} kWh to {recipient.meter_number}")
                        Notification.objects.create(user=recipient, message=f"Received {amount_kwh} kWh from {request.user.meter_number}")

                        Payment.objects.create(user=request.user, amount=0, payment_method='transfer', description=f"Transferred {amount_kwh} kWh to {recipient.meter_number}")
                        Payment.objects.create(user=recipient, amount=0, payment_method='transfer', description=f"Received {amount_kwh} kWh from {request.user.meter_number}")

                        messages.success(request, f"Successfully transferred {amount_kwh} kWh to {recipient.first_name} {recipient.surname}.")
                        return redirect('energy_history')
                else:
                    form.add_error(None, "Insufficient balance to complete the transfer.")
    else:
        form = EnergyTransferForm()
    return render(request, 'transfer_energy.html', {'form': form})

@login_required
def recipient_info(request, meter_number):
    try:
        recipient = User.objects.get(meter_number=meter_number)
        return JsonResponse({'first_name': recipient.first_name, 'surname': recipient.surname, 'address': recipient.address})
    except User.DoesNotExist:
        return JsonResponse({'first_name': '', 'surname': '', 'address': ''})






@login_required
def notifications(request):
    unread_notifications = Notification.objects.filter(user=request.user, is_read=False)
    all_notifications = Notification.objects.filter(user=request.user).order_by('-date_created')
    context = {
        'notifications': all_notifications,
        'unread_count': unread_notifications.count(),
    }
    return render(request, 'notifications.html', context)

@login_required
def mark_notification_as_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    return redirect('notifications')



@login_required
def support_faq(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            email = form.cleaned_data['email']
            # Process the contact form data (e.g., send email or store in database)
            messages.success(request, "Your message has been sent to customer support.")
            return redirect('support_faq')
    else:
        form = ContactForm()

    faq_content = [
        {"question": "How do I view my bills?", "answer": "You can view your bills by navigating to the 'Bills' section in the sidebar."},
        {"question": "How do I purchase energy?", "answer": "You can purchase energy by navigating to the 'Energy' section in the sidebar and clicking on 'Purchase Energy'."},
        {"question": "How do I contact customer support?", "answer": "You can contact customer support by filling out the form below."},
    ]

    tutorials = Tutorial.objects.all()

    context = {
        'form': form,
        'faq_content': faq_content,
        'tutorials': tutorials,
        'live_chat_enabled': True,  # Placeholder for live chat functionality
    }
    return render(request, 'support_faq.html', context)



@login_required
def payment_history(request):
    payments = Payment.objects.filter(user=request.user).order_by('-date')
    context = {
        'payments': payments
    }
    return render(request, 'payment_history.html', context)


@login_required
def settings(request):
    if request.method == "POST":
        # Handle settings update
        form = SettingsForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Settings updated successfully.")
            return redirect('settings')
    else:
        form = SettingsForm(instance=request.user)
    return render(request, 'settings.html', {'form': form})





@login_required
def logout(request):
    auth_logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('login')


from django.shortcuts import render, redirect
from .models import Notification
from django.contrib import messages

def send_notification_to_all(request):
    if request.method == 'POST':
        message = request.POST.get('message', '')
        users = User.objects.all()
        for user in users:
            Notification.objects.create(user=user, message=message)
        messages.success(request, "Notification sent to all users.")
        return redirect('/admin/users/user/')  # Redirect back to the user admin interface

    return render(request, 'admin/send_notification_to_all.html')





@login_required
def data_visualization(request):
    # Example: Visualize energy usage over time
    energy_data = Energy.objects.filter(user=request.user).order_by('date_purchased')
    dates = [e.date_purchased for e in energy_data]
    usage = [e.amount_kwh for e in energy_data]

    plt.figure(figsize=(10, 5))
    plt.plot(dates, usage, marker='o')
    plt.title('Energy Usage Over Time')
    plt.xlabel('Date')
    plt.ylabel('kWh')
    plt.grid(True)

    # Convert plot to image
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    string = base64.b64encode(buf.read())
    uri = 'data:image/png;base64,' + urllib.parse.quote(string)

    context = {
        'data_uri': uri,
    }
    return render(request, 'data_visualization.html', context)




@login_required
def data_visualization(request):
    # Preprocess data
    df = preprocess_energy_data(request.user)

    # Train model and make predictions
    model = train_energy_model(df)
    future_days = [i for i in range(df['day_of_year'].max() + 1, df['day_of_year'].max() + 31)]
    predictions = predict_energy_usage(model, future_days)

    # Plot actual data and predictions
    plt.figure(figsize=(10, 5))
    plt.plot(df.index, df['amount_kwh'], marker='o', label='Actual Usage')
    plt.plot(pd.date_range(start=df.index.max(), periods=30, freq='D'), predictions, marker='x', label='Predicted Usage')
    plt.title('Energy Usage Over Time')
    plt.xlabel('Date')
    plt.ylabel('kWh')
    plt.legend()
    plt.grid(True)

    # Convert plot to image
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    string = base64.b64encode(buf.read())
    uri = 'data:image/png;base64,' + urllib.parse.quote(string)

    context = {
        'data_uri': uri,
    }
    return render(request, 'data_visualization.html', context)





import matplotlib.pyplot as plt
import io
import urllib, base64
from django.shortcuts import render
from .models import Energy
from .data_preprocessing import preprocess_energy_data

@login_required
def energy_usage_analytics(request):
    # Preprocess data
    df = preprocess_energy_data(request.user)

    # Calculate usage patterns and metrics
    daily_usage = df.resample('D').sum()
    weekly_usage = df.resample('W').sum()
    monthly_usage = df.resample('M').sum()
    avg_daily_usage = daily_usage['amount_kwh'].mean()
    avg_weekly_usage = weekly_usage['amount_kwh'].mean()
    avg_monthly_usage = monthly_usage['amount_kwh'].mean()

    # Plot usage patterns
    plt.figure(figsize=(10, 5))
    plt.plot(daily_usage.index, daily_usage['amount_kwh'], label='Daily Usage')
    plt.plot(weekly_usage.index, weekly_usage['amount_kwh'], label='Weekly Usage')
    plt.plot(monthly_usage.index, monthly_usage['amount_kwh'], label='Monthly Usage')
    plt.title('Energy Usage Patterns')
    plt.xlabel('Date')
    plt.ylabel('kWh')
    plt.legend()
    plt.grid(True)

    # Convert plot to image
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    string = base64.b64encode(buf.read())
    uri = 'data:image/png;base64,' + urllib.parse.quote(string)

    context = {
        'data_uri': uri,
        'avg_daily_usage': avg_daily_usage,
        'avg_weekly_usage': avg_weekly_usage,
        'avg_monthly_usage': avg_monthly_usage,
    }
    return render(request, 'energy_usage_analytics.html', context)




from .recommendations import generate_recommendations

@login_required
def personalized_recommendations(request):
    recommendations = generate_recommendations(request.user)
    context = {
        'recommendations': recommendations,
    }
    return render(request, 'personalized_recommendations.html', context)




from .machine_learning import train_energy_model, predict_energy_usage

@login_required
def predictive_energy_forecasting(request):
    df = preprocess_energy_data(request.user)
    model = train_energy_model(df)
    future_days = [i for i in range(df['day_of_year'].max() + 1, df['day_of_year'].max() + 31)]
    predictions = predict_energy_usage(model, future_days)

    plt.figure(figsize=(10, 5))
    plt.plot(df.index, df['amount_kwh'], marker='o', label='Actual Usage')
    plt.plot(pd.date_range(start=df.index.max(), periods=30, freq='D'), predictions, marker='x', label='Predicted Usage')
    plt.title('Energy Usage Forecast')
    plt.xlabel('Date')
    plt.ylabel('kWh')
    plt.legend()
    plt.grid(True)

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    string = base64.b64encode(buf.read())
    uri = 'data:image/png;base64,' + urllib.parse.quote(string)

    context = {
        'data_uri': uri,
    }
    return render(request, 'predictive_energy_forecasting.html', context)



from .anomaly_detection import detect_anomalies

@login_required
def anomaly_detection(request):
    anomaly_dates = detect_anomalies(request.user)
    context = {
        'anomaly_dates': anomaly_dates,
    }
    return render(request, 'anomaly_detection.html', context)






@login_required
def detailed_usage_reports(request):
    df = preprocess_energy_data(request.user)
    
    daily_usage = df.resample('D').sum()
    weekly_usage = df.resample('W').sum()
    monthly_usage = df.resample('M').sum()
    
    comparison_report = {
        'daily': daily_usage.to_dict(),
        'weekly': weekly_usage.to_dict(),
        'monthly': monthly_usage.to_dict(),
    }
    
    context = {
        'comparison_report': comparison_report,
    }
    return render(request, 'detailed_usage_reports.html', context)


@login_required
def energy_efficiency_metrics(request):
    df = preprocess_energy_data(request.user)
    
    df['amount_kwh'] = df['amount_kwh'].astype(float)

    avg_daily_usage = df.resample('D').sum()['amount_kwh'].mean()
    peak_usage = df['amount_kwh'].max()
    efficiency_score = (avg_daily_usage / peak_usage) * 100  # Example metric

    context = {
        'avg_daily_usage': avg_daily_usage,
        'peak_usage': peak_usage,
        'efficiency_score': efficiency_score,
    }
    return render(request, 'energy_efficiency_metrics.html', context)



from django.shortcuts import render, redirect
from .forms import FeedbackForm
from django.contrib import messages

from .models import Feedback

@login_required
def submit_feedback(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.user = request.user
            feedback.save()
            messages.success(request, "Thank you for your feedback!")
            return redirect('submit_feedback')
    else:
        form = FeedbackForm()
    return render(request, 'submit_feedback.html', {'form': form})


@login_required
def view_feedback(request):
    feedback_list = Feedback.objects.all().order_by('-date_submitted')
    context = {'feedback_list': feedback_list}
    return render(request, 'view_feedback.html', context)

@login_required
def onboarding(request):
    return render(request, 'onboarding.html')

@login_required
def manage_smart_devices(request):
    devices = SmartDevice.objects.filter(user=request.user)
    context = {'devices': devices}
    return render(request, 'manage_smart_devices.html', context)


from .models import Energy, SmartDevice
from .data_preprocessing import preprocess_energy_data
from .machine_learning import train_energy_model, predict_energy_usage
from .anomaly_detection import detect_anomalies
from .recommendations import generate_recommendations

@login_required
def energy_management(request):
    transactions = Energy.objects.filter(user=request.user)
    devices = SmartDevice.objects.filter(user=request.user)
    
    df = preprocess_energy_data(request.user)
    daily_usage = df.resample('D').sum()
    model = train_energy_model(df)
    future_days = [i for i in range(df['day_of_year'].max() + 1, df['day_of_year'].max() + 31)]
    predictions = predict_energy_usage(model, future_days)
    anomalies = detect_anomalies(request.user)
    recommendations = generate_recommendations(request.user)

    context = {
        'transactions': transactions,
        'devices': devices,
        'daily_usage': daily_usage,
        'predictions': predictions,
        'anomalies': anomalies,
        'recommendations': recommendations,
    }
    return render(request, 'energy_management.html', context)







@login_required
def billing_payments(request):
    bills = Bill.objects.filter(user=request.user)
    payments = Payment.objects.filter(user=request.user)
    context = {
        'bills': bills,
        'payments': payments,
    }
    return render(request, 'billing_payments.html', context)




# remove this in future






@login_required
def manage_smart_devices(request):
    if request.method == 'POST':
        form = SmartDeviceForm(request.POST)
        if form.is_valid():
            new_device = form.save(commit=False)
            new_device.user = request.user
            new_device.save()
            return redirect('manage_smart_devices')
    else:
        form = SmartDeviceForm()

    devices = SmartDevice.objects.filter(user=request.user)
    context = {'devices': devices, 'form': form}
    return render(request, 'manage_smart_devices.html', context)



@login_required
def update_device_status(request, device_id):
    device = get_object_or_404(SmartDevice, id=device_id, user=request.user)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        device.status = new_status
        device.save()
    return HttpResponseRedirect(reverse('manage_smart_devices'))



@csrf_exempt
def get_device_balance_and_status(request, user_id, device_id):
    try:
        device = SmartDevice.objects.get(user_id=user_id, id=device_id)
        return JsonResponse({'balance': device.energy_balance, 'status': device.status})
    except SmartDevice.DoesNotExist:
        return JsonResponse({'error': 'Device not found'}, status=404)

@csrf_exempt
def update_device_balance(request, user_id, device_id):
    try:
        device = SmartDevice.objects.get(user_id=user_id, id=device_id)
        consumption = float(request.POST.get('consumption', 0))
        status = request.POST.get('status', device.status)
        balance = float(request.POST.get('balance', device.energy_balance))
        device.energy_balance = balance - consumption
        device.energy_consumption += consumption
        device.status = status
        device.last_updated = timezone.now()
        device.save()
        return JsonResponse({'status': 'success'})
    except SmartDevice.DoesNotExist:
        return JsonResponse({'error': 'Device not found'}, status=404)
    



@csrf_exempt
def get_device_balance(request, user_id, device_id):
    try:
        device = SmartDevice.objects.get(user_id=user_id, id=device_id)
        return JsonResponse({'balance': device.energy_balance})
    except SmartDevice.DoesNotExist:
        return JsonResponse({'error': 'Device not found'}, status=404)

@csrf_exempt
def update_device_balance(request, user_id, device_id):
    try:
        device = SmartDevice.objects.get(user_id=user_id, id=device_id)
        consumption = float(request.POST.get('consumption'))
        device.energy_balance -= consumption
        device.energy_consumption += consumption
        device.last_updated = timezone.now()
        device.save()
        return JsonResponse({'status': 'success'})
    except SmartDevice.DoesNotExist:
        return JsonResponse({'error': 'Device not found'}, status=404)