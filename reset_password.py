"""
密码重置工具

使用方法：
1. python reset_password.py - 查看所有用户
2. python reset_password.py <username> <new_password> - 重置指定用户的密码
"""

import sys
from app import create_app, db
from app.models.user import User

def list_users():
    """列出所有用户"""
    users = User.query.all()
    if not users:
        print("数据库中没有用户")
        return

    print("现有用户列表:")
    print("-" * 50)
    for user in users:
        print(f"ID: {user.id}, 用户名: {user.username}, 邮箱: {user.email}, 创建时间: {user.created_at}")

def reset_password(username, new_password):
    """重置用户密码"""
    user = User.query.filter_by(username=username).first()
    if not user:
        print(f"错误: 找不到用户 '{username}'")
        return False

    user.set_password(new_password)
    db.session.commit()
    print(f"成功! 用户 '{username}' 的密码已重置")
    return True

if __name__ == '__main__':
    app = create_app()

    with app.app_context():
        if len(sys.argv) == 1:
            # 没有参数，显示用户列表
            list_users()
        elif len(sys.argv) == 3:
            # 两个参数：用户名和新密码
            username = sys.argv[1]
            new_password = sys.argv[2]
            reset_password(username, new_password)
        else:
            print("使用方法:")
            print("  python reset_password.py                    # 查看所有用户")
            print("  python reset_password.py <用户名> <新密码>   # 重置密码")
