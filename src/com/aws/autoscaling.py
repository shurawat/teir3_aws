class AutoScaling:

    def __init__(self, client):
        self._client = client
        """ :type : pyboto3.autoscaling """

    def create_launch_configuration(self, iam_role, image_id, instance_type, lc_name, sg_id, key_name):
        print('Creating launch configuration with name ' + lc_name)
        self._client.create_launch_configuration(
            IamInstanceProfile=iam_role,
            ImageId=image_id,
            InstanceType=instance_type,
            LaunchConfigurationName=lc_name,
            KeyName=key_name,
            SecurityGroups=[
                sg_id,
            ],
        )

    def create_auto_scaling_group(self, auto_scale_name, lc_name, max_size, min_size, subnet, tg_arns, hc_type, hc_period):
        print('Creating auto scaling group with name ' + auto_scale_name)
        self._client.create_auto_scaling_group(
            AutoScalingGroupName=auto_scale_name,
            LaunchConfigurationName=lc_name,
            MaxSize=max_size,
            MinSize=min_size,
            VPCZoneIdentifier=subnet,
            TargetGroupARNs=tg_arns,
            HealthCheckType=hc_type,
            HealthCheckGracePeriod=hc_period
        )

    def put_scaling_policy(self, policy_name, as_name):
        return self._client.put_scaling_policy(
            AdjustmentType='ChangeInCapacity',
            PolicyName=policy_name,
            AutoScalingGroupName=as_name,
            ScalingAdjustment=-1,
        )
