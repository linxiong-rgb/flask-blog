#!/usr/bin/env python
"""
添加相册公开字段迁移脚本

运行方式: python migrate_add_album_public.py
"""

import os
import sys
from app import create_app, db
from app.models.album import Album

def migrate():
    """添加 is_public 和 access_password 字段到 album 表"""
    app = create_app()

    with app.app_context():
        # 检查字段是否已存在
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns('album')]

        # 添加 is_public 字段
        if 'is_public' not in columns:
            print("添加 is_public 字段...")
            db.execute('ALTER TABLE album ADD COLUMN is_public BOOLEAN DEFAULT FALSE')
            print("✓ is_public 字段已添加")
        else:
            print("○ is_public 字段已存在")

        # 添加 access_password 字段
        if 'access_password' not in columns:
            print("添加 access_password 字段...")
            db.execute('ALTER TABLE album ADD COLUMN access_password VARCHAR(100)')
            print("✓ access_password 字段已添加")
        else:
            print("○ access_password 字段已存在")

        db.session.commit()
        print("\n迁移完成！")

if __name__ == '__main__':
    migrate()
