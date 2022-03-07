#!/usr/bin/python3
# -*- coding=utf-8
#
# pip install -U cos-python-sdk-v5
#
from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
from qcloud_cos import CosServiceError
from qcloud_cos import CosClientError
from qcloud_cos.cos_threadpool import SimpleThreadPool

import sys
import os
import re

secret_id = os.getenv('FC_COS_SECRETID') or ''
secret_key = os.getenv('FC_COS_SECRETKEY') or ''
region = os.getenv('FC_COS_REGION') or 'ap-nanjing'
bucket = os.getenv('FC_COS_BUCKET') or 'fcpub-1301667576'

config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key)
client = CosS3Client(config)

def s3upload(upload_dir, pattern='^fc-[a-zA-Z0-9\._-]*.zip$'):
    uploads = os.walk(upload_dir)
    pat = re.compile(pattern)

    pool = SimpleThreadPool()
    for path, dir_list, file_list in uploads:
        for file_name in file_list:
            if not pat.match(file_name):
                print("ignore {}".format(file_name))
                continue

            absf = os.path.join(path, file_name)
            objkey = file_name

            # 判断COS上文件是否存在
            exists = False
            try:
                response = client.head_object(Bucket=bucket, Key=objkey)
                exists = True
            except CosServiceError as e:
                if e.get_status_code() == 404:
                    exists = False
                else:
                    print("Error happened {}".format(e))

            if not exists:
                print("upload {}...".format(absf))
                pool.add_task(client.upload_file, bucket, objkey, absf)

    pool.wait_completion()
    result = pool.get_result()
    if not result['success_all']:
        print("Not all files upload sucessed. you should retry")

def s3list(prefix=""):
    print("\n-----\nthe latest file lists in cos:")
    response = client.list_objects(Bucket=bucket, Prefix=prefix)
    if response['Contents']:
        for content in response['Contents']:
            print("    - {}".format(content['Key']))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('empty upload dir')
        sys.exit()
    else:
        upload_dir = sys.argv[1] 

    s3upload(upload_dir, ".*.txt$")
    s3list()
