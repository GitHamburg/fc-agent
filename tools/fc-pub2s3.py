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

def s3uploads(upload_dir, pattern='.*'):
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
            else:
                print('ingore {} already exists in cos'.format(absf))

    pool.wait_completion()
    result = pool.get_result()
    if not result.get('success_all'):
        print("Not all files upload sucessed. you should retry")

def s3upload_file(uploadf):
    if not os.path.exists(uploadf) or not os.path.isfile(uploadf):
        print('file not exists or not regular file')
        return

    skey = os.path.basename(uploadf)

    # 判断COS上文件是否存在
    exists = False
    try:
        response = client.head_object(Bucket=bucket, Key=skey)
        exists = True
    except CosServiceError as e:
        if e.get_status_code() == 404:
            exists = False
        else:
            print("error happened when uploading {}".format(e))

    if not exists:
        print("uploading {}...".format(uploadf))
        try:
            client.upload_file(bucket, skey, uploadf)
        except CosServiceError as e:
            print("error happened when uploading {}".format(e))
    else:
        print('ingore {} already exists in cos'.format(uploadf))

def s3list(prefix=""):
    print("---\nthe latest file lists in cos:")
    response = client.list_objects(Bucket=bucket, Prefix=prefix)
    if response.get('Contents'):
        print("    - key\tsize\tlast-modified")
        for content in response['Contents']:
            print("    - {}\t{}\t{}".format(content.get('Key'),
                content.get('Size'), content.get('LastModified')))


def s3remove_file(skey):
    try:
        client.delete_object(Bucket=bucket, Key=skey)
    except CosServiceError as e:
        print("error happened when uploading {}".format(e))

def help():
    print('  {} upload dir/file'.format(sys.argv[0]))
    print('  {} list [prefix]'.format(sys.argv[0]))
    print('  {} rm objectkey'.format(sys.argv[0]))

if __name__ == "__main__":
    try:
        action = sys.argv[1]
    except IndexError:
        help()
        sys.exit()

    if action == "upload":
        try:
            uploads = sys.argv[2]
            if os.path.isfile(uploads):
                s3upload_file(uploads)
            elif os.path.isdir(uploads):
                s3uploads(uploads)
            else:
                print('invalid dir/file to upload')
        except IndexError:
            print("empty dir/file to upload")
    elif action == "list":
        try:
            prefix = sys.argv[2]
        except IndexError:
            prefix = ""
        s3list(prefix)
    elif action == "rm":
        try:
            skey = sys.argv[2]
        except IndexError:
            print('s3 object key to be delete should not empty')
            sys.exit()

        confirm = input("confirm to delete {} [y | yes]?".format(skey))
        if confirm.lower() in ["y","yes"]:
            s3remove_file(skey)
        else:
            sys.exit()
    else:
        print('not supported action')
        help()
        sys.exit()
