"""
Flask 应用工厂模块

该模块负责创建和配置 Flask 应用实例，包括：
- 数据库配置
- 扩展初始化
- 蓝图注册
- 安全配置
"""

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# 初始化扩展
db = SQLAlchemy()
login_manager = LoginManager()


def create_app(config_name='default'):
    """
    创建 Flask 应用工厂

    Args:
        config_name: 配置名称 ('default', 'development', 'production', 'testing')

    Returns:
        Flask: 配置好的应用实例
    """
    app = Flask(__name__)

    # 安全配置 - 使用环境变量
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-请在生产环境修改')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///blog.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # 安全头部
    app.config['SESSION_COOKIE_SECURE'] = os.environ.get('SESSION_SECURE', 'False') == 'True'
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

    # 初始化扩展
    _init_extensions(app)

    # 注册蓝图
    _register_blueprints(app)

    # 创建数据库表
    _init_database(app)

    return app


def _init_extensions(app):
    """初始化 Flask 扩展"""
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = '请先登录'


def _register_blueprints(app):
    """注册所有蓝图"""
    from app.routes import auth, main, admin, export

    app.register_blueprint(auth.bp)
    app.register_blueprint(main.bp)
    app.register_blueprint(admin.bp)
    app.register_blueprint(export.bp)


def _init_database(app):
    """
    初始化数据库表

    在应用上下文中创建所有定义的数据库表。
    仅在表不存在时创建，不会丢失已有数据。
    """
    with app.app_context():
        db.create_all()
