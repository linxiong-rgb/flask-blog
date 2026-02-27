from flask import Blueprint, make_response
from app.models.post import Post
from app import db
from datetime import datetime
import markdown
import bleach
from urllib.parse import quote

# 从 main.py 导入清理配置
from app.routes.main import ALLOWED_TAGS, ALLOWED_ATTRIBUTES

def clean_html(html_content):
    """使用 bleach 清理 HTML，防止 XSS 攻击"""
    return bleach.clean(
        html_content,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        strip=True
    )

bp = Blueprint('export', __name__)


@bp.route('/export/markdown/<int:post_id>')
def export_markdown(post_id):
    """导出文章为 Markdown 格式"""
    post = Post.query.get_or_404(post_id)

    # 构建 Markdown 内容（包含元数据）
    tags_list = [tag.name for tag in post.tags] if post.tags else []
    tags_str = ", ".join(tags_list) if tags_list else ""

    md_content = f"""---
title: {post.title}
author: {post.author.username}
date: {post.created_at.strftime('%Y-%m-%d %H:%M')}
{f'updated: {post.updated_at.strftime("%Y-%m-%d %H:%M")}' if post.updated_at != post.created_at else ''}
{f'category: {post.category.name}' if post.category else ''}
{f'tags: {tags_str}' if tags_str else ''}
---

# {post.title}

{post.content}
"""

    # 创建响应
    response = make_response(md_content)
    response.headers['Content-Type'] = 'text/markdown; charset=utf-8'
    # 使用 URL 编码处理中文文件名
    safe_filename = f"{post.title}.md".replace(' ', '_').replace('/', '_').replace('\\', '_').replace(':', '_')
    encoded_filename = quote(safe_filename, safe='')
    response.headers['Content-Disposition'] = f"attachment; filename*=UTF-8''{encoded_filename}"

    return response


@bp.route('/export/pdf/<int:post_id>')
def export_pdf(post_id):
    """导出文章为 HTML 格式（可打印为 PDF）"""
    post = Post.query.get_or_404(post_id)

    # 将 Markdown 转换为 HTML
    raw_html = markdown.markdown(
        post.content,
        extensions=[
            'fenced_code',
            'tables',
            'nl2br',
            'sane_lists',
            'codehilite',
        ],
        extension_configs={
            'codehilite': {
                'linenums': False,
                'guess_lang': True,
                'noclasses': False,
                'cssclass': 'codehilite'
            }
        }
    )
    # 清理 HTML 防止 XSS 攻击
    content_html = clean_html(raw_html)

    # 获取标签
    tags_html = ""
    if post.tags:
        tag_list = list(post.tags)
        if tag_list:
            tags_html = '<div class="tags">' + "".join([f'<span class="tag">#{tag.name}</span>' for tag in tag_list]) + '</div>'

    # 更新时间
    updated_text = ""
    if post.updated_at != post.created_at:
        updated_text = f' · 更新于：{post.updated_at.strftime("%Y年%m月%d日")}'

    # 分类
    category_text = ""
    if post.category:
        category_text = f' · 分类：{post.category.name}'

    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{post.title}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            line-height: 1.8;
            max-width: 800px;
            margin: 40px auto;
            padding: 20px;
            color: #333;
        }}
        h1 {{
            font-size: 2em;
            font-weight: 700;
            margin-bottom: 0.5em;
            border-bottom: 2px solid #667eea;
            padding-bottom: 0.5em;
        }}
        h2 {{
            font-size: 1.6em;
            font-weight: 600;
            margin-top: 2em;
            margin-bottom: 1em;
            border-bottom: 1px solid #ddd;
            padding-bottom: 0.4em;
        }}
        h3 {{
            font-size: 1.3em;
            font-weight: 600;
            margin-top: 1.8em;
            margin-bottom: 0.8em;
        }}
        p {{
            margin-bottom: 1.2em;
        }}
        code {{
            background: #f5f5f5;
            padding: 2px 6px;
            border-radius: 4px;
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
        }}
        pre {{
            background: #1e1e1e;
            padding: 16px;
            border-radius: 6px;
            overflow-x: auto;
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            font-size: 0.9em;
            line-height: 1.8;
            border: 1px solid #3c3c3c;
        }}
        pre code {{
            background: transparent;
            color: #d4d4d4;
            padding: 0;
        }}
        .codehilite {{
            background: #1e1e1e;
            padding: 16px;
            border-radius: 6px;
            overflow-x: auto;
        }}
        .codehilite pre {{
            background: transparent;
            border: none;
            padding: 0;
        }}
        blockquote {{
            border-left: 4px solid #667eea;
            padding-left: 1.2em;
            margin: 1.5em 0;
            color: #666;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 1.5em 0;
        }}
        table th, table td {{
            padding: 12px 16px;
            border: 1px solid #ddd;
        }}
        table th {{
            background: #f5f5f5;
            font-weight: 600;
        }}
        .meta {{
            color: #666;
            font-size: 0.9em;
            margin-bottom: 2em;
        }}
        .tags {{
            margin-top: 1em;
        }}
        .tag {{
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 2px 10px;
            border-radius: 12px;
            font-size: 0.85em;
            margin-right: 8px;
        }}
    </style>
</head>
<body>
    <h1>{post.title}</h1>
    <div class="meta">
        作者：{post.author.username} ·
        发布于：{post.created_at.strftime('%Y年%m月%d日')}{updated_text}{category_text}
    </div>
    {tags_html}
    <hr style="border: none; border-top: 1px solid #ddd; margin: 2em 0;">
    {content_html}
</body>
</html>
"""

    # 创建响应
    response = make_response(html_content)
    response.headers['Content-Type'] = 'text/html; charset=utf-8'
    # 使用 URL 编码处理中文文件名
    safe_filename = f"{post.title}.html".replace(' ', '_').replace('/', '_').replace('\\', '_').replace(':', '_')
    encoded_filename = quote(safe_filename, safe='')
    response.headers['Content-Disposition'] = f"attachment; filename*=UTF-8''{encoded_filename}"

    return response
