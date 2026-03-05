"""
云相册路由模块

该模块处理云相册功能，包括：
- 相册管理（创建、编辑、删除、移动）
- 图片上传和管理
- 图片分享
- 共享空间
"""

import os
import secrets
import re
from datetime import datetime, timedelta
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app, send_file, session
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from sqlalchemy import or_, and_
from sqlalchemy.orm import joinedload
from io import BytesIO
import mimetypes

from app.models.album import Album, Photo, PhotoTag, PhotoShare
from app.models.user import User
from app import db
from app.utils.storage import get_storage

# 尝试导入PIL，如果失败则设置标志
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    current_app.logger.warning('PIL/Pillow not installed, image processing features will be limited')

bp = Blueprint('gallery', __name__, url_prefix='/gallery')

# 允许的图片扩展名
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'bmp'}

# 缩略图尺寸
THUMBNAIL_SIZES = {
    'small': (200, 200),
    'medium': (400, 400),
    'large': (1200, 900)
}


def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def generate_unique_filename(filename):
    """生成唯一的文件名，使用UUID确保唯一性"""
    import uuid
    name, ext = os.path.splitext(filename)
    # 使用UUID的前8位作为唯一标识，加上用户ID和时间戳
    unique_id = uuid.uuid4().hex[:12]
    return f"{unique_id}{ext}"


def generate_share_token():
    """生成分享令牌"""
    return secrets.token_urlsafe(32)


def create_thumbnail(image_path, size='medium'):
    """创建缩略图"""
    if not PIL_AVAILABLE:
        return None

    try:
        img = Image.open(image_path)
        img.thumbnail(THUMBNAIL_SIZES[size], Image.Resampling.LANCZOS)

        output = BytesIO()
        img.save(output, format='JPEG', quality=85, optimize=True)
        output.seek(0)

        return output
    except Exception as e:
        current_app.logger.error(f'创建缩略图失败: {str(e)}')
        return None


def superuser_required(f):
    """超级管理员权限检查装饰器"""
    from functools import wraps

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({'success': False, 'message': '请先登录'}), 401
        if not getattr(current_user, 'is_superuser', False):
            return jsonify({'success': False, 'message': '需要超级管理员权限'}), 403
        return f(*args, **kwargs)
    return decorated_function


def can_access_album(album):
    """检查用户是否有权限访问相册"""
    if album.user_id == current_user.id:
        return True
    if not album.is_private:
        return True
    if getattr(current_user, 'is_superuser', False):
        return True
    return False


def can_access_photo(photo):
    """检查用户是否有权限访问图片"""
    if photo.user_id == current_user.id:
        return True
    if photo.is_public:
        return True
    if getattr(current_user, 'is_superuser', False):
        return True
    return False


# ==================== 相册管理 ====================

@bp.route('/')
@login_required
def index():
    """
    相册首页

    显示当前用户的所有相册（树形结构）
    超级管理员可以查看所有用户的相册
    """
    is_superuser = getattr(current_user, 'is_superuser', False)

    if is_superuser:
        # 超级管理员查看所有相册
        root_albums = Album.query.filter_by(parent_id=None).order_by(
            Album.sort_order, Album.name
        ).all()
        total_photos = Photo.query.count()
        total_albums = Album.query.count()
    else:
        # 普通用户只查看自己的相册
        root_albums = Album.query.filter_by(
            user_id=current_user.id,
            parent_id=None
        ).order_by(Album.sort_order, Album.name).all()
        total_photos = Photo.query.filter_by(user_id=current_user.id).count()
        total_albums = Album.query.filter_by(user_id=current_user.id).count()

    return render_template('gallery/index.html',
                          root_albums=root_albums,
                          total_photos=total_photos,
                          total_albums=total_albums,
                          is_superuser=is_superuser)


