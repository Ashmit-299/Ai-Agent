#!/usr/bin/env python3
"""
Fix Swagger UI Loading Issue
"""

def create_custom_swagger_html():
    """Create custom Swagger UI HTML with fallback CDN"""
    
    html = """<!DOCTYPE html>
<html>
<head>
    <title>AI Content Uploader Agent - API Documentation</title>
    <meta charset="UTF-8">
    <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@4.15.5/swagger-ui.css" />
    <style>
        html {
            box-sizing: border-box;
            overflow: -moz-scrollbars-vertical;
            overflow-y: scroll;
        }
        *, *:before, *:after {
            box-sizing: inherit;
        }
        body {
            margin:0;
            background: #fafafa;
        }
        .swagger-ui .topbar {
            background-color: #007bff;
        }
        .swagger-ui .topbar .download-url-wrapper {
            display: none;
        }
    </style>
</head>
<body>
    <div id="swagger-ui"></div>
    <script src="https://unpkg.com/swagger-ui-dist@4.15.5/swagger-ui-bundle.js"></script>
    <script src="https://unpkg.com/swagger-ui-dist@4.15.5/swagger-ui-standalone-preset.js"></script>
    <script>
        window.onload = function() {
            try {
                const ui = SwaggerUIBundle({
                    url: '/openapi.json',
                    dom_id: '#swagger-ui',
                    deepLinking: true,
                    presets: [
                        SwaggerUIBundle.presets.apis,
                        SwaggerUIStandalonePreset
                    ],
                    plugins: [
                        SwaggerUIBundle.plugins.DownloadUrl
                    ],
                    layout: "StandaloneLayout",
                    defaultModelsExpandDepth: -1,
                    docExpansion: "list",
                    filter: true,
                    showExtensions: true,
                    showCommonExtensions: true,
                    tryItOutEnabled: true
                });
                
                // Add custom styling
                setTimeout(function() {
                    const topbar = document.querySelector('.topbar');
                    if (topbar) {
                        topbar.style.display = 'none';
                    }
                }, 1000);
                
            } catch (error) {
                console.error('Swagger UI failed to load:', error);
                document.getElementById('swagger-ui').innerHTML = 
                    '<div style="padding: 20px; text-align: center;">' +
                    '<h2>API Documentation Loading Error</h2>' +
                    '<p>Swagger UI failed to load. You can still access the API specification at:</p>' +
                    '<p><a href="/openapi.json" target="_blank">OpenAPI JSON</a></p>' +
                    '<p><a href="/redoc" target="_blank">ReDoc Alternative</a></p>' +
                    '</div>';
            }
        };
    </script>
</body>
</html>"""
    
    return html

if __name__ == "__main__":
    html = create_custom_swagger_html()
    print("Custom Swagger UI HTML created")
    print(f"Length: {len(html)} characters")
    
    # Save for testing
    with open("custom_swagger.html", "w", encoding="utf-8") as f:
        f.write(html)
    
    print("Saved to custom_swagger.html")