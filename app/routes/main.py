"""
博客主要路由模块

该模块处理博客的主要页面路由，包括：
- 首页展示（分页）
- 文章详情页
- 分类和标签页面
- 搜索功能
"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, Response, current_app
from app.models.post import Post, Category, Tag
from app.models.user import User
from app.models.friend_link import FriendLink
from app.models.post_bookmark import PostBookmark
from flask_login import login_required, current_user
from app import db, cache, csrf
import markdown
import bleach
from sqlalchemy import func
from sqlalchemy.orm import joinedload
from datetime import datetime
from feedgen.feed import FeedGenerator

bp = Blueprint('main', __name__)


# Markdown 扩展配置
MD_EXTENSIONS = [
    'fenced_code',      # 围栏代码块 (```)
    'tables',           # 表格支持
    'nl2br',            # 换行符转换
    'sane_lists',       # 改进的列表
    'codehilite',       # 代码高亮
    'toc',              # 目录生成
    'attr_list',        # 属性列表
    'def_list',         # 定义列表
    'abbr',             # 缩写
    'footnotes',        # 脚注
    'md_in_html',       # HTML中的Markdown
]

# 代码高亮配置
MD_EXTENSION_CONFIGS = {
    'codehilite': {
        'linenums': False,
        'guess_lang': True,
        'noclasses': False,
        'cssclass': 'codehilite'
    }
}

# Bleach 配置 - 允许的 HTML 标签和属性
ALLOWED_TAGS = [
    'p', 'br', 'hr',
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'strong', 'em', 'u', 's', 'strike',
    'a', 'img',
    'ul', 'ol', 'li',
    'blockquote', 'pre', 'code',
    'table', 'thead', 'tbody', 'tfoot', 'tr', 'th', 'td',
    'div', 'span',
    'sup', 'sub',
]

ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title', 'target'],
    'img': ['src', 'alt', 'title', 'width', 'height'],
    'div': ['class'],
    'span': ['class'],
    'pre': ['class'],
    'code': ['class'],
    'table': ['class'],
    'th': ['colspan', 'rowspan'],
    'td': ['colspan', 'rowspan'],
}

# 清理 HTML 防止 XSS 攻击
def clean_html(html_content):
    """使用 bleach 清理 HTML，防止 XSS 攻击"""
    return bleach.clean(
        html_content,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        strip=True
    )


@cache.memoize(timeout=300)
def get_hot_posts():
    """获取热门文章（缓存5分钟）"""
    return Post.query.options(
        joinedload(Post.category)
    ).filter_by(published=True).order_by(Post.views.desc()).limit(5).all()


@cache.memoize(timeout=300)
def get_total_views():
    """获取总浏览量（缓存5分钟）"""
    return db.session.query(func.sum(Post.views)).filter_by(published=True).scalar() or 0


@cache.memoize(timeout=300)
def get_hot_tags():
    """获取热门标签（缓存5分钟）"""
    # 子查询：统计每个标签的文章数量
    tag_post_count = db.session.query(
        Tag.id,
        Tag.name,
        func.count(Post.id).label('post_count')
    ).join(Post.tags).filter(
        Post.published == True
    ).group_by(Tag.id).order_by(
        func.count(Post.id).desc()
    ).limit(10).all()

    return tag_post_count


def get_related_posts(current_post, limit=4):
    """
    获取相关文章

    基于相同标签的文章推荐

    Args:
        current_post: 当前文章对象
        limit: 返回数量

    Returns:
        list: 相关文章列表
    """
    if not current_post.tags:
        # 如果没有标签，返回同分类的最新文章
        if current_post.category:
            return Post.query.options(
                joinedload(Post.category)
            ).filter(
                Post.category_id == current_post.category_id,
                Post.id != current_post.id,
                Post.published == True
            ).order_by(Post.created_at.desc()).limit(limit).all()
        return []

    # 获取当前文章的所有标签ID
    tag_ids = [tag.id for tag in current_post.tags]

    # 查询有相同标签的文章
    from sqlalchemy import or_
    related = Post.query.options(
        joinedload(Post.category)
    ).filter(
        Post.id != current_post.id,
        Post.published == True,
        Post.tags.any(Tag.id.in_(tag_ids))
    ).order_by(Post.created_at.desc()).limit(limit).all()

    return related

@bp.route('/')
def index():
    """
    首页路由

    显示已发布的文章列表，包含：
    - 分页文章列表（每页10篇）
    - 热门文章（按浏览量排序）
    - 所有分类和标签
    - 总浏览量统计

    Returns:
        str: 渲染后的首页HTML
    """
    page = request.args.get('page', 1, type=int)
    per_page = 10

    # 使用 eager loading 优化查询，一次性加载关联数据
    posts = Post.query.options(
        joinedload(Post.category),
        joinedload(Post.tags)
    ).filter_by(published=True).order_by(Post.created_at.desc())
    posts = posts.paginate(page=page, per_page=per_page, error_out=False)

    # 获取热门文章（使用缓存）
    hot_posts = get_hot_posts()

    # 获取所有分类和标签
    categories = Category.query.all()
    tags = Tag.query.all()

    # 获取热门标签（按文章数量排序，取前10个）
    hot_tags = get_hot_tags()

    # 计算总浏览量（使用缓存）
    total_views = get_total_views()

    return render_template('index.html', posts=posts, hot_posts=hot_posts,
                          categories=categories, tags=tags, hot_tags=hot_tags, total_views=total_views)

@bp.route('/post/<int:post_id>')
def post(post_id):
    """
    文章详情页路由

    显示单篇文章的完整内容，包含：
    - 文章信息（标题、作者、分类、标签）
    - Markdown 转换后的 HTML 内容
    - 浏览量统计
    - 相关文章推荐

    Args:
        post_id: 文章ID

    Returns:
        str: 渲染后的文章详情页HTML
    """
    post = Post.query.options(
        joinedload(Post.category),
        joinedload(Post.tags)
    ).get_or_404(post_id)

    # 增加浏览量
    post.views += 1
    db.session.commit()

    # 将 Markdown 转换为 HTML
    html_content = markdown.markdown(
        post.content,
        extensions=MD_EXTENSIONS,
        extension_configs=MD_EXTENSION_CONFIGS
    )
    # 清理 HTML 防止 XSS 攻击
    post.content_html = clean_html(html_content)

    # 获取相关文章（基于相同标签）
    related_posts = get_related_posts(post)

    return render_template('post.html', post=post, related_posts=related_posts)

@bp.route('/about')
def about():
    """
    关于页面路由

    Returns:
        str: 渲染后的关于页面HTML
    """
    return render_template('about.html')


@bp.route('/category/<int:category_id>')
def category(category_id):
    """
    分类页面路由

    显示指定分类下的所有已发布文章（分页）

    Args:
        category_id: 分类ID

    Returns:
        str: 渲染后的分类页面HTML
    """
    category = Category.query.get_or_404(category_id)
    page = request.args.get('page', 1, type=int)
    per_page = 10
    # 使用 eager loading 优化查询
    posts = Post.query.options(
        joinedload(Post.tags)
    ).filter_by(category_id=category_id, published=True)\
                     .order_by(Post.created_at.desc())
    posts = posts.paginate(page=page, per_page=per_page, error_out=False)
    return render_template('category.html', category=category, posts=posts)


@bp.route('/tag/<int:tag_id>')
def tag(tag_id):
    """
    标签页面路由

    显示指定标签下的所有已发布文章（分页）

    Args:
        tag_id: 标签ID

    Returns:
        str: 渲染后的标签页面HTML
    """
    tag = Tag.query.get_or_404(tag_id)
    page = request.args.get('page', 1, type=int)
    per_page = 10

    # 使用 join 来预加载 category，避免 N+1 查询
    posts_query = tag.posts.filter_by(published=True)\
                          .join(Post.category)\
                          .order_by(Post.created_at.desc())
    posts = posts_query.paginate(page=page, per_page=per_page, error_out=False)
    return render_template('tag.html', tag=tag, posts=posts)


@bp.route('/categories')
def categories():
    """
    所有分类页面路由

    显示所有分类及其文章数量统计

    Returns:
        str: 渲染后的分类列表页面HTML
    """
    categories = Category.query.all()
    # 获取每个分类的文章数量
    category_stats = db.session.query(
        Category.id,
        Category.name,
        func.count(Post.id).label('post_count')
    ).outerjoin(Post).group_by(Category.id).all()
    return render_template('categories.html', category_stats=category_stats)


@bp.route('/search')
def search():
    """
    搜索功能路由

    在文章标题、内容和摘要中搜索关键词

    Query Parameters:
        q: 搜索关键词
        page: 页码

    Returns:
        str: 渲染后的搜索结果页面HTML
    """
    query = request.args.get('q', '')
    page = request.args.get('page', 1, type=int)
    per_page = 10

    if query:
        search = f"%{query}%"
        posts = Post.query.filter(
            Post.published == True,
            db.or_(
                Post.title.like(search),
                Post.content.like(search),
                Post.summary.like(search)
            )
        ).order_by(Post.created_at.desc())
    else:
        posts = Post.query.filter_by(published=True)

    posts = posts.paginate(page=page, per_page=per_page, error_out=False)
    return render_template('search.html', posts=posts, query=query)


@bp.route('/api/search/suggest')
def search_suggest():
    """
    搜索建议 API

    提供实时搜索建议，返回匹配的文章和标签

    Query Parameters:
        q: 搜索关键词

    Returns:
        JSON: 搜索建议列表
    """
    from flask import jsonify

    query = request.args.get('q', '').strip()
    if not query or len(query) < 2:
        return jsonify({'suggestions': []})

    suggestions = []

    # 搜索文章标题
    posts = Post.query.options(
        joinedload(Post.category)
    ).filter(
        Post.published == True,
        Post.title.like(f'%{query}%')
    ).limit(5).all()

    for post in posts:
        suggestions.append({
            'type': 'post',
            'title': post.title,
            'summary': post.summary[:50] + '...' if post.summary and len(post.summary) > 50 else '',
            'url': url_for('main.post', post_id=post.id)
        })

    # 搜索标签
    tags = Tag.query.filter(Tag.name.like(f'%{query}%')).limit(3).all()

    for tag in tags:
        suggestions.append({
            'type': 'tag',
            'title': f'#{tag.name}',
            'summary': f'{tag.posts.count()} 篇文章',
            'url': url_for('main.tag', tag_id=tag.id)
        })

    # 搜索分类
    categories = Category.query.filter(Category.name.like(f'%{query}%')).limit(2).all()

    for category in categories:
        suggestions.append({
            'type': 'category',
            'title': f'📁 {category.name}',
            'summary': f'{category.posts.count()} 篇文章',
            'url': url_for('main.category', category_id=category.id)
        })

    return jsonify({'suggestions': suggestions[:10]})


@bp.route('/sitemap.xml')
def sitemap():
    """
    Sitemap 生成路由

    生成符合 Google 规范的 XML 站点地图

    Returns:
        str: XML 格式的 sitemap
    """
    from flask import Response

    # 获取所有已发布的文章
    posts = Post.query.filter_by(published=True).order_by(Post.updated_at.desc()).all()

    # 获取所有分类
    categories = Category.query.all()

    # 获取所有标签
    tags = Tag.query.all()

    # 构建 XML
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'

    # 首页
    base_url = request.url_root.rstrip('/')
    xml += f'  <url>\n'
    xml += f'    <loc>{base_url}</loc>\n'
    xml += f'    <changefreq>daily</changefreq>\n'
    xml += f'    <priority>1.0</priority>\n'
    xml += f'  </url>\n'

    # 文章列表
    for post in posts:
        xml += f'  <url>\n'
        xml += f'    <loc>{base_url}/post/{post.id}</loc>\n'
        xml += f'    <lastmod>{post.updated_at.strftime("%Y-%m-%d")}</lastmod>\n'
        xml += f'    <changefreq>weekly</changefreq>\n'
        xml += f'    <priority>0.8</priority>\n'
        xml += f'  </url>\n'

    # 分类页面
    for category in categories:
        xml += f'  <url>\n'
        xml += f'    <loc>{base_url}/category/{category.id}</loc>\n'
        xml += f'    <changefreq>weekly</changefreq>\n'
        xml += f'    <priority>0.6</priority>\n'
        xml += f'  </url>\n'

    # 标签页面
    for tag in tags:
        xml += f'  <url>\n'
        xml += f'    <loc>{base_url}/tag/{tag.id}</loc>\n'
        xml += f'    <changefreq>weekly</changefreq>\n'
        xml += f'    <priority>0.5</priority>\n'
        xml += f'  </url>\n'

    # 静态页面
    static_pages = [
        ('/about', 'weekly', '0.5'),
        ('/categories', 'weekly', '0.5'),
    ]

    for path, changefreq, priority in static_pages:
        xml += f'  <url>\n'
        xml += f'    <loc>{base_url}{path}</loc>\n'
        xml += f'    <changefreq>{changefreq}</changefreq>\n'
        xml += f'    <priority>{priority}</priority>\n'
        xml += f'  </url>\n'

    xml += '</urlset>'

    return Response(xml, mimetype='application/xml')


@bp.route('/robots.txt')
def robots_txt():
    """
    Robots.txt 生成路由

    生成搜索引擎爬虫规则

    Returns:
        str: robots.txt 内容
    """
    from flask import Response

    base_url = request.url_root.rstrip('/')
    robots = f'''User-agent: *
Allow: /
Disallow: /admin/
Disallow: /auth/
Disallow: /export/

Sitemap: {base_url}/sitemap.xml
'''

    return Response(robots, mimetype='text/plain')


@bp.route('/friend-links')
def friend_links():
    """
    友情链接页面

    显示所有友链

    Returns:
        str: 渲染后的友链页面HTML
    """
    links = FriendLink.query.filter_by(is_active=True).order_by(FriendLink.order).all()
    return render_template('friend_links.html', links=links)


@bp.route('/archive')
def archive():
    """
    文章归档页面

    按年月分组显示所有已发布的文章

    Returns:
        str: 渲染后的归档页面HTML
    """
    # 获取所有已发布的文章，按创建时间倒序
    posts = Post.query.options(
        joinedload(Post.category),
        joinedload(Post.tags)
    ).filter_by(published=True).order_by(Post.created_at.desc()).all()

    # 按年月分组
    archive_dict = {}
    total_posts = len(posts)

    for post in posts:
        year = post.created_at.year
        month = post.created_at.strftime('%Y-%m')
        month_name = post.created_at.strftime('%Y年%m月')

        if year not in archive_dict:
            archive_dict[year] = {
                'months': {},
                'count': 0
            }

        if month not in archive_dict[year]['months']:
            archive_dict[year]['months'][month] = {
                'name': month_name,
                'posts': []
            }

        archive_dict[year]['months'][month]['posts'].append(post)
        archive_dict[year]['count'] += 1

    # 获取侧边栏数据
    hot_posts = get_hot_posts()
    categories = Category.query.all()
    tags = Tag.query.all()

    return render_template('archive.html', archive=archive_dict, total_posts=total_posts,
                          hot_posts=hot_posts, categories=categories, tags=tags)


@bp.route('/feed.xml')
@bp.route('/rss.xml')
def rss_feed():
    """
    RSS订阅路由

    生成RSS 2.0格式的订阅源

    Returns:
        Response: RSS XML内容
    """
    base_url = request.url_root.rstrip('/')

    # 获取最新的20篇文章
    posts = Post.query.options(
        joinedload(Post.category),
        joinedload(Post.author),
        joinedload(Post.tags)
    ).filter_by(published=True).order_by(Post.created_at.desc()).limit(20).all()

    # 创建RSS feed
    feed = FeedGenerator()
    feed.title("linxiong's Blog")
    feed.link(href=base_url, rel='alternate')
    feed.description("专注于网络安全与渗透测试的技术博客")
    feed.language("zh-CN")

    for post in posts:
        # 文章内容摘要
        description = post.summary if post.summary else post.content[:200] + '...'

        # 文章URL
        post_url = f"{base_url}/post/{post.id}"

        # 添加文章条目
        entry = feed.add_entry()
        entry.title(post.title)
        entry.link(href=post_url)
        entry.description(description)
        entry.content(markdown.markdown(post.content, extensions=MD_EXTENSIONS), type='html')
        entry.published(post.created_at)
        entry.updated(post.updated_at)
        entry.author({'name': post.author.username})

        # 添加分类
        if post.category:
            entry.category({'term': post.category.name, 'scheme': f"{base_url}/category/{post.category.id}"})

        # 添加标签
        for tag in post.tags:
            entry.category({'term': tag.name, 'scheme': f"{base_url}/tag/{tag.id}"})

    return Response(feed.rss_str(), mimetype='application/rss+xml')


# ========================================
# API 路由
# ========================================

@bp.route('/api/post/<int:post_id>/bookmark', methods=['POST'])
@login_required
@csrf.exempt
def toggle_bookmark(post_id):
    """
    文章收藏 API

    处理文章收藏/取消收藏

    Args:
        post_id: 文章ID

    Returns:
        JSON: 收藏结果和收藏数
    """
    try:
        post = Post.query.get_or_404(post_id)
        user_id = current_user.id

        # 检查是否已收藏
        existing_bookmark = PostBookmark.query.filter_by(post_id=post_id, user_id=user_id).first()

        if existing_bookmark:
            # 取消收藏
            db.session.delete(existing_bookmark)
            db.session.commit()
            bookmarked = False
        else:
            # 添加收藏
            bookmark = PostBookmark(post_id=post_id, user_id=user_id)
            db.session.add(bookmark)
            db.session.commit()
            bookmarked = True

        # 获取收藏数
        bookmark_count = PostBookmark.query.filter_by(post_id=post_id).count()

        return jsonify({
            'success': True,
            'bookmarked': bookmarked,
            'bookmark_count': bookmark_count
        })
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'收藏操作失败: {str(e)}')
        return jsonify({'success': False, 'message': str(e)}), 500


@bp.route('/api/post/<int:post_id>/bookmarks')
def get_post_bookmarks(post_id):
    """
    获取文章收藏数 API

    Args:
        post_id: 文章ID

    Returns:
        JSON: 收藏数和是否已收藏
    """
    post = Post.query.get_or_404(post_id)
    bookmark_count = PostBookmark.query.filter_by(post_id=post_id).count()

    # 检查当前用户是否已收藏
    bookmarked = False
    if current_user.is_authenticated:
        bookmarked = PostBookmark.query.filter_by(post_id=post_id, user_id=current_user.id).first() is not None

    return jsonify({
        'bookmark_count': bookmark_count,
        'bookmarked': bookmarked
    })


@bp.route('/init-db')
def init_database():
    """
    数据库初始化路由

    用于部署后手动初始化数据库表和默认管理员用户
    访问该路由将创建所有数据表和默认管理员账号

    Returns:
        JSON: 初始化结果
    """
    from app import db
    from app.models.friend_link import FriendLink

    try:
        # 创建所有数据库表
        db.create_all()
        current_app.logger.info('数据库表创建成功')

        # 检查管理员是否已存在
        admin = User.query.filter_by(username='admin01').first()
        if not admin:
            # 创建默认管理员
            admin = User(
                username='admin01',
                email='admin01@blog.local'
            )
            admin.set_password('123456')
            db.session.add(admin)
            db.session.commit()
            current_app.logger.info('默认管理员账号创建成功')

        return jsonify({
            'success': True,
            'message': '数据库初始化成功！',
            'admin_created': admin is not None or User.query.filter_by(username='admin01').first() is not None
        })
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'数据库初始化失败: {str(e)}')
        return jsonify({
            'success': False,
            'message': f'初始化失败: {str(e)}'
        }), 500


@bp.route('/check-db')
def check_database():
    """
    数据库状态检查路由

    用于检查数据库表和用户状态

    Returns:
        JSON: 数据库状态信息
    """
    from app import db
    from sqlalchemy import inspect

    try:
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()

        # 获取所有用户
        users = User.query.all()
        user_list = [{'id': u.id, 'username': u.username, 'email': u.email} for u in users]

        # 检查 admin01 是否存在
        admin = User.query.filter_by(username='admin01').first()

        return jsonify({
            'success': True,
            'tables': tables,
            'table_count': len(tables),
            'users': user_list,
            'user_count': len(users),
            'admin_exists': admin is not None,
            'admin_info': {
                'id': admin.id,
                'username': admin.username,
                'email': admin.email,
                'has_password': bool(admin.password_hash)
            } if admin else None
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500