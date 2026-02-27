# 空文件，用于导入模型

from app.models.user import User
from app.models.post import Post, Category, Tag
from app.models.friend_link import FriendLink
from app.models.post_bookmark import PostBookmark

__all__ = ['User', 'Post', 'Category', 'Tag', 'FriendLink', 'PostBookmark']
