"""
云相册数据模型模块

该模块定义云相册的核心数据模型：
- Album: 相册（支持多级目录）
- Photo: 图片（支持EXIF信息、标签）
- PhotoShare: 图片分享（支持分享链接、过期时间）
"""

from datetime import datetime, timedelta
from app import db

# 多对多关系表：图片-标签
photo_tags = db.Table('photo_tags',
    db.Column('photo_id', db.Integer, db.ForeignKey('photo.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('photo_tag.id'), primary_key=True)
)


class PhotoTag(db.Model):
    """图片标签模型"""
    __tablename__ = 'photo_tag'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<PhotoTag {self.name}>'


class Album(db.Model):
    """
    相册模型

    支持多级目录结构
    Attributes:
        id: 相册唯一标识
        name: 相册名称
        description: 相册描述
        user_id: 所属用户ID
        parent_id: 父相册ID（支持多级目录）
        cover_photo_id: 封面图片ID
        is_private: 是否私密（默认True）
        sort_order: 排序顺序
        created_at: 创建时间
        updated_at: 更新时间
    """

    __tablename__ = 'album'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('album.id'), nullable=True)
    cover_photo_id = db.Column(db.Integer, db.ForeignKey('photo.id'), nullable=True)
    is_private = db.Column(db.Boolean, default=True)
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    user = db.relationship('User', backref=db.backref('albums', lazy='dynamic'))
    photos = db.relationship('Photo', backref=db.backref('album', lazy='joined'), lazy='dynamic',
                           cascade='all, delete-orphan',
                           foreign_keys='[Photo.album_id]')
    parent = db.relationship('Album', remote_side=[id], backref=db.backref('children', lazy='dynamic'),
                           foreign_keys=[parent_id])

    @property
    def photo_count(self):
        """获取相册中的图片数量（包括子相册）"""
        count = self.photos.count()
        for child in self.children:
            count += child.photo_count
        return count

    @property
    def path(self):
        """获取相册完整路径"""
        path = [self.name]
        parent = self.parent
        while parent:
            path.insert(0, parent.name)
            parent = parent.parent
        return ' / '.join(path)

    def __repr__(self):
        return f'<Album {self.name}>'


class Photo(db.Model):
    """
    图片模型

    Attributes:
        id: 图片唯一标识
        filename: 原始文件名
        file_path: 存储路径
        file_size: 文件大小（字节）
        width: 图片宽度
        height: 图片高度
        mime_type: MIME类型
        album_id: 所属相册ID
        user_id: 上传用户ID
        title: 图片标题
        description: 图片描述
        exif_data: EXIF数据（JSON格式）
        is_public: 是否公开（在共享空间显示）
        views: 浏览次数
        likes: 点赞次数
        created_at: 上传时间
        taken_at: 拍摄时间（从EXIF读取）
    """

    __tablename__ = 'photo'

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer)
    width = db.Column(db.Integer)
    height = db.Column(db.Integer)
    mime_type = db.Column(db.String(50))
    thumbnail_path = db.Column(db.String(500))

    # 关联
    album_id = db.Column(db.Integer, db.ForeignKey('album.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # 图片信息
    title = db.Column(db.String(200))
    description = db.Column(db.Text)
    exif_data = db.Column(db.JSON)  # 存储EXIF信息

    # 状态
    is_public = db.Column(db.Boolean, default=False)  # 是否在共享空间显示
    access_password = db.Column(db.String(100))  # 访问密码（可选）
    views = db.Column(db.Integer, default=0)
    likes = db.Column(db.Integer, default=0)

    # 时间
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    taken_at = db.Column(db.DateTime)  # 拍摄时间

    # 关系
    user = db.relationship('User', backref=db.backref('photos', lazy='dynamic'))
    tags = db.relationship('PhotoTag', secondary=photo_tags, lazy='subquery',
                          backref=db.backref('photos', lazy='dynamic'))

    @property
    def url(self):
        """获取图片URL"""
        return self.file_path

    @property
    def thumbnail_url(self):
        """获取缩略图URL"""
        return self.thumbnail_path or self.file_path

    @property
    def backup_url(self):
        """获取备用图片URL（CDN和raw互为备份）"""
        import re

        if not self.file_path:
            return self.file_path

        # 如果当前是 jsDelivr CDN URL，返回 GitHub raw URL
        if 'cdn.jsdelivr.net' in self.file_path:
            match = re.match(r'https://cdn\.jsdelivr\.net/gh/([^@]+)@([^/]+)/(.+)', self.file_path)
            if match:
                repo = match.group(1)
                branch = match.group(2)
                path = match.group(3)
                return f'https://raw.githubusercontent.com/{repo}/{branch}/{path}'

        # 如果当前是 GitHub raw URL，返回 jsDelivr CDN URL
        elif 'raw.githubusercontent.com' in self.file_path:
            match = re.match(r'https://raw\.githubusercontent\.com/([^/]+)/([^/]+)/([^/]+)/(.+)', self.file_path)
            if match:
                repo = f"{match.group(1)}/{match.group(2)}"
                branch = match.group(3)
                path = match.group(4)
                return f'https://cdn.jsdelivr.net/gh/{repo}@{branch}/{path}'

        # 其他情况返回原URL
        return self.file_path

    def __repr__(self):
        return f'<Photo {self.filename}>'


class PhotoShare(db.Model):
    """
    图片分享模型

    支持生成临时分享链接
    Attributes:
        id: 分享唯一标识
        share_token: 分享令牌（唯一标识符）
        photo_id: 图片ID
        user_id: 创建用户ID
        expires_at: 过期时间
        access_password: 访问密码
        access_count: 访问次数
        max_access: 最大访问次数
        is_active: 是否有效
        created_at: 创建时间
    """

    __tablename__ = 'photo_share'

    id = db.Column(db.Integer, primary_key=True)
    share_token = db.Column(db.String(64), unique=True, nullable=False, index=True)
    photo_id = db.Column(db.Integer, db.ForeignKey('photo.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    expires_at = db.Column(db.DateTime)
    access_password = db.Column(db.String(100))
    access_count = db.Column(db.Integer, default=0)
    max_access = db.Column(db.Integer)  # 最大访问次数，空表示无限制
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 关系
    photo = db.relationship('Photo', backref=db.backref('shares', lazy='dynamic'))
    user = db.relationship('User', backref=db.backref('photo_shares', lazy='dynamic'))

    @property
    def is_expired(self):
        """检查是否已过期"""
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at

    @property
    def is_access_limit_reached(self):
        """检查是否达到访问次数限制"""
        if self.max_access is None:
            return False
        return self.access_count >= self.max_access

    @property
    def is_valid(self):
        """检查分享链接是否有效"""
        return self.is_active and not self.is_expired and not self.is_access_limit_reached

    def __repr__(self):
        return f'<PhotoShare {self.share_token}>'
