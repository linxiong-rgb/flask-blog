"""
自动生成文章封面图 - 简约黑色风格

根据文章标题生成简约大气的黑色封面图
"""

import os
import uuid
import re
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

# 配置
COVER_WIDTH = 800
COVER_HEIGHT = 400
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'uploads', 'covers')

# 确保上传目录存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def get_font(size, bold=True):
    """获取字体，支持中文 - 优先使用漂亮的粗体字体"""
    # 优先使用粗体和更好的字体
    font_paths = [
        # macOS 优质粗体
        '/System/Library/Fonts/PingFang.ttc',
        '/System/Library/Fonts/STHeiti Medium.ttc',
        '/System/Library/Fonts/Hiragino Sans GB.ttc',
        # Windows 优质粗体
        'C:/Windows/Fonts/msyhbd.ttc',      # 微软雅黑粗体
        'C:/Windows/Fonts/msyh.ttc',        # 微软雅黑
        'C:/Windows/Fonts/simhei.ttf',      # 黑体
        # Linux 优质字体
        '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',
        '/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc',
        '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
    ]

    for font_path in font_paths:
        if os.path.exists(font_path):
            try:
                return ImageFont.truetype(font_path, size)
            except:
                continue

    return ImageFont.load_default()


def generate_cover_image(title, category_name=None, tags=None, content=None):
    """生成简约黑色风格封面图 - 完整标题显示"""
    # 创建纯白背景图片
    image = Image.new('RGB', (COVER_WIDTH, COVER_HEIGHT), (255, 255, 255))
    draw = ImageDraw.Draw(image)

    if not title:
        title = "文章标题"

    # 清理标题，移除Markdown标记
    title = re.sub(r'[#*`_\[\](){}]', '', title)
    title = title.strip()

    if not title:
        title = "文章标题"

    # 纯黑色
    text_color = (0, 0, 0)

    # 根据标题长度计算合适的字体大小
    title_length = len(title)

    # 智能字体大小计算
    if title_length <= 10:
        font_size = 52
    elif title_length <= 15:
        font_size = 44
    elif title_length <= 20:
        font_size = 38
    elif title_length <= 30:
        font_size = 32
    elif title_length <= 45:
        font_size = 26
    else:
        font_size = 22

    # 获取字体
    font = get_font(font_size)

    # 测量文本尺寸
    try:
        bbox = font.getbbox(title)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
    except:
        text_width = len(title) * (font_size // 2)
        text_height = font_size

    # 如果文字太宽，逐步缩小字体
    max_width = COVER_WIDTH - 80
    while text_width > max_width and font_size > 16:
        font_size -= 2
        font = get_font(font_size)
        try:
            bbox = font.getbbox(title)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
        except:
            text_width = len(title) * (font_size // 2)
            text_height = font_size

    # 计算居中位置
    center_x = COVER_WIDTH // 2
    center_y = COVER_HEIGHT // 2

    x = center_x - text_width // 2
    y = center_y - text_height // 2

    # 确保在画布内
    x = max(40, min(x, COVER_WIDTH - text_width - 40))
    y = max(40, min(y, COVER_HEIGHT - text_height - 40))

    # 绘制黑色文字
    draw.text((x, y), title, fill=text_color, font=font)

    # 生成文件名
    filename = f"cover_{uuid.uuid4().hex[:12]}_{int(datetime.now().timestamp())}.png"
    filepath = os.path.join(UPLOAD_FOLDER, filename)

    # 保存
    image.save(filepath, 'PNG', optimize=True)

    return f"/static/uploads/covers/{filename}"


def generate_cover_from_post(post):
    """从文章对象生成封面图"""
    category_name = post.category.name if post.category else None
    tags = [tag.name for tag in post.tags] if post.tags else []
    return generate_cover_image(post.title, category_name, tags, post.content)
