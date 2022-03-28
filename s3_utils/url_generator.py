import boto3


def s3_url_generator(client, bucket, file_on_s3, expiration=7200):
    params = {
                'Bucket': bucket,
                'Key': file_on_s3
            }
    try:
        url = client.generate_presigned_url('get_object', Params=params, 
            ExpiresIn=expiration)
    except Exception as e:
        return None
    
    return url
