import boto3
from botocore.exceptions import NoCredentialsError, ClientError
from werkzeug.utils import secure_filename
from .logger import logger

def create_s3_object(access_key, secret_key):
    try:
        s3 = boto3.client(
            's3',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key
        )
        return s3
    except NoCredentialsError:
        logger.error("AWS credentials not provided or incorrect")
        return None


def upload_file_to_s3(file, bucket_name, s3_obj, s3_location):
    try:
        filename = secure_filename(file.filename)
        s3_obj.upload_fileobj(
            file,
            bucket_name,
            filename,
            ExtraArgs={
                "ContentType": file.content_type
            }
        )
    except ClientError as e:
        logger.error(f"Failed to upload file to S3: {e}")
        return None

    return f"{s3_location}{filename}"


def allowed_file(filename):
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


