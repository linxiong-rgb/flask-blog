"""
博客管理后台路由模块

该模块处理博客管理功能，包括：
- 仪表板首页
- 分类管理（创建、删除）
- 标签管理（创建、删除）
- 文章管理（创建、编辑、删除）
- Markdown 文件导入（单个和批量）
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
import re
from app.models.post import Post, Category, Tag
from app.models.user import User
from app import db

bp = Blueprint('admin', __name__, url_prefix='/admin')

# 文件编码支持列表（按优先级排序）
SUPPORTED_ENCODINGS = ['utf-8', 'utf-8-sig', 'gbk', 'gb2312', 'iso-8859-1']


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
        summary = request.form.get('summary', '')[:300]
        published = request.form.get('published') == 'on'
        category_id = request.form.get('category_id', type=int)
        cover_image = request.form.get('cover_image', '')
        tags = request.form.getlist('tags')

        # 创建文章对象
        post = Post(
            title=title,
            content=content,
            summary=summary,
            user_id=current_user.id,
            category_id=category_id if category_id else None,
            cover_image=cover_image if cover_image else None,
            published=published
        )

        # 添加标签关联
        for tag_id in tags:
            tag = Tag.query.get(int(tag_id))
            if tag:
                post.tags.append(tag)

        db.session.add(post)
        db.session.commit()

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
        post.summary = request.form.get('summary', '')[:300]
        post.published = request.form.get('published') == 'on'
        post.category_id = request.form.get('category_id', type=int) or None
        post.cover_image = request.form.get('cover_image', '') or None

        # 更新标签关联
        post.tags.clear()
        tags = request.form.getlist('tags')
        for tag_id in tags:
            tag = Tag.query.get(int(tag_id))
            if tag:
                post.tags.append(tag)

        db.session.commit()
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

            # 创建文章
            post = Post(
                title=title,
                content=body_content,
                summary=summary,
                user_id=current_user.id,
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

            # 创建文章
            post = Post(
                title=title,
                content=body_content,
                summary=summary,
                user_id=current_user.id,
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
