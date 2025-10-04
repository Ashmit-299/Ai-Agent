#!/usr/bin/env python3
"""
Debug server startup to identify routing conflicts
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

def debug_imports():
    """Debug import issues"""
    print("=== Debugging Imports ===")
    
    try:
        from app.main import app
        print("✅ Successfully imported main app")
        
        # Check routes
        route_count = len(app.routes)
        print(f"✅ Total routes loaded: {route_count}")
        
        # Find upload routes
        upload_routes = []
        for route in app.routes:
            if hasattr(route, 'path') and 'upload' in route.path.lower():
                methods = list(route.methods) if hasattr(route, 'methods') and route.methods else ['GET']
                upload_routes.append(f"{methods} {route.path}")
        
        print(f"✅ Upload routes found: {len(upload_routes)}")
        for route in upload_routes:
            print(f"   - {route}")
            
        return app
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        import traceback
        traceback.print_exc()
        return None

def debug_routers():
    """Debug individual routers"""
    print("\n=== Debugging Individual Routers ===")
    
    try:
        from app.routes import router, step3_router
        print(f"✅ Main router routes: {len(router.routes)}")
        print(f"✅ Step3 router routes: {len(step3_router.routes)}")
        
        from app.cdn_fixed import router as cdn_router
        print(f"✅ CDN router routes: {len(cdn_router.routes)}")
        
        # Check for conflicts
        all_paths = []
        for route in router.routes:
            if hasattr(route, 'path'):
                all_paths.append(('main', route.path))
        
        for route in step3_router.routes:
            if hasattr(route, 'path'):
                all_paths.append(('step3', route.path))
                
        for route in cdn_router.routes:
            if hasattr(route, 'path'):
                all_paths.append(('cdn', route.path))
        
        # Find duplicates
        path_counts = {}
        for source, path in all_paths:
            if path in path_counts:
                path_counts[path].append(source)
            else:
                path_counts[path] = [source]
        
        conflicts = {path: sources for path, sources in path_counts.items() if len(sources) > 1}
        
        if conflicts:
            print(f"⚠️  Route conflicts found: {len(conflicts)}")
            for path, sources in conflicts.items():
                print(f"   - {path}: {sources}")
        else:
            print("✅ No route conflicts detected")
            
    except Exception as e:
        print(f"❌ Router debug error: {e}")
        import traceback
        traceback.print_exc()

def debug_dependencies():
    """Debug key dependencies"""
    print("\n=== Debugging Dependencies ===")
    
    dependencies = [
        ('fastapi', 'FastAPI'),
        ('uvicorn', 'uvicorn'),
        ('sqlmodel', 'SQLModel'),
        ('psycopg2', 'psycopg2'),
        ('core.database', 'DatabaseManager'),
        ('app.auth', 'get_current_user_required'),
        ('app.observability', 'track_performance')
    ]
    
    for module, item in dependencies:
        try:
            if '.' in module:
                exec(f"from {module} import {item}")
            else:
                exec(f"import {module}")
            print(f"✅ {module}.{item}")
        except ImportError as e:
            print(f"❌ {module}.{item}: {e}")
        except Exception as e:
            print(f"⚠️  {module}.{item}: {e}")

def main():
    """Main debug function"""
    print("🔍 Starting server startup debugging...")
    
    # Debug dependencies first
    debug_dependencies()
    
    # Debug routers
    debug_routers()
    
    # Debug main app
    app = debug_imports()
    
    if app:
        print("\n✅ Server debugging completed successfully")
        print("🚀 You can now start the server with: python scripts/start_server.py")
    else:
        print("\n❌ Server debugging failed")
        print("🔧 Check the errors above and fix import issues")

if __name__ == "__main__":
    main()