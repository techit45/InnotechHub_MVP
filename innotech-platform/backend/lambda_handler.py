import json
import os
from mangum import Mangum
from app.main import app

# Lambda environment variables
os.environ["DATABASE_URL"] = "postgresql://postgres:zextoc-mewmu4-rImraw@innotech-platform-db.cjwsk6a0ob16.ap-southeast-2.rds.amazonaws.com:5432/innotech_platform"

# Create Lambda handler
handler = Mangum(app, lifespan="off")

def lambda_handler(event, context):
    """AWS Lambda handler function"""
    return handler(event, context)