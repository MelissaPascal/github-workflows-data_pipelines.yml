"""
Data Pipeline: Oil & Gas Prices
Fetches real-time WTI, Brent, Henry Hub prices
Runs: Every 6 hours
"""

import os
import requests
from datetime import datetime
from supabase import create_client, Client

# Supabase credentials
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# API endpoints (use Alpha Vantage, EIA, or Trading Economics)
OIL_API_URL = "https://www.alphavantage.co/query"
API_KEY = os.getenv("ALPHA_VANTAGE_KEY")

def fetch_oil_prices():
    """Fetch latest WTI and Brent prices"""
    try:
        # WTI (Cushing, OK)
        response_wti = requests.get(
            OIL_API_URL,
            params={
                "function": "WTI",
                "apikey": API_KEY
            }
        )
        wti_data = response_wti.json()
        wti_price = float(wti_data['data'][0]['value'])
        
        # Brent (North Sea)
        response_brent = requests.get(
            OIL_API_URL,
            params={
                "function": "BRENT",
                "apikey": API_KEY
            }
        )
        brent_data = response_brent.json()
        brent_price = float(brent_data['data'][0]['value'])
        
        # Henry Hub Natural Gas
        response_gas = requests.get(
            "https://api.eia.gov/series/",
            params={
                "api_key": os.getenv("EIA_API_KEY"),
                "series_id": "NG.RNGWHHD.D"
            }
        )
        gas_data = response_gas.json()
        gas_price = float(gas_data['series'][0]['data'][0][1])
        
        return {
            'wti': wti_price,
            'brent': brent_price,
            'gas': gas_price,
            'date': datetime.now().date()
        }
    
    except Exception as e:
        print(f"Error fetching oil prices: {e}")
        return None

def update_supabase(data):
    """Insert oil price data into Supabase"""
    try:
        # Get Trinidad ID
        country = supabase.table('countries').select('id').eq('code', 'TTO').execute()
        tto_id = country.data[0]['id']
        
        # Upsert indicator data
        result = supabase.table('economic_indicators').upsert({
            'country_id': tto_id,
            'indicator_date': str(data['date']),
            'oil_price_wti': data['wti'],
            'oil_price_brent': data['brent'],
            'gas_price_henry': data['gas']
        }).execute()
        
        print(f"✅ Oil prices updated: WTI ${data['wti']}, Brent ${data['brent']}")
        
        # Log success
        supabase.table('pipeline_logs').insert({
            'pipeline_name': 'oil_prices',
            'status': 'Success',
            'records_processed': 1
        }).execute()
        
    except Exception as e:
        print(f"❌ Error updating Supabase: {e}")
        supabase.table('pipeline_logs').insert({
            'pipeline_name': 'oil_prices',
            'status': 'Failed',
            'errors': str(e)
        }).execute()

def main():
    """Main pipeline execution"""
    print("🚀 Starting oil price pipeline...")
    data = fetch_oil_prices()
    if data:
        update_supabase(data)
    print("✅ Pipeline complete!")

if __name__ == "__main__":
    main()
