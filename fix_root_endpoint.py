#!/usr/bin/env python3
"""
Fix Root Endpoint HTML Display Issue
"""

def create_clean_html():
    """Create clean HTML without Unicode characters"""
    
    html_content = """<!DOCTYPE html>
<html>
<head>
    <title>AI Content Uploader Agent</title>
    <meta charset="UTF-8">
    <style>
        body { 
            font-family: Arial, sans-serif; 
            margin: 40px; 
            background: #f5f5f5; 
        }
        .container { 
            max-width: 800px; 
            margin: 0 auto; 
            background: white; 
            padding: 30px; 
            border-radius: 8px; 
            box-shadow: 0 2px 10px rgba(0,0,0,0.1); 
        }
        h1 { 
            color: #333; 
            text-align: center;
        }
        .links { 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
            gap: 15px; 
            margin: 20px 0; 
        }
        .link-card { 
            background: #007bff; 
            color: white; 
            padding: 15px; 
            border-radius: 5px; 
            text-decoration: none; 
            text-align: center; 
            display: block;
        }
        .link-card:hover { 
            background: #0056b3; 
        }
        .status { 
            background: #28a745; 
            color: white; 
            padding: 10px; 
            border-radius: 5px; 
            text-align: center; 
            margin: 20px 0; 
        }
        .quick-start {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 5px;
            margin: 20px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>AI Content Uploader Agent</h1>
        <div class="status">Server Running Successfully</div>
        <p>Welcome to the AI-powered content analysis and video generation platform.</p>
        
        <div class="links">
            <a href="/docs" class="link-card">API Documentation</a>
            <a href="/health" class="link-card">Health Check</a>
            <a href="/dashboard" class="link-card">Dashboard</a>
            <a href="/demo-login" class="link-card">Demo Login</a>
        </div>
        
        <div class="quick-start">
            <h3>Quick Start:</h3>
            <ol>
                <li>Get demo credentials from <a href="/demo-login">/demo-login</a></li>
                <li>Visit <a href="/docs">/docs</a> for interactive API testing</li>
                <li>Use POST /users/login to authenticate</li>
                <li>Upload content with POST /upload</li>
            </ol>
        </div>
        
        <div class="quick-start">
            <h3>Server Status:</h3>
            <ul>
                <li>Database: Connected (Supabase)</li>
                <li>Storage: Supabase (1GB free)</li>
                <li>Authentication: JWT enabled</li>
                <li>API Endpoints: 58 routes loaded</li>
            </ul>
        </div>
    </div>
</body>
</html>"""
    
    return html_content

if __name__ == "__main__":
    html = create_clean_html()
    print("Clean HTML created successfully")
    print(f"HTML length: {len(html)} characters")
    
    # Save to file for testing
    with open("test_root.html", "w", encoding="utf-8") as f:
        f.write(html)
    
    print("HTML saved to test_root.html for testing")