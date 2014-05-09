#!/usr/bin/env python
__author__ = 'aub3'

import boto.ec2,time,datetime
CONN = boto.ec2.connect_to_region("us-east-1")

class SpotInstance(object):

    @classmethod
    def get_spot_instances(cls,EC2_Tag):
        """
        Get all spot instances with specified EC2_Tag
        """
        requests = CONN.get_all_spot_instance_requests()
        instances = []
        for request in requests:
            instances.append(SpotInstance(EC2_Tag,request.id,request.instance_id))
        return instances

    def __init__(self,tag,request_id=None,instance_id=None,):
        self.request_id = request_id
        self.instance_id = instance_id
        self.public_dns_name = None
        self.price = None
        self.instance_type = None
        self.image_id = None
        self.key_name = None
        self.fulfilled = False
        self.instance_object = None
        self.valid_until = None
        self.tag = tag
        self.instance_profile = None
        self.user_data = ""
        if self.instance_id:
            self.fulfilled = True
            self.get_instance()

    def add_tag(self):
        if self.request_id:
            CONN.create_tags([self.request_id], {"Tag":self.tag})


    def request_instance(self,price,instance_type,image_id,key_name,user_data,instance_profile):
        self.price = price
        self.instance_type = instance_type
        self.image_id = image_id
        self.key_name = key_name
        self.user_data = user_data
        self.instance_profile = instance_profile
        print "You are launching a spot instance request."
        print "It is important that you closely monitor and cancel unfilled requests using AWS web console."
        if raw_input("\n Please enter 'yes' to start >> ")=='yes':
            self.valid_until = (datetime.datetime.utcnow()+datetime.timedelta(minutes=20)).isoformat() # valid for 20 minutes from now
            print "request valid until UTC: ", self.valid_until
            spot_request = CONN.request_spot_instances(price=price,instance_type=instance_type,image_id=image_id,key_name=key_name,valid_until=self.valid_until,user_data=self.user_data,instance_profile_name=self.instance_profile)
            self.request_id = spot_request[0].id
            time.sleep(30) # wait for some time, otherwise AWS throws up an error
            self.add_tag()
            print "requesting a spot instance"
        else:
            print "Did not request a spot instance"

    def check_allocation(self):
        if self.request_id:
            instance_id = CONN.get_all_spot_instance_requests(request_ids=[self.request_id])[0].instance_id
            while instance_id is None:
                print "waiting"
                time.sleep(60) # Checking every minute
                print "Checking job instance id for this spot request"
                instance_id = CONN.get_all_spot_instance_requests(request_ids=[self.request_id])[0].instance_id
                self.instance_id = instance_id
            self.get_instance()

    def get_instance(self):
            reservations = CONN.get_all_reservations()
            for reservation in reservations:
                instances = reservation.instances
                for instance in instances:
                    if instance.id == self.instance_id:
                        self.public_dns_name =  instance.public_dns_name
                        self.instance_object = instance
                        return
    def status(self):
        return "request",self.request_id,"spot instance",self.instance_id,"with DNS",self.public_dns_name

    def terminate(self):
        print "terminating spot instance",self.instance_id,self.public_dns_name
        if self.instance_object:
            self.instance_object.terminate()