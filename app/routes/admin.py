"""
博客管理后台路由模块

该模块处理博客管理功能，包括：
- 仪表板首页
- 分类管理（创建、删除）
- 标签管理（创建、删除）
- 文章管理（创建、编辑、删除）
- Markdown 文件导入（单个和批量）
- 图片上传处理
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from sqlalchemy import func
import os
import re
from datetime import datetime
from app.models.post import Post, Category, Tag
from app.models.user import User
from app.models.friend_link import FriendLink
from app.models.post_bookmark import PostBookmark
from app import db, cache
from app.utils.storage import get_storage, reset_storage
from app.routes.main import get_hot_posts, get_hot_tags, get_total_views
from PIL import Image
from io import BytesIO

bp = Blueprint('admin', __name__, url_prefix='/admin')

# 文件编码支持列表（按优先级排序）
SUPPORTED_ENCODINGS = ['utf-8', 'utf-8-sig', 'gbk', 'gb2312', 'iso-8859-1']

# 允许的图片扩展名
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# 最大图片尺寸（宽 x 高）
MAX_IMAGE_SIZE = (3000, 3000)


def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS


def generate_unique_filename(filename):
    """生成唯一的文件名（使用时间戳）"""
    name, ext = os.path.splitext(filename)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return f"{timestamp}{ext}"


def process_image(file_path):
    """
    处理图片：验证并优化图片

    Args:
        file_path: 图片文件路径

    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        with Image.open(file_path) as img:
            # 验证图片尺寸
            if img.size[0] > MAX_IMAGE_SIZE[0] or img.size[1] > MAX_IMAGE_SIZE[1]:
                # 调整图片大小
                img.thumbnail(MAX_IMAGE_SIZE, Image.Resampling.LANCZOS)
                img.save(file_path, quality=95, optimize=True)
            else:
                # 优化图片大小
                img.save(file_path, quality=95, optimize=True)

        return True, "图片处理成功"
    except Exception as e:
        return False, f"图片处理失败: {str(e)}"


# ==================== 仪表板 ====================

@bp.route('/')
@login_required
def dashboard():
    """
    管理后台首页

    显示当前用户的所有文章、分类和标签列表

    Returns:
        str: 渲染后的仪表板页面HTML
    """
    posts = Post.query.filter_by(user_id=current_user.id).order_by(Post.created_at.desc()).all()
    categories = Category.query.all()
    tags = Tag.query.all()
    return render_template('admin/dashboard.html', posts=posts, categories=categories, tags=tags)


# ==================== 图片上传 ====================

