"""
配置模块

该模块定义不同环境的配置类：
- Config: 基础配置
- DevelopmentConfig: 开发环境配置
- ProductionConfig: 生产环境配置
- TestingConfig: 测试环境配置
"""

import os
import logging
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """基础配置类"""
    # 安全密钥
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-请在生产环境修改'

    # 数据库配置
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'instance', 'blog.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Session 配置
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_SECURE', 'False') == 'True'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    # 文件上传配置
    UPLOAD_FOLDER = os.path.join(basedir, 'app', 'static', 'uploads', 'covers')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

    # 缓存配置
    CACHE_TYPE = 'SimpleCache'
    CACHE_DEFAULT_TIMEOUT = 300
    CACHE_KEY_PREFIX = 'blog_'

    # 日志配置
    LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT')
    LOG_LEVEL = logging.INFO

    # 分页配置
    ITEMS_PER_PAGE = 10

    # WTF 配置
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None


class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    TESTING = False
    LOG_LEVEL = logging.DEBUG

    # 开发环境使用更详细的错误页面
    TEMPLATES_AUTO_RELOAD = True


class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    TESTING = False

    # 生产环境必须设置安全密钥，否则抛出错误
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError('生产环境必须设置 SECRET_KEY 环境变量')

    # 生产环境 Session 必须使用 HTTPS
    SESSION_COOKIE_SECURE = True

    # 使用性能更好的缓存（如果没有 Redis 则使用 SimpleCache）
    if os.environ.get('REDIS_URL'):
        CACHE_TYPE = 'RedisCache'
        CACHE_REDIS_URL = os.environ.get('REDIS_URL')
    else:
        CACHE_TYPE = 'SimpleCache'


class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    DEBUG = True
    WTF_CSRF_ENABLED = False

    # 使用内存数据库
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


# 配置字典
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config(config_name=None):
    """
    获取配置类

    Args:
        config_name: 配置名称，默认从环境变量获取

    Returns:
        配置类
    """
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')

    return config.get(config_name, DevelopmentConfig)
