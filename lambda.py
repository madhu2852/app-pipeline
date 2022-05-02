import boto3
import logging
import time
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

try:

    autoscaling = boto3.client('autoscaling')
    ec2 = boto3.client('ec2')

except ClientError as e:

    message = 'ERROR CONNECTING TO CLIENT: {}'.format(e)
    logger.error(message)

    raise Exception(message)

def send_lifecycle_action(event, result):

    try:

        response = autoscaling.complete_lifecycle_action(
            LifecycleHookName=event['detail']['LifecycleHookName'],
            AutoScalingGroupName=event['detail']['AutoScalingGroupName'],
            LifecycleActionToken=event['detail']['LifecycleActionToken'],
            LifecycleActionResult=result,
            InstanceId=event['detail']['EC2InstanceId']
        )

        logger.info(response)

        return "SUCCESS"

    except ClientError as e:

        message = 'ERROR SENDING LIFECYCLE ACTION EVENT TO ASG. MESSAGE:- {}'.format(e)
    
        logger.error(message)
        raise Exception(message)

def sanity_check():
    time.sleep(60)
    return 'OK'

def remove_interfaces(event):
    logger.info('REMOVE NETWORK INTERFACES ON EC2: {}'.format(event['detail']['EC2InstanceId']))
    # GET EC2 ID FROM EVENT
    instance_id = event['detail']['EC2InstanceId']
    try:
        eni_ids = []
        eni_attach_ids = []
    # GET NETWORK INTERFACES DETAILS FROM EC2    
        response = ec2.describe_instances(
            InstanceIds=[
                str(instance_id)
            ],
        )
        raw_data = response['Reservations'][0]['Instances'][0]['NetworkInterfaces']
        
        for eni in raw_data:
            if eni['Attachment']['DeviceIndex'] != 0:
                eni_ids.append(eni['NetworkInterfaceId'])
                eni_attach_ids.append(eni['Attachment']['AttachmentId'])

    # DETACH NETWORK INTERFACES FROM EC2 BEFORE DELETING

        for eni_to_detach in eni_attach_ids:
            logger.info('DETACHING ENI: {} BEFORE DELETE.'.format(eni_to_detach))
            detach_enis = ec2.detach_network_interface(
                AttachmentId=str(eni_to_detach),
                Force=True
            )
            logger.info('ENI: {} DETACHED SUCCESSFULLY.'.format(eni_to_detach))

    # REMOVE NETWORK INTERFACES 

        for eni_to_delete in eni_ids:
            waiter = ec2.get_waiter('network_interface_available')
            wait = waiter.wait(NetworkInterfaceIds=[str(eni_to_delete)])
            logger.info('REMOVING ENI: {}'.format(eni_to_delete))       
            remove_eni = ec2.delete_network_interface(
                NetworkInterfaceId=str(eni_to_delete),
            )
            logger.info('SUCCESSFULLY REMOVED ENI {}; STATUS: {}'.format(eni_to_delete,remove_eni))    
        return

    except Exception as e:
        message = 'FAILED TO DETACH/REMOVE NETWORK INTERFACES. MESSAGE: {}'.format(e)
        logger.error(message)
        raise Exception(message)

