import boto3
from boto3.dynamodb.conditions import Key, Attr
from optparse import OptionParser
import logging
import json

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def get_configs():
    parser = OptionParser()
    parser.add_option("--env", "--env",dest="env",help="environment to get the available port",default=None)
    parser.add_option("--region", "--region",dest="region",help="dynamodb region",default=None)
    parser.add_option("--table_name", "--table_name",dest="table_name",help="dynamodb table name to query",default=None)
    parser.add_option("--portnum", "--portnum",dest="portnum",help="assigned port number",default=None)
    parser.add_option("--fqdn", "--fqdn",dest="fqdn",help="fqdn of the application",default=None)
    parser.add_option("--lstnr_rule_arn", "--lstnr_rule_arn",dest="lstnr_rule_arn",help="listener rule of the application",default=None)
    parser.add_option("--cert", "--cert",dest="cert",help="cert of the application",default=None)
    parser.add_option("--alb", "--alb",dest="alb",help="alb used for the application",default=None)
    parser.add_option("--target_grp_arn", "--target_grp_arn",dest="target_grp_arn",help="target group of the application",default=None)
    parser.add_option("--listener_arn", "--listener_arn",dest="listener_arn",help="listener arn of the application",default=None)
    parser.add_option("--state", "--state",dest="state",help="state of the application",default=None)


    (options, args) = parser.parse_args()
    try:
        options.map = json.loads(options.map)
    except:
        options.map = None
    return options


def update_metadata(region,table_name,portnum,fqdn,alb,cert,target_grp_arn,env,lstnr_rule_arn,listener_arn,state):
    try:
        table = boto3.resource('dynamodb',region_name=region).Table(table_name)
        client = boto3.client('ssm',region_name=region)
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
        },
        ReturnValues="UPDATED_NEW"
    )
    json_data = {
            "region": region,
            "table_name": table_name,
            "port": portnum,
            "fqdn": fqdn,
            "alb": alb,
            "cert": cert,
            "target_grp_arn": target_grp_arn,
            "environment": env,
            "lstnr_rule_arn": lstnr_rule_arn,
            "listener_arn": listener_arn,
            "state": state,
        }
    response = client.put_parameter(
        Name="/cldnet/"+fqdn,
        Value=json.dumps(json_data),
        Type='String',
        Description='in-use',
        Overwrite=True,
    )
    return update,response

def main():

    global options
    options = get_configs()

    try:
        metadata = update_metadata(
            options.region,
            options.table_name,
            options.portnum,
            options.fqdn,
            options.alb,
            options.cert,
            options.target_grp_arn,
            options.env,
            options.lstnr_rule_arn,
            options.listener_arn,
            options.state,
            )
        message = "Successfully updated metadata to Dynamodb and SSM"
        logger.info(message)
        return metadata

    except Exception as e:
        message = 'FAILED: Script Failed to Execute {}'.format(e)
        return message

if __name__ == "__main__":
     print(main())
