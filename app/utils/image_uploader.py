"""
Markdown 图片处理工具

自动识别 Markdown 中的本地图片路径并上传到项目
"""

import os
import re
import shutil
import uuid
from datetime import datetime
from PIL import Image


def extract_local_images(markdown_content):
    """
    从 Markdown 内容中提取本地图片路径

    支持的格式：
    - ![alt](C:\\path\\to\\image.jpg)
    - ![alt](D:/path/to/image.jpg)
    - ![alt](file:///path/to/image.jpg)
    - <img src="C:\\path\\to\\image.jpg">

    Args:
        markdown_content: Markdown 文本内容

    Returns:
        list: 本地图片路径列表
    """
    local_images = []

    # 匹配 Markdown 图片语法 ![alt](path)
    md_image_pattern = r'!\[.*?\]\((.*?)\)'
    # 匹配 HTML img 标签 <img src="path">
    html_img_pattern = r'<img\s+src=["\']([^"\']+)["\']'

    patterns = [md_image_pattern, html_img_pattern]

    for pattern in patterns:
        matches = re.findall(pattern, markdown_content)
        for match in matches:
            # 检查是否是本地路径
            if is_local_path(match):
                local_images.append(match)

    return list(set(local_images))  # 去重


def is_local_path(path):
    """
    判断路径是否是本地文件路径

    Args:
        path: 文件路径

    Returns:
        bool: 是否是本地路径
    """
    path = path.strip()

    # Windows 绝对路径: C:\, D:\ 等
    if re.match(r'^[A-Za-z]:[\\/]', path):
        return True

    # Windows UNC 路径: \\server\share
    if path.startswith('\\\\'):
        return True

    # file:// 协议
    if path.startswith('file://'):
        return True

    # 相对路径且文件存在
    if not path.startswith(('http://', 'https://', '/')):
        # 检查是否是相对路径且文件存在
        if os.path.exists(path):
            return True

    return False


def upload_local_image(image_path, upload_dir):
    """
    上传单个本地图片到项目目录

    Args:
        image_path: 本地图片路径
        upload_dir: 上传目录

    Returns:
        tuple: (success: bool, new_path: str, error: str)
    """
    try:
        # 规范化路径
        image_path = os.path.normpath(image_path)

        # 检查文件是否存在
        if not os.path.exists(image_path):
            return False, None, f"文件不存在: {image_path}"

        # 检查是否是图片文件
        try:
            with Image.open(image_path) as img:
                img.verify()
        except Exception as e:
            return False, None, f"不是有效的图片文件: {str(e)}"

        # 获取文件扩展名
        _, ext = os.path.splitext(image_path)
        ext = ext.lower()

        # 确保上传目录存在
        os.makedirs(upload_dir, exist_ok=True)

        # 生成唯一文件名
        timestamp = int(datetime.now().timestamp())
        unique_id = uuid.uuid4().hex[:8]
        new_filename = f"img_{timestamp}_{unique_id}{ext}"
        new_path = os.path.join(upload_dir, new_filename)

        # 复制文件
        shutil.copy2(image_path, new_path)

        # 返回 web 路径
        web_path = f"/static/uploads/covers/{new_filename}"

        return True, web_path, None

    except Exception as e:
        return False, None, str(e)


def process_markdown_images(markdown_content, upload_dir=None):
    """
    处理 Markdown 中的本地图片，自动上传并更新路径

    Args:
        markdown_content: Markdown 文本内容
        upload_dir: 上传目录，默认为 app/static/uploads/covers

    Returns:
        tuple: (processed_content: str, upload_results: dict)
               upload_results 包含:
               - uploaded: 成功上传的图片数
               - failed: 失败的图片数
               - details: 详细信息列表
    """
    if upload_dir is None:
        # 获取默认上传目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        upload_dir = os.path.join(os.path.dirname(current_dir), 'static', 'uploads', 'covers')

    # 提取本地图片路径
    local_images = extract_local_images(markdown_content)

    if not local_images:
        return markdown_content, {
            'uploaded': 0,
            'failed': 0,
            'details': []
        }

    # 上传图片并记录映射关系
    path_mapping = {}
    upload_results = {
        'uploaded': 0,
        'failed': 0,
        'details': []
    }

    for old_path in local_images:
        success, new_path, error = upload_local_image(old_path, upload_dir)

        if success:
            path_mapping[old_path] = new_path
            upload_results['uploaded'] += 1
            upload_results['details'].append({
                'old_path': old_path,
                'new_path': new_path,
                'status': 'success'
            })
        else:
            upload_results['failed'] += 1
            upload_results['details'].append({
                'old_path': old_path,
                'error': error,
                'status': 'failed'
            })

    # 替换 Markdown 中的图片路径
    processed_content = markdown_content

    # 替换 Markdown 图片语法
    for old_path, new_path in path_mapping.items():
        # 转义正则特殊字符
        escaped_old = re.escape(old_path)
        # 替换 ![alt](old_path) 为 ![alt](new_path)
        processed_content = re.sub(
            rf'!\[(.*?)\]\({escaped_old}\)',
            rf'![\1]({new_path})',
            processed_content
        )
        # 替换 HTML img 标签
        processed_content = re.sub(
            rf'<img\s+src=["\']{escaped_old}["\']([^>]*)>',
            rf'<img src="{new_path}"\1>',
            processed_content
        )

    return processed_content, upload_results


# ==================== 便捷函数 ====================

def auto_upload_images(content):
    """
    自动上传 Markdown 内容中的本地图片（便捷函数）

    Args:
        content: Markdown 文本内容

    Returns:
        tuple: (processed_content, results)
    """
    return process_markdown_images(content)


if __name__ == '__main__':
    # 测试代码
    test_markdown = """
# 测试文档

![本地图片](C:\\Users\\Admin\\Desktop\\test.jpg)

![网络图片](https://example.com/image.jpg)

<img src="D:/images/photo.png" />
"""

    processed, results = process_markdown_images(test_markdown)
    print(f"上传: {results['uploaded']}, 失败: {results['failed']}")
    print(processed)
