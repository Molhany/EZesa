from django.urls import path
from .views import signup, login_view, dashboard, profile, bill_list, bill_detail, purchase_energy, recharge_energy, energy_history, transfer_energy, notifications, mark_notification_as_read, support_faq, payment_history, settings, logout, send_notification_to_all, data_visualization, energy_usage_analytics, personalized_recommendations, predictive_energy_forecasting, anomaly_detection, detailed_usage_reports, energy_efficiency_metrics, submit_feedback, view_feedback,  onboarding, manage_smart_devices, energy_management, billing_payments, update_device_status, get_device_balance, update_device_balance, get_device_balance_and_status


urlpatterns = [
    path('signup/', signup, name='signup'),
    path('login/', login_view, name='login'),
    path('dashboard/', dashboard, name='dashboard'),
    path('profile/', profile, name='profile'),
    path('bills/', bill_list, name='bill_list'),
    path('bills/<int:bill_id>/', bill_detail, name='bill_detail'),
    path('purchase_energy/', purchase_energy, name='purchase_energy'),
    path('recharge_energy/', recharge_energy, name='recharge_energy'),
    path('energy_history/', energy_history, name='energy_history'),
    path('transfer_energy/', transfer_energy, name='transfer_energy'),
    path('notifications/', notifications, name='notifications'),
    path('notifications/<int:notification_id>/read/', mark_notification_as_read, name='mark_notification_as_read'),
    path('support_faq/', support_faq, name='support_faq'),
    path('payment_history/', payment_history, name='payment_history'),
    path('settings/', settings, name='settings'),
    path('logout/', logout, name='logout'),
    path('admin/send_notification_to_all/', send_notification_to_all, name='send_notification_to_all'),
    path('data_visualization/', data_visualization, name='data_visualization'),
    path('energy_usage_analytics/', energy_usage_analytics, name='energy_usage_analytics'),
    path('personalized_recommendations/', personalized_recommendations, name='personalized_recommendations'),
    path('predictive_energy_forecasting/', predictive_energy_forecasting, name='predictive_energy_forecasting'),
    path('anomaly_detection/', anomaly_detection, name='anomaly_detection'),

    path('detailed_usage_reports/', detailed_usage_reports, name='detailed_usage_reports'),
    path('energy_efficiency_metrics/', energy_efficiency_metrics, name='energy_efficiency_metrics'),
    
     path('submit_feedback/', submit_feedback, name='submit_feedback'),
    path('view_feedback/', view_feedback, name='view_feedback'),
    
    path('onboarding/', onboarding, name='onboarding'),
    path('manage_smart_devices/', manage_smart_devices, name='manage_smart_devices'),
    


    path('dashboard/', dashboard, name='dashboard'),
    path('energy_management/', energy_management, name='energy_management'),
    path('billing_payments/', billing_payments, name='billing_payments'),
    path('support_faq/', support_faq, name='support_faq'),
    path('profile/', profile, name='profile'),
    path('settings/', settings, name='settings'),
    path('submit_feedback/', submit_feedback, name='submit_feedback'),
    path('view_feedback/', view_feedback, name='view_feedback'),
    path('onboarding/', onboarding, name='onboarding'),
    path('manage_smart_devices/', manage_smart_devices, name='manage_smart_devices'),
    path('data_visualization/', data_visualization, name='data_visualization'),
    path('energy_usage_analytics/', energy_usage_analytics, name='energy_usage_analytics'),
    path('personalized_recommendations/', personalized_recommendations, name='personalized_recommendations'),
    path('predictive_energy_forecasting/', predictive_energy_forecasting, name='predictive_energy_forecasting'),
    path('anomaly_detection/', anomaly_detection, name='anomaly_detection'),
    path('detailed_usage_reports/', detailed_usage_reports, name='detailed_usage_reports'),
    path('energy_efficiency_metrics/', energy_efficiency_metrics, name='energy_efficiency_metrics'),
    path('signup/', signup, name='signup'),
    path('login/', login_view, name='login'),
    path('logout/', logout, name='logout'),
    
    path('api/update_device_status/<int:device_id>/', update_device_status, name='update_device_status'),
    path('api/get_device_balance/<int:user_id>/<int:device_id>/', get_device_balance, name='get_device_balance'),
    path('api/update_device_balance/<int:user_id>/<int:device_id>/', update_device_balance, name='update_device_balance'),
    
    path('api/get_device_balance_and_status/<int:user_id>/<int:device_id>/', get_device_balance_and_status, name='get_device_balance_and_status'),
    path('api/update_device_status/<int:user_id>/<int:device_id>/', update_device_status, name='update_device_status'),
    
    
    
    
]

