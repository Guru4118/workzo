from minio import Minio
import os
from datetime import datetime

minio_client = Minio(
    endpoint=os.getenv("MINIO_ENDPOINT", "localhost:9000"),
    access_key=os.getenv("MINIO_ACCESS_KEY"),
    secret_key=os.getenv("MINIO_SECRET_KEY"),
    secure=False,  # True for TLS
)

def store_html(bucket, key, html_bytes):
    if not minio_client.bucket_exists(bucket):
        minio_client.make_bucket(bucket)
    minio_client.put_object(bucket, key, data=html_bytes, length=len(html_bytes))
    return f"{os.getenv('MINIO_ENDPOINT')}/{bucket}/{key}"

# usage inside scraper before sending:
# raw_html = page.content()
# key = f"snapshots/{source}/{job_hash}.html"
# url = store_html("job-snapshots", key, raw_html.encode("utf-8"))
# job['raw_snapshot_url'] = url
