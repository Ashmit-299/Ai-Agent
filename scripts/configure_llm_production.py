#!/usr/bin/env python3
"""
Production LLM Configuration Script
Configures Perplexity API for production environment
"""

import os
import requests
import json
from datetime import datetime

class LLMProductionConfig:
    def __init__(self):
        self.perplexity_url = "https://api.perplexity.ai/chat/completions"
        self.api_key = None
        
    def validate_api_key(self, api_key):
        """Validate Perplexity API key"""
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        test_payload = {
            "model": "llama-3.1-sonar-small-128k-online",
            "messages": [
                {"role": "user", "content": "Test connection"}
            ],
            "max_tokens": 10
        }
        
        try:
            response = requests.post(self.perplexity_url, headers=headers, json=test_payload, timeout=30)
            if response.status_code == 200:
                print("✅ Perplexity API key validated successfully")
                self.api_key = api_key
                return True
            else:
                print(f"❌ API key validation failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ API key validation error: {e}")
            return False
    
    def test_storyboard_generation(self):
        """Test storyboard generation with Perplexity API"""
        if not self.api_key:
            print("❌ No valid API key available")
            return False
            
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        test_script = "A young entrepreneur starts a tech company in their garage."
        
        payload = {
            "model": "llama-3.1-sonar-small-128k-online",
            "messages": [
                {
                    "role": "user", 
                    "content": f"Generate a video storyboard for this script: {test_script}. Return JSON format with scenes array containing id, text, and duration fields."
                }
            ],
            "max_tokens": 500
        }
        
        try:
            response = requests.post(self.perplexity_url, headers=headers, json=payload, timeout=30)
            if response.status_code == 200:
                result = response.json()
                print("✅ Storyboard generation test successful")
                return True
            else:
                print(f"❌ Storyboard generation failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Storyboard generation error: {e}")
            return False
    
    def update_environment_config(self):
        """Update environment configuration for production"""
        config_updates = {
            "PERPLEXITY_API_KEY": self.api_key,
            "BHIV_LM_URL": "https://api.perplexity.ai",
            "BHIV_LM_API_KEY": self.api_key,
            "BHIV_LM_TIMEOUT": "30"
        }
        
        print("🔧 Production LLM Configuration:")
        for key, value in config_updates.items():
            if "API_KEY" in key:
                print(f"  {key}: {'*' * 20}")  # Hide API key
            else:
                print(f"  {key}: {value}")
        
        return config_updates
    
    def generate_config_report(self):
        """Generate LLM configuration report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "llm_provider": "Perplexity AI",
            "api_endpoint": self.perplexity_url,
            "api_key_configured": bool(self.api_key),
            "validation_passed": bool(self.api_key),
            "recommended_model": "llama-3.1-sonar-small-128k-online",
            "timeout_seconds": 30,
            "fallback_enabled": True
        }
        
        with open("llm_config_report.json", "w") as f:
            json.dump(report, f, indent=2)
        
        print("📋 LLM configuration report saved to llm_config_report.json")
        return report

def main():
    """Main LLM configuration workflow"""
    print("🤖 Production LLM Configuration")
    print("=" * 50)
    
    config = LLMProductionConfig()
    
    # Get API key from user
    api_key = input("Enter your Perplexity API key: ").strip()
    
    if not api_key:
        print("❌ No API key provided")
        return
    
    # Validate API key
    if config.validate_api_key(api_key):
        # Test storyboard generation
        if config.test_storyboard_generation():
            print("✅ LLM service configured successfully!")
            
            # Update environment configuration
            env_config = config.update_environment_config()
            
            print("\n📝 Add these environment variables to your Render.com service:")
            print("PERPLEXITY_API_KEY:", api_key)
            
        else:
            print("⚠️ LLM service validation failed")
    else:
        print("❌ Invalid API key")
    
    # Generate report
    config.generate_config_report()

if __name__ == "__main__":
    main()