"""
相册数据模型模块

简化的相册系统，包含：
- Album: 相册
- Photo: 图片
"""

from datetime import datetime
from app import db


class Album(db.Model):
    """相册模型"""
    __tablename__ = 'gallery_album'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    is_public = db.Column(db.Boolean, default=False)
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
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 关系
    user = db.relationship('User', backref=db.backref('gallery_photos', lazy='dynamic'))

    @property
    def display_name(self):
        """获取显示名称（优先使用标题，否则使用文件名）"""
        return self.title if self.title else self.filename

    def __repr__(self):
        return f'<Photo {self.filename}>'
