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

def delete_aws_resources_listener_rule(listener_rule_arn):
    response = client.delete_rule(
        RuleArn=str(listener_rule_arn)
    )
    return response


def delete_aws_resources_target_group(target_group_arn):
    response = client.delete_target_group(
        TargetGroupArn=str(target_group_arn)
    )
    return response

def main():

    global options
    options = get_configs()

    try:
        if (options.target_group_arn):
            remove = delete_aws_resources_target_group(options.target_group_arn)
            message = remove
        if  (options.listener_rule_arn):
            remove = delete_aws_resources_listener_rule(options.listener_rule_arn)
            message = remove

        return message

    except Exception as e:
        message = 'FAILED: Script Failed to Execute {}'.format(e)
        return message

if __name__ == "__main__":
     print(main())
