This is a multi-tier photo application that allows users to store and view photos.

It consists of a client and web service, the latter of which interacts with AWS S3 and RDS services. The client can also be configured to interact with EC2 if desired.

Replace the AWS RDS credentials and the S3 bucket, region, and access keys in `server/photoapp-config` before using.