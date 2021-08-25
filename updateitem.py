import boto3
from boto3.dynamodb.conditions import Key, Attr
from optparse import OptionParser
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def get_configs():
    parser = OptionParser()
    parser.add_option("--env", "--env",dest="env",help="environment to get the available port",default=None)
    parser.add_option("--region", "--region",dest="region",help="dynamodb region",default=None)
    parser.add_option("--table_name", "--table_name",dest="table_name",help="dynamodb table name to query",default=None)
    parser.add_option("--portnum", "--portnum",dest="portnum",help="assigned port number",default=None)
    parser.add_option("--fqdn", "--fqdn",dest="fqdn",help="fqdn of application",default=None)

    (options, args) = parser.parse_args()
    try:
        options.map = json.loads(options.map)
    except:
        options.map = None
    return options


def update_metadata(region,table_name,portnum,fqdn):
    try:
        table = boto3.resource('dynamodb',region_name=region).Table(table_name)
        client = boto3.client('ssm')
    except Exception as e:
        print(e.response)

    update = table.update_item(
        Key={
            'portnum': portnum
        },
        UpdateExpression="set fqdn = :f, port_state = :s",
        ExpressionAttributeValues={
            ':f': fqdn,
            ':s': 'p'
        }
    )
    response = client.put_parameter(
        Name=fqdn,
        Value=portnum,
        Type='String'
    )
    return update,response

def main():

    global options
    options = get_configs()

    try:
        metadata = update_metadata(options.region,options.table_name,options.portnum,options.fqdn)
        message = "Successfully updated metadata to Dynamodb and SSM"
        logger.info(message)
        return metadata

    except Exception as e:
        message = 'FAILED: Script Failed to Execute {}'.format(e)
        return message

if __name__ == "__main__":
     print(main())
