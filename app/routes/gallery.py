"""
相册路由模块

简化的相册功能：
- 相册列表（我的相册 + 公开相册）
- 相册详情（支持密码保护）
- 创建相册（支持公开和密码保护）
- 上传图片
- 编辑图片（支持公开和密码保护）
- 删除图片/相册

访问权限说明：
- 私有相册/图片：仅所有者可访问
- 公开相册/图片：所有登录用户可访问
- 密码保护：需要输入正确密码才能访问
"""

import os
import uuid
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app, session
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
    """相册首页 - 显示我的相册和公开相册"""
    # 我的相册
    my_albums = Album.query.filter_by(user_id=current_user.id)\
        .order_by(Album.updated_at.desc()).all()

    # 其他用户的相册（需要在 Python 中过滤公开相册）
    all_other_albums = Album.query.filter(Album.user_id != current_user.id)\
        .options(joinedload(Album.user))\
        .order_by(Album.updated_at.desc()).all()
    # 过滤出公开的相册
    public_albums = []
    for album in all_other_albums:
        if getattr(album, 'is_public', False):
            public_albums.append(album)

    total_albums = len(my_albums)
    total_photos = Photo.query.filter_by(user_id=current_user.id).count()

    # 为所有相册添加安全的属性访问
    for album in my_albums + public_albums:
        album._is_public = getattr(album, 'is_public', False)
        album._has_password = getattr(album, 'has_password', False)

    return render_template('gallery/index.html',
                          my_albums=my_albums,
                          public_albums=public_albums,
                          total_albums=total_albums,
                          total_photos=total_photos)


@bp.route('/public')
@login_required
def public_albums():
    """所有公开相册页面"""
    all_albums = Album.query.options(joinedload(Album.user))\
        .order_by(Album.updated_at.desc()).all()

    # 过滤出公开的相册
    albums = []
    for album in all_albums:
        if getattr(album, 'is_public', False):
            album._is_public = True
            album._has_password = getattr(album, 'has_password', False)
            albums.append(album)

    return render_template('gallery/public_albums.html',
                          albums=albums,
                          total_albums=len(albums))


# ==================== 创建相册 ====================

