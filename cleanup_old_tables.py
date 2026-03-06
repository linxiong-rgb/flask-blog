#!/usr/bin/env python
"""
清理旧相册表脚本

删除不再使用的旧相册系统相关表：
- album (旧相册表)
- photo (旧图片表)  
- photo_share (旧图片分享表)
- photo_tag (旧图片标签关联表)
- photo_tags (旧标签表)

新的相册系统使用 gallery_album 和 gallery_photo 表。
"""

from app import create_app, db
from sqlalchemy import text

def cleanup_old_tables():
    """清理旧的相册相关表"""
    app = create_app()

    with app.app_context():
        with db.engine.connect() as conn:
            # 检查数据库类型
            db_type = conn.dialect.name
            print(f"数据库类型: {db_type}")

            # 要删除的旧表
            old_tables = [
                'photo_share',
                'photo_tag', 
                'photo_tags',
                'photo',
                'album'
            ]

            # 检查哪些表存在
            result = conn.execute(text("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
                ORDER BY name
            """ if db_type == 'sqlite' else """
                SELECT table_name FROM information_schema.tables
                WHERE table_schema = 'public'
                ORDER BY table_name
            """))
            
            existing_tables = [row[0] for row in result]
            print(f"\n当前数据库表: {existing_tables}")

            # 删除存在的旧表
            for table in old_tables:
                if table in existing_tables:
                    try:
                        if db_type == 'sqlite':
                            conn.execute(text(f"DROP TABLE IF EXISTS {table}"))
                        else:
                            conn.execute(text(f'DROP TABLE IF EXISTS "{table}" CASCADE'))
                        conn.commit()
                        print(f"✓ 删除旧表: {table}")
                    except Exception as e:
                        print(f"× 删除 {table} 失败: {e}")
                else:
                    print(f"○ 表不存在: {table}")

            # 显示清理后的表列表
            result = conn.execute(text("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
                ORDER BY name
            """ if db_type == 'sqlite' else """
                SELECT table_name FROM information_schema.tables
                WHERE table_schema = 'public'
                ORDER BY table_name
            """))
            
            remaining_tables = [row[0] for row in result]
            print(f"\n清理后剩余表: {remaining_tables}")
            print(f"表总数: {len(remaining_tables)}")

        print("\n旧表清理完成！")

if __name__ == '__main__':
    cleanup_old_tables()
