"""
文件存储工具模块

支持多种存储后端：
- 本地文件系统（开发环境）
- Cloudflare R2（生产环境，兼容 S3 API）
"""

import os
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from flask import current_app


class StorageBackend:
    """存储后端基类"""

    def upload_file(self, file_path, object_name):
        """上传文件"""
        raise NotImplementedError

    def delete_file(self, object_name):
        """删除文件"""
        raise NotImplementedError

    def get_url(self, object_name):
        """获取文件访问URL"""
        raise NotImplementedError

    def file_exists(self, object_name):
        """检查文件是否存在"""
        raise NotImplementedError


class LocalStorage(StorageBackend):
    """本地文件系统存储"""

    def __init__(self, upload_folder):
        self.upload_folder = upload_folder

    def upload_file(self, file_path, object_name=None):
        """本地存储实际上只是移动文件"""
        import shutil
        if object_name:
            dest_path = os.path.join(self.upload_folder, object_name)
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            shutil.copy2(file_path, dest_path)
            return True
        return False

    def delete_file(self, object_name):
        """删除文件"""
        file_path = os.path.join(self.upload_folder, object_name)
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False

    def get_url(self, object_name):
        """获取本地文件URL"""
        return f'/static/uploads/{object_name}'

    def file_exists(self, object_name):
        """检查文件是否存在"""
        file_path = os.path.join(self.upload_folder, object_name)
        return os.path.exists(file_path)


class R2Storage(StorageBackend):
    """Cloudflare R2 对象存储（S3兼容）"""

    def __init__(self, account_id, access_key, secret_key, bucket_name, public_domain=None):
        """
        初始化 R2 存储

        Args:
            account_id: Cloudflare 账户 ID
            access_key: R2 API 访问密钥
            secret_key: R2 API 密钥
            bucket_name: R2 存储桶名称
            public_domain: 自定义域名（可选，用于访问文件）
        """
        self.account_id = account_id
        self.bucket_name = bucket_name
        self.public_domain = public_domain

        # R2 endpoint
        self.endpoint = f'https://{account_id}.r2.cloudflarestorage.com'

        # 创建 S3 客户端
        self.s3_client = boto3.client(
            's3',
            endpoint_url=self.endpoint,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name='auto'
        )

    def upload_file(self, file_path, object_name, content_type=None):
        """上传文件到 R2"""
        try:
            extra_args = {}
            if content_type:
                extra_args['ContentType'] = content_type

            # 设置缓存策略
            extra_args['CacheControl'] = 'public, max-age=31536000'  # 1年

            self.s3_client.upload_file(
                file_path,
                self.bucket_name,
                object_name,
                ExtraArgs=extra_args
            )
            return True
        except (ClientError, NoCredentialsError) as e:
            current_app.logger.error(f'R2 上传失败: {str(e)}')
            return False

    def upload_fileobj(self, file_obj, object_name, content_type=None):
        """上传文件对象到 R2"""
        try:
            extra_args = {}
            if content_type:
                extra_args['ContentType'] = content_type

            # 设置缓存策略
            extra_args['CacheControl'] = 'public, max-age=31536000'  # 1年

            self.s3_client.upload_fileobj(
                file_obj,
                self.bucket_name,
                object_name,
                ExtraArgs=extra_args
            )
            return True
        except (ClientError, NoCredentialsError) as e:
            current_app.logger.error(f'R2 上传失败: {str(e)}')
            return False

    def delete_file(self, object_name):
        """删除 R2 中的文件"""
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=object_name
            )
            return True
        except ClientError as e:
            current_app.logger.error(f'R2 删除失败: {str(e)}')
            return False

    def get_url(self, object_name):
        """获取 R2 文件访问 URL"""
        if self.public_domain:
            # 使用自定义域名
            return f'https://{self.public_domain}/{object_name}'
        else:
            # 使用 R2 默认公开 URL
            return f'https://pub-{self.account_id}.r2.dev/{object_name}'

    def file_exists(self, object_name):
        """检查文件是否存在"""
        try:
            self.s3_client.head_object(
                Bucket=self.bucket_name,
                Key=object_name
            )
            return True
        except ClientError:
            return False


# 全局存储实例
_storage = None


def get_storage():
    """获取当前配置的存储后端"""
    global _storage

    if _storage is not None:
        return _storage

    # 检查是否配置了 R2
    r2_account_id = os.environ.get('R2_ACCOUNT_ID')
    r2_access_key = os.environ.get('R2_ACCESS_KEY')
    r2_secret_key = os.environ.get('R2_SECRET_KEY')
    r2_bucket_name = os.environ.get('R2_BUCKET_NAME')
    r2_public_domain = os.environ.get('R2_PUBLIC_DOMAIN')

    # 如果配置了 R2，使用 R2 存储
    if all([r2_account_id, r2_access_key, r2_secret_key, r2_bucket_name]):
        _storage = R2Storage(
            account_id=r2_account_id,
            access_key=r2_access_key,
            secret_key=r2_secret_key,
            bucket_name=r2_bucket_name,
            public_domain=r2_public_domain
        )
        current_app.logger.info('使用 Cloudflare R2 存储')
        return _storage

    # 否则使用本地存储
    from flask import current_app
    upload_folder = current_app.config['UPLOAD_FOLDER']
    # 获取相对路径用于 URL 生成
    static_uploads = upload_folder.split('static/uploads/')[-1] if 'static/uploads/' in upload_folder else 'covers'
    _storage = LocalStorage(upload_folder)
    current_app.logger.info(f'使用本地存储: {upload_folder}')
    return _storage


def reset_storage():
    """重置存储实例（用于测试或配置更改）"""
    global _storage
    _storage = None
