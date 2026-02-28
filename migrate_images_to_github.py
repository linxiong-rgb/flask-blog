"""
批量迁移文章中的图片链接到 GitHub 图床

将文章内容中的本地图片路径替换为 GitHub 图床 URL
"""

import os
import re
from app import create_app, db
from app.models.post import Post
from app.utils.storage import get_storage


def migrate_post_images():
    """迁移文章中的图片链接"""
    app = create_app()

    with app.app_context():
        storage = get_storage()

        # 检查是否配置了 GitHub 存储
        if not hasattr(storage, 'token'):
            print("错误：未配置 GitHub 存储")
            print("请先设置以下环境变量：")
            print("  - GITHUB_TOKEN")
            print("  - GITHUB_REPO")
            return

        print(f"使用 GitHub 存储: {storage.repo}/{storage.path}")
        print()

        # 获取所有文章
        posts = Post.query.all()
        print(f"找到 {len(posts)} 篇文章")
        print()

        migrated_count = 0
        skipped_count = 0
        error_count = 0

        for post in posts:
            updated = False
            content = post.content

            # 查找所有 Markdown 图片语法
            pattern = r'!\[([^\]]*)\]\(([^)]+)\)'

            def replace_image(match):
                nonlocal updated
                alt_text = match.group(1)
                img_url = match.group(2)

                # 只处理本地路径的图片
                if img_url.startswith('/static/uploads/') or img_url.startswith('https://flask-blog'):
                    # 提取文件名
                    filename = os.path.basename(img_url)

                    # 构建新的 GitHub URL
                    new_url = storage.get_url(f'covers/{filename}')

                    updated = True
                    return f'![{alt_text}]({new_url})'

                return match.group(0)

            # 替换内容中的图片链接
            new_content = re.sub(pattern, replace_image, content)

            # 更新封面图
            if post.cover_image and (post.cover_image.startswith('/static/uploads/') or
                                     post.cover_image.startswith('https://flask-blog')):
                filename = os.path.basename(post.cover_image)
                post.cover_image = storage.get_url(f'covers/{filename}')
                updated = True

            # 如果有更新，保存到数据库
            if updated:
                post.content = new_content
                migrated_count += 1
                print(f"✓ 已迁移: {post.title}")
            else:
                skipped_count += 1
                print(f"- 跳过: {post.title} (已经是 GitHub URL)")

        # 提交更改
        try:
            db.session.commit()
            print()
            print("=" * 50)
            print(f"迁移完成！")
            print(f"  已迁移: {migrated_count} 篇")
            print(f"  已跳过: {skipped_count} 篇")
            print(f"  错误: {error_count} 篇")
            print("=" * 50)
        except Exception as e:
            db.session.rollback()
            print(f"\n错误：保存失败 - {str(e)}")


if __name__ == '__main__':
    migrate_post_images()
