import os
import boto3
from boto3.dynamodb.conditions import Key
from typing import Any, Dict, Optional
from app.core.config import Settings

class DynamoClient:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.table_name = settings.DDB_TABLE
        
        if settings.USE_DYNAMODB_LOCAL and settings.AWS_ENDPOINT_URL:
            print(f"🔧 Conectando ao DynamoDB Local: {settings.AWS_ENDPOINT_URL}")
            
            # Cliente para operações diretas (create table, etc.)
            self.ddb_client = boto3.client(
                "dynamodb",
                region_name=settings.AWS_REGION,
                endpoint_url=settings.AWS_ENDPOINT_URL,
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID or "dummy",
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY or "dummy",
            )
            
            # Resource para operações de alto nível
            self.ddb_resource = boto3.resource(
                "dynamodb",
                region_name=settings.AWS_REGION,
                endpoint_url=settings.AWS_ENDPOINT_URL,
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID or "dummy",
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY or "dummy",
            )
        else:
            print(f"🌐 Conectando ao DynamoDB AWS na região: {settings.AWS_REGION}")
            
            session = (
                boto3.Session(
                    # profile_name=settings.AWS_PROFILE, 
                    region_name=settings.AWS_REGION
                )
                if settings.AWS_PROFILE
                else boto3.Session(region_name=settings.AWS_REGION)
            )
            
            self.ddb_client = session.client("dynamodb")
            self.ddb_resource = session.resource("dynamodb")
        
        self.table = self.ddb_resource.Table(self.table_name)

    def put(self, item: Dict[str, Any]):
        return self.table.put_item(Item=item)

    def get(self, pk: str, sk: str) -> Optional[Dict[str, Any]]:
        resp = self.table.get_item(Key={"PK": pk, "SK": sk})
        return resp.get("Item")

    def query(self, **kwargs):
        return self.table.query(**kwargs)

    def update(self, key, update_expr, vals, names=None, condition=None):
        params = {
            "Key": key,
            "UpdateExpression": update_expr,
            "ExpressionAttributeValues": vals,
        }
        if names:
            params["ExpressionAttributeNames"] = names
        if condition:
            params["ConditionExpression"] = condition
        return self.table.update_item(**params)

    def delete(self, pk: str, sk: str):
        return self.table.delete_item(Key={"PK": pk, "SK": sk})

    def scan(self, **kwargs):
        return self.table.scan(**kwargs)