@bp.route('/upload/cover', methods=['POST'])
@login_required
def upload_cover_image():
    """
    上传封面图片或内容图片

    处理图片上传、验证和优化
    支持本地存储和 GitHub 仓库存储

    Returns:
        JSON响应：包含成功状态和图片URL或错误消息
    """
    # 检查是否有文件
    if 'cover_image' not in request.files:
        return jsonify({'success': False, 'message': '没有选择文件'}), 400

    file = request.files['cover_image']

    # 检查文件名
    if file.filename == '':
        return jsonify({'success': False, 'message': '没有选择文件'}), 400

    # 检查文件类型
    if not allowed_file(file.filename):
        return jsonify({
            'success': False,
            'message': f'不支持的文件类型。支持的格式: {", ".join(ALLOWED_IMAGE_EXTENSIONS)}'
        }), 400

    try:
        # 生成唯一文件名
        filename = generate_unique_filename(file.filename)

        # 获取存储后端
        storage = get_storage()

        # 检测存储类型
        is_github = hasattr(storage, 'token')

        if is_github:
            # 使用 GitHub 存储：直接上传文件对象
            object_name = f'covers/{filename}'

            # 先处理图片（验证和优化）
            file.seek(0)
            img_data = file.read()

            # 使用 PIL 处理图片
            try:
                with Image.open(BytesIO(img_data)) as img:
                    # 验证图片尺寸
                    if img.size[0] > MAX_IMAGE_SIZE[0] or img.size[1] > MAX_IMAGE_SIZE[1]:
                        # 调整图片大小
                        img.thumbnail(MAX_IMAGE_SIZE, Image.Resampling.LANCZOS)

                    # 保存到内存
                    output = BytesIO()
                    img_format = img.format or 'JPEG'
                    img.save(output, format=img_format, quality=95, optimize=True)
                    output.seek(0)

                    # 上传到 GitHub
                    if storage.upload_fileobj(output, object_name):
                        image_url = storage.get_url(object_name)
                    else:
                        return jsonify({'success': False, 'message': '上传到 GitHub 失败'}), 500
            except Exception as e:
                return jsonify({'success': False, 'message': f'图片处理失败: {str(e)}'}), 400

        else:
            # 使用本地存储
            upload_folder = current_app.config['UPLOAD_FOLDER']
            os.makedirs(upload_folder, exist_ok=True)

            file_path = os.path.join(upload_folder, filename)

            # 保存文件
            file.save(file_path)

            # 处理图片（验证和优化）
            success, message = process_image(file_path)
            if not success:
                # 处理失败，删除文件
                if os.path.exists(file_path):
                    os.remove(file_path)
                return jsonify({'success': False, 'message': message}), 400

            # 返回本地存储的图片URL
            image_url = f'/static/uploads/covers/{filename}'

        return jsonify({
            'success': True,
            'message': '图片上传成功',
            'image_url': image_url
        })

    except Exception as e:
        current_app.logger.error(f'图片上传失败: {str(e)}')
        return jsonify({'success': False, 'message': f'上传失败: {str(e)}'}), 500


@bp.route('/api/detect-local-images', methods=['POST'])
@login_required
def detect_local_images():
    """
    检测 Markdown 内容中的本地图片路径

    分析 MD 内容，找出所有本地图片路径，返回需要上传的图片列表

    Returns:
        JSON: 包含检测到的本地图片信息
    """
    data = request.get_json()
    content = data.get('content', '')

    if not content:
        return jsonify({'local_images': [], 'count': 0})

    import re

    local_images = []

    # 匹配 Markdown 图片语法 ![alt](path)
    md_pattern = r'!\[.*?\]\((.*?)\)'
    # 匹配 HTML img 标签 <img src="path">
    html_pattern = r'<img\s+src=["\']([^"\']+)["\']'

    patterns = [
        (md_pattern, 'markdown'),
        (html_pattern, 'html')
    ]

    for pattern, img_type in patterns:
        matches = re.findall(pattern, content)
        for match in matches:
            # 检查是否是本地路径
            if is_local_image_path(match):
                # 提取文件名
                filename = os.path.basename(match).strip()
                if filename:
                    local_images.append({
                        'path': match,
                        'filename': filename,
                        'type': img_type
                    })

    # 去重
    seen = set()
    unique_images = []
    for img in local_images:
        if img['filename'] not in seen:
            seen.add(img['filename'])
            unique_images.append(img)

    return jsonify({
        'local_images': unique_images,
        'count': len(unique_images)
    })


def is_local_image_path(path):
    """判断路径是否是本地文件路径"""
    path = path.strip()

    # Windows 绝对路径: C:\, D:\ 等
    if len(path) >= 2 and path[1] == ':' and path[0].isalpha():
        return True

    # Windows UNC 路径: \\server\share
    if path.startswith('\\\\'):
        return True

    # file:// 协议
    if path.startswith('file://'):
        return True

    return False


# ==================== 分类管理 ====================

@bp.route('/category/new', methods=['GET', 'POST'])
@login_required
def new_category():
    """
    创建新分类

    GET: 显示创建分类表单
    POST: 处理分类创建请求

    Returns:
        str: 渲染后的表单页面或重定向
    """
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')

        # 检查分类名是否已存在
        if Category.query.filter_by(name=name).first():
            flash('分类已存在')
            return redirect(url_for('admin.dashboard'))

        category = Category(name=name, description=description)
        db.session.add(category)
        db.session.commit()

        flash('分类创建成功')
        return redirect(url_for('admin.dashboard'))

    return render_template('admin/edit_category.html')


