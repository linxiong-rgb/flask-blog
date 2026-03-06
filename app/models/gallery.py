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
    __tablename__ = 'album'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    is_public = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    user = db.relationship('User', backref=db.backref('albums', lazy='dynamic', cascade='all, delete-orphan'))
    photos = db.relationship('Photo', backref=db.backref('album', lazy='joined'), lazy='dynamic',
                           cascade='all, delete-orphan',
                           foreign_keys='[Photo.album_id]')

    @property
    def photo_count(self):
        """获取相册中的图片数量"""
        try:
            return self.photos.count()
        except Exception:
            return 0

    @property
    def cover_url(self):
        """获取封面图片URL"""
        cover = self.photos.order_by(Photo.created_at.desc()).first()
        return cover.file_path if cover else '/static/img/no-image.png'

    def __repr__(self):
        return f'<Album {self.name}>'


class Photo(db.Model):
    """图片模型"""
    __tablename__ = 'photo'

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer)
    width = db.Column(db.Integer)
    height = db.Column(db.Integer)
    mime_type = db.Column(db.String(50))
    album_id = db.Column(db.Integer, db.ForeignKey('album.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 关系
    user = db.relationship('User', backref=db.backref('photos', lazy='dynamic'))

    @property
    def url(self):
        """获取图片URL"""
        return self.file_path

    def __repr__(self):
        return f'<Photo {self.filename}>'
