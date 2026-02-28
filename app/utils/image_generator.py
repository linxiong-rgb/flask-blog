"""
自动生成文章封面图 - 简约黑色风格

根据文章标题生成简约大气的黑色封面图
支持跨平台中文字体自动检测
"""

import os
import uuid
import re
import logging
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

# 配置日志
logger = logging.getLogger(__name__)

# 配置
COVER_WIDTH = 800
COVER_HEIGHT = 400
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'uploads', 'covers')

# 确保上传目录存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 字体缓存（避免重复加载）
_font_cache = {}


def get_project_font_dir():
    """获取项目内字体目录的绝对路径"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(os.path.dirname(current_dir), 'static', 'fonts')


def get_font(size, bold=True):
    """
    获取支持中文的字体

    优先级：
    1. 项目内字体 (app/static/fonts/)
    2. macOS 系统字体
    3. Windows 系统字体
    4. Linux 系统字体 (Render/服务器)

    Args:
        size: 字体大小
        bold: 是否使用粗体

    Returns:
        PIL.ImageFont: 字体对象
    """
    # 使用缓存键
    cache_key = f"font_{size}_{bold}"
    if cache_key in _font_cache:
        return _font_cache[cache_key]

    # 项目内字体目录
    project_font_dir = get_project_font_dir()

    # 字体路径列表（按优先级排序）
    font_paths = [
        # === 项目内字体（最高优先级，确保部署可用）===
        os.path.join(project_font_dir, 'simkai.ttf'),  # 楷体
        os.path.join(project_font_dir, 'simsunb.ttf'), # 加粗宋体
        os.path.join(project_font_dir, 'simsun.ttc'),  # 宋体
        os.path.join(project_font_dir, 'msyhbd.ttc'),  # 微软雅黑粗体
        os.path.join(project_font_dir, 'msyh.ttc'),    # 微软雅黑
        os.path.join(project_font_dir, 'simhei.ttf'),  # 黑体
        os.path.join(project_font_dir, 'wqy-zenhei.ttc'),  # 文泉驿正黑
        os.path.join(project_font_dir, '*.ttf'),       # 任意 ttf
        os.path.join(project_font_dir, '*.ttc'),       # 任意 ttc

        # === macOS 系统字体 ===
        '/System/Library/Fonts/PingFang.ttc',
        '/System/Library/Fonts/STHeiti Medium.ttc',
        '/System/Library/Fonts/Hiragino Sans GB.ttc',
        '/Library/Fonts/Arial Unicode.ttf',

        # === Windows 系统字体 ===
        'C:/Windows/Fonts/msyhbd.ttc',
        'C:/Windows/Fonts/msyh.ttc',
        'C:/Windows/Fonts/simhei.ttf',
        'C:/Windows/Fonts/simsun.ttc',
        'C:/Windows/Fonts/simkai.ttf',

        # === Linux 中文字体（Render/服务器环境）===
        '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',
        '/usr/share/fonts/truetype/wqy/wqy-microhei.ttc',
        '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc',
        '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
        '/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc',
        '/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc',
        '/usr/share/fonts/noto-cjk/NotoSansCJK-Bold.ttc',
        '/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc',
        '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',  # 备用
    ]

    # 如果项目内有字体文件，也动态扫描
    if os.path.exists(project_font_dir):
        for f in sorted(os.listdir(project_font_dir)):
            if f.endswith(('.ttf', '.ttc', '.otf')):
                full_path = os.path.join(project_font_dir, f)
                if full_path not in font_paths:
                    font_paths.insert(0, full_path)  # 插入到最前面

    # 尝试加载字体
    for font_path in font_paths:
        # 跳过通配符路径
        if '*' in font_path:
            continue

        if os.path.exists(font_path):
            try:
                font = ImageFont.truetype(font_path, size)
                logger.debug(f"使用字体: {font_path} (size={size})")
                _font_cache[cache_key] = font
                return font
            except Exception as e:
                logger.warning(f"字体加载失败 {font_path}: {e}")
                continue

    # 如果所有字体都失败，记录警告并使用默认字体
    logger.warning("无法加载中文字体，使用默认字体（中文将显示为方块）")
    default_font = ImageFont.load_default()
    _font_cache[cache_key] = default_font
    return default_font


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

    logger.info(f"封面图已生成: {filename} (标题: {title})")

    return f"/static/uploads/covers/{filename}"


def generate_cover_from_post(post):
    """从文章对象生成封面图"""
    category_name = post.category.name if post.category else None
    tags = [tag.name for tag in post.tags] if post.tags else []
    return generate_cover_image(post.title, category_name, tags, post.content)


def test_font_loading():
    """测试字体加载（用于调试）"""
    print("=== 字体加载测试 ===")

    # 测试不同大小的字体
    for size in [20, 30, 40]:
        font = get_font(size)
        print(f"Size {size}: {font}")

    # 测试中文文本
    test_text = "信息安全专业大三突围指南"
    print(f"\n测试文本: {test_text}")
    font = get_font(40)
    bbox = font.getbbox(test_text)
    print(f"文本尺寸: {bbox}")

    # 项目字体目录
    project_font_dir = get_project_font_dir()
    print(f"\n项目字体目录: {project_font_dir}")
    if os.path.exists(project_font_dir):
        print("字体文件:")
        for f in os.listdir(project_font_dir):
            print(f"  - {f}")
    else:
        print("字体目录不存在！")


if __name__ == '__main__':
    test_font_loading()
