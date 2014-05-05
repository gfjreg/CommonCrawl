__author__ = 'aub3'
# Put AWS credentials in /etc/boto.cfg these will be copied to the spot instance

key_filename = '/users/aub3/.ssh/cornellmacos.pem' # please replace

price = 0.30 # slightly above the reserve price of the r3.8xlarge instance
instance_type = 'r3.8xlarge'
image_id = 'ami-978d91fe' # default AMI for Amazin Linux HVM
key_name = 'cornellmacos' # replace with name of your configured key-pair




JOB_QUEUE = 'cc_amazon_text' # SQS queue name
OUTPUT_S3_BUCKET = 'cc_amazon_text' # S3 bucket