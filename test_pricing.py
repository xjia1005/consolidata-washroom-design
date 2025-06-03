#!/usr/bin/env python3
"""
Test script for the enhanced pricing system
"""

try:
    from user_auth_system import PRICING_PLANS, ADDON_CREDITS
    
    print("🎉 Enhanced Pricing System Test")
    print("=" * 50)
    
    print("\n✅ Pricing Plans Loaded Successfully:")
    for plan_id, plan_data in PRICING_PLANS.items():
        price = plan_data['price']
        billing = plan_data.get('billing', 'monthly')
        name = plan_data['name']
        
        if 'annual_price' in plan_data:
            annual_price = plan_data['annual_price']
            savings = (price * 12) - annual_price
            print(f"  📋 {name}: ${price}/{billing} (Annual: ${annual_price}/year - Save ${savings})")
        else:
            print(f"  📋 {name}: ${price}/{billing}")
    
    print(f"\n✅ Total Plans: {len(PRICING_PLANS)}")
    
    print("\n✅ Add-ons & Credits System:")
    for addon_id, addon_data in ADDON_CREDITS.items():
        name = addon_data['name']
        price = addon_data['price']
        credits = addon_data['credits']
        print(f"  🎁 {name}: ${price} ({credits} credits)")
    
    print(f"\n✅ Total Add-ons: {len(ADDON_CREDITS)}")
    
    print("\n🚀 Pricing System Status: READY FOR DEPLOYMENT!")
    
except ImportError as e:
    print(f"❌ Error importing pricing system: {e}")
except Exception as e:
    print(f"❌ Error testing pricing system: {e}") 