

class VPC:

    def __init__(self, client):
        self._client = client

    def create_vpc(self, cidr_block):
        print('Creating a VPC...')
        return self._client.create_vpc(
            CidrBlock=cidr_block
        )

    def add_name_tag(self, resource_id, resource_name):
        print('Adding ' + resource_name + ' tag to the ' + resource_id)
        return self._client.create_tags(
            Resources=[resource_id],
            Tags=[{
                'Key': 'Name',
                'Value': resource_name
            }]
        )

    def create_internet_gateway(self):
        print('Creating an Internet Gateway...')
        return self._client.create_internet_gateway()

    def attach_igw_to_vpc(self, vpc_id, igw_id):
        print('Attaching Internet Gateway ' + igw_id + ' to VPC ' + vpc_id)
        return self._client.attach_internet_gateway(
            InternetGatewayId=igw_id,
            VpcId=vpc_id
            )

    def create_subnet(self, vpc_id, cidr_block, availability_zone):
        print('Creating a subnet for VPC' + vpc_id + ' with CIDR block ' + cidr_block)
        return self._client.create_subnet(
            VpcId=vpc_id,
            CidrBlock=cidr_block,
            AvailabilityZone=availability_zone
        )

    def create_route_table(self, vpc_id):
        print('Creating public Route Table for VPC ' + vpc_id)
        return self._client.create_route_table(VpcId=vpc_id)

    def create_igw_route_to_route_table(self, rtb_id, igw_id, destination_cidr_block):
        print('Adding route for IGW ' + igw_id + ' to Route Table ' + rtb_id)
        return self._client.create_route(
            RouteTableId=rtb_id,
            GatewayId=igw_id,
            DestinationCidrBlock=destination_cidr_block
        )

    def associate_subnet_with_route_table(self, subnet_id, rtb_id):
        print('Associating subnet ' + subnet_id + ' with Route Table ' + rtb_id)
        return self._client.associate_route_table(
            SubnetId=subnet_id,
            RouteTableId=rtb_id
        )

    def allow_auto_assign_ip_addresses_for_subnet(self, subnet_id):
        print('Allow auto assign ip address for subnet ' + subnet_id)
        return self._client.modify_subnet_attribute(
            SubnetId=subnet_id,
            MapPublicIpOnLaunch={'Value': True})

    def create_nat_gateway(self, subnet_id, allocation_id):
        print('create NAT GW for ' + subnet_id + ' and allocation id ' +allocation_id )
        return self._client.create_nat_gateway(
            SubnetId=subnet_id,
            AllocationId=allocation_id)

    def allocate_eip(self, domain):
        print('allocating EIP for domain' + domain)
        return self._client.allocate_address(Domain=domain)

    def associate_nat_with_route_table(self, rtb_id, nat_id, destination_cidr_block):
        print('Adding route for NAT GW ' + nat_id + ' to Route Table ' + rtb_id)
        return self._client.create_route(
            RouteTableId=rtb_id,
            NatGatewayId=nat_id,
            DestinationCidrBlock=destination_cidr_block
        )
