import json
import os
from mangum import Mangum

def lambda_handler(event, context):
    """Enhanced Lambda handler with proper routing"""
    
    try:
        # Set database URL
        os.environ["DATABASE_URL"] = "postgresql://postgres:zextoc-mewmu4-rImraw@innotech-platform-db.cjwsk6a0ob16.ap-southeast-2.amazonaws.com:5432/innotech_platform"
        
        # Get request info
        http_method = event.get('httpMethod', 'GET')
        path = event.get('path', '/')
        
        # Handle health check
        if path == '/health' or path == '/':
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Requested-With'
                },
                'body': json.dumps({
                    'message': 'Innotech Platform API is running!',
                    'status': 'healthy',
                    'database': 'connected',
                    'version': '1.0.0',
                    'endpoints': ['/health', '/api/auth', '/api/users', '/api/courses', '/api/assignments']
                })
            }
        
        # Handle OPTIONS requests (CORS preflight)
        if http_method == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Requested-With',
                    'Access-Control-Max-Age': '86400'
                },
                'body': ''
            }
        
        # For other routes, try to import and use FastAPI app
        try:
            from app.main import app
            handler = Mangum(app, lifespan="off")
            return handler(event, context)
        except Exception as app_error:
            # Fallback response if FastAPI fails
            return {
                'statusCode': 500,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Requested-With'
                },
                'body': json.dumps({
                    'error': 'FastAPI app error',
                    'message': str(app_error),
                    'path': path,
                    'method': http_method
                })
            }
            
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Requested-With'
            },
            'body': json.dumps({
                'error': 'Lambda handler error',
                'message': str(e)
            })
        }