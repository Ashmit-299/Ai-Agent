#!/usr/bin/env python3
"""
Fix bcrypt warnings and import issues
"""

import warnings
import os

# Suppress bcrypt warnings
warnings.filterwarnings("ignore", message=".*bcrypt.*")
warnings.filterwarnings("ignore", category=UserWarning, module="passlib")

# Set environment variable to suppress bcrypt warnings
os.environ["PASSLIB_SUPPRESS_WARNINGS"] = "1"

print("Bcrypt warnings suppressed")