import boto3
from boto3.dynamodb.conditions import Key, Attr
from optparse import OptionParser
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def get_configs():
    parser = OptionParser()
    parser.add_option("--listener_rule_arn", "--listener_rule_arn",dest="listener_rule_arn",help="fqdn of the app to remove",default=None)
    parser.add_option("--target_group_arn", "--target_group_arn",dest="target_group_arn",help="dynamodb region",default=None)
    parser.add_option("--region", "--region",dest="region",help="dynamodb region",default=None)
    parser.add_option("--portnum", "--portnum",dest="portnum",help="assigned port number",default=None)
    parser.add_option("--fqdn", "--fqdn",dest="fqdn",help="fqdn of the application",default=None)
    parser.add_option("--table_name", "--table_name",dest="table_name",help="dynamodb table name to query",default=None)
    parser.add_option("--json_data", "--json_data",dest="json_data",help="json data from ssm param store",default=None)


    (options, args) = parser.parse_args()
    try:
        options.map = json.loads(options.map)
    except:
        options.map = None
    return options

try:
    client = boto3.client('elbv2', region_name='us-east-1')
except Exception as e:
    message = 'FAILED: Unable to establish connection to ELB - {}'.format(e)
    raise Exception(message) 

def delete_aws_resources(listener_rule_arn,target_group_arn):
    delete_lstnr_rule = client.delete_rule(
        RuleArn=str(listener_rule_arn)
    )
    delete_tg_grp = client.delete_target_group(
        TargetGroupArn=str(target_group_arn)
    )
    return delete_lstnr_rule,delete_tg_grp


def update_ddb_ssm(region,table_name,portnum,fqdn,json_data):

    try:
        ddb_table = boto3.resource('dynamodb',region_name=region).Table(table_name)
        ssm_client = boto3.client('ssm',region_name=region)
    except Exception as e:
        raise Exception(e)


    update_ddb = ddb_table.update_item(
        Key={
            'portnum': portnum
        },
        UpdateExpression=("SET port_state = :s REMOVE fqdn"),
        ExpressionAttributeValues={
            ':s': 'a'
        },
    )

    update_ssm = ssm_client.put_parameter(
        Name=fqdn,
        Description='not-in-use',
        Value=json.dumps(json_data),
        Overwrite=True,
        Type='String',
    )
    return update_ddb

def main():

    global options
    options = get_configs()

    try:
        remove_aws = delete_aws_resources(options.listener_rule_arn,options.target_group_arn)
        update_metadata_ddb_ssm = update_ddb_ssm(options.region,options.table_name,options.portnum,options.fqdn,options.json_data)

        return remove_aws,update_metadata_ddb_ssm

    except Exception as e:
        message = 'FAILED: Script Failed to Execute {}'.format(e)
        return message

if __name__ == "__main__":
     print(main())
