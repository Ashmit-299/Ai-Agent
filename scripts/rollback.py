#!/usr/bin/env python3
"""
Python-based automated rollback system
Cross-platform rollback for failed deployments
"""

import os
import sys
import subprocess
import requests
import time
import json
from datetime import datetime
from pathlib import Path
import argparse

class RollbackManager:
    def __init__(self, environment="production", target="previous"):
        self.environment = environment
        self.target = target
        self.backup_dir = None
        
    def get_previous_version(self):
        """Get previous working version from git"""
        try:
            # Try to get previous tag
            result = subprocess.run(
                ["git", "describe", "--tags", "--abbrev=0", "HEAD~1"],
                capture_output=True, text=True, check=False
            )
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
            
            # Fallback to commit hash
            result = subprocess.run(
                ["git", "rev-parse", "HEAD~1"],
                capture_output=True, text=True, check=False
            )
            if result.returncode == 0:
                return result.stdout.strip()[:8]
                
        except FileNotFoundError:
            pass
        
        return "latest"
    
    def backup_current_state(self):
        """Create backup of current state"""
        print("[BACKUP] Creating backup of current state...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.backup_dir = Path(f"backups/{timestamp}")
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Backup database if PostgreSQL
        database_url = os.getenv("DATABASE_URL", "")
        if database_url.startswith("postgresql"):
            print("[BACKUP] Backing up database...")
            try:
                subprocess.run([
                    "pg_dump", database_url, 
                    "-f", str(self.backup_dir / "database_backup.sql")
                ], check=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                print("[WARNING] Database backup failed, continuing rollback...")
        
        # Backup logs
        logs_dir = Path("logs")
        if logs_dir.exists():
            subprocess.run([
                "cp", "-r", str(logs_dir), str(self.backup_dir)
            ], check=False)
        
        # Store current version
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                capture_output=True, text=True, check=False
            )
            current_version = result.stdout.strip() if result.returncode == 0 else "unknown"
        except FileNotFoundError:
            current_version = "unknown"
        
        (self.backup_dir / "current_version.txt").write_text(current_version)
        
        print(f"[OK] Backup created in {self.backup_dir}")
    
    def rollback_render_deployment(self, service_id, version):
        """Rollback Render deployment"""
        api_key = os.getenv("RENDER_API_KEY")
        if not api_key or not service_id:
            print("[WARNING] Render API key or service ID not found")
            return False
        
        url = f"https://api.render.com/v1/services/{service_id}/deploys"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "imageUrl": f"ashmitpandey299/ai-uploader-agent:{version}",
            "clearCache": "clear"
        }
        
        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            print(f"[OK] Render deployment rollback initiated")
            return True
        except requests.RequestException as e:
            print(f"[ERROR] Render rollback failed: {e}")
            return False
    
    def perform_rollback(self, target_version):
        """Perform the actual rollback"""
        print(f"[ROLLBACK] Rolling back to version: {target_version}")
        
        if self.environment == "production":
            service_id = os.getenv("RENDER_PRODUCTION_SERVICE_ID")
            self.rollback_render_deployment(service_id, target_version)
        elif self.environment == "staging":
            service_id = os.getenv("RENDER_STAGING_SERVICE_ID")
            self.rollback_render_deployment(service_id, target_version)
        else:
            print(f"[ERROR] Rollback not configured for environment: {self.environment}")
            return False
        
        return True
    
    def verify_rollback(self, api_url):
        """Verify rollback was successful"""
        print("[VERIFY] Verifying rollback...")
        
        # Wait for deployment
        time.sleep(60)
        
        # Health check attempts
        for attempt in range(1, 6):
            try:
                response = requests.get(f"{api_url}/health", timeout=10)
                if response.status_code == 200:
                    print(f"[OK] Health check passed (attempt {attempt})")
                    break
            except requests.RequestException:
                pass
            
            print(f"[WARNING] Health check failed (attempt {attempt}), retrying...")
            time.sleep(30)
            
            if attempt == 5:
                print("[ERROR] Rollback verification failed!")
                return False
        
        # Test API docs endpoint
        try:
            response = requests.get(f"{api_url}/docs", timeout=10)
            if response.status_code != 200:
                print("[ERROR] API docs not accessible after rollback")
                return False
        except requests.RequestException:
            print("[ERROR] API docs not accessible after rollback")
            return False
        
        print("[OK] Rollback verification successful")
        return True
    
    def notify_rollback(self, status, version):
        """Send rollback notifications"""
        print("[NOTIFY] Sending rollback notification...")
        
        # Sentry notification
        sentry_dsn = os.getenv("SENTRY_DSN")
        if sentry_dsn:
            try:
                import sentry_sdk
                sentry_sdk.init(sentry_dsn)
                level = "error" if status == "failed" else "warning"
                sentry_sdk.capture_message(
                    f"Rollback {status} to version {version}",
                    level=level
                )
            except ImportError:
                print("[WARNING] Sentry SDK not available")
    
    def execute_rollback(self):
        """Main rollback execution"""
        print("🚨 ROLLBACK INITIATED 🚨")
        print(f"Environment: {self.environment}")
        print(f"Target: {self.target}")
        
        # Determine target version
        if self.target == "previous":
            target_version = self.get_previous_version()
        else:
            target_version = self.target
        
        if not target_version:
            print("[ERROR] Could not determine target version for rollback")
            return False
        
        print(f"Target version: {target_version}")
        
        # Interactive confirmation
        if sys.stdin.isatty():
            response = input(f"⚠️ Are you sure you want to rollback to {target_version}? (y/N): ")
            if response.lower() != 'y':
                print("[CANCELLED] Rollback cancelled")
                return False
        
        # Execute rollback steps
        self.backup_current_state()
        
        if not self.perform_rollback(target_version):
            print("[ERROR] Rollback execution failed")
            return False
        
        # Determine API URL
        if self.environment == "production":
            api_url = os.getenv("PRODUCTION_API_URL", "https://ai-agent-aff6.onrender.com")
        else:
            api_url = os.getenv("STAGING_API_URL", "https://staging-ai-agent.onrender.com")
        
        # Verify rollback
        if self.verify_rollback(api_url):
            print("🎉 Rollback completed successfully!")
            self.notify_rollback("completed", target_version)
            return True
        else:
            print("❌ Rollback verification failed!")
            self.notify_rollback("failed", target_version)
            return False

def main():
    parser = argparse.ArgumentParser(description="Automated rollback system")
    parser.add_argument("environment", choices=["production", "staging"], 
                       default="production", nargs="?",
                       help="Target environment")
    parser.add_argument("target", default="previous", nargs="?",
                       help="Rollback target (previous or specific version)")
    
    args = parser.parse_args()
    
    rollback_manager = RollbackManager(args.environment, args.target)
    success = rollback_manager.execute_rollback()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()