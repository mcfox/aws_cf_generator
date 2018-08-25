from troposphere import Base64, Join, GetAtt, Tags, Parameter, Ref, Template
from troposphere.autoscaling import AutoScalingGroup, Tag, LaunchConfiguration
from troposphere.elasticloadbalancing import LoadBalancer
from troposphere.policies import AutoScalingReplacingUpdate, AutoScalingRollingUpdate, UpdatePolicy
from troposphere.route53 import RecordSetType
from troposphere.ec2 import SecurityGroupIngress


import troposphere.ec2 as ec2
import troposphere.elasticloadbalancingv2 as elb

# global variables
# python parameters
app_name = 'taxmap'

env = 'staging'
# derived variables
stack_name = None
stack_name_strict = None
# cloud formation parameters
ssl_certificate_arn = None
vpc_id = None
subnet_id1 = None
subnet_id2 = None
alb_health_check_path = None
base_ami = None
instance_type = None


# get user inputs
def define_python_parameters():
    # input params
    global app_name
    default = app_name
    app_name = raw_input('What is the application name? [' + default + '] ') or default

    global env
    default = env
    env = raw_input('What is the environment (production/staging)? [' + default + '] ') or default

    # derived variables 
    env_suffix = 'Hml' if env == 'staging' else ''
    global stack_name
    stack_name = app_name.lower().replace(' ', '-')
    if env_suffix:
        stack_name = stack_name + "-" + env_suffix.lower()

    global stack_name_strict
    stack_name_strict = app_name.replace(' ', '').replace('-', '').replace('_', '') + env_suffix


def define_cloud_formation_parameters(template):
    global db_security_group_id
    db_security_group_id = Parameter(
        "DbSecurityGroupId",
        Type="AWS::EC2::SecurityGroup::Id",
        Default="sg-7aef2509",
        Description="The id of the security group of the database. The resources of the stack will be given access to the DB port in this security group.",
    )
    template.add_parameter(db_security_group_id)

    global db_port
    db_port = Parameter(
        "DbPort",
        Type="Number",
        Default="5432",
        Description="The port where the DB listens for incoming connections. The resources of the stack will be given access to this port in the DB security group.",
    )
    template.add_parameter(db_port)

    global ssl_certificate_arn
    ssl_certificate_arn = Parameter(
        "SSLCertificateARN",
        Type="String",
        Default="arn:aws:acm:us-west-2:676854543053:certificate/ab8afefd-5f93-48c2-a3fa-ae5a8e5f99e6",
        Description="ARN of the SSL certificate for load balancer."
    )
    template.add_parameter(ssl_certificate_arn)

    global vpc_id
    vpc_id = Parameter(
        "VpcId",
        Type="String",
        Default="vpc-ebe0c38e",
        Description="Id of the VPC which will hold the resources"
    )
    template.add_parameter(vpc_id)

    global subnet_id1
    subnet_id1 = Parameter(
        "SubnetId1",
        Type="String",
        Default="subnet-0b3b0d6e",
        Description="Id of the 1st Subnet which will hold the resources"
    )
    template.add_parameter(subnet_id1)

    global subnet_id2
    subnet_id2 = Parameter(
        "SubnetId2",
        Type="String",
        Default="subnet-2f267258",
        Description="Id of the 2nd Subnet which will hold the resources"
    )
    template.add_parameter(subnet_id2)

    global alb_health_check_path
    alb_health_check_path = Parameter(
        "AlbHealthCheckPath",
        Type="String",
        Default="/authentication/sign_in",
        Description="Ping path destination used by the load balancer to check server health"
    )
    template.add_parameter(alb_health_check_path)

    global base_ami
    base_ami = Parameter(
        "BaseAMI",
        Type="String",
        Default="ami-0272537a",
        Description="Id of the base AMI"
    )
    template.add_parameter(base_ami)

    global instance_type
    instance_type = Parameter(
        "InstanceType",
        Type="String",
        Default="t2.micro",
        Description="Type of the instance to be used."
    )
    template.add_parameter(instance_type)


def define_security_group(template):
    sg = ec2.SecurityGroup(
        stack_name_strict + 'SG',
        GroupDescription="Security Group for " + stack_name + " stack.",
        Tags=Tags(
            Name=stack_name,
            Custo=app_name
        ),
        SecurityGroupIngress=[
            ec2.SecurityGroupRule(
                IpProtocol="tcp",
                FromPort="22",
                ToPort="22",
                CidrIp="0.0.0.0/0"
            ),
            ec2.SecurityGroupRule(
                IpProtocol="tcp",
                FromPort="9090",
                ToPort="9090",
                CidrIp="0.0.0.0/0"
            ),
            ec2.SecurityGroupRule(
                IpProtocol="tcp",
                FromPort="80",
                ToPort="80",
                CidrIp="0.0.0.0/0"
            ),
            ec2.SecurityGroupRule(
                IpProtocol="tcp",
                FromPort="443",
                ToPort="443",
                CidrIp="0.0.0.0/0"
            )
        ],
        VpcId=Ref(vpc_id)
    )
    template.add_resource(sg)
    return sg


