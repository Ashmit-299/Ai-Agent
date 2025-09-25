#!/usr/bin/env python3
"""
Project Organization Script
Reorganizes files according to systematic directory structure
"""

import os
import shutil
from pathlib import Path

def create_directories():
    """Create organized directory structure"""
    dirs = [
        'docs/reports',
        'docs/deployment', 
        'scripts/maintenance',
        'scripts/deployment',
        'scripts/migration',
        'tests/integration',
        'tests/unit',
        'tests/fixtures',
        'data/reports'
    ]
    
    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"Created directory: {dir_path}")

def move_files():
    """Move files to organized locations"""
    
    # Documentation files to docs/reports/
    doc_files = [
        'BUCKET_SAVE_FIX_SUMMARY.md',
        'DEPLOYMENT_GUIDE.md', 
        'INTEGRATION_SUCCESS_REPORT.md',
        'OBSERVABILITY_SUMMARY.md',
        'OBSERVABILITY_VERIFICATION_REPORT.md',
        'ONBOARDING_GUIDE.md',
        'START_SERVER.md',
        'SUPABASE_CONNECTION_FIXED.md',
        'TEST_SUMMARY.md',
        'UNIT_TESTS_SUMMARY.md'
    ]
    
    for file in doc_files:
        if os.path.exists(file):
            shutil.move(file, f'docs/reports/{file}')
            print(f"Moved {file} -> docs/reports/")
    
    # Deployment docs
    deploy_docs = ['render_deploy.md']
    for file in deploy_docs:
        if os.path.exists(file):
            shutil.move(file, f'docs/deployment/{file}')
            print(f"Moved {file} -> docs/deployment/")
    
    # General docs
    general_docs = ['endpoint_security_guide.md', 'testing_instructions.md']
    for file in general_docs:
        if os.path.exists(file):
            shutil.move(file, f'docs/{file}')
            print(f"Moved {file} -> docs/")
    
    # Maintenance scripts
    maintenance_files = [
        'check_connection_status.py', 'debug_demo_auth.py', 'debug_metrics.py',
        'debug_registration.py', 'debug_test.txt', 'debug_video.py',
        'fix_bcrypt.py', 'fix_data_saving.py', 'fix_demo_password.py',
        'fix_demo_simple.py', 'fix_demo_user.py', 'fix_metrics.py',
        'fix_moviepy.py', 'fix_postgres_schema.py', 'fix_server.py',
        'fix_supabase_schema.py', 'fix_supabase_tables.py', 'fix_swagger_auth.py',
        'fix_user_schema.py', 'posthog_integration.py', 'quick_metrics_fix.py',
        'suppress_bcrypt_warning.py', 'verify_all_endpoints.py',
        'verify_integrations.py', 'verify_metrics_fix.py', 'verify_supabase_connection.py',
        'verify_supabase_save.py', 'video_generation_fix.py', 'final_test.py',
        'simple_test.py', 'wait_and_test.py', 'create_demo_in_supabase.py'
    ]
    
    for file in maintenance_files:
        if os.path.exists(file):
            shutil.move(file, f'scripts/maintenance/{file}')
            print(f"Moved {file} -> scripts/maintenance/")
    
    # Deployment scripts
    deployment_files = [
        'build.sh', 'complete_execution_checklist.py', 'deploy.py',
        'deploy_to_render.py', 'force_deployment.py'
    ]
    
    for file in deployment_files:
        if os.path.exists(file):
            shutil.move(file, f'scripts/deployment/{file}')
            print(f"Moved {file} -> scripts/deployment/")
    
    # Migration scripts
    migration_files = [
        'migrate_bucket_to_supabase.py', 'run_migrations.py',
        'run_migrations_simple.py', 'simple_migrate.py'
    ]
    
    for file in migration_files:
        if os.path.exists(file):
            shutil.move(file, f'scripts/migration/{file}')
            print(f"Moved {file} -> scripts/migration/")
    
    # General scripts
    script_files = [
        'install_imagemagick.py', 'install_psycopg2.py', 'run_all_tests.py',
        'run_basic_tests.py', 'run_enhanced_tests.py', 'run_server.py',
        'run_tests.py', 'run_with_setup.py', 'setup_posthog.py',
        'setup_project.py', 'start.bat', 'start_dashboard.py',
        'start_server.py', 'upload_to_git.bat'
    ]
    
    for file in script_files:
        if os.path.exists(file):
            shutil.move(file, f'scripts/{file}')
            print(f"Moved {file} -> scripts/")
    
    # Test files
    test_integration = [
        'test_auth_flow.py', 'test_demo_login.py', 'test_jwt_debug.py',
        'test_registration.py', 'test_supabase.py', 'test_supabase_live.py'
    ]
    
    for file in test_integration:
        if os.path.exists(file):
            shutil.move(file, f'tests/integration/{file}')
            print(f"Moved {file} -> tests/integration/")
    
    test_unit = [
        'test_bucket_save.py', 'test_ci_simple.py', 'test_ci_simulation.py',
        'test_content_retrieval.py', 'test_dashboard.py', 'test_dashboard_connection.py',
        'test_database.py', 'test_db_connection.py', 'test_db_direct.py',
        'test_debug_endpoint.py', 'test_env_loading.py', 'test_fixes.py',
        'test_metrics_endpoint.py', 'test_new_split.py', 'test_observability.py',
        'test_posthog_events.py', 'test_script_save.py', 'test_sentences.py',
        'test_server.py', 'test_server_observability.py', 'test_simple.py',
        'test_specific_content.py', 'test_streamlit_fix.py', 'test_with_server.py'
    ]
    
    for file in test_unit:
        if os.path.exists(file):
            shutil.move(file, f'tests/unit/{file}')
            print(f"Moved {file} -> tests/unit/")
    
    # Test fixtures
    test_fixtures = ['test_output.txt', 'test_user_credentials.json']
    for file in test_fixtures:
        if os.path.exists(file):
            shutil.move(file, f'tests/fixtures/{file}')
            print(f"Moved {file} -> tests/fixtures/")
    
    # Data files
    data_files = [
        'data.db-shm', 'data.db-wal', 'deployment_report_local.json',
        'execution_validation_report.json', 'health-check-1758783224.json',
        'health-check-1758783254.json', 'supabase_live_test_report.json'
    ]
    
    for file in data_files:
        if os.path.exists(file):
            if file.endswith('.json'):
                shutil.move(file, f'data/reports/{file}')
                print(f"Moved {file} -> data/reports/")
            else:
                Path('data').mkdir(exist_ok=True)
                shutil.move(file, f'data/{file}')
                print(f"Moved {file} -> data/")
    
    # Dashboard files to app/
    dashboard_files = ['streamlit_dashboard.py', 'streamlit_dashboard_fixed.py']
    for file in dashboard_files:
        if os.path.exists(file):
            shutil.move(file, f'app/{file}')
            print(f"Moved {file} -> app/")

