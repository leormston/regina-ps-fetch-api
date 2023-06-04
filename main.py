import json
import boto3
from boto3.dynamodb.conditions import Key

def get_all_blogs():
    dynamodb = boto3.resource('dynamodb',region_name='eu-west-1')
    
    table = dynamodb.Table('regina-ps-blog')
    try:
        response = table.scan()
        data = response['Items']
    
        while 'LastEvaluatedKey' in response:
            response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            data.extend(response['Items'])
        return data
    except Exception as e:
        return str(e)
        
def get_blog_by_id(id):
    dynamodb = boto3.resource('dynamodb',region_name='eu-west-1')
    
    table = dynamodb.Table('regina-ps-blog')
    
    response = table.query(
    KeyConditionExpression=Key('blogId').eq(id))
    
    return response.get("Items", None)

def get_all_credits():
    dynamodb = boto3.resource('dynamodb',region_name='eu-west-1')
    
    table = dynamodb.Table('regina-ps-credits')
    try:
        response = table.scan()
        data = response['Items']
    
        while 'LastEvaluatedKey' in response:
            response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            data.extend(response['Items'])
        return data
    except Exception as e:
        return str(e)

def auth(username, password):
    dynamodb = boto3.resource('dynamodb',region_name='eu-west-1')
    
    table = dynamodb.Table('regina-ps-users')
    
    response = table.query(
    KeyConditionExpression=Key('username').eq(username))
    
    if len(response.get("Items", None)) == 1:
        if password ==  response.get("Items", None)[0]["password"]:
            return True
    return False

def lambda_handler(event, context):
    try:
        headers = {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
            'Access-Control-Allow-Headers': '*',
            'Access-Control-Allow-Credentials': True,
            'mode': 'cors'
            
        }
        print(event)
        path = event['path'].split("/")
        print(path)
        basePath = path[1]
        print(f"base path: {basePath}")

            # data = json.loads(str(event['body']))
        if len(path) == 2:
            if basePath == "blogs":
                data = get_all_blogs()
            if basePath == "credits":
                data = get_all_credits()
            
            if basePath == "auth":
                if event['body'] != None:
                    username = json.loads(event['body'])['a']
                    password = json.loads(event['body'])['b']
                    authorized = auth(username, password)
                    if not authorized:
                        return {
                        'statusCode': 404,
                        'headers': headers,
                        'body': json.dumps("Login Details Incorrect")
                            }
                    data = authorized
                else:
                    data = ""
                
        elif len(path) == 3:
            secondPath = path[2]
            if basePath == "blogs":
                data = get_blog_by_id(secondPath)
        else:
            data = "Incorrect API Path"
            
        return {
        'statusCode': 200,
        'headers': headers,
        'body': json.dumps(data)
            }

    except Exception as e:
        print(e)
        return {
        'statusCode': 500,
        'body': json.dumps(str(e))
            }
        


