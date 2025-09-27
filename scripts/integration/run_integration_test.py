#!/usr/bin/env python3
"""
Run Integration Test for All Supabase Tables
Quick script to test database integration
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def main():
    print("🚀 Running Supabase Tables Integration Test...")
    print("=" * 50)
    
    try:
        # Run the migration first
        print("📋 Running database migrations...")
        os.system("python scripts/migration/run_migrations.py upgrade")
        
        # Run the integration test
        print("🔗 Testing table connections...")
        from scripts.integration.connect_all_tables import main as integration_main
        success = integration_main()
        
        if success:
            print("\n✅ ALL TABLES SUCCESSFULLY INTEGRATED!")
            print("🎯 Your Supabase database is fully connected")
            print("📊 Check /dashboard for live data")
            print("📈 Use /bhiv/analytics for detailed metrics")
        else:
            print("\n⚠️  Some integration issues found")
            print("🔧 Check the logs above for details")
        
        return success
        
    except Exception as e:
        print(f"\n❌ Integration test failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)