"""
博客数据模型模块

该模块定义博客的核心数据模型：
- Category: 文章分类
- Tag: 文章标签
- Post: 文章（支持多对多标签关系）
"""

from datetime import datetime
from app import db

# 多对多关系表：文章-标签
post_tags = db.Table('post_tags',
    db.Column('post_id', db.Integer, db.ForeignKey('post.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True)
)


class Category(db.Model):
    """
    文章分类模型

    Attributes:
        id: 分类唯一标识
        name: 分类名称（唯一）
        description: 分类描述
        posts: 该分类下的所有文章
        created_at: 创建时间
    """

    __tablename__ = 'category'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(200))
    posts = db.relationship('Post', backref='category', lazy=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Category {self.name}>'


class Tag(db.Model):
    """
    文章标签模型

    Attributes:
        id: 标签唯一标识
        name: 标签名称（唯一）
        created_at: 创建时间
    """

    __tablename__ = 'tag'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Tag {self.name}>'


class Post(db.Model):
    """
    文章模型

    Attributes:
        id: 文章唯一标识
        title: 文章标题
        content: Markdown 格式的文章内容
        summary: 文章摘要（最多300字）
        user_id: 作者ID（外键）
        category_id: 分类ID（外键，可选）
        tags: 文章标签（多对多关系）
        views: 浏览次数
        created_at: 创建时间
        updated_at: 最后更新时间
        published: 是否已发布
        cover_image: 封面图片URL
    """

    __tablename__ = 'post'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    summary = db.Column(db.String(300))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))

    # 多对多关系：文章-标签
    # lazy='dynamic' 允许在 tag.posts 上使用过滤器
    tags = db.relationship('Tag', secondary=post_tags, lazy='subquery',
                          backref=db.backref('posts', lazy='dynamic'))

    views = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published = db.Column(db.Boolean, default=True)
    cover_image = db.Column(db.String(500))

    def __repr__(self):
        return f'<Post {self.title}>'
