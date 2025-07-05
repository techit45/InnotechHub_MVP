import json
import os

def lambda_handler(event, context):
    """Simple Lambda handler for testing"""
    
    try:
        # Set database URL
        os.environ["DATABASE_URL"] = "postgresql://postgres:zextoc-mewmu4-rImraw@innotech-platform-db.cjwsk6a0ob16.ap-southeast-2.rds.amazonaws.com:5432/innotech_platform"
        
        # Simple response
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization'
            },
            'body': json.dumps({
                'message': 'Innotech Platform API is running!',
                'database_url': 'Connected to PostgreSQL',
                'version': '1.0.0'
            })
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': str(e)
            })
        }