@bp.route('/category/<int:category_id>/delete', methods=['POST'])
@login_required
def delete_category(category_id):
    """
    删除分类

    Args:
        category_id: 要删除的分类ID

    Returns:
        str: 重定向到仪表板
    """
    category = Category.query.get_or_404(category_id)
    db.session.delete(category)
    db.session.commit()
    flash('分类已删除')
    return redirect(url_for('admin.dashboard'))


# ==================== 标签管理 ====================

@bp.route('/tag/new', methods=['POST'])
@login_required
def new_tag():
    """
    创建新标签

    Returns:
        str: 重定向到仪表板
    """
    name = request.form.get('name')

    # 检查标签名是否已存在
    if Tag.query.filter_by(name=name).first():
        flash('标签已存在')
        return redirect(url_for('admin.dashboard'))

    tag = Tag(name=name)
    db.session.add(tag)
    db.session.commit()

    flash('标签创建成功')
    return redirect(url_for('admin.dashboard'))


@bp.route('/tag/<int:tag_id>/delete', methods=['POST'])
@login_required
def delete_tag(tag_id):
    """
    删除标签

    Args:
        tag_id: 要删除的标签ID

    Returns:
        str: 重定向到仪表板
    """
    tag = Tag.query.get_or_404(tag_id)
    db.session.delete(tag)
    db.session.commit()
    flash('标签已删除')
    return redirect(url_for('admin.dashboard'))


# ==================== 文章管理 ====================

@bp.route('/post/new', methods=['GET', 'POST'])
@login_required
def new_post():
    """
    创建新文章

    GET: 显示创建文章表单
    POST: 处理文章创建请求

    Returns:
        str: 渲染后的表单页面或重定向
    """
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        summary = request.form.get('summary', '').strip()
        published = request.form.get('published') == 'on'
        category_id = request.form.get('category_id', type=int)

        # 处理定时发布
        scheduled = request.form.get('scheduled') == 'on'
        scheduled_at = None
        if scheduled:
            scheduled_date = request.form.get('scheduled_date')
            scheduled_time = request.form.get('scheduled_time', '00:00')
            if scheduled_date:
                try:
                    scheduled_at = datetime.strptime(f'{scheduled_date} {scheduled_time}', '%Y-%m-%d %H:%M')
                    # 如果定时发布，则不立即发布
                    published = False
                except ValueError:
                    flash('定时发布时间格式错误', 'danger')
                    categories = Category.query.all()
                    tags = Tag.query.all()
                    return render_template('admin/edit_post.html', categories=categories, tags=tags)

        # 处理封面图片：优先使用上传的文件路径，其次是 URL
        cover_image = request.form.get('cover_image', '') or request.form.get('cover_image_url', '')

        tags = request.form.getlist('tags')

        # 如果没有提供摘要，自动生成
        if not summary:
            from app.utils.text import generate_summary
            summary = generate_summary(content, max_length=300)

        # 如果没有封面图，自动生成
        if not cover_image:
            from app.utils.image_generator import generate_cover_image
            # 获取分类名称
            category_obj = Category.query.get(category_id) if category_id else None
            category_name = category_obj.name if category_obj else None
            # 获取标签名称
            tag_names = []
            for tag_id in tags:
                tag = Tag.query.get(int(tag_id))
                if tag:
                    tag_names.append(tag.name)
            # 生成封面图（传递内容用于提取关键词）
            cover_image = generate_cover_image(title, category_name, tag_names, content)

        # 创建文章对象
        post = Post(
            title=title,
            content=content,
            summary=summary,
            user_id=current_user.id,
            category_id=category_id if category_id else None,
            cover_image=cover_image,
            published=published,
            scheduled_at=scheduled_at
        )

        # 添加标签关联
        for tag_id in tags:
            tag = Tag.query.get(int(tag_id))
            if tag:
                post.tags.append(tag)

        db.session.add(post)
        db.session.commit()

        if scheduled_at:
            flash(f'文章已保存，将于 {scheduled_at.strftime("%Y-%m-%d %H:%M")} 自动发布')
        else:
            flash('文章创建成功')
        return redirect(url_for('admin.dashboard'))

    categories = Category.query.all()
    tags = Tag.query.all()
    return render_template('admin/edit_post.html', categories=categories, tags=tags)


