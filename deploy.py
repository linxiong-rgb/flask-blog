# -*- coding: utf-8 -*-
"""
部署辅助脚本

用于生成部署所需的配置和密钥
"""
import secrets
import os
import sys


def generate_secret_key():
    """生成 Flask SECRET_KEY"""
    return secrets.token_hex(32)


def generate_env_content():
    """生成 .env 文件内容"""
    secret_key = generate_secret_key()

    env_content = f"""# Flask 配置
SECRET_KEY={secret_key}
DEBUG=False
PORT=5000

# 数据库配置
# 本地开发使用 SQLite
DATABASE_URL=sqlite:///blog.db

# Render 部署时，请在 Render 控制台设置环境变量：
# DATABASE_URL=postgresql://用户名:密码@主机地址/数据库名
"""
    return env_content


def main():
    # 设置控制台编码
    if sys.platform == 'win32':
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

    print("=" * 50)
    print("linxiong's Blog - 部署辅助脚本")
    print("=" * 50)
    print()

    # 生成 SECRET_KEY
    secret_key = generate_secret_key()
    print("[OK] 生成的 SECRET_KEY:")
    print(f"  {secret_key}")
    print()

    # 询问是否创建 .env 文件
    env_file = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_file):
        print(f"[WARN] .env 文件已存在: {env_file}")
        try:
            choice = input("是否覆盖？: ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\n跳过 .env 文件创建")
            choice = 'n'

        if choice == 'y' or choice == 'yes':
            with open(env_file, 'w', encoding='utf-8') as f:
                f.write(generate_env_content())
            print("[OK] .env 文件已更新")
        else:
            print("[INFO] 跳过 .env 文件创建")
    else:
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(generate_env_content())
        print(f"[OK] .env 文件已创建: {env_file}")

    print()
    print("=" * 50)
    print("部署步骤：")
    print("=" * 50)
    print()
    print("1. Git 初始化和推送：")
    print("   git init")
    print("   git add .")
    print('   git commit -m "Initial commit"')
    print("   git remote add origin https://github.com/你的用户名/my-blog.git")
    print("   git branch -M main")
    print("   git push -u origin main")
    print()
    print("2. 在 Render 创建 Web Service：")
    print("   - 访问 https://dashboard.render.com")
    print("   - 点击 'New +' -> 'Web Service'")
    print("   - 连接 GitHub 仓库")
    print("   - 配置如下：")
    print("     Environment: Python 3")
    print("     Build Command: pip install -r requirements.txt")
    print("     Start Command: gunicorn app:create_app()")
    print()
    print("3. 设置环境变量（在 Render 控制台）：")
    print(f"   SECRET_KEY = {secret_key}")
    print("   DATABASE_URL = postgresql://... (使用 Render PostgreSQL)")
    print("   PORT = 5000")
    print("   DEBUG = False")
    print()


if __name__ == '__main__':
    main()