@bp.route('/album/new', methods=['GET', 'POST'])
@login_required
def new_album():
    """
    创建新相册

    GET: 显示创建表单
    POST: 处理创建请求
    """
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        parent_id = request.form.get('parent_id', type=int) or None
        is_private = request.form.get('is_private') == 'on'

        if not name:
            flash('相册名称不能为空', 'danger')
            return redirect(url_for('gallery.index'))

        album = Album(
            name=name,
            description=description,
            user_id=current_user.id,
            parent_id=parent_id,
            is_private=is_private
        )

        db.session.add(album)
        db.session.commit()

        flash('相册创建成功')
        return redirect(url_for('gallery.index'))

    # 获取可以放置的父相册列表
    parent_albums = Album.query.filter_by(user_id=current_user.id).all()
    return render_template('gallery/new_album.html', parent_albums=parent_albums)


@bp.route('/album/<int:album_id>')
@login_required
def view_album(album_id):
    """
    查看相册详情

    显示相册中的所有图片
    超级管理员可以查看所有相册
    非私密相册：其他用户只能看到公开的图片
    """
    album = Album.query.get_or_404(album_id)

    # 权限检查（超级管理员可以访问所有相册）
    is_superuser = getattr(current_user, 'is_superuser', False)
    is_owner = (album.user_id == current_user.id)

    if not is_owner and not is_superuser:
        # 非所有者访问
        if album.is_private:
            # 私密相册，拒绝访问
            flash('您没有权限访问此相册', 'warning')
            return redirect(url_for('gallery.index'))
        # 公开相册，只显示公开的图片
        photos = Photo.query.filter_by(album_id=album_id, is_public=True).order_by(Photo.created_at.desc()).all()
    else:
        # 所有者或超级管理员，显示所有图片
        photos = Photo.query.filter_by(album_id=album_id).order_by(Photo.created_at.desc()).all()

    # 获取子相册
    child_albums = Album.query.filter_by(parent_id=album_id).order_by(Album.sort_order, Album.name).all()

    return render_template('gallery/view_album.html',
                          album=album,
                          photos=photos,
                          child_albums=child_albums,
                          is_superuser=is_superuser,
                          is_owner=is_owner)


@bp.route('/album/<int:album_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_album(album_id):
    """
    编辑相册

    GET: 显示编辑表单
    POST: 处理更新请求
    超级管理员可以编辑所有相册
    """
    album = Album.query.get_or_404(album_id)

    # 权限检查（超级管理员可以编辑所有相册）
    is_superuser = getattr(current_user, 'is_superuser', False)
    if album.user_id != current_user.id and not is_superuser:
        flash('您没有权限编辑此相册')
        return redirect(url_for('gallery.index'))

    if request.method == 'POST':
        album.name = request.form.get('name')
        album.description = request.form.get('description')
        album.is_private = request.form.get('is_private') == 'on'

        db.session.commit()
        flash('相册更新成功')
        return redirect(url_for('gallery.view_album', album_id=album_id))

    parent_albums = Album.query.filter(
        Album.id != album_id  # 不能选择自己作为父相册
    ).all()

    return render_template('gallery/edit_album.html',
                          album=album,
                          parent_albums=parent_albums,
                          is_superuser=is_superuser)


@bp.route('/album/<int:album_id>/delete', methods=['POST'])
@login_required
def delete_album(album_id):
    """
    删除相册

    注意：会删除相册中的所有图片
    超级管理员可以删除任何相册
    """
    try:
        album = Album.query.get(album_id)
        if not album:
            return jsonify({'success': False, 'message': '相册不存在'}), 404

        # 权限检查（超级管理员可以删除任何相册）
        is_superuser = getattr(current_user, 'is_superuser', False)
        if album.user_id != current_user.id and not is_superuser:
            return jsonify({'success': False, 'message': '您没有权限删除此相册'}), 403

        # 获取相册中的所有图片
        photos = Photo.query.filter_by(album_id=album_id).all()

        # 删除每张图片及其关联数据
        for photo in photos:
            # 删除分享记录
            from app.models.album import PhotoShare
            PhotoShare.query.filter_by(photo_id=photo.id).delete()
            # 删除标签关系
            photo.tags.clear()
            # 删除文件
            delete_photo_file(photo)
            # 删除记录
            db.session.delete(photo)

        # 删除相册
        db.session.delete(album)
        db.session.commit()

        return jsonify({'success': True, 'message': '相册及所有照片已删除'})

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'删除相册失败 [ID:{album_id}]: {str(e)}', exc_info=True)
        return jsonify({'success': False, 'message': f'删除失败，请稍后重试'}), 500


