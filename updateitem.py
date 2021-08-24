
import sys
import boto3

table = boto3.resource('dynamodb',region_name='us-east-1').Table('dev-ports')

#update single record with fqdn & port_state
if str(sys.argv[1]) == "provision":
    response = table.update_item(
        Key={
            'portnum': str(sys.argv[2])
        },
        UpdateExpression="set fqdn = :f, port_state = :s",
        ExpressionAttributeValues={
            ':f': str(sys.argv[3]),
            ':s': 'p'
        },
        ReturnValues="UPDATED_NEW"
    )
    print("Record# "+str(sys.argv[2]) + " added fqdn - " + str(sys.argv[3]))

#print('Number of arguments:', len(sys.argv), 'arguments.')
#print('Argument List:', str(sys.argv[1]))

#clear single record fqdn & port_state
if str(sys.argv[1]) == "clear":
    response = table.update_item(
        Key={
            'portnum': str(sys.argv[2])
        },
        UpdateExpression=("SET port_state = :s REMOVE fqdn"),
        ExpressionAttributeValues={
            ':s': 'a'
        },
        ReturnValues="UPDATED_NEW"
    )
    print("Record# "+str(sys.argv[2]) + " cleared")

#NOT IN USE - Just an example
"""
#Bulk update
for x in range(8000, 8019):
    response = table.update_item(
        Key={
            'portnum': str(x)
        },
        UpdateExpression="set port_state = :s",
        ExpressionAttributeValues={
            ':s': 'a'
        },
        ReturnValues="UPDATED_NEW"
)
print("Record updated")
"""
