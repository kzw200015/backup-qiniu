#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from qiniu import Auth, put_file, etag, BucketManager
import qiniu.config
from datetime import datetime, timedelta
import os

### 配置部分
access_key = 'Access_Key' #AK，在七牛云的后台查看
secret_key = 'Secret_Key' #SK，同上
bucket_name = 'Bucket_Name' #空间名称
backup_name = 'website-backup' #备份的名称
backup_dir = ['typecho','wordpress'] #你要备份的目录，用单引号包裹，不同项之间用逗号隔开
backup_pre_dir = '/home/wwwroot/' #备份目录的上级目录，结尾不要漏掉斜杠
backup_database = ['typecho','wordpress'] #备份的数据库名，用单引号包裹，不同项之间用逗号隔开
mysql_user = 'root' #数据库用户名
mysql_passwd = '' #数据库密码
### 配置部分结束

auth = Auth(access_key, secret_key)
old_key = backup_name + '-' + (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d') + '.zip'
key = backup_name + '-' + (datetime.now()).strftime('%Y-%m-%d') + '.zip'
token = auth.upload_token(bucket_name, key, 3600)
localfile = backup_pre_dir + key
cwd = os.getcwd()
bucket = BucketManager(auth)

print('正在打包')
os.chdir(backup_pre_dir)
for each_dir in backup_dir:
    os.system('zip -q -r ' + each_dir + '.zip ' + each_dir)
for each_database in backup_database:
    os.system('mysqldump -u' + mysql_user + ' -p' + mysql_passwd + ' ' + each_database + ' > ' + each_database + '.sql')

os.system('zip -q -r ' + key + ' *.zip *.sql')

print('正在上传')
ret, info = put_file(token, key, localfile)
assert ret['key'] == key
assert ret['hash'] == etag(localfile)

print('正在清理临时文件')
os.system('rm -rf *.zip *.sql')

print('正在删除旧备份')
bucket.delete(bucket_name, old_key)

os.chdir(cwd)
print('操作完成')