# ==================== 图片上传 ====================

@bp.route('/album/<int:album_id>/upload', methods=['POST'])
@login_required
def upload_photos(album_id):
    """
    上传图片到相册

    支持单张和多张上传
    超级管理员可以上传到任何相册
    """
    album = Album.query.get_or_404(album_id)

    # 权限检查（超级管理员可以上传到任何相册）
    is_superuser = getattr(current_user, 'is_superuser', False)
    if album.user_id != current_user.id and not is_superuser:
        return jsonify({'success': False, 'message': '您没有权限上传到此相册'}), 403

    if 'photos' not in request.files:
        return jsonify({'success': False, 'message': '没有选择文件'}), 400

    files = request.files.getlist('photos')
    uploaded = []
    failed = []

    storage = get_storage()

    for file in files:
        if file.filename == '':
            continue

        if not allowed_file(file.filename):
            failed.append({'filename': file.filename, 'error': '不支持的文件类型'})
            continue

        try:
            # 生成唯一文件名
            filename = generate_unique_filename(file.filename)
            object_name = f'gallery/{current_user.id}/{filename}'

            # 读取并验证图片
            file.seek(0)
            img_data = file.read()

            # 获取图片尺寸（如果PIL可用）
            width, height, img_format = None, None, None
            if PIL_AVAILABLE:
                try:
                    img = Image.open(BytesIO(img_data))
                    width, height = img.width, img.height
                    img_format = img.format or 'JPEG'
                except Exception as e:
                    current_app.logger.error(f'读取图片信息失败: {str(e)}')
            else:
                img_format = 'JPEG'

            # 上传原图
            file.seek(0)
            if storage.upload_fileobj(file, object_name):
                image_url = storage.get_url(object_name)
            else:
                failed.append({'filename': file.filename, 'error': '上传失败'})
                continue

            # 创建缩略图
            thumbnail_url = image_url
            try:
                thumbnail = create_thumbnail(BytesIO(img_data), 'medium')
                if thumbnail:
                    thumb_filename = f'thumb_{filename}'
                    thumb_object_name = f'gallery/{current_user.id}/thumbnails/{thumb_filename}'
                    if storage.upload_fileobj(thumbnail, thumb_object_name):
                        thumbnail_url = storage.get_url(thumb_object_name)
            except:
                pass

            # 保存图片信息
            photo = Photo(
                filename=file.filename,
                file_path=image_url,
                file_size=len(img_data),
                width=width,
                height=height,
                mime_type=f'image/{img_format.lower()}' if img_format else 'image/jpeg',
                thumbnail_path=thumbnail_url,
                album_id=album_id,
                user_id=current_user.id
            )

            db.session.add(photo)
            uploaded.append(photo.filename)

        except Exception as e:
            current_app.logger.error(f'上传图片失败: {str(e)}')
            failed.append({'filename': file.filename, 'error': str(e)})

    try:
        db.session.commit()
    except:
        db.session.rollback()

    return jsonify({
        'success': True,
        'uploaded': len(uploaded),
        'failed': len(failed),
        'message': f'成功上传 {len(uploaded)} 张图片'
    })


