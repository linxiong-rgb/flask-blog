"""
文章收藏数据模型
"""

from datetime import datetime
from app import db


class PostBookmark(db.Model):
    """文章收藏模型"""
    __tablename__ = 'post_bookmark'

    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 关系 - post属性由Post模型的backref自动创建
    user = db.relationship('User', backref='user_bookmarks')

    # 唯一约束：同一用户不能重复收藏同一文章
    __table_args__ = (db.UniqueConstraint('post_id', 'user_id', name='unique_post_user_bookmark'),)

    def __repr__(self):
        return f'<PostBookmark post_id={self.post_id} user_id={self.user_id}>'
