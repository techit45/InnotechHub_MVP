import json
import os
import logging

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    """Simplified Lambda handler for testing connectivity"""
    
    try:
        logger.info(f"Event: {json.dumps(event)}")
        
        # Get request info
        http_method = event.get('httpMethod', 'GET')
        path = event.get('path', '/')
        
        logger.info(f"Request: {http_method} {path}")
        
        # Handle CORS preflight
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
        
        # Handle health check and root paths  
        if path in ['/', '/health', '/prod', '/prod/', '/prod/health', '', '/root']:
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
                    'version': '1.0.0',
                    'path': path,
                    'method': http_method,
                    'timestamp': context.aws_request_id,
                    'endpoints': {
                        'health': '/health',
                        'auth': '/api/auth',
                        'users': '/api/users', 
                        'courses': '/api/courses'
                    }
                })
            }
        
        # Handle API routes
        if path.startswith('/api/') or path.startswith('/prod/api/'):
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'message': f'API endpoint {path}',
                    'method': http_method,
                    'status': 'endpoint available',
                    'note': 'Database integration coming soon'
                })
            }
        
        # Default 404 for unhandled paths
        return {
            'statusCode': 404,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Not Found',
                'path': path,
                'method': http_method,
                'message': 'Endpoint not found',
                'available_endpoints': ['/health', '/api/*']
            })
        }
        
    except Exception as e:
        logger.error(f"Lambda error: {e}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Internal Server Error',
                'message': str(e),
                'path': path if 'path' in locals() else 'unknown'
            })
        }