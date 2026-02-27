"""
Render 部署配置生成器
"""

import secrets

print("=" * 50)
print("Render 部署配置")
print("=" * 50)
print()

print("1. SECRET_KEY (请复制到 Render 环境变量中):")
print("-" * 50)
secret_key = secrets.token_hex(32)
print(secret_key)
print()

print("2. 数据库初始化:")
print("-" * 50)
print("部署完成后，访问你的应用，添加 /reset 到 URL 末尾来初始化数据库")
print("例如: https://你的应用名.onrender.com/reset")
print()

print("3. 默认管理员账号:")
print("-" * 50)
print("用户名: admin01")
print("密码: 123456")
print()

print("=" * 50)
