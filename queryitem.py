import boto3
from boto3.dynamodb.conditions import Key, Attr
from optparse import OptionParser
import logging
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def get_configs():
    parser = OptionParser()
    parser.add_option("--env", "--env",dest="env",help="environment to get the available port",default=None)
    parser.add_option("--region", "--region",dest="region",help="dynamodb region",default=None)
    parser.add_option("--table_name", "--table_name",dest="table_name",help="dynamodb table name to query",default=None)
    (options, args) = parser.parse_args()
    try:
        options.map = json.loads(options.map)
    except:
        options.map = None
    return options


def query_ddb_next_avail_port(region,table_name,port):
    try:
        table = boto3.resource('dynamodb',region_name=region).Table(table_name)
    except botocore.exceptions.ClientError as e:
        print(e.response)

    response = table.query(
        IndexName='StateIndex',
        KeyConditionExpression=Key('port_state').eq('a')& Key('portnum').gte(port)
    )
    if 'Items' in response and len(response['Items']) == 1:
        response = response['Items'][0]

    return response['Items'][0].get('portnum')

def main():

    global options
    options = get_configs()

    if options.env == 'DEV':
        port = "8000"
    elif options.env  == "STG":
        port = "12000"
    elif options.env == "PRD":
        port = "12000"
    else:
        message = 'FAILED: Invalid environment input'
        logger.error(message)

    try:
        available_port = query_ddb_next_avail_port(options.region,options.table_name,port)
        return available_port

    except Exception as e:
        message = 'FAILED: Script Failed to Execute {}'.format(e)
        return message


if __name__ == "__main__":
     print(main())
