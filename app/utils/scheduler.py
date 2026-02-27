"""
定时任务调度模块

该模块提供定时任务功能：
- 自动发布定时文章
- 清理过期数据
"""

from datetime import datetime
from app import create_app, db
from app.models.post import Post
import logging

logger = logging.getLogger(__name__)


def publish_scheduled_posts():
    """
    发布已到发布时间的文章

    该函数应被定时任务定期调用
    """
    app = create_app()

    with app.app_context():
        try:
            # 查找所有已到发布时间但未发布的文章
            now = datetime.utcnow()
            scheduled_posts = Post.query.filter(
                Post.published == False,
                Post.scheduled_at <= now
            ).all()

            published_count = 0
            for post in scheduled_posts:
                post.published = True
                published_count += 1
                logger.info(f'自动发布文章: {post.title} (ID: {post.id})')

            if published_count > 0:
                db.session.commit()
                logger.info(f'成功发布 {published_count} 篇定时文章')
                return published_count

            return 0

        except Exception as e:
            logger.error(f'发布定时文章时出错: {str(e)}')
            db.session.rollback()
            return -1


def get_scheduled_posts_stats():
    """
    获取定时文章统计信息

    Returns:
        dict: 统计信息
    """
    app = create_app()

    with app.app_context():
        try:
            total_scheduled = Post.query.filter(
                Post.published == False,
                Post.scheduled_at.isnot(None)
            ).count()

            # 即将发布的文章（未来24小时内）
            from datetime import timedelta
            soon = datetime.utcnow() + timedelta(hours=24)
            publishing_soon = Post.query.filter(
                Post.published == False,
                Post.scheduled_at <= soon
            ).count()

            return {
                'total_scheduled': total_scheduled,
                'publishing_soon': publishing_soon
            }

        except Exception as e:
            logger.error(f'获取定时文章统计时出错: {str(e)}')
            return {
                'total_scheduled': 0,
                'publishing_soon': 0
            }


if __name__ == '__main__':
    # 直接运行此文件时，执行一次发布任务
    logging.basicConfig(level=logging.INFO)
    count = publish_scheduled_posts()
    if count == 0:
        print('没有需要发布的定时文章')
    elif count > 0:
        print(f'成功发布 {count} 篇文章')
    else:
        print('发布定时文章时出错')
