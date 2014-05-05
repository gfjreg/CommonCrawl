__author__ = 'aub3'
# Put AWS credentials in /etc/boto.cfg these will be copied to the spot instance

key_filename = '/users/aub3/.ssh/cornellmacos.pem' # please replace this with path to your pem

price = 0.30 # 30 cents per hour slightly above the reserve price of the r3.8xlarge instance on the spot market
instance_type = 'r3.8xlarge'
image_id = 'ami-978d91fe' # default AMI for Amazon Linux HVM
key_name = 'cornellmacos' # replace with name of your configured key-pair

EC2_Tag = "cc_amazon_text"
JOB_QUEUE = 'cc_amazon_text' # SQS queue name
OUTPUT_S3_BUCKET = 'cc_amazon_text' # S3 bucket