def delete_photo_file(photo):
    """删除图片文件（非阻塞，失败不影响数据库操作）"""
    try:
        storage = get_storage()

        # 删除原图
        if photo.file_path:
            object_name = None
            # 从URL中提取对象名
            # GitHub raw: https://raw.githubusercontent.com/user/repo/branch/images/gallery/1/filename.jpg
            # jsDelivr: https://cdn.jsdelivr.net/gh/user/repo@branch/images/gallery/1/filename.jpg
            # 本地: /static/uploads/gallery/1/filename.jpg

            # 提取 gallery/ 后面的完整路径
            if 'gallery/' in photo.file_path:
                gallery_index = photo.file_path.find('gallery/')
                object_name = photo.file_path[gallery_index:]

            if object_name:
                try:
                    storage.delete_file(object_name)
                    current_app.logger.info(f'已删除文件: {object_name}')
                except Exception as e:
                    current_app.logger.warning(f'删除文件失败 {object_name}: {str(e)}')

        # 删除缩略图
        if photo.thumbnail_path and photo.thumbnail_path != photo.file_path:
            thumb_object_name = None
            if 'gallery/' in photo.thumbnail_path:
                gallery_index = photo.thumbnail_path.find('gallery/')
                thumb_object_name = photo.thumbnail_path[gallery_index:]

            if thumb_object_name and thumb_object_name != object_name:
                try:
                    storage.delete_file(thumb_object_name)
                    current_app.logger.info(f'已删除缩略图: {thumb_object_name}')
                except Exception as e:
                    current_app.logger.warning(f'删除缩略图失败 {thumb_object_name}: {str(e)}')

    except Exception as e:
        # 删除文件失败不应该影响数据库删除操作
        current_app.logger.warning(f'删除图片文件时出错（已忽略）: {str(e)}')


@bp.route('/photo/<int:photo_id>/delete', methods=['POST'])
@login_required
def delete_photo(photo_id):
    """
    删除图片
    超级管理员可以删除任何图片
    """
    try:
        photo = Photo.query.get(photo_id)
        if not photo:
            return jsonify({'success': False, 'message': '图片不存在'}), 404

        # 权限检查（超级管理员可以删除任何图片）
        is_superuser = getattr(current_user, 'is_superuser', False)
        if photo.user_id != current_user.id and not is_superuser:
            return jsonify({'success': False, 'message': '您没有权限删除此图片'}), 403

        # 先删除关联的分享记录
        from app.models.album import PhotoShare
        PhotoShare.query.filter_by(photo_id=photo_id).delete()

        # 删除关联的标签关系（不会删除标签本身，只删除关系）
        photo.tags.clear()

        # 删除文件
        delete_photo_file(photo)

        # 删除数据库记录
        db.session.delete(photo)
        db.session.commit()

        return jsonify({'success': True, 'message': '图片已删除'})

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'删除图片失败 [ID:{photo_id}]: {str(e)}', exc_info=True)
        return jsonify({'success': False, 'message': f'删除失败，请稍后重试'}), 500


@bp.route('/photo/<int:photo_id>/move', methods=['POST'])
@login_required
def move_photo(photo_id):
    """
    移动图片到其他相册
    超级管理员可以移动任何图片
    """
    photo = Photo.query.get_or_404(photo_id)
    target_album_id = request.json.get('album_id')

    # 权限检查（超级管理员可以移动任何图片）
    is_superuser = getattr(current_user, 'is_superuser', False)
    if photo.user_id != current_user.id and not is_superuser:
        return jsonify({'success': False, 'message': '您没有权限移动此图片'}), 403

    # 验证目标相册
    if target_album_id:
        target_album = Album.query.get(target_album_id)
        if not target_album or target_album.user_id != current_user.id:
            return jsonify({'success': False, 'message': '目标相册不存在'}), 404

    photo.album_id = target_album_id
    db.session.commit()

    return jsonify({'success': True, 'message': '图片已移动'})


