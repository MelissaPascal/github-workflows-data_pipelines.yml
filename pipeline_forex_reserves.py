"""
Data Pipeline: Forex Reserves
Scrapes Central Bank of Trinidad & Tobago
Runs: Weekly (Monday 9 AM)
"""

import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from supabase import create_client, Client

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def scrape_central_bank():
    """Scrape Central Bank forex reserves page"""
    try:
        url = "https://www.central-bank.org.tt/foreign-reserves-monthly/"
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find latest reserves figure (adjust selector based on actual HTML)
        reserves_text = soup.select_one('.reserves-value').text
        reserves_value = float(reserves_text.replace('US$', '').replace('M', '').replace(',', '').strip())
        
        # Calculate import cover (reserves / monthly imports)
        # Assume average monthly imports $700M
        import_cover = reserves_value / 700
        
        return {
            'reserves': reserves_value,
            'import_cover': round(import_cover, 2),
            'date': datetime.now().date()
        }
    
    except Exception as e:
        print(f"Error scraping Central Bank: {e}")
        return None

def update_supabase(data):
    """Update forex reserves in Supabase"""
    try:
        country = supabase.table('countries').select('id').eq('code', 'TTO').execute()
        tto_id = country.data[0]['id']
        
        supabase.table('economic_indicators').upsert({
            'country_id': tto_id,
            'indicator_date': str(data['date']),
            'forex_reserves': data['reserves'],
            'import_cover_months': data['import_cover']
        }).execute()
        
        print(f"✅ Forex reserves updated: ${data['reserves']}M, {data['import_cover']} months cover")
        
        supabase.table('pipeline_logs').insert({
            'pipeline_name': 'forex_reserves',
            'status': 'Success',
            'records_processed': 1
        }).execute()
        
    except Exception as e:
        print(f"❌ Error updating Supabase: {e}")
        supabase.table('pipeline_logs').insert({
            'pipeline_name': 'forex_reserves',
            'status': 'Failed',
            'errors': str(e)
        }).execute()

def main():
    print("🚀 Starting forex reserves pipeline...")
    data = scrape_central_bank()
    if data:
        update_supabase(data)
    print("✅ Pipeline complete!")

if __name__ == "__main__":
    main()
