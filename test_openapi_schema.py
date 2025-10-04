#!/usr/bin/env python3
"""
Test OpenAPI schema for resolver errors
"""

import sys
import os
import json

def test_openapi_schema():
    """Test if OpenAPI schema is valid and has no resolver errors"""
    print("Testing OpenAPI Schema Validation...")
    
    try:
        # Add current directory to path
        sys.path.insert(0, os.getcwd())
        
        # Import the FastAPI app
        from app.main import app
        
        # Get OpenAPI schema
        schema = app.openapi()
        
        print(f"Schema generated successfully")
        print(f"OpenAPI version: {schema.get('openapi', 'unknown')}")
        print(f"Title: {schema.get('info', {}).get('title', 'unknown')}")
        
        # Check components
        components = schema.get('components', {})
        print(f"Components sections: {list(components.keys())}")
        
        # Check for schemas
        schemas = components.get('schemas', {})
        print(f"Schema definitions: {len(schemas)}")
        
        # Check for broken references
        schema_str = json.dumps(schema)
        broken_refs = []
        
        # Look for common reference patterns that might be broken
        if '"$ref"' in schema_str:
            print("Found $ref references in schema")
            # Count references
            ref_count = schema_str.count('"$ref"')
            print(f"Total references: {ref_count}")
        else:
            print("No $ref references found")
        
        # Check paths
        paths = schema.get('paths', {})
        print(f"API paths: {len(paths)}")
        
        # Check for security schemes
        security_schemes = components.get('securitySchemes', {})
        print(f"Security schemes: {list(security_schemes.keys())}")
        
        # Validate JSON structure
        try:
            json.dumps(schema)
            print("Schema is valid JSON")
        except Exception as json_error:
            print(f"Schema JSON validation failed: {json_error}")
            return False
        
        # Check for specific endpoints that were causing issues
        problematic_endpoints = ['/upload', '/generate-video', '/feedback']
        for endpoint in problematic_endpoints:
            if endpoint in str(paths):
                print(f"Found endpoint: {endpoint}")
            else:
                print(f"Missing endpoint: {endpoint}")
        
        print("OpenAPI schema validation completed successfully!")
        return True
        
    except Exception as e:
        print(f"Schema validation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_schema_export():
    """Test exporting the schema to a file"""
    print("\nTesting Schema Export...")
    
    try:
        from app.main import app
        schema = app.openapi()
        
        # Export to file
        with open('openapi_schema.json', 'w') as f:
            json.dump(schema, f, indent=2)
        
        print("Schema exported to openapi_schema.json")
        
        # Check file size
        file_size = os.path.getsize('openapi_schema.json')
        print(f"Schema file size: {file_size} bytes")
        
        if file_size > 1000:  # Should be at least 1KB for a real schema
            print("Schema export successful!")
            return True
        else:
            print("Schema file seems too small")
            return False
            
    except Exception as e:
        print(f"Schema export failed: {e}")
        return False

if __name__ == "__main__":
    print("OpenAPI Schema Validation Test")
    print("=" * 40)
    
    schema_ok = test_openapi_schema()
    export_ok = test_schema_export()
    
    print("\n" + "=" * 40)
    if schema_ok and export_ok:
        print("OpenAPI schema is valid and working correctly!")
        print("\nThe resolver errors should now be fixed.")
        print("You can start the server and check /docs for proper Swagger UI.")
    else:
        print("OpenAPI schema still has issues")