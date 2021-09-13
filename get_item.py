import boto3
import os
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError
from optparse import OptionParser
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def get_configs():
    parser = OptionParser()
    parser.add_option("--fqdn", "--fqdn",dest="fqdn",help="fqdn of the app to remove",default=None)
    parser.add_option("--region", "--region",dest="region",help="dynamodb region",default=None)
    parser.add_option("--check", "--check",dest="check",help="check if app fqdn already exists",default=None)

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
                str(fqdn),
            ],
            WithDecryption=True
        )
        return response['Parameters'][0]['Value']
    except Exception as e:
        message = 'FAILED: Script Failed to connect to SSM or Input Parameter Not Found {}'.format(e)
        sys.exit(2)
        return message

## Check APP FQDN already in use. If in use exit.

def fqdn_verify(region,fqdn):
    try:
        ssm = boto3.client('ssm', region_name=region)
        response = ssm.get_parameters(
            Names=[
                str(fqdn),
            ],
            WithDecryption=True
        )
        json_data = response['Parameters'][0]['Value']
        print(json_data)
        fqdn_state = json_data['State']
        if fqdn_state == "in-use":
            message = 'Match Found: FQDN is already in use. Exiting....'
            print(message)
            sys.exit(2)
        return response['Parameters'][0]['Value']
    except ssm.exceptions.ParameterNotFound as e:
        message = 'Success: Parameter Not Found. Available to use. Proceeding.... {}'.format(e)
        print(message)
        sys.exit(0)
    except ssm.exceptions.InvalidKeyId as e:
        message = 'FAILED: Invalid Key ID. Exiting.... {}'.format(e)
        print(message)
        sys.exit(2)
    except ssm.exceptions.InternalServerError as e:
        message = 'FAILED: Internal Server Error. Exiting.... {}'.format(e)
        print(message)
        sys.exit(2)
    except ssm.exceptions.ParameterVersionNotFound as e:
        message = 'FAILED: Parameter Version not found!!!. Exiting.... {}'.format(e)
        print(message)
        sys.exit(2)

def main():

    global options
    options = get_configs()

    try:
        if (options.check):
            fqdn_validate  = fqdn_verify(options.region,options.fqdn)
            return fqdn_validate
        else:
            metadata = get_parameters(options.region,options.fqdn)
            return metadata
    except Exception as e:
        message = 'FAILED: Script Failed to Execute {}'.format(e)
        return message

if __name__ == "__main__":
     print(main())
