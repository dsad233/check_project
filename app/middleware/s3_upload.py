import io
import boto3
s3_client = boto3.client(
    "s3",
    aws_access_key_id="aws-access-key",  # 본인 소유의 키를 입력
    aws_secret_access_key="aws-secret-key",  # 본인 소유의 키를 입력
    region_name="ap-northeast-2",
)
def upload_to_s3(file: io.BytesIO, bucket_name: str, file_name: str) -> None:
    s3_client.upload_fileobj(
        file,
        bucket_name,
        file_name,
        ExtraArgs={"ContentType": "image/jpeg"},
    )