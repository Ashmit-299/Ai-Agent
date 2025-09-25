#!/usr/bin/env python3
"""Fix Swagger UI authorization button"""

import json

# Read the current OpenAPI schema and add security
def fix_openapi_security():
    """Add security scheme to OpenAPI configuration"""
    
    # This will be added to the main.py file
    security_config = '''
# Add security configuration after app creation
from fastapi.security import HTTPBearer

# Create security scheme
security = HTTPBearer()

# Override OpenAPI schema to include security
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    from fastapi.openapi.utils import get_openapi
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    
    # Add security scheme
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Enter: Bearer <your-token-here>"
        }
    }
    
    # Add global security requirement
    openapi_schema["security"] = [{"BearerAuth": []}]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
'''
    
    print("Security configuration to add to main.py:")
    print(security_config)
    
    # Also create a simple test endpoint
    test_endpoint = '''
@app.get("/test-auth")
async def test_auth(token: str = Depends(security)):
    """Test endpoint to verify JWT token"""
    return {"message": "Token received", "token_preview": token[:20] + "..."}
'''
    
    print("\nOptional test endpoint:")
    print(test_endpoint)

if __name__ == "__main__":
    fix_openapi_security()