# instance
# instance = ec2.Instance(
#    "troposphereec2",
#    ImageId="ami-9ba6ece3",
#    InstanceType="t1.micro",
#    KeyName="taxweb-AWS-US-West",
# VpcId="vpc-ebe0c38e",
#    SubnetId=subnet_id1,
#    SecurityGroupIds=[Ref(sg)]
# )
# template.add_resource(instance)

def define_load_balancer(template, sg):
    alb_target_group_80 = elb.TargetGroup(
        stack_name_strict + "TG80",
        Tags=Tags(
            Name=stack_name,
            Custo=app_name
        ),
        HealthCheckPath=Ref(alb_health_check_path),
        HealthCheckIntervalSeconds="30",
        HealthCheckProtocol="HTTP",
        HealthCheckTimeoutSeconds="10",
        HealthyThresholdCount="3",
        Matcher=elb.Matcher(
            HttpCode="301"),
        Port=80,
        Protocol="HTTP",
        UnhealthyThresholdCount="2",
        VpcId=Ref(vpc_id)
    )
    template.add_resource(alb_target_group_80)

    alb_target_group_9090 = elb.TargetGroup(
        stack_name_strict + "TG9090",
        Tags=Tags(
            Name=stack_name,
            Custo=app_name
        ),
        HealthCheckPath=Ref(alb_health_check_path),
        HealthCheckIntervalSeconds="30",
        HealthCheckProtocol="HTTP",
        HealthCheckTimeoutSeconds="10",
        HealthyThresholdCount="3",
        Matcher=elb.Matcher(
            HttpCode="200"),
        Port=9090,
        Protocol="HTTP",
        UnhealthyThresholdCount="2",
        VpcId=Ref(vpc_id)
    )
    template.add_resource(alb_target_group_9090)

    alb = elb.LoadBalancer(
        stack_name_strict + "ALB",
        Tags=Tags(
            Name=stack_name,
            Custo=app_name
        ),
        Scheme="internet-facing",
        Subnets=[Ref(subnet_id1), Ref(subnet_id2)],
        SecurityGroups=[Ref(sg)]
    )
    template.add_resource(alb)

    alb_listener_80 = elb.Listener(
        stack_name_strict + "ListenerALB80",
        Port=80,
        Protocol="HTTP",
        LoadBalancerArn=Ref(alb),
        DefaultActions=[elb.Action(
            Type="forward",
            TargetGroupArn=Ref(alb_target_group_80)
        )]
    )
    template.add_resource(alb_listener_80)

    alb_listener_443 = elb.Listener(
        stack_name_strict + "ListenerALB443",
        Port=443,
        Protocol="HTTPS",
        Certificates=[elb.Certificate(
            CertificateArn=Ref(ssl_certificate_arn)
        )],
        LoadBalancerArn=Ref(alb),
        DefaultActions=[elb.Action(
            Type="forward",
            TargetGroupArn=Ref(alb_target_group_9090)
        )]
    )
    template.add_resource(alb_listener_443)

    return {"loadbalancer": alb,
            "alb_target_group_80": alb_target_group_80,
            "alb_target_group_9090": alb_target_group_9090,
            "alb_listener_80": alb_listener_80,
            "alb_listener_9090": alb_listener_443}


def define_web_auto_scaling(template, alb_target_group_80, alb_target_group_9090, sg):
    web_launch_config = LaunchConfiguration(
        stack_name_strict + "WebLC",
        UserData=Base64(Join('', [
            '#!/bin/bash\n',
            'set -x\n',
            'exec > >(tee /tmp/user-data.log|logger -t user-data ) 2>&1\n',
            'sudo su - deploy -c "echo \\"export RAILS_ENV=' + env + '\\" >> ~/.bashrc"\n',
            'sudo su - deploy -c "cd ~/app/current; wget http://taxweb-deploy.s3.amazonaws.com/' + app_name + '/app_update.sh -O app_update.sh >/dev/null 2>&1"\n',
            'sudo su - deploy -c "cd ~/app/current && chmod 755 app_update.sh && ./app_update.sh ' + env + ' web ' + app_name + '"\n'
        ])),
        ImageId=Ref(base_ami),
        InstanceType=Ref(instance_type),
        KeyName="taxweb-AWS-US-West",
        SecurityGroups=[Ref(sg)]
    )
    template.add_resource(web_launch_config)

    web_autoscaling_group = AutoScalingGroup(
        stack_name_strict + "WebASG",
        Tags=[
            Tag("Name", stack_name + "-web", True),
            Tag("Custo", app_name, True),
            Tag("Env", env, True),
            Tag("Role", "web", True),
        ],
        LaunchConfigurationName=Ref(web_launch_config),
        MinSize=1,
        MaxSize=1,
        DesiredCapacity=1,
        VPCZoneIdentifier=[Ref(subnet_id1), Ref(subnet_id2)],
        TargetGroupARNs=[Ref(alb_target_group_80), Ref(alb_target_group_9090)],
        HealthCheckType="ELB",
        HealthCheckGracePeriod="300",
    )
    template.add_resource(web_autoscaling_group)

    return {"launch_config": web_launch_config,
            "autoscaling_group": web_autoscaling_group}


