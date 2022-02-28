client = boto3.client('elbv2')

header_list = []

lb_api = client.describe_load_balancers(
    Names=[
        'public-alb-dev',
    ],
)

lb_arn = lb_api['LoadBalancers'][0]['LoadBalancerArn']

lstrn_api = client.describe_listeners(
    LoadBalancerArn=str(lb_arn),
)

lstnr_arn = lstrn_api['Listeners'][0]['ListenerArn'] 

response = client.describe_rules(
    ListenerArn=str(lstnr_arn),
)
for rules in response['Rules']:
    try:
       header_list.append(rules['Conditions'][0]['Values'][0])
    except IndexError as error:
       print(end="")
print(header_list)
