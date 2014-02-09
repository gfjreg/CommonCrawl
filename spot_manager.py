#!/usr/bin/env python
__author__ = 'aub3'

import boto.ec2

conn = boto.ec2.connect_to_region("us-east-1")
reservations = conn.get_all_reservations()

warning = """you are launching a spot instance its important that you closely monitor"""

def launch_spot_instance():
    """
    This function launches a spot instance and periodically checks for its availability.

    """
    #raw_input()
    pass

print reservations
print reservations[0].id,reservations[0].region
instances = reservations[0].instances
#print dir(instances[0])
print instances[0].instance_type
print instances[0].image_id
print instances[0].ip_address
print instances[0].public_dns_name