def run_command(event):

    # verify eni before create

    eni = []

    # GET EC2 ID FROM EVENT
   
    logger.info('CREATE NETWORK INTERFACE FOR EC2: {}'.format(event['detail']['EC2InstanceId']))

    instance_id = event['detail']['EC2InstanceId']
    
    # Check if EC2 already has Network Interaces attached in correct locations

    try:

    # GET EC2 AVAILABILITY ZONE ID and NETWORK INTERFACE INFO

        get_ec2_data = ec2.describe_instances(
            Filters=[
                    {
                        'Name': 'instance-state-name',
                        'Values': [
                            'running',
                        ]
                    },
                ],
            InstanceIds=[
                    instance_id,
                ],)

        ec2_interfaces = get_ec2_data['Reservations'][0]['Instances'][0]['NetworkInterfaces']

        for interface in ec2_interfaces:
            eni.append(interface['NetworkInterfaceId'])

        if len(eni) == 3:
            logger.info('EC2 INSTANCE ALREDY HAS INTERFACES ATTACHED DURING WARM POOL STEP. SKIPPING ENI CREATION')

        elif len(eni) <= 1:
            logger.info('INITIAL ASG EC2 CREATE REQUEST RECEIVED - PROCEEDING TO CREATE AND ATTACH NETWORK INTERFACES')
            instance_az = get_ec2_data['Reservations'][0]['Instances'][0]['Placement']['AvailabilityZone']
            
            logger.info('CREATING NETWORK INTERFACE IN AZ: {}'.format(instance_az))

            # GET MGMT SUBNET ID BASED ON TAG NAME

            get_mgmt_subnet = ec2.describe_subnets(
                Filters=[
                            {
                                'Name': 'tag:Name',
                                'Values': [
                                    'mgmt-subnet-az1',
                                    'mgmt-subnet-az2',
                                    ]
                            },
                            {
                                'Name': 'availabilityZone',
                                'Values': [
                                    instance_az,
                                ]
                            },        
                        ],
                    )
            logger.info('DEBUG: {}'.format(get_mgmt_subnet))
            mgmt_subent_id = get_mgmt_subnet['Subnets'][0]['SubnetId']
            logger.info('DEBUG: {}'.format(mgmt_subent_id))

            # GET SECURITY GROUP ID BASED ON TAG NAME

            get_mgmt_sg_id = ec2.describe_security_groups(
                Filters=[
                    {
                        'Name': 'tag:Name',
                        'Values': [
                            'custom_vpc_sec_grp',
                        ]
                    },
                ]
            )
            logger.info('DEBUG: {}'.format(get_mgmt_sg_id))
            mgmt_sg_id = get_mgmt_sg_id['SecurityGroups'][0]['GroupId']
            logger.info('DEBUG: {}'.format(mgmt_sg_id))
            
            logger.info('SECURITY GROUP ID TO ATTACH TO THE ENI: {}'.format(mgmt_sg_id)) 

            # GET PRIVATE SUBNET ID BASED ON TAG NAME

            get_private_subnet = ec2.describe_subnets(
                Filters=[
                            {
                                'Name': 'tag:Name',
                                'Values': [
                                    'data-subnet-az1',
                                    'data-subnet-az2',
                                    ]
                            },
                            {
                                'Name': 'availabilityZone',
                                'Values': [
                                    instance_az,
                                ]
                            },
                        ],
                    )

            private_subnet_id = get_private_subnet['Subnets'][0]['SubnetId']
            
            # CREATE MGMT NETWORK INTERFACE
            logger.info('CREATE MGMT NETWORK INTERFACE IN SUBNET: {}'.format(mgmt_subent_id))  
            create_eni_mgmt = ec2.create_network_interface(
                    Description='AWS Lambda Created ENI - MGMT',
                    Groups=[str(mgmt_sg_id)],
                    SubnetId=str(mgmt_subent_id),
                    TagSpecifications=[
                            {
                                'ResourceType': 'network-interface',
                                'Tags': [
                                    {
                                        'Key': 'Name',
                                        'Value': "mgmt-eni-"+instance_az
                                        },
                                    ]
                                },
                            ],
                        )
            mgmt_eni_id = create_eni_mgmt['NetworkInterface']['NetworkInterfaceId']
            logger.info('WAITING FOR MGMT ENI {} TO BECOME AVAILABLE.'.format(mgmt_eni_id))
            waiter = ec2.get_waiter('network_interface_available')
            wait = waiter.wait(NetworkInterfaceIds=[str(mgmt_eni_id)])
            logger.info('MGMT ENI {} IS NOW AVAILABLE TO ATTACH'.format(mgmt_eni_id))
            
            # CREATE PRIVATE NETWORK INTERFACE
            logger.info('CREATE PRIVATE NETWORK INTERFACE IN SUBNET: {}'.format(private_subnet_id))
            create_eni_private = ec2.create_network_interface(
                    Description='AWS Lambda Created ENI - Private',
                    SubnetId=str(private_subnet_id),
                    TagSpecifications=[
                            {
                                'ResourceType': 'network-interface',
                                'Tags': [
                                    {
                                        'Key': 'Name',
                                        'Value': "private-eni-"+instance_az
                                        },
                                    ]
                                },
                            ],
                        )
            eni_id_private = create_eni_private['NetworkInterface']['NetworkInterfaceId']
            logger.info('WAITING FOR PRIVATE ENI {} TO BECOME AVAILABLE.'.format(eni_id_private))        
            waiter = ec2.get_waiter('network_interface_available')
            wait = waiter.wait(NetworkInterfaceIds=[str(eni_id_private)])
            logger.info('PRIVATE ENI {} IS NOW AVAILABLE TO ATTACH'.format(eni_id_private))

            #ATTACH MGMT ENI TO EC2

            logger.info('ATTACHING MGMT NETWORK INTERFACE: {} TO THE EC2: {}'.format(mgmt_eni_id,instance_id))
            attach_eni_mgmt = ec2.attach_network_interface(
                    DeviceIndex=1,
                    NetworkInterfaceId=mgmt_eni_id,
                    DryRun=False,
                    InstanceId=instance_id,
                    )                
            if attach_eni_mgmt['ResponseMetadata']['HTTPStatusCode'] == 200:
                message = 'SUCCESSFULLY ATTACHED MGMT ENI TO THE EC2'
                logger.info(message)
            else:
                message = 'MGMT NETWORK INTERFACE ATTACH FAILED!!!!!'
                logger.error(message)

            #ATTACH PRIVATE NETWORK INTERFACE TO EC2

            logger.info('ATTACHING PRIVATE NETWORK INTERFACE: {} TO THE EC2: {}'.format(eni_id_private,instance_id))
            attach_eni_private = ec2.attach_network_interface(
                    DeviceIndex=2,
                    NetworkInterfaceId=eni_id_private,
                    DryRun=False,
                    InstanceId=instance_id,
                    )                
            if attach_eni_private['ResponseMetadata']['HTTPStatusCode'] == 200:
                message = 'SUCCESSFULLY ATTACHED PRIVATE ENI TO THE EC2'
                logger.info(message)
            else:
                message = 'MGMT NETWORK INTERFACE ATTACH FAILED!!!!!'
                logger.error(message)
            return
        else:
            message = 'CONDITION TO CREATE NETWORK INTERFACES NOT MET. EXITING.....'
            logger.error(message)
            raise Exception(message)

    except Exception as e:
        message = 'NETWORK INTERFACE CREATION AND ATTACHMENT FAILED: {}'.format(e)
        logger.error(message)
        raise Exception(message)

