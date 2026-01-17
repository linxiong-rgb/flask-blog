"""
博客主要路由模块

该模块处理博客的主要页面路由，包括：
- 首页展示（分页）
- 文章详情页
- 分类和标签页面
- 搜索功能
"""

from flask import Blueprint, render_template, request
from app.models.post import Post, Category, Tag
from app.models.user import User
from flask_login import login_required, current_user
from app import db
import markdown
from sqlalchemy import func

bp = Blueprint('main', __name__)


# Markdown 扩展配置
MARKDOWN_EXTENSIONS = [
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
    posts = Post.query.filter_by(published=True).order_by(Post.created_at.desc())
    posts = posts.paginate(page=page, per_page=per_page, error_out=False)

    # 获取热门文章（按浏览量）
    hot_posts = Post.query.filter_by(published=True).order_by(Post.views.desc()).limit(5).all()

    # 获取所有分类和标签
    categories = Category.query.all()
    tags = Tag.query.all()

    # 计算总浏览量
    total_views = db.session.query(func.sum(Post.views)).filter_by(published=True).scalar() or 0

    return render_template('index.html', posts=posts, hot_posts=hot_posts,
                          categories=categories, tags=tags, total_views=total_views)

@bp.route('/post/<int:post_id>')
def post(post_id):
    """
    文章详情页路由

    显示单篇文章的完整内容，包含：
    - 文章信息（标题、作者、分类、标签）
    - Markdown 转换后的 HTML 内容
    - 浏览量统计

    Args:
        post_id: 文章ID

    Returns:
        str: 渲染后的文章详情页HTML
    """
    post = Post.query.get_or_404(post_id)
    # 增加浏览量
    post.views += 1
    db.session.commit()
    # 将 Markdown 转换为 HTML
    post.content_html = markdown.markdown(post.content, extensions=MARKDOWN_EXTENSIONS)
    return render_template('post.html', post=post)

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
    posts = Post.query.filter_by(category_id=category_id, published=True)\
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
    posts = tag.posts.filter_by(published=True)\
                    .order_by(Post.created_at.desc())
    posts = posts.paginate(page=page, per_page=per_page, error_out=False)
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