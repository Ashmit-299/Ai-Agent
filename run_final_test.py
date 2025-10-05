#!/usr/bin/env python3
"""
Run Final Test with Environment
Loads environment variables and runs the fixed checklist
"""

import os
import sys
import subprocess
from dotenv import load_dotenv

def main():
    """Load environment and run test"""
    print("Loading environment variables...")
    
    # Load .env file
    load_dotenv()
    
    # Verify environment variables are loaded
    required_vars = ["DATABASE_URL", "JWT_SECRET_KEY", "ENVIRONMENT"]
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"LOADED: {var}")
        else:
            print(f"MISSING: {var}")
    
    print("\nRunning fixed pre-production checklist...")
    
    # Run the fixed checklist
    try:
        result = subprocess.run([
            sys.executable, 
            "scripts/pre_production_checklist_fixed.py",
            "--api-url", "http://localhost:9000"
        ], timeout=120)
        
        if result.returncode == 0:
            print("\n100% SUCCESS ACHIEVED!")
            return True
        else:
            print(f"\nTest failed with return code: {result.returncode}")
            return False
            
    except Exception as e:
        print(f"Error running test: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)