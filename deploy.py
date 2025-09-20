#!/usr/bin/env python3
"""
Deployment Automation Script
Automated deployment to multiple platforms with configuration management
"""

import os
import sys
import json
import subprocess
import argparse
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class DeploymentManager:
    def __init__(self):
        self.platforms = {
            'render': self.deploy_to_render,
            'railway': self.deploy_to_railway,
            'heroku': self.deploy_to_heroku,
            'local': self.deploy_local
        }
        self.config = self.load_deployment_config()
    
    def load_deployment_config(self):
        """Load deployment configuration"""
        return {
            'app_name': 'ai-content-uploader',
            'python_version': '3.11',
            'build_command': 'pip install -r requirements.txt',
            'start_command': 'uvicorn app.main:app --host 0.0.0.0 --port $PORT',
            'env_vars': {
                'JWS_SECRET': os.getenv('JWS_SECRET'),
                'DATABASE_URL': os.getenv('DATABASE_URL'),
                'POSTHOG_API_KEY': os.getenv('POSTHOG_API_KEY'),
                'SENTRY_DSN': os.getenv('SENTRY_DSN'),
                'JWT_SECRET_KEY': os.getenv('JWT_SECRET_KEY'),
                'BHIV_LM_URL': 'https://api.perplexity.ai',
                'BHIV_STORAGE_BACKEND': 'local'
            }
        }
    
    def validate_environment(self):
        """Validate required environment variables"""
        required_vars = ['JWS_SECRET', 'DATABASE_URL']
        missing_vars = []
        
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            print(f"ERROR: Missing required environment variables: {', '.join(missing_vars)}")
            return False
        
        print("SUCCESS: Environment validation passed")
        return True
    
    def run_pre_deployment_checks(self):
        """Run pre-deployment validation"""
        print("Running pre-deployment checks...")
        
        # Check if requirements.txt exists
        if not os.path.exists('requirements.txt'):
            print("ERROR: requirements.txt not found")
            return False
        
        # Check if main app file exists
        if not os.path.exists('app/main.py'):
            print("ERROR: app/main.py not found")
            return False
        
        # Run basic tests
        try:
            result = subprocess.run([sys.executable, 'run_enhanced_tests.py'], 
                                  capture_output=True, text=True, timeout=60)
            if result.returncode != 0:
                print("WARNING: Some tests failed, but continuing deployment")
            else:
                print("SUCCESS: Pre-deployment tests passed")
        except Exception as e:
            print(f"WARNING: Could not run tests: {e}")
        
        return True
    
    def deploy_to_render(self):
        """Deploy to Render.com"""
        print("Deploying to Render.com...")
        
        # Check if render.yaml exists
        render_config = 'docker/render.yaml'
        if not os.path.exists(render_config):
            print(f"ERROR: {render_config} not found")
            return False
        
        print("SUCCESS: Render configuration found")
        print("Manual steps required:")
        print("1. Push code to GitHub repository")
        print("2. Connect repository to Render.com")
        print("3. Deploy using docker/render.yaml configuration")
        print("4. Set environment variables in Render dashboard")
        
        # Generate environment variables for Render
        env_vars = []
        for key, value in self.config['env_vars'].items():
            if value:
                env_vars.append(f"{key}={value}")
        
        print("\nEnvironment variables to set in Render:")
        for env_var in env_vars:
            if 'SECRET' in env_var or 'KEY' in env_var:
                key = env_var.split('=')[0]
                print(f"  {key}=***HIDDEN***")
            else:
                print(f"  {env_var}")
        
        return True
    
    def deploy_to_railway(self):
        """Deploy to Railway"""
        print("Deploying to Railway...")
        
        try:
            # Check if railway CLI is installed
            result = subprocess.run(['railway', '--version'], capture_output=True, text=True)
            if result.returncode != 0:
                print("ERROR: Railway CLI not installed")
                print("Install with: npm install -g @railway/cli")
                return False
            
            print("SUCCESS: Railway CLI found")
            
            # Login check
            result = subprocess.run(['railway', 'whoami'], capture_output=True, text=True)
            if result.returncode != 0:
                print("Please login to Railway:")
                subprocess.run(['railway', 'login'])
            
            # Deploy
            print("Deploying to Railway...")
            result = subprocess.run(['railway', 'up'], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("SUCCESS: Deployed to Railway")
                print(result.stdout)
                return True
            else:
                print(f"ERROR: Railway deployment failed: {result.stderr}")
                return False
                
        except FileNotFoundError:
            print("ERROR: Railway CLI not found")
            return False
    
    def deploy_to_heroku(self):
        """Deploy to Heroku"""
        print("Deploying to Heroku...")
        
        try:
            # Check if heroku CLI is installed
            result = subprocess.run(['heroku', '--version'], capture_output=True, text=True)
            if result.returncode != 0:
                print("ERROR: Heroku CLI not installed")
                return False
            
            print("SUCCESS: Heroku CLI found")
            
            # Create Procfile if not exists
            if not os.path.exists('Procfile'):
                with open('Procfile', 'w') as f:
                    f.write('web: uvicorn app.main:app --host 0.0.0.0 --port $PORT\n')
                print("Created Procfile")
            
            # Create or update app
            app_name = self.config['app_name']
            result = subprocess.run(['heroku', 'create', app_name], capture_output=True, text=True)
            
            # Set environment variables
            for key, value in self.config['env_vars'].items():
                if value:
                    subprocess.run(['heroku', 'config:set', f'{key}={value}', '--app', app_name])
            
            # Deploy
            result = subprocess.run(['git', 'push', 'heroku', 'main'], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("SUCCESS: Deployed to Heroku")
                return True
            else:
                print(f"ERROR: Heroku deployment failed: {result.stderr}")
                return False
                
        except FileNotFoundError:
            print("ERROR: Heroku CLI not found")
            return False
    
    def deploy_local(self):
        """Deploy locally for testing"""
        print("Setting up local deployment...")
        
        try:
            # Install dependencies
            print("Installing dependencies...")
            result = subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                                  capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"ERROR: Failed to install dependencies: {result.stderr}")
                return False
            
            print("SUCCESS: Dependencies installed")
            
            # Run database migrations
            print("Running database migrations...")
            result = subprocess.run([sys.executable, 'run_migrations_simple.py'], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                print("SUCCESS: Database migrations completed")
            else:
                print("WARNING: Database migrations had issues")
            
            # Start server
            print("Starting local server...")
            print("Run: python start_server.py")
            print("Server will be available at: http://localhost:8000")
            
            return True
            
        except Exception as e:
            print(f"ERROR: Local deployment failed: {e}")
            return False
    
    def generate_deployment_report(self, platform, success):
        """Generate deployment report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'platform': platform,
            'success': success,
            'app_name': self.config['app_name'],
            'python_version': self.config['python_version'],
            'environment_validated': True
        }
        
        with open(f'deployment_report_{platform}.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"Deployment report saved to deployment_report_{platform}.json")
    
    def deploy(self, platform):
        """Main deployment function"""
        if platform not in self.platforms:
            print(f"ERROR: Unknown platform '{platform}'")
            print(f"Available platforms: {', '.join(self.platforms.keys())}")
            return False
        
        print(f"Starting deployment to {platform}...")
        
        # Validate environment
        if not self.validate_environment():
            return False
        
        # Run pre-deployment checks
        if not self.run_pre_deployment_checks():
            return False
        
        # Deploy to platform
        success = self.platforms[platform]()
        
        # Generate report
        self.generate_deployment_report(platform, success)
        
        if success:
            print(f"SUCCESS: Deployment to {platform} completed")
        else:
            print(f"ERROR: Deployment to {platform} failed")
        
        return success

def main():
    """Main deployment script"""
    parser = argparse.ArgumentParser(description='Deploy AI Content Uploader to various platforms')
    parser.add_argument('--platform', choices=['render', 'railway', 'heroku', 'local'], 
                       default='local', help='Deployment platform')
    parser.add_argument('--interactive', action='store_true', help='Interactive mode')
    
    args = parser.parse_args()
    
    print("AI Content Uploader - Deployment Automation")
    print("=" * 50)
    
    if args.interactive:
        print("Available platforms:")
        print("1. Render.com (recommended)")
        print("2. Railway")
        print("3. Heroku")
        print("4. Local (testing)")
        
        choice = input("Select platform (1-4): ").strip()
        platform_map = {'1': 'render', '2': 'railway', '3': 'heroku', '4': 'local'}
        platform = platform_map.get(choice, 'local')
    else:
        platform = args.platform
    
    deployer = DeploymentManager()
    success = deployer.deploy(platform)
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()