@bp.route('/album/new', methods=['GET', 'POST'])
@login_required
def new_album():
    """创建新相册"""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        is_public = request.form.get('is_public') == 'on'
        access_password = request.form.get('access_password', '').strip() or None

        if not name:
            flash('相册名称不能为空', 'danger')
            return redirect(url_for('gallery.index'))

        album = Album(
            name=name,
            description=description,
            user_id=current_user.id,
            is_public=is_public,
            access_password=access_password
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
    is_owner = (album.user_id == current_user.id)

    # 为相册添加安全的属性访问
    album._is_public = getattr(album, 'is_public', False)
    album._has_password = getattr(album, 'has_password', False)

    # 安全地获取访问密码
    album_password = getattr(album, 'access_password', None)
    session_key = f'album_password_{album_id}'
    password_verified = session.get(session_key) == album_password

    # 权限检查
    if not is_owner:
        album_is_public = getattr(album, 'is_public', False)
        if not album_is_public:
            flash('您没有权限访问此相册', 'warning')
            return redirect(url_for('gallery.index'))
        # 密码保护的相册
        if album._has_password and not password_verified:
            return render_template('gallery/album_password.html', album=album)

    # 查询相册中的图片
    # 所有者可以看到所有图片，其他用户只能看到公开的图片
    if is_owner:
        photos = Photo.query.filter_by(album_id=album_id)\
            .order_by(Photo.created_at.desc()).all()
    else:
        photos = Photo.query.filter_by(album_id=album_id)\
            .order_by(Photo.created_at.desc()).all()
        # 过滤出公开的图片
        photos = [p for p in photos if getattr(p, 'is_public', False)]

    # 获取已验证的图片密码
    verified_photo_passwords = session.get('verified_photo_passwords', {})

    # 为每张照片添加安全的属性访问
    for photo in photos:
        photo._is_public = getattr(photo, 'is_public', False)
        photo._has_password = getattr(photo, 'has_password', False)

    return render_template('gallery/view_album.html',
                          album=album,
                          photos=photos,
                          is_owner=is_owner,
                          verified_photo_passwords=verified_photo_passwords)


@bp.route('/album/<int:album_id>/verify-password', methods=['POST'])
@login_required
def verify_album_password(album_id):
    """验证相册访问密码"""
    album = Album.query.get_or_404(album_id)

    if album.user_id == current_user.id:
        return jsonify({'success': True, 'message': '所有者无需验证密码'})

    password = request.get_json().get('password', '')

    if not album.has_password:
        return jsonify({'success': True, 'message': '相册未设置密码'})

    # 安全地获取密码
    album_password = getattr(album, 'access_password', None)
    if password == album_password:
        # 在 session 中标记已验证
        session[f'album_password_{album_id}'] = password
        return jsonify({'success': True, 'message': '密码验证成功'})
    else:
        return jsonify({'success': False, 'message': '密码错误'}), 401


# ==================== 编辑相册 ====================

@bp.route('/album/<int:album_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_album(album_id):
    """编辑相册"""
    album = Album.query.get_or_404(album_id)

    if album.user_id != current_user.id:
        flash('您没有权限编辑此相册', 'danger')
        return redirect(url_for('gallery.index'))

    # 为相册添加安全的属性访问（用于模板显示）
    album._is_public = getattr(album, 'is_public', False)
    album._has_password = getattr(album, 'has_password', False)
    # 暴露当前密码给模板（用于编辑时显示）
    album.access_password = getattr(album, 'access_password', '')

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        is_public = request.form.get('is_public') == 'on'
        access_password = request.form.get('access_password', '').strip()
        clear_password = request.form.get('clear_password') == '1'

        if not name:
            flash('相册名称不能为空', 'danger')
            return redirect(url_for('gallery.edit_album', album_id=album_id))

        album.name = name
        album.description = description
        album.is_public = is_public

        # 处理密码更新
        if clear_password:
            # 清除密码
            album.access_password = None
        elif access_password:
            # 更新密码
            album.access_password = access_password
        # 如果密码为空且没有清除标记，保持原密码不变

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
                user_id=current_user.id,
                is_public=getattr(album, 'is_public', False)  # 继承相册的公开设置
            )
            db.session.add(photo)
            uploaded.append(file.filename)

    db.session.commit()
    return jsonify({
        'success': True,
        'uploaded': len(uploaded),
        'message': f'成功上传 {len(uploaded)} 张图片'
    })


# ==================== 编辑图片 ====================

@bp.route('/photo/<int:photo_id>/edit', methods=['POST'])
@login_required
@csrf.exempt
def edit_photo(photo_id):
    """编辑图片信息"""
    photo = Photo.query.get_or_404(photo_id)

    if photo.user_id != current_user.id:
        return jsonify({'success': False, 'message': '您没有权限编辑此图片'}), 403

    data = request.get_json()
    title = data.get('title', '').strip()
    is_public = data.get('is_public', False)
    access_password = data.get('access_password', '').strip() or None

    photo.title = title if title else None
    photo.is_public = is_public
    photo.access_password = access_password
    db.session.commit()

    return jsonify({
        'success': True,
        'message': '图片信息已更新',
        'display_name': photo.display_name,
        'is_public': photo.is_public,
        'has_password': photo.has_password
    })


@bp.route('/photo/<int:photo_id>/verify-password', methods=['POST'])
@login_required
def verify_photo_password(photo_id):
    """验证图片访问密码"""
    photo = Photo.query.get_or_404(photo_id)

    if photo.user_id == current_user.id:
        return jsonify({'success': True, 'message': '所有者无需验证密码'})

    password = request.get_json().get('password', '')

    if not photo.has_password:
        return jsonify({'success': True, 'message': '图片未设置密码'})

    # 安全地获取密码
    photo_password = getattr(photo, 'access_password', None)
    if password == photo_password:
        # 在 session 中标记已验证
        if 'verified_photo_passwords' not in session:
            session['verified_photo_passwords'] = {}
        session['verified_photo_passwords'][str(photo_id)] = password
        session.modified = True
        return jsonify({'success': True, 'message': '密码验证成功'})
    else:
        return jsonify({'success': False, 'message': '密码错误'}), 401


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
