import boto3
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key, Attr
from optparse import OptionParser
import logging
import json
import sys

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def get_configs():
    usage = "usage: %prog [options] arg"
    parser = OptionParser(usage)
    parser.add_option("--env", "--env",dest="env",help="environment to get the available port")
    parser.add_option("--lstnr_rule_arn", "--lstnr_rule_arn",dest="lstnr_rule_arn",help="fqdn of the app to remove")
    parser.add_option("--target_grp_arn", "--target_grp_arn",dest="target_grp_arn",help="dynamodb region")
    parser.add_option("--region", "--region",dest="region",help="dynamodb region")
    parser.add_option("--portnum", "--portnum",dest="portnum",help="assigned port number")
    parser.add_option("--fqdn", "--fqdn",dest="fqdn",help="fqdn of the application")
    parser.add_option("--table_name", "--table_name",dest="table_name",help="dynamodb table name to query")
    parser.add_option("--cert", "--cert",dest="cert",help="app cert arn")
    parser.add_option("--alb", "--alb",dest="alb",help="alb used for the application")
    parser.add_option("--listener_arn", "--listener_arn",dest="listener_arn",help="listener arn")
    parser.add_option("--state", "--state",dest="state",help="state of the application")
    (options, args) = parser.parse_args()

    return options


def delete_aws_resources(
    lstnr_rule_arn,
    target_grp_arn,
    listener_arn,
    cert,
    region):

    try:
        client = boto3.client('elbv2', region_name=region)

        delete_lstnr_rule = client.delete_rule(
            RuleArn=str(lstnr_rule_arn)
        )
        delete_tg_grp = client.delete_target_group(
            TargetGroupArn=str(target_grp_arn)
        )

        # remove_lstnr_cert = client.remove_listener_certificates(
        #     ListenerArn=str(listener_arn),
        #     Certificates=[
        #         {
        #             'CertificateArn': str(cert),
        #         },
        #     ]
        # )
        return delete_lstnr_rule,delete_tg_grp #,remove_lstnr_cert

    except ClientError as e:
        message = 'Reason - {}'.format(e)
        raise ClientError(message)


def update_ddb_ssm(
    region,
    table_name,
    portnum,
    fqdn,
    alb,
    cert,
    target_grp_arn,
    env,
    lstnr_rule_arn,
    listener_arn,
    state): 

    try:
        ddb_table = boto3.resource('dynamodb',region_name=region).Table(table_name)
        ssm_client = boto3.client('ssm',region_name=region)

        update_ddb = ddb_table.update_item(
            Key={
                'portnum': portnum
            },
            UpdateExpression=("SET port_state = :s REMOVE fqdn"),
            ExpressionAttributeValues={
                ':s': 'a'
            },
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

        update_ssm = ssm_client.put_parameter(
            Name=fqdn,
            Description='not-in-use',
            Value=json.dumps(json_data),
            Overwrite=True,
            Type='String',
        )

        return update_ddb,update_ssm

    except ClientError as e:
        message = 'Reason - {}'.format(e)
        raise ClientError(message)

def main():
    options = get_configs()
    option_dict = vars(options)
    if ('') in option_dict.values():
        message = "Empty Values Found. Nothing to delete here. Skipping... {}".format(option_dict.values())
        print(message)
        sys.exit(0)
    else:
        try:
            remove_aws = delete_aws_resources(
                options.lstnr_rule_arn,
                options.target_grp_arn,
                options.listener_arn,
                options.cert,
                options.region,
                )
            update_metadata_ddb_ssm = update_ddb_ssm(
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

            print(remove_aws,update_metadata_ddb_ssm)

        except Exception as e:
            message = 'FAILED: Script Failed to Execute {}'.format(e)
            raise Exception(message)

if __name__ == "__main__":
     main()