@bp.route('/photo/<int:photo_id>/toggle-public', methods=['POST'])
@login_required
def toggle_photo_public(photo_id):
    """
    切换图片公开/私密状态

    公开的图片会在共享空间展示
    超级管理员可以修改任何图片的状态
    """
    photo = Photo.query.get_or_404(photo_id)

    # 权限检查（超级管理员可以修改任何图片）
    is_superuser = getattr(current_user, 'is_superuser', False)
    if photo.user_id != current_user.id and not is_superuser:
        return jsonify({'success': False, 'message': '您没有权限修改此图片'}), 403

    # 切换状态
    photo.is_public = not photo.is_public
    db.session.commit()

    status = '公开' if photo.is_public else '私密'
    return jsonify({
        'success': True,
        'is_public': photo.is_public,
        'message': f'图片已设为{status}'
    })


@bp.route('/photo/<int:photo_id>/public', methods=['POST'])
@login_required
def set_photo_public(photo_id):
    """
    设置图片公开状态
    超级管理员可以设置任何图片的状态
    支持设置访问密码
    """
    photo = Photo.query.get_or_404(photo_id)

    # 权限检查（超级管理员可以设置任何图片的状态）
    is_superuser = getattr(current_user, 'is_superuser', False)
    if photo.user_id != current_user.id and not is_superuser:
        return jsonify({'success': False, 'message': '您没有权限修改此图片'}), 403

    data = request.json
    is_public = data.get('is_public', False)
    access_password = data.get('access_password')

    photo.is_public = is_public

    # 设置或清除密码
    if access_password:
        photo.access_password = access_password
    elif access_password == '' or access_password is None:
        photo.access_password = None

    db.session.commit()

    return jsonify({
        'success': True,
        'is_public': photo.is_public,
        'has_password': bool(photo.access_password),
        'message': f'图片已设为{"公开" if is_public else "私密"}'
    })


@bp.route('/photo/<int:photo_id>/edit-info', methods=['POST'])
@login_required
def edit_photo_info(photo_id):
    """
    编辑图片标题、描述和访问密码
    超级管理员可以编辑任何图片的信息
    """
    photo = Photo.query.get_or_404(photo_id)

    # 权限检查（超级管理员可以编辑任何图片）
    is_superuser = getattr(current_user, 'is_superuser', False)
    if photo.user_id != current_user.id and not is_superuser:
        return jsonify({'success': False, 'message': '您没有权限编辑此图片'}), 403

    data = request.json
    title = data.get('title')
    description = data.get('description')
    access_password = data.get('access_password')

    photo.title = title if title else None
    photo.description = description if description else None

    # 处理密码更新
    if access_password is not None:
        # 空字符串表示移除密码
        if access_password == '':
            photo.access_password = None
        else:
            photo.access_password = access_password if access_password else None

    db.session.commit()

    return jsonify({
        'success': True,
        'message': '图片信息已更新',
        'has_password': bool(photo.access_password)
    })


# ==================== 图片分享 ====================

@bp.route('/photo/<int:photo_id>/share', methods=['POST'])
@login_required
def create_share(photo_id):
    """
    创建图片分享链接
    """
    photo = Photo.query.get_or_404(photo_id)

    # 权限检查
    if photo.user_id != current_user.id:
        return jsonify({'success': False, 'message': '您没有权限分享此图片'}), 403

    # 获取分享设置
    expires_days = request.json.get('expires_days')
    access_password = request.json.get('access_password')
    max_access = request.json.get('max_access')

    # 创建分享
    share = PhotoShare(
        share_token=generate_share_token(),
        photo_id=photo_id,
        user_id=current_user.id
    )

    # 设置过期时间
    if expires_days:
        share.expires_at = datetime.utcnow() + timedelta(days=expires_days)

    # 设置访问密码
    if access_password:
        share.access_password = access_password

    # 设置最大访问次数
    if max_access:
        share.max_access = max_access

    db.session.add(share)
    db.session.commit()

    # 生成分享链接
    share_url = url_for('gallery.shared_photo', token=share.share_token, _external=True)

    return jsonify({
        'success': True,
        'share_url': share_url,
        'share_token': share.share_token
    })


