"""
应用启动脚本

这是博客应用的入口文件，用于启动开发服务器。
在生产环境中，建议使用 Gunicorn 或 uWSGI 等 WSGI 服务器。

环境变量:
    PORT: 服务器端口 (默认: 5000)
    DEBUG: 调试模式 (默认: True)
    SECRET_KEY: 应用密钥

使用示例:
    python run.py                    # 开发模式
    PORT=8000 python run.py            # 指定端口
    DEBUG=False python run.py          # 生产模式
"""

import os
from app import create_app

# 创建应用实例
app = create_app()

if __name__ == '__main__':
    # 从环境变量读取配置，提供默认值
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'True') == 'True'

    # 启动开发服务器
    # 注意：Flask 开发服务器不适合生产环境
    # 生产环境请使用 gunicorn 或 uWSGI
    app.run(debug=debug, host='0.0.0.0', port=port)
