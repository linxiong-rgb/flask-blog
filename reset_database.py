"""
完整重置并重建数据库
WARNING: 此操作将删除所有现有数据！
"""
import os
import sys

def reset_database():
    # 删除旧数据库
    db_path = os.path.join('instance', 'blog.db')
    if os.path.exists(db_path):
        print(f"删除旧数据库: {db_path}")
        os.remove(db_path)
        print("旧数据库已删除")

    # 导入应用并创建新数据库
    sys.path.insert(0, os.path.dirname(__file__))
    from app import create_app, db
    from app.models.user import User
    from app.models.post import Post, Category, Tag

    app = create_app()

    with app.app_context():
        # 创建所有表
        db.create_all()
        print("\n数据库表创建成功！")

        # 显示表结构
        print("\n=== 数据库表结构 ===")
        tables = ['user', 'post', 'category', 'tag', 'post_tags']
        for table in tables:
            print(f"\n{table.upper()} 表:")
            result = db.session.execute(db.text(f"PRAGMA table_info({table})"))
            for col in result:
                print(f"  - {col[1]}: {col[2]}")

        print("\n" + "="*50)
        print("数据库重置完成！")
        print("="*50)

if __name__ == '__main__':
    print("="*50)
    print("数据库重置脚本")
    print("="*50)
    print("\n警告：此操作将删除所有现有数据！")

    response = input("\n确定要继续吗？(yes/no): ")
    if response.lower() in ['yes', 'y']:
        try:
            reset_database()
        except Exception as e:
            print(f"\n错误: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("操作已取消")
