import time
from src.com.aws.ClientLocator import Client
from src.com.aws.vpc import VPC
from src.com.aws.elb import ELB
from src.com.aws.ec2 import EC2
from src.com.aws.autoscaling import AutoScaling


class DeployALL:

    @staticmethod
    def deploy_tier3():
        cidr_block = '10.0.0.0/16'
        vpc_name = 'Tier3VPC'
        igw_name = 'Tier3IGW'
        tier3_subnet_map = {'subnet_1': ['tier3_public_subnet_1', '10.0.1.0/24', 'us-east-1a'],
                            'subnet_2': ['tier3_public_subnet_2', '10.0.2.0/24', 'us-east-1b'],
                            'subnet_3': ['tier3_private_subnet_3', '10.0.3.0/24', 'us-east-1a'],
                            'subnet_4': ['tier3_private_subnet_4', '10.0.4.0/24', 'us-east-1b']}

        be_inbound_rules = [{
                'IpProtocol': 'tcp',
                'FromPort': 80,
                'ToPort': 80,
                'IpRanges': [{'CidrIp': '10.0.1.0/24'}]
            },
            {
                'IpProtocol': 'tcp',
                'FromPort': 443,
                'ToPort': 443,
                'IpRanges': [{'CidrIp': '10.0.1.0/24'}]
            },
            {
                'IpProtocol': 'tcp',
                'FromPort': 22,
                'ToPort': 22,
                'IpRanges': [{'CidrIp': '10.0.1.0/24'}]
            },
            {
                'IpProtocol': 'tcp',
                'FromPort': 80,
                'ToPort': 80,
                'IpRanges': [{'CidrIp': '10.0.2.0/24'}]
            },
            {
                'IpProtocol': 'tcp',
                'FromPort': 443,
                'ToPort': 443,
                'IpRanges': [{'CidrIp': '10.0.2.0/24'}]
            },
            {
                'IpProtocol': 'tcp',
                'FromPort': 22,
                'ToPort': 22,
                'IpRanges': [{'CidrIp': '10.0.2.0/24'}]
            }
        ]

        fe_inbound_rules = [{
                'IpProtocol': 'tcp',
                'FromPort': 80,
                'ToPort': 80,
                'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
            },
            {
                'IpProtocol': 'tcp',
                'FromPort': 443,
                'ToPort': 443,
                'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
            },
            {
                'IpProtocol': 'tcp',
                'FromPort': 22,
                'ToPort': 22,
                'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
            }
        ]
        # creating VPC
        # Getting EC2 client object
        ec2_client = Client('ec2').get_client()

        # setting EC2 object in VPC
        vpc = VPC(ec2_client)

        # create vpc
        vpc_response = vpc.create_vpc(cidr_block)
        vpc_id = vpc_response['Vpc']['VpcId']

        # change vpc name tag
        vpc.add_name_tag(vpc_id, vpc_name)

        # create internet gateway

        igw_response = vpc.create_internet_gateway()
        igw_id = igw_response['InternetGateway']['InternetGatewayId']

        # change igw tag name
        vpc.add_name_tag(igw_id, igw_name)

        # attach igw with vpc
        vpc.attach_igw_to_vpc(vpc_id, igw_id)

        # create subnet's
        for subnet_value in tier3_subnet_map.values():
            subnet_value.append(vpc.create_subnet(vpc_id, subnet_value[1], subnet_value[2])['Subnet']['SubnetId'])
            # add tag to subnet
            vpc.add_name_tag(subnet_value[3], subnet_value[0])

        # create public route table
        public_route_table_id = vpc.create_route_table(vpc_id)['RouteTable']['RouteTableId']
        private_route_table_id = vpc.create_route_table(vpc_id)['RouteTable']['RouteTableId']

        # add tag to rt's
        vpc.add_name_tag(public_route_table_id, 'public_route_table')
        vpc.add_name_tag(private_route_table_id, 'private_route_table')

        # associate subnet rts to subnet
        private_subnets = []
        public_subnets = []
        i = 0
        for subnet_value in tier3_subnet_map.values():
            if i < 2:
                vpc.associate_subnet_with_route_table(subnet_value[3], public_route_table_id)
                vpc.allow_auto_assign_ip_addresses_for_subnet(subnet_value[3])
                public_subnets.append(subnet_value[3])
            else:
                vpc.associate_subnet_with_route_table(subnet_value[3], private_route_table_id)
                private_subnets.append(subnet_value[3])
            i = i + 1

        # associate Public RT with IGW
        vpc.create_igw_route_to_route_table(public_route_table_id, igw_id, '0.0.0.0/0')

        # allocate eip

        allocation_id = vpc.allocate_eip('vpc')['AllocationId']

        # create nat gateway
        nat_gw_id = vpc.create_nat_gateway(tier3_subnet_map.get('subnet_2')[3],
                                           allocation_id)['NatGateway']['NatGatewayId']

        time.sleep(30)
        # assign nat gateway to private rt
        vpc.associate_nat_with_route_table(private_route_table_id, nat_gw_id, '0.0.0.0/0')

        # configure ELB
        elb_client = Client('elbv2').get_client()
        elb = ELB(elb_client)

        # creating SG for FE
        ec2 = EC2(ec2_client)
        fe_sg_id = ec2.create_security_group('FE_SG', 'front end security group', vpc_id)['GroupId']

        # adding inbound rules to SG FE
        ec2.add_inbound_rule_to_sg(fe_sg_id, fe_inbound_rules)

        # creating SG for BE
        ec2 = EC2(ec2_client)
        be_sg_id = ec2.create_security_group('BE_SG', 'back end security group', vpc_id)['GroupId']

        # adding inbound rules to SG BE
        ec2.add_inbound_rule_to_sg(be_sg_id, be_inbound_rules)

        # create target group
        fe_target_grp_name = 'Frontend2-TG'
        fe_tg_arn = elb.create_target_group(vpc_id, fe_target_grp_name, 80, 'HTTP', 'instance', '200')['TargetGroups'][0]['TargetGroupArn']

        be_target_grp_name = 'Backend3-TG'
        be_tg_arn = elb.create_target_group(vpc_id, be_target_grp_name, 80, 'HTTP', 'instance', '200')['TargetGroups'][0][
            'TargetGroupArn']

        public_elb_arn = elb.create_load_balancer('internetloadbalancer', 'internet-facing', public_subnets, fe_sg_id)['LoadBalancers'][0]['LoadBalancerArn']
        print(public_elb_arn)
        private_elb_arn = elb.create_load_balancer('internaloadbalancer', 'internal', private_subnets, be_sg_id)['LoadBalancers'][0]['LoadBalancerArn']
        print(private_elb_arn)

        # create listeners
        tg_type = 'forward'
        elb.create_listener(fe_tg_arn, tg_type, public_elb_arn, 'HTTP', 80)

        elb.create_listener(be_tg_arn, tg_type, private_elb_arn, 'HTTP', 80)

        # configure auto scaling
        as_client = Client('autoscaling').get_client()
        auto_scale = AutoScaling(as_client)

        # create Launch configuration public

        key_name = 'my_tier3_key'
        key_value = ec2.create_key_pair(key_name)['KeyMaterial']

        with open(key_name+".pem", "w") as text_file:
            text_file.write(key_value)

        fe_lc_name = 'FE_LC'
        auto_scale.create_launch_configuration('ec2_s3_role', 'ami-04bfee437f38a691e', 't2.micro', fe_lc_name, fe_sg_id, key_name)

        # create public auto scale group
        fe_as_name = 'AS_FE'
        pr_sub = private_subnets[0] + ', ' + private_subnets[1]
        auto_scale.create_auto_scaling_group(fe_as_name, fe_lc_name, 3, 2, pr_sub, [fe_tg_arn], 'ELB', 120)

        # create Launch configuration private
        be_lc_name = 'LC_BE'
        auto_scale.create_launch_configuration('ec2_s3_role', 'ami-04bfee437f38a691e', 't2.micro', be_lc_name, be_sg_id, key_name)

        # create private auto scale group
        pr_as_name = 'AS_BE'
        auto_scale.create_auto_scaling_group(pr_as_name, be_lc_name, 3, 2, pr_sub, [be_tg_arn], 'ELB', 120)

        # create public SG
        public_sg_id = ec2.create_security_group('Public_SG', 'SG for public server', vpc_id)['GroupId']

        # adding inbound rules to Public_SG
        ec2.add_inbound_rule_to_sg(public_sg_id, fe_inbound_rules)

        # create public ec2 instance
        user_data = """#!/bin/bash
                    yum update -y
                    yum install httpd24 -y
                    service httpd start
                    chkconfig httpd on
                    echo "<html><body><h1>Hello from <b>Boto3</b> using Python!</h1></body></html>" > /var/www/html/index.html"""

        ec2.launch_ec2_instance('ami-04bfee437f38a691e', key_name, 1, 1, public_sg_id, public_subnets[0], user_data)
