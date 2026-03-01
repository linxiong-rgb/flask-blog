"""
Flask 应用工厂模块

该模块负责创建和配置 Flask 应用实例，包括：
- 数据库配置
- 扩展初始化
- 蓝图注册
- 安全配置
"""

import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_caching import Cache
from config import get_config

# 初始化扩展
db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()
cache = Cache()


def create_app(config_name='default'):
    """
    创建 Flask 应用工厂

    Args:
        config_name: 配置名称 ('default', 'development', 'production', 'testing')

    Returns:
        Flask: 配置好的应用实例
    """
    app = Flask(__name__)

    # 加载配置
    config_class = get_config(config_name)
    app.config.from_object(config_class)

    # 初始化扩展
    _init_extensions(app)

    # 注册蓝图
    _register_blueprints(app)

    # 配置日志
    _init_logging(app)

    # 创建数据库表
    _init_database(app)

    # 注册 CLI 命令
    _register_commands(app)

    return app


def _register_commands(app):
    """注册 CLI 命令"""
    @app.cli.command()
    def publish_scheduled():
        """发布定时文章"""
        from app.utils.scheduler import publish_scheduled_posts
        import click

        with app.app_context():
            count = publish_scheduled_posts()
            if count == 0:
                click.echo('没有需要发布的定时文章')
            elif count > 0:
                click.echo(f'成功发布 {count} 篇文章')
            else:
                click.echo('发布定时文章时出错', err=True)

    @app.cli.command()
    def scheduled_stats():
        """显示定时文章统计"""
        from app.utils.scheduler import get_scheduled_posts_stats
        import click

        with app.app_context():
            stats = get_scheduled_posts_stats()
            click.echo(f'定时文章总数: {stats["total_scheduled"]}')
            click.echo(f'即将发布(24小时内): {stats["publishing_soon"]}')


def _init_extensions(app):
    """初始化 Flask 扩展"""
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    # 配置缓存
    cache.init_app(app)

    login_manager.login_view = 'auth.login'
    login_manager.login_message = '请先登录'


def _register_blueprints(app):
    """注册所有蓝图"""
    from app.routes import auth, main, admin, export

    app.register_blueprint(auth.bp)
    app.register_blueprint(main.bp)
    app.register_blueprint(admin.bp)
    app.register_blueprint(export.bp)


def _init_logging(app):
    """配置日志系统"""
    # 创建 logs 目录
    log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # 配置日志格式
    formatter = logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    )

    # 文件日志处理器 - 自动轮转
    file_handler = RotatingFileHandler(
        os.path.join(log_dir, 'app.log'),
        maxBytes=10485760,  # 10MB
        backupCount=10
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)

    # 错误日志处理器
    error_handler = RotatingFileHandler(
        os.path.join(log_dir, 'error.log'),
        maxBytes=10485760,  # 10MB
        backupCount=10
    )
    error_handler.setFormatter(formatter)
    error_handler.setLevel(logging.ERROR)

    # 控制台日志处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.DEBUG if app.debug else logging.INFO)

    # 添加处理器
    app.logger.addHandler(file_handler)
    app.logger.addHandler(error_handler)
    app.logger.addHandler(console_handler)

    # 设置日志级别
    app.logger.setLevel(logging.DEBUG if app.debug else logging.INFO)

    app.logger.info('博客应用启动')


def _init_database(app):
    """
    初始化数据库表

    在应用上下文中创建所有定义的数据库表。
    仅在表不存在时创建，不会丢失已有数据。
    """
    try:
        with app.app_context():
            db.create_all()
    except Exception as e:
        # 表已存在或其他错误，忽略
        app.logger.debug(f'Database creation info: {e}')
        pass
