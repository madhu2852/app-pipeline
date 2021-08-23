import boto3
from boto3.dynamodb.conditions import Key, Attr
import json

table = boto3.resource('dynamodb').Table('dev-ports')

#queries dynamodb table looking for port_state equal to 'a' or available and returns next available port that can be assigned
response = table.query(
    IndexName='StateIndex',
    KeyConditionExpression=Key('port_state').eq('a')& Key('portnum').gte('8000')
)

if 'Items' in response and len(response['Items']) == 1:
    response = json.loads(response['Items'][0])

print(response['Items'][0])
