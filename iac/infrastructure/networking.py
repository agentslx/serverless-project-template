"""VPC, private subnets, VPC peering, and internal DNS resolution.

Provides networking infrastructure for Lambdas that need VPC access
(e.g. RDS, ElastiCache) and internal DNS routing via organization's
local DNS (bypassing public Route 53).

Not used by the default template — enable when Lambdas require VPC
ENI access or when internal service resolution is needed.
"""
from __future__ import annotations

import json
import pulumi
import pulumi_aws as aws


class Networking:
    """VPC with private subnets and optional VPC peering for internal DNS.

    Args:
        prefix: Project prefix for naming.
        stack: Stack name (dev/prod).
        cidr_block: VPC CIDR (default "10.0.0.0/16").
        azs: Availability zones for subnet distribution.
        peer_vpc_id: VPC ID to peer with (for internal DNS resolution).
        peer_vpc_cidr: CIDR of the peer VPC (for route table entries).
    """

    def __init__(
        self,
        prefix: str,
        stack: str,
        *,
        cidr_block: str = "10.0.0.0/16",
        azs: list[str] | None = None,
        peer_vpc_id: str | None = None,
        peer_vpc_cidr: str | None = None,
    ):
        if azs is None:
            azs = ["ap-southeast-2a", "ap-southeast-2b"]

        vpc_name = f"{prefix}-{stack}-vpc"
        self.vpc = aws.ec2.Vpc(
            vpc_name,
            cidr_block=cidr_block,
            enable_dns_support=True,
            enable_dns_hostnames=True,
            tags={"Name": vpc_name, "app": prefix, "stack": stack},
        )

        self.private_subnets: list[aws.ec2.Subnet] = []
        for i, az in enumerate(azs):
            subnet = aws.ec2.Subnet(
                f"{vpc_name}-private-{i}",
                vpc_id=self.vpc.id,
                cidr_block=f"10.0.{i + 1}.0/24",
                availability_zone=az,
                tags={"Name": f"{vpc_name}-private-{az}", "app": prefix, "stack": stack},
            )
            self.private_subnets.append(subnet)

        self.security_group = aws.ec2.SecurityGroup(
            f"{vpc_name}-lambda-sg",
            vpc_id=self.vpc.id,
            description="Security group for Lambda functions in VPC",
            egress=[aws.ec2.SecurityGroupEgressArgs(
                protocol="-1",
                from_port=0,
                to_port=0,
                cidr_blocks=["0.0.0.0/0"],
            )],
            tags={"Name": f"{vpc_name}-lambda-sg", "app": prefix, "stack": stack},
        )

        if peer_vpc_id and peer_vpc_cidr:
            peering = aws.ec2.VpcPeeringConnection(
                f"{vpc_name}-peering",
                vpc_id=self.vpc.id,
                peer_vpc_id=peer_vpc_id,
                auto_accept=True,
                tags={"Name": f"{vpc_name}-peering", "app": prefix, "stack": stack},
            )

            route_table = aws.ec2.RouteTable(
                f"{vpc_name}-rt",
                vpc_id=self.vpc.id,
                routes=[aws.ec2.RouteTableRouteArgs(
                    cidr_block=peer_vpc_cidr,
                    vpc_peering_connection_id=peering.id,
                )],
                tags={"Name": f"{vpc_name}-rt", "app": prefix, "stack": stack},
            )

            for i, subnet in enumerate(self.private_subnets):
                aws.ec2.RouteTableAssociation(
                    f"{vpc_name}-rta-{i}",
                    subnet_id=subnet.id,
                    route_table_id=route_table.id,
                )

    @property
    def vpc_id(self) -> pulumi.Output[str]:
        return self.vpc.id

    @property
    def subnet_ids(self) -> list[pulumi.Output[str]]:
        return [s.id for s in self.private_subnets]

    @property
    def security_group_id(self) -> pulumi.Output[str]:
        return self.security_group.id
