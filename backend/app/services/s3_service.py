import boto3
import logging
from botocore.exceptions import ClientError

from app.config import settings

logger = logging.getLogger(__name__)

class S3Service:
    def __init__(self):
        self.bucket_name = settings.S3_BUCKET_NAME
        self.mock_mode = settings.MOCK_MODE or not (
            settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY and self.bucket_name
        )
        self.s3_client = None

        if not self.mock_mode:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_REGION
            )
    
    def generate_presigned_url(self, object_key: str, content_type: str = "image/jpeg", expires_in: int = 3600) -> str:
        """Generate presigned URL for direct browser upload."""
        if self.mock_mode:
            return f"https://mock-s3.local/{self.bucket_name}/{object_key}?expires_in={expires_in}"

        try:
            url = self.s3_client.generate_presigned_url(
                'put_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': object_key,
                    'ContentType': content_type
                },
                ExpiresIn=expires_in
            )
            return url
        except ClientError as e:
            logger.error(f"Failed to generate presigned URL: {e}")
            raise
    
    def get_object_url(self, object_key: str) -> str:
        """Get public URL for object."""
        return f"https://{self.bucket_name}.s3.{settings.AWS_REGION}.amazonaws.com/{object_key}"
    
    def delete_object(self, object_key: str) -> bool:
        """Delete object from S3."""
        if self.mock_mode:
            return True

        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=object_key)
            return True
        except ClientError as e:
            logger.error(f"Failed to delete object: {e}")
            return False
