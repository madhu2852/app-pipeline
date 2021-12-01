import boto3
from boto3.dynamodb.conditions import Key, Attr
from optparse import OptionParser
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def get_configs():
    parser = OptionParser()
    parser.add_option("--fqdn", "--fqdn",dest="fqdn",help="fqdn of the app to remove",default=None)
    parser.add_option("--region", "--region",dest="region",help="dynamodb region",default=None)
    (options, args) = parser.parse_args()
    try:
        options.map = json.loads(options.map)
    except:
        options.map = None
    return options


def get_parameters(region,fqdn):
    try:
        ssm = boto3.client('ssm', region_name=region)
        response = ssm.get_parameters(
            Names=[
                fqdn,
            ],
            WithDecryption=True
        )
        return response['Parameters'][0]['Value']
    except IndexError:
        return None 

def main():

    global options
    options = get_configs()

    try:
        metadata = get_parameters(options.region,options.fqdn)

        return metadata

    except Exception as e:
        message = 'FAILED: Script Failed to Execute {}'.format(e)
        return message

if __name__ == "__main__":
     print(main())
