

class ELB:

    def __init__(self, client):
        self._client = client
        """ :type : pyboto3.elb """

    def create_load_balancer(self, name, scheme, subnets, sg_id):
        print('create load balancer with name ' + name)
        return self._client.create_load_balancer(
            Name=name,
            Subnets=subnets,
            SecurityGroups=[
                sg_id,
            ],
            Scheme=scheme
        )

    def create_target_group(self, vpcid, name, port, protocol, target_type, http_code):
        print('create target group with name ' + name)
        return self._client.create_target_group(
            Name=name,
            Protocol=protocol,
            Port=port,
            Matcher={
                'HttpCode': http_code
                },
            VpcId=vpcid,
            TargetType=target_type
        )

    def create_listener(self, tg_arn, tg_type, load_balancer_arn, protocol, port):
        print('create listener with tg arn ' + tg_arn)
        return self._client.create_listener(
            DefaultActions=[
                {
                    'TargetGroupArn': tg_arn,
                    'Type': tg_type,
                },
            ],
            LoadBalancerArn=load_balancer_arn,
            Protocol=protocol,
            Port=port
        )
