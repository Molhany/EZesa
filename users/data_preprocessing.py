
import pandas as pd
from .models import Energy

def preprocess_energy_data(user):
    energy_data = Energy.objects.filter(user=user).values('date_purchased', 'amount_kwh')
    df = pd.DataFrame(list(energy_data))
    df['date_purchased'] = pd.to_datetime(df['date_purchased'])
    df.set_index('date_purchased', inplace=True)
    return df