def update_imports():
    """Update import statements in moved files"""
    print("\nUpdating import statements...")
    
    # Update scripts to reference correct paths
    script_dirs = ['scripts', 'scripts/maintenance', 'scripts/deployment', 'scripts/migration']
    
    for script_dir in script_dirs:
        if os.path.exists(script_dir):
            for file in os.listdir(script_dir):
                if file.endswith('.py'):
                    file_path = os.path.join(script_dir, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # Update common import paths
                        content = content.replace('from app.', 'from ..app.')
                        content = content.replace('from core.', 'from ..core.')
                        content = content.replace('from video.', 'from ..video.')
                        
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(content)
                        
                        print(f"Updated imports in {file_path}")
                    except Exception as e:
                        print(f"Warning: Could not update {file_path}: {e}")

def create_init_files():
    """Create __init__.py files for Python packages"""
    init_dirs = [
        'scripts', 'scripts/maintenance', 'scripts/deployment', 
        'scripts/migration', 'data', 'docs'
    ]
    
    for dir_path in init_dirs:
        if os.path.exists(dir_path):
            init_file = os.path.join(dir_path, '__init__.py')
            if not os.path.exists(init_file):
                with open(init_file, 'w') as f:
                    f.write('"""Package initialization"""')
                print(f"Created {init_file}")

def main():
    """Main organization function"""
    print("Starting project organization...")
    print("=" * 50)
    
    # Change to project directory
    os.chdir(Path(__file__).parent)
    
    # Create directory structure
    print("\nCreating directory structure...")
    create_directories()
    
    # Move files
    print("\nMoving files to organized locations...")
    move_files()
    
    # Update imports
    update_imports()
    
    # Create init files
    print("\nCreating package initialization files...")
    create_init_files()
    
    print("\n" + "=" * 50)
    print("Project organization complete!")
    print("\nNew structure:")
    print("├── docs/           # Documentation")
    print("├── scripts/        # Utility scripts")
    print("├── tests/          # Test suite")
    print("├── data/           # Data files")
    print("├── app/            # FastAPI application")
    print("├── core/           # Core business logic")
    print("├── video/          # Video generation")
    print("└── migrations/     # Database migrations")

if __name__ == "__main__":
    main()