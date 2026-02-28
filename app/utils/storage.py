"""
文件存储工具模块

支持多种存储后端：
- 本地文件系统（开发环境）
- GitHub 仓库（生产环境，作为图床）
"""

import os
import base64
import logging
import requests

# 配置日志
logger = logging.getLogger(__name__)


class StorageBackend:
    """存储后端基类"""

    def upload_file(self, file_path, object_name):
        """上传文件"""
        raise NotImplementedError

    def upload_fileobj(self, file_obj, object_name):
        """上传文件对象"""
        raise NotImplementedError

    def delete_file(self, object_name):
        """删除文件"""
        raise NotImplementedError

    def get_url(self, object_name):
        """获取文件访问URL"""
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

    def upload_fileobj(self, file_obj, object_name):
        """上传文件对象"""
        import shutil
        dest_path = os.path.join(self.upload_folder, object_name)
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        with open(dest_path, 'wb') as f:
            shutil.copyfileobj(file_obj, f)
        return True

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


class GitHubStorage(StorageBackend):
    """GitHub 仓库作为图床"""

    def __init__(self, token, repo, branch='main', path='images'):
        """
        初始化 GitHub 存储

        Args:
            token: GitHub Personal Access Token
            repo: 仓库格式 "username/repo-name"
            branch: 分支名（默认 main）
            path: 图片存储路径（默认 images）
        """
        self.token = token
        self.repo = repo
        self.branch = branch
        self.path = path

        # GitHub API 配置
        self.api_base = 'https://api.github.com'
        self.raw_base = 'https://raw.githubusercontent.com'

        # 请求头
        self.headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json'
        }

    def upload_fileobj(self, file_obj, object_name):
        """上传文件对象到 GitHub"""
        try:
            # 读取文件内容
            file_content = file_obj.read()
            # 转换为 base64
            b64_content = base64.b64encode(file_content).decode('utf-8')

            # 构建文件路径
            file_path = f'{self.path}/{object_name}'

            # 构造 API 请求
            url = f'{self.api_base}/repos/{self.repo}/contents/{file_path}'

            # 首先检查文件是否存在
            existing_file = None
            try:
                response = requests.get(url, headers=self.headers, timeout=10)
                if response.status_code == 200:
                    existing_file = response.json()
            except:
                pass

            # 准备请求数据
            data = {
                'message': f'Upload image: {object_name}',
                'content': b64_content,
                'branch': self.branch
            }

            # 如果文件已存在，需要提供 sha
            if existing_file:
                data['sha'] = existing_file['sha']

            # 上传文件
            response = requests.put(url, headers=self.headers, json=data, timeout=30)

            if response.status_code in [201, 200]:
                logger.info(f'图片已上传到 GitHub: {object_name}')
                return True
            else:
                logger.error(f'GitHub 上传失败: {response.text}')
                return False

        except Exception as e:
            logger.error(f'GitHub 上传异常: {str(e)}')
            return False

    def upload_file(self, file_path, object_name):
        """上传文件到 GitHub"""
        try:
            with open(file_path, 'rb') as f:
                return self.upload_fileobj(f, object_name)
        except Exception as e:
            logger.error(f'读取文件失败: {str(e)}')
            return False

    def delete_file(self, object_name):
        """删除 GitHub 中的文件"""
        try:
            file_path = f'{self.path}/{object_name}'
            url = f'{self.api_base}/repos/{self.repo}/contents/{file_path}'

            # 获取文件信息
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code != 200:
                return False

            file_data = response.json()
            sha = file_data['sha']

            # 删除文件
            data = {
                'message': f'Delete image: {object_name}',
                'sha': sha,
                'branch': self.branch
            }

            response = requests.delete(url, headers=self.headers, json=data, timeout=30)
            return response.status_code == 200

        except Exception as e:
            logger.error(f'GitHub 删除失败: {str(e)}')
            return False

    def get_url(self, object_name):
        """获取 GitHub 文件访问 URL"""
        # 使用 jsDelivr CDN 加速，国内可直接访问
        # 格式: https://cdn.jsdelivr.net/gh/user/repo@branch/path/file
        return f'https://cdn.jsdelivr.net/gh/{self.repo}@{self.branch}/{self.path}/{object_name}'


# 全局存储实例
_storage = None


def get_storage():
    """获取当前配置的存储后端"""
    global _storage

    if _storage is not None:
        return _storage

    # 检查是否配置了 GitHub 存储
    github_token = os.environ.get('GITHUB_TOKEN')
    github_repo = os.environ.get('GITHUB_REPO')
    github_branch = os.environ.get('GITHUB_BRANCH', 'main')
    github_path = os.environ.get('GITHUB_PATH', 'images')

    # 如果配置了 GitHub，使用 GitHub 存储
    if github_token and github_repo:
        _storage = GitHubStorage(
            token=github_token,
            repo=github_repo,
            branch=github_branch,
            path=github_path
        )
        logger.info(f'使用 GitHub 图床: {github_repo}/{github_path}')
        return _storage

    # 否则使用本地存储
    from flask import current_app
    upload_folder = current_app.config['UPLOAD_FOLDER']
    _storage = LocalStorage(upload_folder)
    logger.info(f'使用本地存储: {upload_folder}')
    return _storage


def reset_storage():
    """重置存储实例（用于测试或配置更改）"""
    global _storage
    _storage = None
