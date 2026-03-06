#!/usr/bin/env python
"""
数据库更新脚本

运行此脚本更新本地数据库表结构
"""

from app import create_app, db
from sqlalchemy import text

def update_database():
    """更新数据库表结构"""
    app = create_app()

    with app.app_context():
        with db.engine.connect() as conn:
            # 检查数据库类型
            db_type = conn.dialect.name
            print(f"数据库类型: {db_type}")

            # 更新 user 表
            try:
                if db_type == 'sqlite':
                    # SQLite 不支持直接添加带默认值的列
                    try:
                        conn.execute(text("ALTER TABLE user ADD COLUMN is_superuser BOOLEAN DEFAULT 0"))
                        conn.commit()
                        print("✓ 添加 user.is_superuser 列")
                    except Exception as e:
                        if "duplicate column" not in str(e).lower():
                            print(f"user.is_superuser: {e}")
                else:
                    # PostgreSQL
                    result = conn.execute(text("""
                        SELECT column_name FROM information_schema.columns
                        WHERE table_name = 'user' AND column_name = 'is_superuser'
                    """))
                    if not result.fetchone():
                        conn.execute(text("ALTER TABLE \"user\" ADD COLUMN is_superuser BOOLEAN DEFAULT FALSE"))
                        conn.commit()
                        print("✓ 添加 user.is_superuser 列")
            except Exception as e:
                print(f"user 表更新: {e}")

            # 更新 post 表
            try:
                if db_type == 'sqlite':
                    columns = [
                        ('visibility', "VARCHAR(20) DEFAULT 'public'"),
                        ('access_password', 'VARCHAR(100)'),
                        ('content_type', 'VARCHAR(20) DEFAULT "markdown"'),
                        ('pdf_attachment', 'VARCHAR(500)'),
                        ('pdf_page_count', 'INTEGER DEFAULT 0')
                    ]
                    for col_name, col_def in columns:
                        try:
                            conn.execute(text(f"ALTER TABLE post ADD COLUMN {col_name} {col_def}"))
                            conn.commit()
                            print(f"+ Added post.{col_name}")
                        except Exception as e:
                            if 'duplicate column' not in str(e).lower():
                                print(f"post.{col_name}: {e}")
                else:
                    # PostgreSQL
                    columns = [
                        ('visibility', "VARCHAR(20) DEFAULT 'public'"),
                        ('access_password', 'VARCHAR(100)'),
                        ('content_type', "VARCHAR(20) DEFAULT 'markdown'"),
                        ('pdf_attachment', 'VARCHAR(500)'),
                        ('pdf_page_count', 'INTEGER DEFAULT 0')
                    ]
                    for col_name, col_def in columns:
                        result = conn.execute(text("""
                            SELECT column_name FROM information_schema.columns
                            WHERE table_name = 'post' AND column_name = :col_name
                        """), {'col_name': col_name})
                        if not result.fetchone():
                            conn.execute(text(f'ALTER TABLE post ADD COLUMN {col_name} {col_def}'))
                            conn.commit()
                            print(f"+ Added post.{col_name}")
            except Exception as e:
                print(f"post table error: {e}")

            # 创建相册表
            try:
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS gallery_album (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name VARCHAR(100) NOT NULL,
                        description VARCHAR(500),
                        user_id INTEGER NOT NULL REFERENCES user(id),
                        is_public BOOLEAN DEFAULT 0,
                        created_at DATETIME,
                        updated_at DATETIME
                    )
                """))
                conn.commit()
                print("✓ 创建 gallery_album 表")
            except Exception as e:
                print(f"gallery_album 表: {e}")

            try:
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS gallery_photo (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        filename VARCHAR(255) NOT NULL,
                        file_path VARCHAR(500) NOT NULL,
                        album_id INTEGER NOT NULL REFERENCES gallery_album(id),
                        user_id INTEGER NOT NULL REFERENCES user(id),
                        created_at DATETIME
                    )
                """))
                conn.commit()
                print("✓ 创建 gallery_photo 表")
            except Exception as e:
                print(f"gallery_photo 表: {e}")

        print("\n数据库更新完成！")
        print("请重启应用以使更改生效。")

if __name__ == '__main__':
    update_database()
