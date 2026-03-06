"""
相册路由模块

简化的相册功能：
- 相册列表
- 相册详情
- 创建相册
- 上传图片
- 删除图片/相册
"""

import os
import uuid
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from sqlalchemy.orm import joinedload

from app.models.gallery import Album, Photo
from app import db, csrf
from app.utils.storage import get_storage

bp = Blueprint('gallery', __name__, url_prefix='/gallery')

# 允许的图片扩展名
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}


def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def generate_unique_filename(filename):
    """生成唯一的文件名"""
    name, ext = os.path.splitext(filename)
    unique_id = uuid.uuid4().hex[:12]
    return f"{unique_id}{ext}"


# ==================== 相册列表 ====================

@bp.route('/')
@login_required
def index():
    """相册首页"""
    try:
        # 获取当前用户的所有相册
        albums = Album.query.filter_by(user_id=current_user.id)\
            .order_by(Album.updated_at.desc()).all()

        # 统计信息
        total_albums = len(albums)
        total_photos = Photo.query.filter_by(user_id=current_user.id).count()

        return render_template('gallery/index.html',
                              albums=albums,
                              total_albums=total_albums,
                              total_photos=total_photos)
    except Exception as e:
        current_app.logger.error(f'加载相册列表失败: {str(e)}', exc_info=True)
        flash('加载相册列表失败', 'danger')
        return render_template('gallery/index.html',
                              albums=[],
                              total_albums=0,
                              total_photos=0)


# ==================== 创建相册 ====================

@bp.route('/album/new', methods=['GET', 'POST'])
@login_required
def new_album():
    """创建新相册"""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        is_public = request.form.get('is_public') == 'on'

        if not name:
            flash('相册名称不能为空', 'danger')
            return redirect(url_for('gallery.index'))

        try:
            album = Album(
                name=name,
                description=description,
                user_id=current_user.id,
                is_public=is_public
            )
            db.session.add(album)
            db.session.commit()
            flash('相册创建成功', 'success')
            return redirect(url_for('gallery.index'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'创建相册失败: {str(e)}', exc_info=True)
            flash('创建相册失败', 'danger')

    return render_template('gallery/new_album.html')


# ==================== 查看相册 ====================

@bp.route('/album/<int:album_id>')
@login_required
def view_album(album_id):
    """查看相册详情"""
    try:
        album = Album.query.options(joinedload(Album.user)).get_or_404(album_id)

        # 权限检查
        if album.user_id != current_user.id and not album.is_public:
            flash('您没有权限访问此相册', 'warning')
            return redirect(url_for('gallery.index'))

        # 获取图片
        photos = Photo.query.filter_by(album_id=album_id)\
            .order_by(Photo.created_at.desc()).all()

        return render_template('gallery/view_album.html',
                              album=album,
                              photos=photos,
                              is_owner=(album.user_id == current_user.id))
    except Exception as e:
        current_app.logger.error(f'查看相册失败: {str(e)}', exc_info=True)
        flash('加载相册失败', 'danger')
        return redirect(url_for('gallery.index'))


# ==================== 编辑相册 ====================

@bp.route('/album/<int:album_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_album(album_id):
    """编辑相册"""
    album = Album.query.get_or_404(album_id)

    # 权限检查
    if album.user_id != current_user.id:
        flash('您没有权限编辑此相册', 'danger')
        return redirect(url_for('gallery.index'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        is_public = request.form.get('is_public') == 'on'

        if not name:
            flash('相册名称不能为空', 'danger')
            return redirect(url_for('gallery.edit_album', album_id=album_id))

        try:
            album.name = name
            album.description = description
            album.is_public = is_public
            db.session.commit()
            flash('相册更新成功', 'success')
            return redirect(url_for('gallery.view_album', album_id=album_id))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'更新相册失败: {str(e)}', exc_info=True)
            flash('更新相册失败', 'danger')

    return render_template('gallery/edit_album.html', album=album)


# ==================== 删除相册 ====================

@bp.route('/album/<int:album_id>/delete', methods=['POST'])
@login_required
@csrf.exempt
def delete_album(album_id):
    """删除相册"""
    try:
        album = Album.query.get(album_id)
        if not album:
            return jsonify({'success': False, 'message': '相册不存在'}), 404

        # 权限检查
        if album.user_id != current_user.id:
            return jsonify({'success': False, 'message': '您没有权限删除此相册'}), 403

        # 删除相册（会级联删除照片）
        db.session.delete(album)
        db.session.commit()

        return jsonify({'success': True, 'message': '相册已删除'})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'删除相册失败: {str(e)}', exc_info=True)
        return jsonify({'success': False, 'message': '删除失败'}), 500


# ==================== 上传图片 ====================

@bp.route('/album/<int:album_id>/upload', methods=['POST'])
@login_required
def upload_photos(album_id):
    """上传图片到相册"""
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

            # 上传文件
            file.seek(0)
            if storage.upload_fileobj(file, object_name):
                image_url = storage.get_url(object_name)

                # 保存图片信息
                photo = Photo(
                    filename=file.filename,
                    file_path=image_url,
                    file_size=0,  # 简化处理，不获取文件大小
                    album_id=album_id,
                    user_id=current_user.id,
                    mime_type=file.mimetype
                )
                db.session.add(photo)
                uploaded.append(file.filename)
            else:
                failed.append({'filename': file.filename, 'error': '上传失败'})

        except Exception as e:
            current_app.logger.error(f'上传图片失败: {str(e)}')
            failed.append({'filename': file.filename, 'error': str(e)})

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()

    return jsonify({
        'success': True,
        'uploaded': len(uploaded),
        'failed': len(failed),
        'message': f'成功上传 {len(uploaded)} 张图片'
    })


# ==================== 删除图片 ====================

@bp.route('/photo/<int:photo_id>/delete', methods=['POST'])
@login_required
@csrf.exempt
def delete_photo(photo_id):
    """删除图片"""
    try:
        photo = Photo.query.get(photo_id)
        if not photo:
            return jsonify({'success': False, 'message': '图片不存在'}), 404

        # 权限检查
        if photo.user_id != current_user.id:
            return jsonify({'success': False, 'message': '您没有权限删除此图片'}), 403

        db.session.delete(photo)
        db.session.commit()

        return jsonify({'success': True, 'message': '图片已删除'})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'删除图片失败: {str(e)}', exc_info=True)
        return jsonify({'success': False, 'message': '删除失败'}), 500
