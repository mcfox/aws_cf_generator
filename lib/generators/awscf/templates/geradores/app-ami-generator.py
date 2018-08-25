from troposphere import Base64, Join, Parameter, Ref, Template, Tags
import troposphere.ec2 as ec2

# template
template = Template()
template.add_version("2010-09-09")
template.add_description("AWS CloudFormation template for base instance")

app_name = 'taxmap'
app_name_capitalize = 'TaxMap'

# parameters
subnet_id = Parameter(
    "SubnetId",
    Type="AWS::EC2::Subnet::Id",
    Default="subnet-0b3b0d6e",
    Description="Id of the Subnet which will hold the instance"
)
template.add_parameter(subnet_id)

vpc_id = Parameter(
    "VpcId",
    Type="AWS::EC2::VPC::Id",
    Default="vpc-ebe0c38e",
    Description="Id of the VPC which will hold the instance"
)
template.add_parameter(vpc_id)


# security group
sg = ec2.SecurityGroup(
    app_name_capitalize + 'SG',
    GroupDescription="Security Group for base instance.",
    Tags=Tags(
       Name= app_name + '-base-instance-sg',
       Custo= app_name
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


# instance
instance = ec2.Instance(
    app_name_capitalize + "BaseInstance",
    Tags=Tags(
        Name= app_name + '-Base-Instance',
        Custo= app_name
    ),
    ImageId="ami-a9d09ed1",
    InstanceType="t2.medium",
    KeyName="taxweb-AWS-US-West",
    SubnetId=Ref(subnet_id),
    SecurityGroupIds=[Ref(sg)],
    UserData=Base64(Join('', [
        '#!/bin/bash\n',
        'set -x\n',
        'exec > >(tee /tmp/user-data.log|logger -t user-data ) 2>&1\n',
	'# create user deploy\n'
	'sudo useradd deploy\n',
	'sudo bash -c "echo -e \\"deploy\tALL=(ALL) NOPASSWD: ALL\\" >> /etc/sudoers"\n',
	'# install rvm and ruby\n',
	'sudo yum install -y gcc openssl-devel libyaml libyaml-devel libffi-devel libreadline readline-devel zlib1g zlib-devel gdbm-devel ncurses ncurses-devel ruby-devel gcc-c++ jq git patch libtool bison build-essential libc6 libgdbm\n',
	'sudo yum install -y postgresql-devel\n',
	'sudo su - deploy -c "curl -sSL https://rvm.io/mpapis.asc | gpg2 --import -"\n',
	'sudo su - deploy -c "curl -sSL https://get.rvm.io | bash -s stable"\n',
	'sudo su - deploy -c "yes | rvm install 2.4.1"\n',
	'# install bundler\n',
	'sudo su - deploy -c "gem install bundler"\n',
	'# create ~/app and install the application dependencies\n',
	'sudo su - deploy -c "mkdir -p ~/app/current"\n',
	'sudo su - deploy -c "mkdir -p ~/app/shared/log"\n',
	'sudo su - deploy -c "mkdir -p ~/app/shared/tmp/pids"\n',
	'sudo su - deploy -c "mkdir -p ~/app/shared/tmp/sockets"\n',
	'sudo yum -y install ImageMagick ImageMagick-devel\n',
	'# install yarn\n',
	'sudo su - -c "curl --silent --location https://dl.yarnpkg.com/rpm/yarn.repo | sudo tee /etc/yum.repos.d/yarn.repo"\n',
	'sudo su - -c "curl --silent --location https://rpm.nodesource.com/setup_6.x | bash -"\n',
	'sudo yum -y install yarn\n',
	'# install nginx\n',
	'sudo amazon-linux-extras install nginx1.12 -y\n',
	'# config nginx\n',
	'sudo su - -c "cd /etc/nginx/ && rm nginx.conf; wget http://taxweb-deploy.s3.amazonaws.com/' + app_name + '/nginx_default.conf -O nginx.conf"\n',
	'sudo su - -c "cd /etc/nginx/conf.d/ && wget http://taxweb-deploy.s3.amazonaws.com/' + app_name + '/app_nginx.conf -O app.conf"\n',
	'sudo service nginx restart\n',
	'# access to puma.sock to all users (otherwise nginx cant read it)\n',
	'sudo chmod 755 /home\n',
	'sudo chmod 755 /home/deploy\n',
	'sudo chmod 755 /home/deploy/app\n',
	'sudo chmod 755 /home/deploy/app/shared\n',
	'sudo chmod 755 /home/deploy/app/shared/tmp\n',
	'sudo chmod 755 /home/deploy/app/shared/tmp/sockets\n',
    '# execute app_update.sh\n',
    'sudo su - deploy -c "cd ~/app/current; wget http://taxweb-deploy.s3.amazonaws.com/' + app_name + '/app_update.sh -O app_update.sh >/dev/null 2>&1"\n',
    'sudo su - deploy -c "cd ~/app/current && chmod 755 app_update.sh && ./app_update.sh staging web ' + app_name + '"\n',
    '# finished\n',
    'echo "Instance configuration finished!"\n'
    ]))
)
template.add_resource(instance)


f = open("../cloud_formation/" + app_name + "-ami-cf.json", "w+")
f.write(template.to_json())
f.close()