# ==================== 共享空间 ====================
# 注意：更具体的路由必须在通用路由之前

@bp.route('/shared/<int:photo_id>', methods=['GET', 'POST'])
@login_required
def shared_detail(photo_id):
    """
    共享图片详情页 - 检查密码后显示
    """
    photo = Photo.query.options(
        joinedload(Photo.user)
    ).get_or_404(photo_id)

    # 验证图片是否公开
    if not photo.is_public:
        flash('该图片未公开分享', 'warning')
        return redirect(url_for('gallery.shared'))

    # 检查访问密码
    if photo.access_password:
        session_key = f'shared_photo_{photo_id}'
        if session.get(session_key) != photo.access_password:
            if request.method == 'POST':
                if request.form.get('password') == photo.access_password:
                    session[session_key] = photo.access_password
                    return redirect(url_for('gallery.shared_detail', photo_id=photo_id))
                else:
                    flash('密码错误，请重试', 'danger')
            return render_template('gallery/shared_password.html', photo=photo)

    # 增加浏览次数
    photo.views += 1
    db.session.commit()

    return render_template('gallery/shared_detail.html', photo=photo)


@bp.route('/shared/album/<int:album_id>', methods=['GET', 'POST'])
@login_required
def shared_album_detail(album_id):
    """
    共享相册详情页 - 检查密码后显示所有图片
    """
    album = Album.query.options(
        joinedload(Album.user),
        joinedload(Album.cover_photo)
    ).get_or_404(album_id)

    # 验证相册是否公开
    if not album.is_public:
        flash('该相册未公开分享', 'warning')
        return redirect(url_for('gallery.shared'))

    # 检查访问密码
    if album.access_password:
        session_key = f'shared_album_{album_id}'
        if session.get(session_key) != album.access_password:
            if request.method == 'POST':
                if request.form.get('password') == album.access_password:
                    session[session_key] = album.access_password
                    return redirect(url_for('gallery.shared_album_detail', album_id=album_id))
                else:
                    flash('密码错误，请重试', 'danger')
            return render_template('gallery/shared_album_password.html', album=album)

    # 获取相册中的所有公开图片
    photos = Photo.query.options(
        joinedload(Photo.user)
    ).filter_by(album_id=album_id, is_public=True).order_by(
        Photo.created_at.desc()
    ).all()

    return render_template('gallery/shared_album_detail.html', album=album, photos=photos)


