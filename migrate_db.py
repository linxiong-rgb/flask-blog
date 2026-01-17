"""
数据库迁移脚本
用于更新现有数据库结构，添加新字段
"""
import sqlite3
import os

def migrate_database():
    db_path = os.path.join('instance', 'blog.db')

    if not os.path.exists(db_path):
        print("数据库文件不存在，将创建新数据库")
        return

    print(f"正在迁移数据库: {db_path}")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # 检查是否已经迁移过
        cursor.execute("PRAGMA table_info(post)")
        columns = [column[1] for column in cursor.fetchall()]

        # 检查并添加新字段
        migrations = [
            ('category_id', 'ALTER TABLE post ADD COLUMN category_id INTEGER REFERENCES category(id)'),
            ('views', 'ALTER TABLE post ADD COLUMN views INTEGER DEFAULT 0'),
            ('cover_image', 'ALTER TABLE post ADD COLUMN cover_image VARCHAR(500)')
        ]

        for column_name, sql in migrations:
            if column_name not in columns:
                print(f"添加字段: {column_name}")
                cursor.execute(sql)
            else:
                print(f"字段已存在: {column_name}")

        # 创建 category 表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS category (
                id INTEGER NOT NULL PRIMARY KEY,
                name VARCHAR(50) NOT NULL UNIQUE,
                description VARCHAR(200),
                created_at DATETIME
            )
        """)
        print("创建/检查 category 表")

        # 创建 tag 表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tag (
                id INTEGER NOT NULL PRIMARY KEY,
                name VARCHAR(50) NOT NULL UNIQUE,
                created_at DATETIME
            )
        """)
        print("创建/检查 tag 表")

        # 创建 post_tags 关联表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS post_tags (
                post_id INTEGER NOT NULL,
                tag_id INTEGER NOT NULL,
                PRIMARY KEY (post_id, tag_id),
                FOREIGN KEY(post_id) REFERENCES post (id),
                FOREIGN KEY(tag_id) REFERENCES tag (id)
            )
        """)
        print("创建/检查 post_tags 关联表")

        conn.commit()
        print("[SUCCESS] 数据库迁移成功！")

    except Exception as e:
        conn.rollback()
        print(f"[ERROR] 迁移失败: {e}")
        raise
    finally:
        conn.close()

if __name__ == '__main__':
    migrate_database()