@bp.route('/post/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    """
    编辑文章

    GET: 显示编辑文章表单
    POST: 处理文章更新请求

    Args:
        post_id: 要编辑的文章ID

    Returns:
        str: 渲染后的表单页面或重定向
    """
    post = Post.query.get_or_404(post_id)

    # 权限检查
    if post.author != current_user:
        flash('你没有权限编辑这篇文章')
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        # 更新文章基本信息
        post.title = request.form.get('title')
        post.content = request.form.get('content')
        summary = request.form.get('summary', '').strip()

        # 如果没有提供摘要，自动生成
        if not summary:
            from app.utils.text import generate_summary
            summary = generate_summary(post.content, max_length=300)

        post.summary = summary

        # 处理定时发布
        scheduled = request.form.get('scheduled') == 'on'
        scheduled_at = None
        if scheduled:
            scheduled_date = request.form.get('scheduled_date')
            scheduled_time = request.form.get('scheduled_time', '00:00')
            if scheduled_date:
                try:
                    scheduled_at = datetime.strptime(f'{scheduled_date} {scheduled_time}', '%Y-%m-%d %H:%M')
                    # 如果定时发布，则不立即发布
                    post.published = False
                    post.scheduled_at = scheduled_at
                except ValueError:
                    flash('定时发布时间格式错误', 'danger')
                    categories = Category.query.all()
                    all_tags = Tag.query.all()
                    return render_template('admin/edit_post.html', post=post,
                                          categories=categories, tags=all_tags)
            else:
                post.scheduled_at = None
                post.published = request.form.get('published') == 'on'
        else:
            post.scheduled_at = None
            post.published = request.form.get('published') == 'on'

        post.category_id = request.form.get('category_id', type=int) or None

        # 处理封面图片：优先使用上传的文件路径，其次是 URL
        cover_image = request.form.get('cover_image', '') or request.form.get('cover_image_url', '')

        # 如果没有封面图且之前也没有，自动生成
        if not cover_image and not post.cover_image:
            from app.utils.image_generator import generate_cover_image
            # 获取分类名称
            category_obj = Category.query.get(post.category_id) if post.category_id else None
            category_name = category_obj.name if category_obj else None
            # 获取标签名称
            tags = [tag.name for tag in post.tags] if post.tags else []
            # 生成封面图（传递内容用于提取关键词）
            cover_image = generate_cover_image(post.title, category_name, tags, post.content)

        # 更新封面图（如果有新的）
        if cover_image:
            post.cover_image = cover_image

        # 更新标签关联
        post.tags.clear()
        tags = request.form.getlist('tags')
        for tag_id in tags:
            tag = Tag.query.get(int(tag_id))
            if tag:
                post.tags.append(tag)

        db.session.commit()

        if post.scheduled_at:
            flash(f'文章已更新，将于 {post.scheduled_at.strftime("%Y-%m-%d %H:%M")} 自动发布')
        else:
            flash('文章更新成功')
        return redirect(url_for('admin.dashboard'))

    categories = Category.query.all()
    all_tags = Tag.query.all()
    return render_template('admin/edit_post.html', post=post,
                          categories=categories, tags=all_tags)


@bp.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    """
    删除文章

    Args:
        post_id: 要删除的文章ID

    Returns:
        str: 重定向到仪表板
    """
    post = Post.query.get_or_404(post_id)

    # 权限检查
    if post.author != current_user:
        flash('你没有权限删除这篇文章')
        return redirect(url_for('main.index'))

    db.session.delete(post)
    db.session.commit()

    # 清除相关缓存
    cache.delete_memoized(get_hot_posts)
    cache.delete_memoized(get_hot_tags)
    cache.delete_memoized(get_total_views)

    flash('文章已删除')
    return redirect(url_for('admin.dashboard'))


# ==================== Markdown 导入 ====================

@bp.route('/import', methods=['GET', 'POST'])
@login_required
def import_markdown():
    """
    导入单个 Markdown 文件

    GET: 显示导入页面
    POST: 处理文件上传和解析

    支持特性：
    - 自动检测文件编码
    - 解析 YAML front matter
    - 提取标题和摘要

    Returns:
        str: 渲染后的页面或JSON响应
    """
    if request.method == 'POST':
        # 检查是否有文件
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': '没有选择文件'}), 400

        file = request.files['file']

        # 检查文件名
        if file.filename == '':
            return jsonify({'success': False, 'message': '没有选择文件'}), 400

        # 检查文件类型
        if not file.filename.endswith('.md'):
            return jsonify({'success': False, 'message': '只支持 .md 文件'}), 400

        try:
            # 读取文件内容，尝试多种编码
            content = _read_file_content(file)

            if content is None:
                return jsonify({
                    'success': False,
                    'message': '文件编码不支持，请使用 UTF-8 编码'
                }), 400

            # 解析 Markdown 文件
            title, summary, body_content = parse_markdown(content)

            # 从文件名获取标题（如果没有在内容中找到）
            if not title:
                title = os.path.splitext(file.filename)[0]

            # 自动生成封面图（传递内容用于提取关键词）
            from app.utils.image_generator import generate_cover_image
            cover_image = generate_cover_image(title, None, None, body_content)

            # 创建文章
            post = Post(
                title=title,
                content=body_content,
                summary=summary,
                user_id=current_user.id,
                cover_image=cover_image,
                published=False  # 默认为草稿，需要手动发布
            )

            db.session.add(post)
            db.session.commit()

            return jsonify({
                'success': True,
                'message': '导入成功',
                'post_id': post.id,
                'title': title
            })

        except Exception as e:
            return jsonify({'success': False, 'message': f'导入失败: {str(e)}'}), 500

    return render_template('admin/import.html')


@bp.route('/import/batch', methods=['POST'])
@login_required
def import_batch():
    """
    批量导入多个 Markdown 文件

    支持一次上传多个 .md 文件，返回成功和失败的文件列表

    Returns:
        JSON响应：包含成功数量、失败文件列表
    """
    if 'files' not in request.files:
        return jsonify({'success': False, 'message': '没有选择文件'}), 400

    files = request.files.getlist('files')
    success_count = 0
    failed_files = []

    for file in files:
        if file.filename == '':
            continue

        if not file.filename.endswith('.md'):
            failed_files.append(f"{file.filename} (不支持的格式)")
            continue

        try:
            # 读取文件内容
            content = _read_file_content(file)

            if content is None:
                failed_files.append(f"{file.filename} (编码错误)")
                continue

            # 解析 Markdown 文件
            title, summary, body_content = parse_markdown(content)

            # 从文件名获取标题
            if not title:
                title = os.path.splitext(file.filename)[0]

            # 自动生成封面图（传递内容用于提取关键词）
            from app.utils.image_generator import generate_cover_image
            cover_image = generate_cover_image(title, None, None, body_content)

            # 创建文章
            post = Post(
                title=title,
                content=body_content,
                summary=summary,
                user_id=current_user.id,
                cover_image=cover_image,
                published=False
            )

            db.session.add(post)
            success_count += 1

        except Exception as e:
            failed_files.append(f"{file.filename} ({str(e)})")

    try:
        db.session.commit()
        message = f'成功导入 {success_count} 个文件'
        if failed_files:
            message += f'，{len(failed_files)} 个文件失败'
        return jsonify({
            'success': True,
            'message': message,
            'failed_files': failed_files
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'保存失败: {str(e)}'}), 500


# ==================== 辅助函数 ====================

def _read_file_content(file):
    """
    读取文件内容，自动检测编码

    Args:
        file: 上传的文件对象

    Returns:
        str|None: 文件内容（解码后），如果所有编码都失败则返回 None
    """
    content = None
    for encoding in SUPPORTED_ENCODINGS:
        try:
            file.seek(0)
            content = file.read().decode(encoding)
            break
        except (UnicodeDecodeError, UnicodeError):
            continue
    return content


def parse_markdown(content):
    """
    解析 Markdown 文件内容

    提取以下信息：
    - 标题（从 YAML front matter 或第一个 # 标题）
    - 摘要（前200字或第一段）
    - 正文内容

    Args:
        content (str): Markdown 文件内容

    Returns:
        tuple: (title, summary, body_content)
    """
    lines = content.split('\n')

    title = None
    summary = None
    body_lines = []
    front_matter = []
    in_front_matter = False
    body_started = False

    # 检查是否有 YAML front matter
    if lines and lines[0].strip() == '---':
        in_front_matter = True
        lines = lines[1:]  # 移除第一个 ---

    for i, line in enumerate(lines):
        # 处理 front matter 结束
        if in_front_matter and line.strip() == '---':
            in_front_matter = False
            continue

        # 在 front matter 中
        if in_front_matter:
            front_matter.append(line)
            # 尝试提取 title
            if line.startswith('title:'):
                title = line.split(':', 1)[1].strip().strip('"\'')
            continue

        # 提取第一个 # 标题作为文章标题
        if not title and line.strip().startswith('#'):
            title_match = re.match(r'^#+\s+(.+)$', line)
            if title_match:
                title = title_match.group(1).strip()
                continue  # 不将标题加入正文

        # 正文开始
        if not body_started and line.strip():
            body_started = True

        # 添加到正文
        body_lines.append(line)

        # 提取摘要（前200字或第一段）
        if not summary and line.strip() and len('\n'.join(body_lines)) > 0:
            preview = '\n'.join(body_lines).strip()
            if len(preview) > 200:
                summary = preview[:200] + '...'
            elif line.strip() == '' and len(preview) > 50:
                summary = preview

    body_content = '\n'.join(body_lines).strip()

    # 如果没有摘要，使用正文前300字
    if not summary and body_content:
        summary = body_content[:300] + ('...' if len(body_content) > 300 else '')

    return title, summary, body_content


# ========================================
# 友情链接管理
# ========================================

@bp.route('/friend-links')
@login_required
def friend_links():
    """友情链接管理页面"""
    links = FriendLink.query.order_by(FriendLink.order, FriendLink.created_at.desc()).all()
    return render_template('admin/friend_links.html', links=links)


@bp.route('/friend-links/new', methods=['POST'])
@login_required
def new_friend_link():
    """添加友情链接"""
    name = request.form.get('name')
    url = request.form.get('url')
    description = request.form.get('description')
    logo = request.form.get('logo')

    if not name or not url:
        return jsonify({'success': False, 'message': '网站名称和URL不能为空'}), 400

    link = FriendLink(
        name=name,
        url=url,
        description=description,
        logo=logo
    )
    db.session.add(link)
    db.session.commit()

    return jsonify({'success': True, 'message': '友情链接添加成功'})


@bp.route('/friend-links/<int:link_id>/delete', methods=['POST'])
@login_required
def delete_friend_link(link_id):
    """删除友情链接"""
    link = FriendLink.query.get_or_404(link_id)
    db.session.delete(link)
    db.session.commit()

    return jsonify({'success': True, 'message': '友情链接已删除'})


@bp.route('/regenerate-covers', methods=['POST'])
@login_required
def regenerate_covers():
    """
    为当前用户的所有文章重新生成封面图

    限制：
    - 只处理当前登录用户创建的文章
    - 跳过已上传封面图的文章（非自动生成的封面）

    Returns:
        JSON: 生成结果
    """
    # 只获取当前用户的文章
    posts = Post.query.filter_by(user_id=current_user.id).all()

    if not posts:
        return jsonify({'success': True, 'message': '没有文章', 'count': 0})

    from app.utils.image_generator import generate_cover_from_post

    success_count = 0
    skipped_count = 0  # 跳过的文章数（已有上传的封面图）
    failed_count = 0
    failed_posts = []
    skipped_posts = []  # 记录跳过的文章

    for post in posts:
        # 检查是否有封面图
        if post.cover_image:
            # 判断是否是自动生成的封面图
            # 自动生成的封面图路径格式：/static/uploads/covers/cover_
            # 用户上传的封面图通常包含 uploads 但不是 cover_ 开头
            if '/static/uploads/covers/cover_' in post.cover_image:
                # 是自动生成的，可以重新生成
                pass
            else:
                # 是用户上传的图片，跳过
                skipped_count += 1
                skipped_posts.append(post.title)
                continue

        try:
            post.cover_image = generate_cover_from_post(post)
            success_count += 1
        except Exception as e:
            failed_count += 1
            failed_posts.append(f"{post.title}: {str(e)}")

    try:
        db.session.commit()

        # 构建返回消息
        message_parts = []
        if success_count > 0:
            message_parts.append(f'成功生成 {success_count} 张封面图')
        if skipped_count > 0:
            message_parts.append(f'跳过 {skipped_count} 篇已有封面图的文章')
        if failed_count > 0:
            message_parts.append(f'失败 {failed_count} 张')

        message = '，'.join(message_parts) if message_parts else '没有处理任何文章'

        return jsonify({
            'success': True,
            'message': message,
            'count': success_count,
            'skipped': skipped_count,
            'skipped_posts': skipped_posts[:10],  # 最多返回10个跳过的文章
            'failed': failed_count,
            'failed_posts': failed_posts[:10]  # 最多返回10个失败项
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'保存失败: {str(e)}'}), 500


# ==================== API 路由 ====================

@bp.route('/api/generate-summary', methods=['POST'])
@login_required
def api_generate_summary():
    """
    自动生成文章摘要 API

    从文章内容中提取关键句子生成摘要

    Request Body:
        JSON: { "content": "文章内容" }

    Returns:
        JSON: { "summary": "生成的摘要" }
    """
    from app.utils.text import generate_summary

    data = request.get_json()
    content = data.get('content', '')

    if not content:
        return jsonify({'error': '内容不能为空'}), 400

    try:
        summary = generate_summary(content, max_length=300)
        return jsonify({'summary': summary})
    except Exception as e:
        current_app.logger.error(f'生成摘要失败: {str(e)}')
        return jsonify({'error': '生成摘要失败'}), 500


@bp.route('/bookmarks')
@login_required
def bookmarks():
    """
    收藏文章管理页面

    显示所有被用户收藏的文章列表
    """
    # 获取所有收藏记录，按收藏时间倒序
    bookmarks_query = PostBookmark.query.order_by(PostBookmark.created_at.desc())

    # 分页
    page = request.args.get('page', 1, type=int)
    per_page = 20
    bookmarks_pagination = bookmarks_query.paginate(page=page, per_page=per_page, error_out=False)

    return render_template('admin/bookmarks.html', bookmarks=bookmarks_pagination)


@bp.route('/bookmark/<int:bookmark_id>/delete', methods=['POST'])
@login_required
def delete_bookmark(bookmark_id):
    """
    删除收藏记录 API

    删除指定的收藏记录

    Args:
        bookmark_id: 收藏记录ID

    Returns:
        JSON: 操作结果
    """
    bookmark = PostBookmark.query.get_or_404(bookmark_id)

    try:
        db.session.delete(bookmark)
        db.session.commit()
        return jsonify({'success': True, 'message': '收藏已删除'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
