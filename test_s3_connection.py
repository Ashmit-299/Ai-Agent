#!/usr/bin/env python3
"""
Test S3 Connection Script
Run this after configuring your AWS credentials
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_s3_connection():
    """Test S3 connection with configured credentials"""
    
    # Check if credentials are configured
    access_key = os.getenv('AWS_ACCESS_KEY_ID')
    secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    bucket_name = os.getenv('S3_BUCKET_NAME')
    region = os.getenv('S3_REGION')
    
    print("🔍 Checking S3 Configuration...")
    print(f"Access Key: {'✅ Set' if access_key and access_key != 'YOUR_AWS_ACCESS_KEY_HERE' else '❌ Not configured'}")
    print(f"Secret Key: {'✅ Set' if secret_key and secret_key != 'YOUR_AWS_SECRET_KEY_HERE' else '❌ Not configured'}")
    print(f"Bucket Name: {bucket_name}")
    print(f"Region: {region}")
    
    if not access_key or access_key == 'YOUR_AWS_ACCESS_KEY_HERE':
        print("\n❌ Please update AWS_ACCESS_KEY_ID in .env file")
        return False
        
    if not secret_key or secret_key == 'YOUR_AWS_SECRET_KEY_HERE':
        print("\n❌ Please update AWS_SECRET_ACCESS_KEY in .env file")
        return False
    
    try:
        import boto3
        from botocore.exceptions import ClientError, NoCredentialsError
        
        print("\n🔗 Testing S3 Connection...")
        
        # Create S3 client
        s3_client = boto3.client(
            's3',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region
        )
        
        # Test 1: List buckets (verify credentials)
        print("1. Testing credentials...")
        response = s3_client.list_buckets()
        print("✅ Credentials valid")
        
        # Test 2: Check if bucket exists
        print(f"2. Checking bucket '{bucket_name}'...")
        try:
            s3_client.head_bucket(Bucket=bucket_name)
            print("✅ Bucket exists and accessible")
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                print(f"❌ Bucket '{bucket_name}' not found")
                print(f"💡 Create bucket at: https://s3.console.aws.amazon.com/s3/bucket/create")
                return False
            elif error_code == '403':
                print(f"❌ Access denied to bucket '{bucket_name}'")
                print("💡 Check IAM permissions")
                return False
            else:
                print(f"❌ Error accessing bucket: {e}")
                return False
        
        # Test 3: Test upload/download permissions
        print("3. Testing upload permissions...")
        test_key = "test-connection.txt"
        test_content = "S3 connection test successful!"
        
        try:
            # Upload test file
            s3_client.put_object(
                Bucket=bucket_name,
                Key=test_key,
                Body=test_content.encode('utf-8'),
                ContentType='text/plain'
            )
            print("✅ Upload successful")
            
            # Download test file
            response = s3_client.get_object(Bucket=bucket_name, Key=test_key)
            downloaded_content = response['Body'].read().decode('utf-8')
            
            if downloaded_content == test_content:
                print("✅ Download successful")
            else:
                print("❌ Download content mismatch")
                return False
            
            # Clean up test file
            s3_client.delete_object(Bucket=bucket_name, Key=test_key)
            print("✅ Cleanup successful")
            
        except ClientError as e:
            print(f"❌ Upload/Download test failed: {e}")
            return False
        
        print("\n🎉 S3 Connection Test PASSED!")
        print("Your S3 bucket is ready for the AI Agent")
        return True
        
    except NoCredentialsError:
        print("❌ AWS credentials not found")
        return False
    except ImportError:
        print("❌ boto3 not installed. Run: pip install boto3")
        return False
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False

def test_enhanced_bucket():
    """Test the enhanced bucket system"""
    try:
        print("\n🔍 Testing Enhanced Bucket System...")
        from core.bhiv_bucket_enhanced import enhanced_bucket
        
        if enhanced_bucket.s3_adapter:
            print("✅ S3 adapter initialized successfully")
            
            # Test presigned URL generation
            test_url = enhanced_bucket.generate_presigned_upload_url("test-file.txt", "text/plain")
            if test_url:
                print("✅ Presigned URL generation working")
            else:
                print("❌ Presigned URL generation failed")
                
        else:
            print("❌ S3 adapter not initialized - check credentials")
            
    except Exception as e:
        print(f"❌ Enhanced bucket test failed: {e}")

if __name__ == "__main__":
    print("🚀 AI Agent S3 Connection Test")
    print("=" * 40)
    
    success = test_s3_connection()
    
    if success:
        test_enhanced_bucket()
        print("\n✅ All tests passed! S3 is ready.")
    else:
        print("\n❌ S3 setup incomplete. Please fix the issues above.")
        print("\n📋 Next Steps:")
        print("1. Update .env file with correct AWS credentials")
        print("2. Create S3 bucket if it doesn't exist")
        print("3. Verify IAM permissions")
        print("4. Run this test again")