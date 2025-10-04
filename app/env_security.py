#!/usr/bin/env python3
"""
Secure environment variable management and validation
"""

import os
import secrets
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path

logger = logging.getLogger(__name__)

class EnvironmentSecurityManager:
    """Secure environment variable management"""
    
    # Required environment variables for production
    REQUIRED_PRODUCTION_VARS = {
        'DATABASE_URL': 'Database connection string',
        'JWT_SECRET_KEY': 'JWT signing secret',
        'SENTRY_DSN': 'Sentry error tracking DSN',
        'POSTHOG_API_KEY': 'PostHog analytics API key'
    }
    
    # Optional environment variables
    OPTIONAL_VARS = {
        'SUPABASE_URL': 'Supabase project URL',
        'SUPABASE_JWT_SECRET': 'Supabase JWT secret',
        'PERPLEXITY_API_KEY': 'Perplexity AI API key',
        'BHIV_LM_URL': 'Language model service URL',
        'BHIV_LM_API_KEY': 'Language model API key',
        'ENVIRONMENT': 'Deployment environment (development/production)',
        'POSTHOG_HOST': 'PostHog host URL'
    }
    
    # Sensitive variables that should never be logged
    SENSITIVE_VARS = {
        'JWT_SECRET_KEY', 'SENTRY_DSN', 'POSTHOG_API_KEY', 
        'SUPABASE_JWT_SECRET', 'PERPLEXITY_API_KEY', 'BHIV_LM_API_KEY',
        'DATABASE_URL'
    }
    
    @classmethod
    def validate_environment(cls) -> Dict[str, Any]:
        """Validate environment configuration"""
        validation_result = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'missing_required': [],
            'missing_optional': [],
            'insecure_values': []
        }
        
        environment = os.getenv('ENVIRONMENT', 'development')
        
        # Check required variables for production
        if environment == 'production':
            for var_name, description in cls.REQUIRED_PRODUCTION_VARS.items():
                value = os.getenv(var_name)
                if not value:
                    validation_result['missing_required'].append({
                        'name': var_name,
                        'description': description
                    })
                    validation_result['valid'] = False
                else:
                    # Check for insecure default values
                    if cls._is_insecure_value(var_name, value):
                        validation_result['insecure_values'].append({
                            'name': var_name,
                            'issue': 'Using default or weak value'
                        })
                        validation_result['warnings'].append(f"{var_name} appears to use a default or weak value")
        
        # Check optional variables
        for var_name, description in cls.OPTIONAL_VARS.items():
            value = os.getenv(var_name)
            if not value:
                validation_result['missing_optional'].append({
                    'name': var_name,
                    'description': description
                })
            elif cls._is_insecure_value(var_name, value):
                validation_result['insecure_values'].append({
                    'name': var_name,
                    'issue': 'Using default or weak value'
                })
        
        # Check for .env file security
        env_file_path = Path('.env')
        if env_file_path.exists():
            try:
                # Check file permissions (Unix-like systems)
                if hasattr(os, 'stat'):
                    stat_info = env_file_path.stat()
                    # Check if file is readable by others (not secure)
                    if stat_info.st_mode & 0o044:  # Check other read permissions
                        validation_result['warnings'].append('.env file has overly permissive permissions')
            except Exception:
                pass  # Skip permission check on Windows or if it fails
        
        return validation_result
    
    @classmethod
    def _is_insecure_value(cls, var_name: str, value: str) -> bool:
        """Check if environment variable has insecure default value"""
        insecure_patterns = {
            'JWT_SECRET_KEY': ['your-secret-key', 'change-me', 'secret', 'jwt-secret'],
            'DATABASE_URL': ['sqlite:///', 'postgres://user:pass@localhost'],
            'SENTRY_DSN': ['https://example@sentry.io'],
            'POSTHOG_API_KEY': ['phc_example', 'your-api-key'],
            'SUPABASE_JWT_SECRET': ['your-jwt-secret'],
            'PERPLEXITY_API_KEY': ['your-perplexity-key'],
            'BHIV_LM_API_KEY': ['demo_api_key', 'your-api-key']
        }
        
        if var_name in insecure_patterns:
            value_lower = value.lower()
            for pattern in insecure_patterns[var_name]:
                if pattern.lower() in value_lower:
                    return True
        
        # Check for very short secrets (likely insecure)
        if 'secret' in var_name.lower() or 'key' in var_name.lower():
            if len(value) < 32:
                return True
        
        return False
    
    @classmethod
    def generate_secure_jwt_secret(cls) -> str:
        """Generate a cryptographically secure JWT secret"""
        return secrets.token_urlsafe(64)
    
    @classmethod
    def mask_sensitive_value(cls, var_name: str, value: str) -> str:
        """Mask sensitive values for logging"""
        if var_name in cls.SENSITIVE_VARS:
            if len(value) <= 8:
                return '*' * len(value)
            else:
                return value[:4] + '*' * (len(value) - 8) + value[-4:]
        return value
    
    @classmethod
    def get_safe_env_summary(cls) -> Dict[str, Any]:
        """Get environment summary with sensitive values masked"""
        summary = {
            'environment': os.getenv('ENVIRONMENT', 'development'),
            'configured_vars': {},
            'missing_vars': []
        }
        
        # Check all known variables
        all_vars = {**cls.REQUIRED_PRODUCTION_VARS, **cls.OPTIONAL_VARS}
        
        for var_name, description in all_vars.items():
            value = os.getenv(var_name)
            if value:
                summary['configured_vars'][var_name] = {
                    'configured': True,
                    'value': cls.mask_sensitive_value(var_name, value),
                    'description': description
                }
            else:
                summary['missing_vars'].append({
                    'name': var_name,
                    'description': description,
                    'required': var_name in cls.REQUIRED_PRODUCTION_VARS
                })
        
        return summary
    
    @classmethod
    def create_secure_env_template(cls) -> str:
        """Create a secure .env template"""
        template_lines = [
            "# AI Content Uploader Environment Variables",
            "# SECURITY: Keep this file secure and never commit to version control",
            "",
            "# Environment Configuration",
            "ENVIRONMENT=development",
            "",
            "# Database Configuration",
            "# For production, use PostgreSQL/Supabase",
            "DATABASE_URL=postgresql://user:password@host:port/database",
            "",
            "# Security Configuration",
            f"JWT_SECRET_KEY={cls.generate_secure_jwt_secret()}",
            "",
            "# Observability Configuration",
            "SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id",
            "POSTHOG_API_KEY=phc_your_posthog_api_key",
            "POSTHOG_HOST=https://us.posthog.com",
            "",
            "# Optional: Supabase Configuration",
            "SUPABASE_URL=https://your-project.supabase.co",
            "SUPABASE_JWT_SECRET=your-supabase-jwt-secret",
            "",
            "# Optional: AI/LLM Configuration",
            "PERPLEXITY_API_KEY=your-perplexity-api-key",
            "BHIV_LM_URL=http://localhost:8001",
            "BHIV_LM_API_KEY=your-lm-api-key",
            "",
            "# Storage Configuration",
            "BHIV_STORAGE_BACKEND=local",
            "BHIV_BUCKET_PATH=bucket",
            "",
            "# Performance Monitoring",
            "ENABLE_PERFORMANCE_MONITORING=true",
            "ENABLE_USER_ANALYTICS=true",
            "ENABLE_ERROR_REPORTING=true"
        ]
        
        return '\n'.join(template_lines)
    
    @classmethod
    def secure_env_file(cls, env_file_path: str = '.env') -> bool:
        """Secure .env file permissions (Unix-like systems only)"""
        try:
            env_path = Path(env_file_path)
            if env_path.exists() and hasattr(os, 'chmod'):
                # Set file permissions to read/write for owner only
                os.chmod(env_path, 0o600)
                logger.info(f"Secured {env_file_path} file permissions")
                return True
        except Exception as e:
            logger.warning(f"Could not secure {env_file_path} permissions: {e}")
        
        return False
    
    @classmethod
    def check_env_file_security(cls, env_file_path: str = '.env') -> Dict[str, Any]:
        """Check .env file security"""
        security_check = {
            'file_exists': False,
            'permissions_secure': False,
            'contains_secrets': False,
            'recommendations': []
        }
        
        env_path = Path(env_file_path)
        
        if env_path.exists():
            security_check['file_exists'] = True
            
            # Check permissions (Unix-like systems)
            try:
                if hasattr(os, 'stat'):
                    stat_info = env_path.stat()
                    # Check if file is only readable by owner
                    if (stat_info.st_mode & 0o077) == 0:
                        security_check['permissions_secure'] = True
                    else:
                        security_check['recommendations'].append(
                            "Set secure file permissions: chmod 600 .env"
                        )
            except Exception:
                security_check['recommendations'].append(
                    "Could not check file permissions"
                )
            
            # Check for secrets in file
            try:
                with open(env_path, 'r') as f:
                    content = f.read()
                    for var_name in cls.SENSITIVE_VARS:
                        if var_name in content:
                            security_check['contains_secrets'] = True
                            break
            except Exception:
                pass
            
            # Add general recommendations
            if security_check['contains_secrets']:
                security_check['recommendations'].extend([
                    "Never commit .env file to version control",
                    "Use different secrets for each environment",
                    "Rotate secrets regularly"
                ])
        else:
            security_check['recommendations'].append(
                "Create .env file from .env.example template"
            )
        
        return security_check

def validate_environment() -> Dict[str, Any]:
    """Public function for environment validation"""
    return EnvironmentSecurityManager.validate_environment()

def get_env_security_status() -> Dict[str, Any]:
    """Get comprehensive environment security status"""
    return {
        'validation': EnvironmentSecurityManager.validate_environment(),
        'env_summary': EnvironmentSecurityManager.get_safe_env_summary(),
        'file_security': EnvironmentSecurityManager.check_env_file_security()
    }