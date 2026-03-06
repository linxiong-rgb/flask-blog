"""
相册数据模型模块

简化的相册系统，包含：
- Album: 相册
- Photo: 图片

访问权限说明：
- 私有相册/图片：仅所有者可访问
- 公开相册/图片：所有登录用户可访问
- 密码保护：需要输入正确密码才能访问
"""

from datetime import datetime
from app import db
from sqlalchemy import inspect


class Album(db.Model):
    """相册模型"""
    __tablename__ = 'gallery_album'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    # 注意：is_public 和 access_password 字段可能不存在于旧数据库
    # 这些字段由迁移脚本动态添加
    is_public = db.Column(db.Boolean, default=False, nullable=True)
    access_password = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    user = db.relationship('User', backref=db.backref('gallery_albums', lazy='dynamic', cascade='all, delete-orphan'))
    photos = db.relationship('Photo', backref=db.backref('album', lazy='joined'), lazy='dynamic',
                           cascade='all, delete-orphan',
                           foreign_keys='[Photo.album_id]')

    @property
    def photo_count(self):
        """获取相册中的图片数量"""
        return self.photos.count()

    @property
    def cover_url(self):
        """获取封面图片URL"""
        cover = self.photos.order_by(Photo.created_at.desc()).first()
        return cover.file_path if cover else '/static/img/no-image.png'

    @property
    def has_password(self):
        """是否设置了访问密码"""
        try:
            return bool(getattr(self, 'access_password', None))
        except:
            return False

    def can_access(self, user):
        """检查用户是否有权限访问此相册"""
        # 所有者可以访问
        if user.is_authenticated and user.id == self.user_id:
            return True
        # 私有相册只有所有者可访问
        try:
            is_public = getattr(self, 'is_public', False)
        except:
            is_public = False
        if not is_public:
            return False
        # 公开相册所有登录用户可访问
        return user.is_authenticated

    def __repr__(self):
        return f'<Album {self.name}>'


class Photo(db.Model):
    """图片模型"""
    __tablename__ = 'gallery_photo'

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    title = db.Column(db.String(200))  # 图片主题/标题
    album_id = db.Column(db.Integer, db.ForeignKey('gallery_album.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    is_public = db.Column(db.Boolean, default=False)  # 是否公开
    access_password = db.Column(db.String(100))  # 访问密码（可选）
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 关系
    user = db.relationship('User', backref=db.backref('gallery_photos', lazy='dynamic'))

    @property
    def display_name(self):
        """获取显示名称（优先使用标题，否则使用文件名）"""
        return self.title if self.title else self.filename

    @property
    def has_password(self):
        """是否设置了访问密码"""
        try:
            return bool(getattr(self, 'access_password', None))
        except:
            return False

    def can_access(self, user, session_passwords=None):
        """
        检查用户是否有权限访问此图片

        Args:
            user: 当前用户对象
            session_passwords: session 中已验证的密码字典 {photo_id: password}

        Returns:
            bool: 是否有权限访问
        """
        # 所有者可以访问
        if user.is_authenticated and user.id == self.user_id:
            return True

        # 检查是否在 session 中已验证过密码
        if session_passwords and str(self.id) in session_passwords:
            return True

        # 私有图片只有所有者可访问
        try:
            is_public = getattr(self, 'is_public', False)
        except:
            is_public = False
        if not is_public:
            return False

        # 公开图片所有登录用户可访问
        return user.is_authenticated

    def __repr__(self):
        return f'<Photo {self.filename}>'