def lambda_handler(event, context):

    message = 'ASG LIFECYCLE EVENT RECEIVED. EVENT DATA:- {}'.format(event)
    logger.info(message)


    if event['detail']['Destination'] == "WarmPool":
        try:
            run_command(event)
            sanity_check()
            send_lifecycle_action(event, 'CONTINUE')
            message = 'SUCCESS: LIFECYCLE ACTION COMPLETED'
            logger.info(message)
            return message

        except Exception as e:
            send_lifecycle_action(event, 'ABANDON')
            message = 'FAILED: LIFECYCLE ACTION FAILED. MESSAGE: {}'.format(e)
            logger.error(message)            
            raise Exception(message)

    elif event['detail']['LifecycleTransition'] == "autoscaling:EC2_INSTANCE_LAUNCHING":
        try:
            #here: sanity_check to confirm all of the panorama templates are applied, device in sync and connected state.
            run_command(event)
            send_lifecycle_action(event, 'CONTINUE')
            message = 'SUCCESS: LIFECYCLE ACTION COMPLETED'
            logger.info(message)
            return message

        except Exception as e:
            send_lifecycle_action(event, 'ABANDON')
            message = 'FAILED: LIFECYCLE ACTION FAILED. MESSAGE: {}'.format(e)
            logger.error(message)            
            raise Exception(message)


    elif event['detail']['LifecycleTransition'] == "autoscaling:EC2_INSTANCE_TERMINATING":
        try:
            remove_interfaces(event)
            send_lifecycle_action(event, 'CONTINUE')
            message = 'SUCCESS: LIFECYCLE ACTION COMPLETED'
            logger.info(message)
            return message
            
        except Exception as e:
            send_lifecycle_action(event, 'ABANDON')
            message = 'FAILED: LIFECYCLE ACTION FAILED. MESSAGE: {}'.format(e)
            logger.error(message)            
            raise Exception(message)

    else:
        message = 'LIFECYCLE TRANSITION CONDITION NOT MET.'
        logger.error(message)
        return message
