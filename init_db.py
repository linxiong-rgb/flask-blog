"""
数据库初始化脚本

用于创建数据库表和初始管理员账号
"""
from app import create_app, db
from app.models.user import User
from app.models.post import Category, Tag


def init_database():
    """初始化数据库"""
    app = create_app()

    with app.app_context():
        # 创建所有表
        db.create_all()
        print("✓ 数据库表创建成功")

        # 检查是否已有用户
        existing_user = User.query.first()
        if existing_user:
            print(f"⚠ 数据库已存在用户: {existing_user.username}")
            choice = input("是否创建新管理员账号？(y/N): ").strip().lower()
            if choice != 'y':
                print("初始化完成")
                return

        # 获取管理员信息
        print()
        print("=" * 50)
        print("创建管理员账号")
        print("=" * 50)
        username = input("用户名 [默认: linxiong]: ").strip() or "linxiong"
        email = input("邮箱 [默认: 3497875641@qq.com]: ").strip() or "3497875641@qq.com"
        password = input("密码: ").strip()

        if not password:
            print("✗ 密码不能为空")
            return

        # 创建管理员
        admin = User(username=username, email=email)
        admin.set_password(password)
        db.session.add(admin)
        db.session.commit()
        print(f"✓ 管理员账号创建成功: {username}")

        # 创建默认分类
        default_categories = [
            {"name": "网络安全", "description": "网络安全相关文章"},
            {"name": "渗透测试", "description": "渗透测试实战经验"},
            {"name": "漏洞分析", "description": "漏洞分析与利用"},
            {"name": "工具教程", "description": "安全工具使用教程"},
        ]

        for cat_data in default_categories:
            if not Category.query.filter_by(name=cat_data["name"]).first():
                category = Category(**cat_data)
                db.session.add(category)

        db.session.commit()
        print("✓ 默认分类创建成功")

        # 创建默认标签
        default_tags = [
            "Web安全", "CTF", "SQL注入", "XSS", "提权",
            "内网渗透", "代码审计", "工具", "Writeup"
        ]

        for tag_name in default_tags:
            if not Tag.query.filter_by(name=tag_name).first():
                tag = Tag(name=tag_name)
                db.session.add(tag)

        db.session.commit()
        print("✓ 默认标签创建成功")

        print()
        print("=" * 50)
        print("数据库初始化完成！")
        print("=" * 50)


if __name__ == '__main__':
    init_database()