def define_auto_scaling(template, sg, role):
    launch_config = LaunchConfiguration(
        stack_name_strict + role + "LC",
        UserData=Base64(Join('', [
            '#!/bin/bash\n',
            'set -x\n',
            'exec > >(tee /tmp/user-data.log|logger -t user-data ) 2>&1\n',
            'sudo su - deploy -c "echo \\"export RAILS_ENV=' + env + '\\" >> ~/.bashrc"\n',
            'sudo su - deploy -c "cd ~/app/current; wget http://taxweb-deploy.s3.amazonaws.com/' + app_name + '/app_update.sh -O app_update.sh >/dev/null 2>&1"\n',
            'sudo su - deploy -c "cd ~/app/current && chmod 755 app_update.sh && ./app_update.sh ' + env + ' ' + role + ' ' + app_name + '"\n'
        ])),
        ImageId=Ref(base_ami),
        InstanceType=Ref(instance_type),
        KeyName="taxweb-AWS-US-West",
        SecurityGroups=[Ref(sg)]
    )
    template.add_resource(launch_config)

    autoscaling_group = AutoScalingGroup(
        stack_name_strict + role + "ASG",
        Tags=[
            Tag("Name", stack_name + "-" + role, True),
            Tag("Custo", app_name, True),
            Tag("Env", env, True),
            Tag("Role", role, True),
        ],
        LaunchConfigurationName=Ref(launch_config),
        MinSize=1,
        MaxSize=1,
        DesiredCapacity=1,
        VPCZoneIdentifier=[Ref(subnet_id1), Ref(subnet_id2)],
        HealthCheckType="EC2",
        HealthCheckGracePeriod="300",
    )
    template.add_resource(autoscaling_group)

    return {"launch_config": launch_config,
            "autoscaling_group": autoscaling_group}


def define_dns(template, alb):
    route53_record = template.add_resource(RecordSetType(
        stack_name_strict + "WebDNS",
        HostedZoneName="taxweb.com.br.",
        Name=stack_name + ".taxweb.com.br.",
        ResourceRecords=[GetAtt(alb, "DNSName")],
        TTL=60,
        Type="CNAME"
    ))

    return route53_record


def add_ingress_rule_to_db_security_group(template, db_sg, db_port, stack_sg):
    sg_ingress = SecurityGroupIngress(
            stack_name_strict + "DbIngressRule",
            IpProtocol="tcp",
            FromPort=Ref(db_port),
            ToPort=Ref(db_port),
            SourceSecurityGroupId=Ref(stack_sg),
            GroupId=Ref(db_sg)
    )
    template.add_resource(sg_ingress)


def gerador():
    # template
    template = Template()
    template.add_version("2010-09-09")
    template.add_description("AWS CloudFormation template for Taxweb RoR applications")

    # python parameters
    define_python_parameters()

    # parameters
    define_cloud_formation_parameters(template)

    # security group
    sg = define_security_group(template)

    # ALB (Application Load Balancer)
    alb = define_load_balancer(template, sg)

    # web auto scaling
    define_web_auto_scaling(template, alb["alb_target_group_80"], alb["alb_target_group_9090"], sg)

    # worker-master auto scaling
    define_auto_scaling(template, sg, 'workermaster')

    # worker-tasks auto scaling
    define_auto_scaling(template, sg, 'workertasks')

    # operation auto scaling
    define_auto_scaling(template, sg, 'operation')

    # DNS
    define_dns(template, alb["loadbalancer"])

    # Add ingress rule to db security group
    add_ingress_rule_to_db_security_group(template, db_security_group_id, db_port, sg)

    final_json = template.to_json()

    f = open("../cloud_formation/" + stack_name + "-stack-cf.json", "w+")
    f.write(final_json)
    f.close()


# Chammo o Gerador do Arquivo
gerador()
