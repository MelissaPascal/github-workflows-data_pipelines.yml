"""
Data Pipeline: Budget Promise Tracker
Manual data entry helper with validation
Runs: On-demand or weekly
"""

import os
from datetime import datetime
from supabase import create_client, Client

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def add_budget_promise(
    year: int,
    promise_text: str,
    category: str,
    status: str = "Promised"
):
    """Add a new budget promise to tracker"""
    try:
        # Get fiscal year ID
        fiscal_year = supabase.table('fiscal_years')\
            .select('id')\
            .eq('year', year)\
            .eq('country_id', '(SELECT id FROM countries WHERE code = \'TTO\')')\
            .execute()
        
        fy_id = fiscal_year.data[0]['id']
        
        # Insert promise
        supabase.table('budget_promises').insert({
            'fiscal_year_id': fy_id,
            'promise_text': promise_text,
            'category': category,
            'status': status
        }).execute()
        
        print(f"✅ Added promise: {promise_text[:50]}...")
        
    except Exception as e:
        print(f"❌ Error adding promise: {e}")

def update_promise_status(promise_id: str, new_status: str, delivery_date: str = None):
    """Update status of existing promise"""
    try:
        update_data = {'status': new_status}
        if delivery_date:
            update_data['delivery_date'] = delivery_date
        
        supabase.table('budget_promises')\
            .update(update_data)\
            .eq('id', promise_id)\
            .execute()
        
        print(f"✅ Updated promise {promise_id} to {new_status}")
        
    except Exception as e:
        print(f"❌ Error updating promise: {e}")

# Example usage
if __name__ == "__main__":
    # Add FY 2026 promises
    add_budget_promise(
        year=2026,
        promise_text="$1 per litre reduction in super gasoline",
        category="Energy/Fuel",
        status="Delivered"
    )
    
    add_budget_promise(
        year=2026,
        promise_text="VAT removal on 16+ food items",
        category="Tax Relief",
        status="Delivered"
    )
    
    add_budget_promise(
        year=2026,
        promise_text="$793.7M agriculture support grants",
        category="Agriculture",
        status="Promised"
    )
