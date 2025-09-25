import warnings
import sys
import os

# Redirect stderr to suppress the error
class SuppressStderr:
    def __enter__(self):
        self._original_stderr = sys.stderr
        sys.stderr = open(os.devnull, 'w')
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stderr.close()
        sys.stderr = self._original_stderr

# Monkey patch passlib to suppress the error
try:
    import passlib.handlers.bcrypt
    original_load_backend = passlib.handlers.bcrypt.bcrypt._load_backend_mixin
    
    def silent_load_backend(self):
        with SuppressStderr():
            try:
                return original_load_backend(self)
            except AttributeError:
                import bcrypt as _bcrypt
                if not hasattr(_bcrypt, '__about__'):
                    class MockAbout:
                        __version__ = "4.1.2"
                    _bcrypt.__about__ = MockAbout()
                return original_load_backend(self)
    
    passlib.handlers.bcrypt.bcrypt._load_backend_mixin = silent_load_backend
except:
    pass