@bp.route('/shared')
@login_required
def shared():
    """
    共享空间 - 显示所有用户公开分享的图片
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = current_app.config.get('PHOTOS_PER_PAGE', 20)

        # 获取所有公开图片，按创建时间倒序
        # 不使用 joinedload，让 SQLAlchemy 自动处理
        photos = Photo.query.filter_by(is_public=True).order_by(
            Photo.created_at.desc()
        ).paginate(page=page, per_page=per_page, error_out=False)

        # 创建空的相册分页对象（模拟 Pagination 接口）
        class EmptyPagination:
            def __init__(self):
                self.items = []
                self.total = 0
                self.pages = 0
                self.page = 1
                self.has_prev = False
                self.has_next = False
                self.prev_num = None
                self.next_num = None
                self.iter_pages = lambda: []

        albums = EmptyPagination()

        return render_template('gallery/shared_space.html', photos=photos, albums=albums)

    except Exception as e:
        # 记录错误并显示友好的错误消息
        current_app.logger.error(f'Error in shared route: {str(e)}')
        flash(f'加载共享空间时出错: {str(e)}', 'danger')

        # 返回一个简化的错误页面
        return render_template('gallery/shared_space.html',
                             photos=type('obj', (object,), {'items': [], 'total': 0, 'pages': 0, 'page': 1,
                                                           'has_prev': False, 'has_next': False,
                                                           'prev_num': None, 'next_num': None,
                                                           'iter_pages': lambda: []})(),
                             albums=type('obj', (object,), {'items': [], 'total': 0, 'pages': 0, 'page': 1,
                                                           'has_prev': False, 'has_next': False,
                                                           'prev_num': None, 'next_num': None,
                                                           'iter_pages': lambda: []})())


@bp.route('/shared/<token>')
def shared_photo(token):
    """
    访问分享的图片（通过token）
    """
    share = PhotoShare.query.filter_by(share_token=token).first_or_404()

    # 检查分享是否有效
    if not share.is_valid:
        flash('此分享链接已失效或已过期', 'warning')
        return redirect(url_for('main.index'))

    # 检查访问密码
    if share.access_password:
        session_key = f'share_password_{share.id}'
        if session.get(session_key) != share.access_password:
            if request.method == 'POST':
                password = request.form.get('password')
                if password == share.access_password:
                    session[session_key] = password
                else:
                    flash('密码错误', 'danger')
                    return render_template('gallery/share_password.html', share=share)

            return render_template('gallery/share_password.html', share=share)

    # 增加访问计数
    share.access_count += 1
    db.session.commit()

    # 增加图片浏览次数
    share.photo.views += 1
    db.session.commit()

    return render_template('gallery/shared_photo.html',
                          share=share,
                          photo=share.photo)


# ==================== 批量操作 ====================

@bp.route('/batch/move', methods=['POST'])
@login_required
def batch_move():
    """
    批量移动图片
    """
    photo_ids = request.json.get('photo_ids', [])
    target_album_id = request.json.get('album_id')

    # 验证目标相册
    if target_album_id:
        target_album = Album.query.get(target_album_id)
        if not target_album or target_album.user_id != current_user.id:
            return jsonify({'success': False, 'message': '目标相册不存在'}), 404

    # 获取图片并检查权限
    photos = Photo.query.filter(
        Photo.id.in_(photo_ids),
        Photo.user_id == current_user.id
    ).all()

    for photo in photos:
        photo.album_id = target_album_id

    db.session.commit()

    return jsonify({'success': True, 'message': f'已移动 {len(photos)} 张图片'})


@bp.route('/batch/delete', methods=['POST'])
@login_required
def batch_delete():
    """
    批量删除图片
    """
    try:
        photo_ids = request.json.get('photo_ids', [])

        if not photo_ids:
            return jsonify({'success': False, 'message': '未选择任何图片'}), 400

        # 超级管理员检查
        is_superuser = getattr(current_user, 'is_superuser', False)

        # 构建查询条件
        query = Photo.query.filter(Photo.id.in_(photo_ids))
        if not is_superuser:
            query = query.filter_by(user_id=current_user.id)

        photos = query.all()

        deleted_count = 0
        for photo in photos:
            # 先删除关联的分享记录
            from app.models.album import PhotoShare
            PhotoShare.query.filter_by(photo_id=photo.id).delete()

            # 删除关联的标签关系
            photo.tags.clear()

            # 删除文件
            delete_photo_file(photo)

            # 删除数据库记录
            db.session.delete(photo)
            deleted_count += 1

        db.session.commit()

        return jsonify({'success': True, 'message': f'已删除 {deleted_count} 张图片'})

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'批量删除图片失败: {str(e)}', exc_info=True)
        return jsonify({'success': False, 'message': f'删除失败，请稍后重试'}), 500


@bp.route('/batch/share', methods=['POST'])
@login_required
def batch_share():
    """
    批量设置图片为公开/私密
    """
    photo_ids = request.json.get('photo_ids', [])
    is_public = request.json.get('is_public', False)

    # 获取图片并检查权限
    Photo.query.filter(
        Photo.id.in_(photo_ids),
        Photo.user_id == current_user.id
    ).update({'is_public': is_public})

    db.session.commit()

    return jsonify({'success': True, 'message': f'已更新 {len(photo_ids)} 张图片'})


@bp.route('/migrate-urls', methods=['POST'])
@login_required
def migrate_urls():
    """
    迁移图片URL格式
    - direction='to_raw': 从 jsDelivr CDN 迁移到 GitHub raw
    - direction='to_cdn': 从 GitHub raw 迁移到 jsDelivr CDN
    """
    # 只允许超级管理员执行
    is_superuser = getattr(current_user, 'is_superuser', False)
    if not is_superuser:
        return jsonify({'success': False, 'message': '需要超级管理员权限'}), 403

    direction = request.json.get('direction', 'to_cdn')

    try:
        migrated = 0

        if direction == 'to_cdn':
            # 从 GitHub raw 迁移到 jsDelivr CDN
            photos = Photo.query.filter(Photo.file_path.like('https://raw.githubusercontent.com/%')).all()
            for photo in photos:
                # Raw: https://raw.githubusercontent.com/user/repo/branch/path/file
                # CDN: https://cdn.jsdelivr.net/gh/user/repo@branch/path/file
                old_url = photo.file_path
                match = re.match(r'https://raw\.githubusercontent\.com/([^/]+)/([^/]+)/([^/]+)/(.+)', old_url)
                if match:
                    repo = f"{match.group(1)}/{match.group(2)}"
                    branch = match.group(3)
                    path = match.group(4)
                    new_url = f'https://cdn.jsdelivr.net/gh/{repo}@{branch}/{path}'

                    photo.file_path = new_url
                    migrated += 1

                    # 同样更新缩略图 URL
                    if photo.thumbnail_path and photo.thumbnail_path.startswith('https://raw.githubusercontent.com/'):
                        match_thumb = re.match(r'https://raw\.githubusercontent\.com/([^/]+)/([^/]+)/([^/]+)/(.+)', photo.thumbnail_path)
                        if match_thumb:
                            repo = f"{match_thumb.group(1)}/{match_thumb.group(2)}"
                            branch = match_thumb.group(3)
                            path = match_thumb.group(4)
                            photo.thumbnail_path = f'https://cdn.jsdelivr.net/gh/{repo}@{branch}/{path}'

        else:  # to_raw
            # 从 jsDelivr CDN 迁移到 GitHub raw
            photos = Photo.query.filter(Photo.file_path.like('https://cdn.jsdelivr.net/%')).all()
            for photo in photos:
                # CDN: https://cdn.jsdelivr.net/gh/user/repo@branch/path/file
                # Raw: https://raw.githubusercontent.com/user/repo/branch/path/file
                old_url = photo.file_path
                match = re.match(r'https://cdn\.jsdelivr\.net/gh/([^@]+)@([^/]+)/(.+)', old_url)
                if match:
                    repo = match.group(1)
                    branch = match.group(2)
                    path = match.group(3)
                    new_url = f'https://raw.githubusercontent.com/{repo}/{branch}/{path}'

                    photo.file_path = new_url
                    migrated += 1

                    # 同样更新缩略图 URL
                    if photo.thumbnail_path and photo.thumbnail_path.startswith('https://cdn.jsdelivr.net/'):
                        match_thumb = re.match(r'https://cdn\.jsdelivr\.net/gh/([^@]+)@([^/]+)/(.+)', photo.thumbnail_path)
                        if match_thumb:
                            repo = match_thumb.group(1)
                            branch = match_thumb.group(2)
                            path = match_thumb.group(3)
                            photo.thumbnail_path = f'https://raw.githubusercontent.com/{repo}/{branch}/{path}'

        db.session.commit()

        return jsonify({
            'success': True,
            'migrated': migrated,
            'message': f'已迁移 {migrated} 张图片的URL'
        })

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'URL迁移失败: {str(e)}')
        return jsonify({'success': False, 'message': f'迁移失败: {str(e)}'}), 500
