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
    'small': (150, 150),
    'medium': (300, 300),
    'large': (800, 600)
}


def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def generate_unique_filename(filename):
    """生成唯一的文件名"""
    name, ext = os.path.splitext(filename)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    random_str = secrets.token_hex(4)
    return f"{timestamp}_{random_str}{ext}"


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


# ==================== 相册管理 ====================

@bp.route('/')
@login_required
def index():
    """
    相册首页

    显示当前用户的所有相册（树形结构）
    """
    # 获取根相册（没有父相册的）
    root_albums = Album.query.filter_by(
        user_id=current_user.id,
        parent_id=None
    ).order_by(Album.sort_order, Album.name).all()

    # 统计信息
    total_photos = Photo.query.filter_by(user_id=current_user.id).count()
    total_albums = Album.query.filter_by(user_id=current_user.id).count()

    return render_template('gallery/index.html',
                          root_albums=root_albums,
                          total_photos=total_photos,
                          total_albums=total_albums)


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
    """
    album = Album.query.get_or_404(album_id)

    # 权限检查
    if album.user_id != current_user.id:
        flash('您没有权限访问此相册')
        return redirect(url_for('gallery.index'))

    # 获取相册中的图片
    photos = Photo.query.filter_by(album_id=album_id).order_by(Photo.created_at.desc()).all()

    # 获取子相册
    child_albums = Album.query.filter_by(parent_id=album_id).order_by(Album.sort_order, Album.name).all()

    return render_template('gallery/view_album.html',
                          album=album,
                          photos=photos,
                          child_albums=child_albums)


@bp.route('/album/<int:album_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_album(album_id):
    """
    编辑相册

    GET: 显示编辑表单
    POST: 处理更新请求
    """
    album = Album.query.get_or_404(album_id)

    # 权限检查
    if album.user_id != current_user.id:
        flash('您没有权限编辑此相册')
        return redirect(url_for('gallery.index'))

    if request.method == 'POST':
        album.name = request.form.get('name')
        album.description = request.form.get('description')
        album.is_private = request.form.get('is_private') == 'on'

        db.session.commit()
        flash('相册更新成功')
        return redirect(url_for('gallery.view_album', album_id=album_id))

    parent_albums = Album.query.filter_by(
        user_id=current_user.id
    ).filter(
        Album.id != album_id  # 不能选择自己作为父相册
    ).all()

    return render_template('gallery/edit_album.html',
                          album=album,
                          parent_albums=parent_albums)


@bp.route('/album/<int:album_id>/delete', methods=['POST'])
@login_required
def delete_album(album_id):
    """
    删除相册

    注意：会删除相册中的所有图片
    """
    album = Album.query.get_or_404(album_id)

    # 权限检查
    if album.user_id != current_user.id:
        return jsonify({'success': False, 'message': '您没有权限删除此相册'}), 403

    try:
        # 删除相册中的所有图片文件
        for photo in album.photos:
            delete_photo_file(photo)

        db.session.delete(album)
        db.session.commit()

        return jsonify({'success': True, 'message': '相册已删除'})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'删除相册失败: {str(e)}')
        return jsonify({'success': False, 'message': '删除失败'}), 500


# ==================== 图片上传 ====================

@bp.route('/album/<int:album_id>/upload', methods=['POST'])
@login_required
def upload_photos(album_id):
    """
    上传图片到相册

    支持单张和多张上传
    """
    album = Album.query.get_or_404(album_id)

    # 权限检查
    if album.user_id != current_user.id:
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
    """删除图片文件"""
    try:
        storage = get_storage()
        # 从URL中提取文件名并删除
        if photo.file_path:
            filename = photo.file_path.split('/')[-1]
            storage.delete_file(f'gallery/{photo.user_id}/{filename}')
        if photo.thumbnail_path and photo.thumbnail_path != photo.file_path:
            thumb_filename = photo.thumbnail_path.split('/')[-1]
            storage.delete_file(f'gallery/{photo.user_id}/thumbnails/{thumb_filename}')
    except Exception as e:
        current_app.logger.error(f'删除图片文件失败: {str(e)}')


@bp.route('/photo/<int:photo_id>/delete', methods=['POST'])
@login_required
def delete_photo(photo_id):
    """
    删除图片
    """
    photo = Photo.query.get_or_404(photo_id)

    # 权限检查
    if photo.user_id != current_user.id:
        return jsonify({'success': False, 'message': '您没有权限删除此图片'}), 403

    try:
        delete_photo_file(photo)
        db.session.delete(photo)
        db.session.commit()

        return jsonify({'success': True, 'message': '图片已删除'})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'删除图片失败: {str(e)}')
        return jsonify({'success': False, 'message': '删除失败'}), 500


@bp.route('/photo/<int:photo_id>/move', methods=['POST'])
@login_required
def move_photo(photo_id):
    """
    移动图片到其他相册
    """
    photo = Photo.query.get_or_404(photo_id)
    target_album_id = request.json.get('album_id')

    # 权限检查
    if photo.user_id != current_user.id:
        return jsonify({'success': False, 'message': '您没有权限移动此图片'}), 403

    # 验证目标相册
    if target_album_id:
        target_album = Album.query.get(target_album_id)
        if not target_album or target_album.user_id != current_user.id:
            return jsonify({'success': False, 'message': '目标相册不存在'}), 404

    photo.album_id = target_album_id
    db.session.commit()

    return jsonify({'success': True, 'message': '图片已移动'})


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


@bp.route('/shared/<token>')
def shared_photo(token):
    """
    访问分享的图片
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


# ==================== 共享空间 ====================

@bp.route('/shared')
@login_required
def shared_space():
    """
    共享空间

    显示所有用户公开分享的图片
    """
    # 分页
    page = request.args.get('page', 1, type=int)
    per_page = 20

    # 获取所有公开的图片，预加载用户信息
    photos = Photo.query.options(
        joinedload(Photo.user)
    ).filter_by(is_public=True).order_by(
        Photo.created_at.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)

    return render_template('gallery/shared_space.html', photos=photos)


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
    photo_ids = request.json.get('photo_ids', [])

    # 获取图片并检查权限
    photos = Photo.query.filter(
        Photo.id.in_(photo_ids),
        Photo.user_id == current_user.id
    ).all()

    for photo in photos:
        delete_photo_file(photo)
        db.session.delete(photo)

    db.session.commit()

    return jsonify({'success': True, 'message': f'已删除 {len(photos)} 张图片'})


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
