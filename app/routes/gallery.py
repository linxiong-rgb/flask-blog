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
    albums = Album.query.filter_by(user_id=current_user.id)\
        .order_by(Album.updated_at.desc()).all()
    total_albums = len(albums)
    total_photos = Photo.query.filter_by(user_id=current_user.id).count()

    return render_template('gallery/index.html',
                          albums=albums,
                          total_albums=total_albums,
                          total_photos=total_photos)


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

    return render_template('gallery/new_album.html')


# ==================== 查看相册 ====================

@bp.route('/album/<int:album_id>')
@login_required
def view_album(album_id):
    """查看相册详情"""
    album = Album.query.options(joinedload(Album.user)).get_or_404(album_id)

    # 权限检查
    if album.user_id != current_user.id and not album.is_public:
        flash('您没有权限访问此相册', 'warning')
        return redirect(url_for('gallery.index'))

    photos = Photo.query.filter_by(album_id=album_id)\
        .order_by(Photo.created_at.desc()).all()

    return render_template('gallery/view_album.html',
                          album=album,
                          photos=photos,
                          is_owner=(album.user_id == current_user.id))


# ==================== 编辑相册 ====================

@bp.route('/album/<int:album_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_album(album_id):
    """编辑相册"""
    album = Album.query.get_or_404(album_id)

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

        album.name = name
        album.description = description
        album.is_public = is_public
        db.session.commit()
        flash('相册更新成功', 'success')
        return redirect(url_for('gallery.view_album', album_id=album_id))

    return render_template('gallery/edit_album.html', album=album)


# ==================== 删除相册 ====================

@bp.route('/album/<int:album_id>/delete', methods=['POST'])
@login_required
@csrf.exempt
def delete_album(album_id):
    """删除相册"""
    album = Album.query.get(album_id)
    if not album:
        return jsonify({'success': False, 'message': '相册不存在'}), 404

    if album.user_id != current_user.id:
        return jsonify({'success': False, 'message': '您没有权限删除此相册'}), 403

    db.session.delete(album)
    db.session.commit()
    return jsonify({'success': True, 'message': '相册已删除'})


# ==================== 上传图片 ====================

@bp.route('/album/<int:album_id>/upload', methods=['POST'])
@login_required
def upload_photos(album_id):
    """上传图片到相册"""
    album = Album.query.get_or_404(album_id)

    if album.user_id != current_user.id:
        return jsonify({'success': False, 'message': '您没有权限上传到此相册'}), 403

    if 'photos' not in request.files:
        return jsonify({'success': False, 'message': '没有选择文件'}), 400

    files = request.files.getlist('photos')
    uploaded = []

    storage = get_storage()

    for file in files:
        if file.filename == '' or not allowed_file(file.filename):
            continue

        # 生成唯一文件名
        filename = generate_unique_filename(file.filename)
        object_name = f'gallery/{current_user.id}/{filename}'

        # 上传文件
        file.seek(0)
        if storage.upload_fileobj(file, object_name):
            photo = Photo(
                filename=file.filename,
                file_path=storage.get_url(object_name),
                album_id=album_id,
                user_id=current_user.id
            )
            db.session.add(photo)
            uploaded.append(file.filename)

    db.session.commit()
    return jsonify({
        'success': True,
        'uploaded': len(uploaded),
        'message': f'成功上传 {len(uploaded)} 张图片'
    })


# ==================== 编辑图片主题 ====================

@bp.route('/photo/<int:photo_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_photo(photo_id):
    """编辑图片主题"""
    photo = Photo.query.get_or_404(photo_id)

    if photo.user_id != current_user.id:
        return jsonify({'success': False, 'message': '您没有权限编辑此图片'}), 403

    if request.method == 'POST':
        data = request.get_json()
        title = data.get('title', '').strip()

        photo.title = title if title else None
        db.session.commit()

        return jsonify({
            'success': True,
            'message': '主题已更新',
            'display_name': photo.display_name
        })

    return jsonify({
        'success': True,
        'photo_id': photo.id,
        'title': photo.title or '',
        'filename': photo.filename
    })


# ==================== 删除图片 ====================

@bp.route('/photo/<int:photo_id>/delete', methods=['POST'])
@login_required
@csrf.exempt
def delete_photo(photo_id):
    """删除图片"""
    photo = Photo.query.get(photo_id)
    if not photo:
        return jsonify({'success': False, 'message': '图片不存在'}), 404

    if photo.user_id != current_user.id:
        return jsonify({'success': False, 'message': '您没有权限删除此图片'}), 403

    db.session.delete(photo)
    db.session.commit()
    return jsonify({'success': True, 'message': '图片已删除'})
