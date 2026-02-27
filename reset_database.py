"""
数据库重置脚本

功能：
1. 删除所有现有数据（用户、文章、分类、标签、收藏、友链）
2. 创建超级管理员账号 admin01 / 123456

使用方法：
    python reset_database.py
"""

import os
import sys
from werkzeug.security import generate_password_hash

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.user import User
from app.models.post import Post, Category, Tag
from app.models.friend_link import FriendLink
from app.models.post_bookmark import PostBookmark


def reset_database():
    """重置数据库并创建超级管理员"""
    app = create_app()

    with app.app_context():
        print("=" * 50)
        print("数据库重置脚本")
        print("=" * 50)

        # 确认操作
        confirm = input("\n⚠️  警告：此操作将删除所有数据！\n是否继续？(yes/no): ")
        if confirm.lower() != 'yes':
            print("操作已取消")
            return

        print("\n正在删除现有数据...")

        # 删除所有数据（按照依赖关系顺序）
        # PostBookmark 依赖 Post 和 User
        PostBookmark.query.delete()
        print("  ✓ 已删除所有收藏记录")

        # Post 依赖 User, Category, Tag
        Post.query.delete()
        print("  ✓ 已删除所有文章")

        # Category 和 Tag 相对独立
        Category.query.delete()
        print("  ✓ 已删除所有分类")

        Tag.query.delete()
        print("  ✓ 已删除所有标签")

        # FriendLink 是独立的
        FriendLink.query.delete()
        print("  ✓ 已删除所有友情链接")

        # User 删除所有用户
        User.query.delete()
        print("  ✓ 已删除所有用户")

        # 提交删除操作
        db.session.commit()

        print("\n正在创建超级管理员账号...")

        # 创建超级管理员
        admin = User(
            username='admin01',
            email='admin01@blog.local'
        )
        admin.set_password('123456')

        db.session.add(admin)
        db.session.commit()

        print(f"  ✓ 超级管理员创建成功")
        print(f"    用户名: admin01")
        print(f"    密码: 123456")
        print(f"    邮箱: admin01@blog.local")

        print("\n" + "=" * 50)
        print("数据库重置完成！")
        print("=" * 50)
        print("\n请使用以下账号登录：")
        print("  用户名: admin01")
        print("  密码: 123456")
        print()


if __name__ == '__main__':
    reset_database()
