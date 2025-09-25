#!/usr/bin/env python3
"""
Suppress bcrypt version warning from passlib
"""

import warnings
import sys
import logging

def suppress_bcrypt_warnings():
    """Suppress bcrypt version warnings"""
    # Suppress specific bcrypt warnings
    warnings.filterwarnings("ignore", message=".*bcrypt.*", category=UserWarning)
    warnings.filterwarnings("ignore", message=".*__about__.*", category=UserWarning)
    
    # Patch passlib to handle missing __about__ attribute
    try:
        import passlib.handlers.bcrypt
        original_load_backend = passlib.handlers.bcrypt.bcrypt._load_backend_mixin
        
        def patched_load_backend(self):
            try:
                return original_load_backend(self)
            except AttributeError as e:
                if "__about__" in str(e):
                    # Silently handle missing __about__ attribute
                    import bcrypt as _bcrypt
                    # Set a fallback version
                    if not hasattr(_bcrypt, '__about__'):
                        class MockAbout:
                            __version__ = "4.1.2"
                        _bcrypt.__about__ = MockAbout()
                    return original_load_backend(self)
                raise
        
        passlib.handlers.bcrypt.bcrypt._load_backend_mixin = patched_load_backend
        
    except ImportError:
        pass  # passlib not available
    except Exception:
        pass  # Silently ignore patching errors

# Apply suppression immediately when imported
suppress_bcrypt_warnings()