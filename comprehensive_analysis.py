#!/usr/bin/env python3
"""
Comprehensive AI-Agent Project Analysis and Testing Script
"""

import os
import sys
import json
import time
import traceback
from pathlib import Path
from typing import Dict, List, Any

class ProjectAnalyzer:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.issues = []
        self.fixes_applied = []
        self.test_results = []
        
    def log_issue(self, category: str, description: str, severity: str = "medium", fix: str = None):
        """Log an issue found during analysis"""
        issue = {
            "category": category,
            "description": description,
            "severity": severity,
            "fix": fix,
            "timestamp": time.time()
        }
        self.issues.append(issue)
        print(f"[{severity.upper()}] {category}: {description}")
        if fix:
            print(f"  → Fix: {fix}")
    
    def log_fix(self, description: str, success: bool = True):
        """Log a fix that was applied"""
        fix = {
            "description": description,
            "success": success,
            "timestamp": time.time()
        }
        self.fixes_applied.append(fix)
        status = "✅" if success else "❌"
        print(f"{status} Fix applied: {description}")
    
    def check_environment(self) -> Dict[str, Any]:
        """Check environment configuration"""
        print("\n🔍 CHECKING ENVIRONMENT...")
        
        env_file = self.project_root / ".env"
        env_example = self.project_root / ".env.example"
        
        results = {
            "env_file_exists": env_file.exists(),
            "env_example_exists": env_example.exists(),
            "required_vars": [],
            "missing_vars": [],
            "database_config": {}
        }
        
        if not env_file.exists():
            self.log_issue("Environment", ".env file missing", "high", 
                          "Copy .env.example to .env and configure")
            return results
        
        # Read environment variables
        try:
            with open(env_file, 'r') as f:
                env_content = f.read()
            
            required_vars = [
                "DATABASE_URL", "JWT_SECRET_KEY", "SENTRY_DSN", 
                "POSTHOG_API_KEY", "ENVIRONMENT"
            ]
            
            for var in required_vars:
                if var in env_content:
                    results["required_vars"].append(var)
                else:
                    results["missing_vars"].append(var)
                    self.log_issue("Environment", f"Missing {var}", "medium")
            
            # Check database URL
            if "DATABASE_URL" in env_content:
                if "postgresql" in env_content:
                    results["database_config"]["type"] = "postgresql"
                elif "sqlite" in env_content:
                    results["database_config"]["type"] = "sqlite"
                else:
                    results["database_config"]["type"] = "unknown"
            
        except Exception as e:
            self.log_issue("Environment", f"Error reading .env: {e}", "high")
        
        return results
    
    def check_dependencies(self) -> Dict[str, Any]:
        """Check if all dependencies are installed"""
        print("\n📦 CHECKING DEPENDENCIES...")
        
        requirements_file = self.project_root / "requirements.txt"
        results = {
            "requirements_exists": requirements_file.exists(),
            "installed_packages": [],
            "missing_packages": [],
            "import_errors": []
        }
        
        if not requirements_file.exists():
            self.log_issue("Dependencies", "requirements.txt not found", "high")
            return results
        
        # Test critical imports
        critical_imports = [
            ("fastapi", "FastAPI framework"),
            ("uvicorn", "ASGI server"),
            ("sqlmodel", "Database ORM"),
            ("psycopg2", "PostgreSQL adapter"),
            ("pydantic", "Data validation"),
            ("python_jose", "JWT handling"),
            ("passlib", "Password hashing"),
            ("moviepy", "Video processing"),
            ("sentry_sdk", "Error tracking"),
            ("posthog", "Analytics")
        ]
        
        for package, description in critical_imports:
            try:
                __import__(package)
                results["installed_packages"].append(package)
                print(f"✅ {package} - {description}")
            except ImportError as e:
                results["missing_packages"].append(package)
                results["import_errors"].append(str(e))
                self.log_issue("Dependencies", f"Missing {package} - {description}", 
                              "high", f"pip install {package}")
        
        return results
    
    def check_database_connection(self) -> Dict[str, Any]:
        """Test database connectivity"""
        print("\n🗄️ CHECKING DATABASE CONNECTION...")
        
        results = {
            "connection_successful": False,
            "database_type": "unknown",
            "error": None
        }
        
        try:
            # Load environment
            from dotenv import load_dotenv
            load_dotenv()
            
            database_url = os.getenv("DATABASE_URL")
            if not database_url:
                self.log_issue("Database", "DATABASE_URL not set", "high")
                return results
            
            if "postgresql" in database_url:
                results["database_type"] = "postgresql"
                try:
                    import psycopg2
                    conn = psycopg2.connect(database_url)
                    cursor = conn.cursor()
                    cursor.execute("SELECT 1")
                    cursor.fetchone()
                    conn.close()
                    results["connection_successful"] = True
                    print("✅ PostgreSQL connection successful")
                except Exception as e:
                    results["error"] = str(e)
                    self.log_issue("Database", f"PostgreSQL connection failed: {e}", "high")
            
            elif "sqlite" in database_url:
                results["database_type"] = "sqlite"
                try:
                    import sqlite3
                    conn = sqlite3.connect(database_url.replace("sqlite:///", ""))
                    conn.execute("SELECT 1")
                    conn.close()
                    results["connection_successful"] = True
                    print("✅ SQLite connection successful")
                except Exception as e:
                    results["error"] = str(e)
                    self.log_issue("Database", f"SQLite connection failed: {e}", "medium")
        
        except Exception as e:
            results["error"] = str(e)
            self.log_issue("Database", f"Database check failed: {e}", "high")
        
        return results
    
    def test_application_import(self) -> Dict[str, Any]:
        """Test if the main application can be imported"""
        print("\n🚀 TESTING APPLICATION IMPORT...")
        
        results = {
            "main_app_import": False,
            "routes_import": False,
            "models_import": False,
            "errors": []
        }
        
        # Test main app import
        try:
            sys.path.insert(0, str(self.project_root))
            from app.main import app
            results["main_app_import"] = True
            print("✅ Main application imported successfully")
        except Exception as e:
            results["errors"].append(f"Main app import: {str(e)}")
            self.log_issue("Application", f"Main app import failed: {e}", "high")
        
        # Test routes import
        try:
            from app.routes import router
            results["routes_import"] = True
            print("✅ Routes imported successfully")
        except Exception as e:
            results["errors"].append(f"Routes import: {str(e)}")
            self.log_issue("Application", f"Routes import failed: {e}", "medium")
        
        # Test models import
        try:
            from app.models import ContentResponse
            results["models_import"] = True
            print("✅ Models imported successfully")
        except Exception as e:
            results["errors"].append(f"Models import: {str(e)}")
            self.log_issue("Application", f"Models import failed: {e}", "medium")
        
        return results
    
    def test_core_functionality(self) -> Dict[str, Any]:
        """Test core functionality without starting server"""
        print("\n⚙️ TESTING CORE FUNCTIONALITY...")
        
        results = {
            "database_manager": False,
            "video_generator": False,
            "bucket_storage": False,
            "rl_agent": False,
            "errors": []
        }
        
        # Test database manager
        try:
            from core.database import DatabaseManager
            db = DatabaseManager()
            results["database_manager"] = True
            print("✅ Database manager working")
        except Exception as e:
            results["errors"].append(f"Database manager: {str(e)}")
            self.log_issue("Core", f"Database manager failed: {e}", "high")
        
        # Test video generator
        try:
            from video.generator import create_simple_video
            results["video_generator"] = True
            print("✅ Video generator available")
        except Exception as e:
            results["errors"].append(f"Video generator: {str(e)}")
            self.log_issue("Core", f"Video generator failed: {e}", "medium", 
                          "Install moviepy: pip install moviepy==1.0.3")
        
        # Test bucket storage
        try:
            from core.bhiv_bucket import save_json, get_bucket_path
            test_path = get_bucket_path("logs", "test.json")
            results["bucket_storage"] = True
            print("✅ Bucket storage working")
        except Exception as e:
            results["errors"].append(f"Bucket storage: {str(e)}")
            self.log_issue("Core", f"Bucket storage failed: {e}", "medium")
        
        # Test RL agent
        try:
            from app.agent import RLAgent
            agent = RLAgent()
            results["rl_agent"] = True
            print("✅ RL agent working")
        except Exception as e:
            results["errors"].append(f"RL agent: {str(e)}")
            self.log_issue("Core", f"RL agent failed: {e}", "low")
        
        return results
    
    def check_file_structure(self) -> Dict[str, Any]:
        """Check project file structure"""
        print("\n📁 CHECKING FILE STRUCTURE...")
        
        required_files = [
            "app/main.py",
            "app/routes.py", 
            "app/models.py",
            "app/auth.py",
            "core/database.py",
            "core/models.py",
            "video/generator.py",
            "requirements.txt",
            ".env.example"
        ]
        
        required_dirs = [
            "app",
            "core", 
            "video",
            "bucket",
            "scripts",
            "tests"
        ]
        
        results = {
            "missing_files": [],
            "missing_dirs": [],
            "extra_files": [],
            "structure_score": 0
        }
        
        # Check files
        for file_path in required_files:
            full_path = self.project_root / file_path
            if not full_path.exists():
                results["missing_files"].append(file_path)
                self.log_issue("Structure", f"Missing file: {file_path}", "medium")
        
        # Check directories
        for dir_path in required_dirs:
            full_path = self.project_root / dir_path
            if not full_path.exists():
                results["missing_dirs"].append(dir_path)
                self.log_issue("Structure", f"Missing directory: {dir_path}", "medium")
        
        # Calculate structure score
        total_required = len(required_files) + len(required_dirs)
        missing_count = len(results["missing_files"]) + len(results["missing_dirs"])
        results["structure_score"] = ((total_required - missing_count) / total_required) * 100
        
        print(f"📊 Structure completeness: {results['structure_score']:.1f}%")
        
        return results
    
    def apply_fixes(self) -> Dict[str, Any]:
        """Apply automatic fixes for common issues"""
        print("\n🔧 APPLYING AUTOMATIC FIXES...")
        
        fixes_applied = []
        
        # Create missing directories
        missing_dirs = ["bucket/logs", "bucket/videos", "bucket/scripts", 
                       "bucket/storyboards", "bucket/ratings", "uploads"]
        
        for dir_path in missing_dirs:
            full_path = self.project_root / dir_path
            if not full_path.exists():
                try:
                    full_path.mkdir(parents=True, exist_ok=True)
                    self.log_fix(f"Created directory: {dir_path}")
                    fixes_applied.append(f"Created {dir_path}")
                except Exception as e:
                    self.log_fix(f"Failed to create {dir_path}: {e}", False)
        
        # Fix .env if missing
        env_file = self.project_root / ".env"
        env_example = self.project_root / ".env.example"
        
        if not env_file.exists() and env_example.exists():
            try:
                import shutil
                shutil.copy(env_example, env_file)
                self.log_fix("Created .env from .env.example")
                fixes_applied.append("Created .env file")
            except Exception as e:
                self.log_fix(f"Failed to create .env: {e}", False)
        
        return {"fixes_applied": fixes_applied}
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive analysis report"""
        print("\n📋 GENERATING ANALYSIS REPORT...")
        
        report = {
            "timestamp": time.time(),
            "project_root": str(self.project_root),
            "analysis_summary": {
                "total_issues": len(self.issues),
                "critical_issues": len([i for i in self.issues if i["severity"] == "high"]),
                "medium_issues": len([i for i in self.issues if i["severity"] == "medium"]),
                "low_issues": len([i for i in self.issues if i["severity"] == "low"]),
                "fixes_applied": len(self.fixes_applied)
            },
            "issues": self.issues,
            "fixes_applied": self.fixes_applied,
            "recommendations": []
        }
        
        # Generate recommendations
        if report["analysis_summary"]["critical_issues"] > 0:
            report["recommendations"].append(
                "🚨 Critical issues found - address these before deployment"
            )
        
        if any("moviepy" in str(issue) for issue in self.issues):
            report["recommendations"].append(
                "📹 Install MoviePy for video generation: pip install moviepy==1.0.3"
            )
        
        if any("database" in str(issue).lower() for issue in self.issues):
            report["recommendations"].append(
                "🗄️ Fix database configuration and connectivity issues"
            )
        
        report["recommendations"].append(
            "✅ Run comprehensive tests after fixing issues"
        )
        
        return report

def main():
    """Main analysis function"""
    project_root = os.getcwd()
    print(f"🔍 Starting comprehensive analysis of AI-Agent project")
    print(f"📁 Project root: {project_root}")
    
    analyzer = ProjectAnalyzer(project_root)
    
    # Run all checks
    env_results = analyzer.check_environment()
    deps_results = analyzer.check_dependencies()
    db_results = analyzer.check_database_connection()
    structure_results = analyzer.check_file_structure()
    import_results = analyzer.test_application_import()
    core_results = analyzer.test_core_functionality()
    
    # Apply fixes
    fix_results = analyzer.apply_fixes()
    
    # Generate report
    report = analyzer.generate_report()
    
    # Save report
    report_file = f"analysis_report_{int(time.time())}.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    # Print summary
    print("\n" + "="*60)
    print("📊 ANALYSIS SUMMARY")
    print("="*60)
    
    summary = report["analysis_summary"]
    print(f"Total Issues Found: {summary['total_issues']}")
    print(f"  🚨 Critical: {summary['critical_issues']}")
    print(f"  ⚠️  Medium: {summary['medium_issues']}")
    print(f"  ℹ️  Low: {summary['low_issues']}")
    print(f"Fixes Applied: {summary['fixes_applied']}")
    
    print(f"\n📄 Detailed report saved to: {report_file}")
    
    # Print recommendations
    if report["recommendations"]:
        print("\n💡 RECOMMENDATIONS:")
        for rec in report["recommendations"]:
            print(f"  {rec}")
    
    # Return success if no critical issues
    return summary['critical_issues'] == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)