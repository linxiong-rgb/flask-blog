"""
用户数据模型模块

该模块定义用户相关的数据模型：
- User: 用户模型（集成 Flask-Login）
- load_user: Flask-Login 用户加载器
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager


class User(UserMixin, db.Model):
    """
    用户模型

    继承 UserMixin 以支持 Flask-Login 的默认方法：
    - is_authenticated
    - is_active
    - is_anonymous
    - get_id()

    Attributes:
        id: 用户唯一标识
        username: 用户名（唯一）
        email: 邮箱（唯一）
        password_hash: 密码哈希值（不存储明文密码）
        posts: 用户创建的所有文章
        created_at: 账号创建时间
    """

    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255))
    posts = db.relationship('Post', backref='author', lazy=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 密码重置相关字段
    reset_token = db.Column(db.String(100), unique=True, nullable=True)
    reset_token_expires = db.Column(db.DateTime, nullable=True)

    def set_password(self, password):
        """
        设置用户密码

        使用 werkzeug 的安全哈希算法存储密码

        Args:
            password (str): 明文密码
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """
        验证用户密码

        Args:
            password (str): 明文密码

        Returns:
            bool: 密码是否正确
        """
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


@login_manager.user_loader
def load_user(user_id):
    """
    Flask-Login 用户加载器

    根据用户ID从数据库加载用户对象

    Args:
        user_id: 用户ID

    Returns:
        User|None: 用户对象，如果不存在则返回 None
    """
    return User.query.get(int(user_id))
