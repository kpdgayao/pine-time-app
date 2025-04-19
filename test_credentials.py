import boto3
import sys

def test_aws_credentials(access_key, secret_key, region='ap-southeast-1'):
    try:
        print(f"[DEBUG] Starting AWS credential test for region: {region}")
        print(f"[DEBUG] Access Key: {access_key[:4]}... (truncated)")
        print(f"[DEBUG] Creating boto3 session...")
        session = boto3.Session(
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region
        )
        print(f"[DEBUG] boto3 session created: {session}")

        # Test Elastic Beanstalk permissions
        print("[DEBUG] Creating Elastic Beanstalk client...")
        eb_client = session.client('elasticbeanstalk')
        print("Testing Elastic Beanstalk permissions...")
        applications = eb_client.describe_applications()
        print(f"[DEBUG] Elastic Beanstalk describe_applications response: {applications}")
        print(f"Successfully connected to Elastic Beanstalk!")
        print(f"Found {len(applications['Applications'])} applications")
        
        # Test S3 permissions (needed for EB deployments)
        print("[DEBUG] Creating S3 client...")
        s3_client = session.client('s3')
        print("\nTesting S3 permissions...")
        buckets = s3_client.list_buckets()
        print(f"[DEBUG] S3 list_buckets response: {buckets}")
        print(f"Successfully connected to S3!")
        print(f"Found {len(buckets['Buckets'])} buckets")
        
        # Test EC2 permissions (needed for EB environment management)
        print("[DEBUG] Creating EC2 client...")
        ec2_client = session.client('ec2')
        print("\nTesting EC2 permissions...")
        vpcs = ec2_client.describe_vpcs()
        print(f"[DEBUG] EC2 describe_vpcs response: {vpcs}")
        print(f"Successfully connected to EC2!")
        print(f"Found {len(vpcs['Vpcs'])} VPCs")
        
        print("\n✅ All permission tests passed! Your IAM user has the necessary permissions.")
        return True
    
    except Exception as e:
        print(f"[DEBUG] Exception occurred: {repr(e)}")
        print(f"\n❌ Error testing AWS credentials: {str(e)}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python test_credentials.py <access_key_id> <secret_access_key> [region]")
        sys.exit(1)
    
    access_key = sys.argv[1]
    secret_key = sys.argv[2]
    region = sys.argv[3] if len(sys.argv) > 3 else 'ap-southeast-1'
    
    test_aws_credentials(access_key, secret_key, region)