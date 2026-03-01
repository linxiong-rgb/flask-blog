"""
推送订阅数据模型

用于存储 Web Push API 的订阅信息
"""

from app import db
from datetime import datetime


class PushSubscription(db.Model):
    """
    推送订阅模型

    存储用户的浏览器推送订阅信息

    Attributes:
        id: 订阅唯一标识
        endpoint: 推送服务的端点URL
        p256dh: 密钥（用于加密）
        auth: 认证密钥
        user_agent: 用户代理信息（用于识别设备）
        created_at: 订阅时间
    """

    __tablename__ = 'push_subscription'

    id = db.Column(db.Integer, primary_key=True)
    endpoint = db.Column(db.String(500), nullable=False, unique=True)
    p256dh = db.Column(db.String(100), nullable=False)
    auth = db.Column(db.String(100), nullable=False)
    user_agent = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<PushSubscription {self.endpoint[:50]}...>'
