Common Crawl Dev
=================
A simple app for mining common crawl data

Author
--------
Akshay Uday Bhat (www.akshaybhat.com)


Description:
--------
This repo contains code for accessing Common Crawl crawls (2013 & later) & code for launching spot instances for analyzing the crawl data.
The code follows most of the best practices, such as:

1. An SQS queue is used to track progress of the job.

2. Output is stored in an S3 Bucket with reduced redundancy to reduce costs

3. Permissions are passed to EC2 instances via IAM roles and instance profiles. Only required services S3 & SQS are authorized.

4. Code is stored in an S3 bucket and is downloaded by the spot instance when instance is allocated via user_data script.

5. Fabric is used to run tasks to get information, execute code and terminate instances.


The current worker.py implements a simple function which stores count of urls and domains with at least 10 urls in the file.
The function and configuration can be easily modified to support more complex analysis.

Dependancies
--------
- Boto (latest)
- Fabric (1.8.1)
- Flask (Optional)



Configuration
--------

- Access & Security
- Put boto configuration in /etc/boto.cfg on your local machine, note that this information is never sent to EC2 machines
- key_filename = Path to your private key file
- IAM_ROLE = "ccSpot_role" # Role name, no need to change
- IAM_PROFILE = "ccSpot_profile" # Profile name, no need to change
- IAM_POLICY_NAME = "ccSpt_policy" # Policy name, no need to change
- IAM_POLICY = # Policy, no need to change unless you are accessing other services such as SNS etc.

- Instance Configuration
- price = price in dollars for a spot instance
- instance_type =
- image_id = # Amazon Machine Image (AMI) ID
- key_name = name of your configured key-pair, should be same key as the pem file above
- NUM_WORKERS = Number of worker processes per machine depends on the instance type & memory foot print
- VISIBILITY_TIMEOUT = Seconds during which a worker process has time to process the message, this value should be the maximum time a worker process will take to process a single process
- MAX_TIME_MINS = 230 # maxiumum amount of time the instance should run 60 * 3 + 50 mins  = 230 minutes (This limits the cost in case you forget to terminate the instance)

- Job Configuration
- EC2_Tag = "cc_wat_13_2"
- JOB_QUEUE =  SQS queue name
- OUTPUT_S3_BUCKET = S3 bucket
- CODE_BUCKET = bucket used to store code & configuration make sure this is different from output bucket above
- CODE_KEY =  key for storing code which will be downloaded by user-data script
- FILE_TYPE = "wat" # Type of files you wish to process choose from {"wat","wet","text","warc"}
- CRAWL_ID = crawl id choose from  { '2013_1','2013_2','2014_1',"ALL"}
- USED_DATA = script run by the spot instance the "first time" it is booted up


Instructions / Tasks
--------
1. AWS credentials should be stored in /etc/boto.cfg, the credentials are not transferred
2. To install library locally run "fab update_lib"
3. To set up job run "fab setup_job", this will create IAM roles, S3 output bucket and SQS queue.
4. To test worker script run "fab test_worker"
5. To save code to S3 run "fab push_code"
6. To request spot instances run "fab request_spot_instance" the spot instance once allocated will start running code automatically.
7. To list current spot instances run "fab ls_instances"
8. To terminate all instances run "fab terminate_instances" (NOTE its important that you manually terminate all instances.)

Optional
--------
* Use "fab ls_bucket" to check status of the output bucket and to download one randomly selected key to temp.json.
* Use "fab rm_bucket:bucket_name" to delete a bucket and all keys inside it.
* Use "fab run_server" to run a local server, the local server allows you to monitor progress and explore results.


Files
--------
* libs/setup.py

* libs/cclib/commoncrawl13.py

* libs/cclib/data/*.gz pickle files containing list of keys/files in each crawl

* config.py Contains configuration for launching job, identifiers for bucket, queue etc.

* worker.py Code executed on each file in the crawl

* fabfile.py Contains tasks for setting up, running, monitoring and terminating jobs.

* spotinstance.py A small class to keep track of spot instance requests.

* filequeue.py A small class to keep track of files in SQS queue.

* example.json Example of output stored in the bucket from one file, using current worker.py

* server.py A flask server to explore results and to keep track of instances, queue positions.
