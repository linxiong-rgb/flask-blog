"""
文本处理工具模块

该模块提供文本处理相关的工具函数：
- 自动生成文章摘要
- 文本截断和清理
"""

import re
from collections import Counter


def generate_summary(content, max_length=80):
    """
    从文章内容生成精炼摘要（一句话）

    使用智能算法选择最能概括文章内容的句子

    Args:
        content: 文章内容（Markdown格式）
        max_length: 摘要最大长度（默认80字符）

    Returns:
        str: 生成的摘要（一句话，概括文章核心内容）
    """
    if not content:
        return ''

    # 清理内容
    cleaned = _clean_content(content)

    if not cleaned or len(cleaned) < 10:
        return ''

    # 分句
    sentences = _split_sentences(cleaned)

    if not sentences:
        # 如果没有有效句子，直接截取
        return _truncate_cleanly(cleaned, max_length)

    # 提取关键词
    keywords = _extract_keywords(cleaned)[:8]

    # 为每个句子计算综合得分
    scored_sentences = []
    for i, sentence in enumerate(sentences):
        # 跳过过短或过长的句子
        if len(sentence) < 8 or len(sentence) > max_length + 30:
            continue

        score = _calculate_sentence_score(sentence, i, len(sentences), keywords)

        # 长度惩罚：过长或过短的句子降低得分
        length = len(sentence)
        if 15 <= length <= 50:
            score *= 1.3  # 理想长度
        elif 10 <= length <= 70:
            score *= 1.1  # 可接受长度
        elif length > max_length:
            score *= 0.7  # 过长需要截断

        scored_sentences.append((score, i, sentence))

    # 按得分排序
    scored_sentences.sort(key=lambda x: x[0], reverse=True)

    # 选择得分最高的句子
    if scored_sentences:
        best = scored_sentences[0][2]
        # 截断到最大长度
        return _truncate_cleanly(best, max_length)

    # 后备方案：返回第一个有效句子
    return _truncate_cleanly(sentences[0], max_length)


def _calculate_sentence_score(sentence, index, total_sentences, keywords):
    """
    计算句子的综合得分

    Args:
        sentence: 待评分的句子
        index: 句子在原文中的位置
        total_sentences: 总句子数
        keywords: 提取的关键词列表

    Returns:
        float: 句子得分
    """
    score = 0.0

    # 1. 位置得分（首尾句更重要）
    if index == 0:
        score += 15  # 首句最重要
    elif index == total_sentences - 1:
        score += 10  # 尾句通常是总结
    elif index < total_sentences * 0.15:
        score += 7   # 前15%的句子
    elif index > total_sentences * 0.85:
        score += 7   # 后15%的句子

    # 2. 关键词密度得分（最高25分）
    keyword_count = sum(1 for kw in keywords if kw in sentence)
    score += min(keyword_count * 6, 25)

    # 3. 核心指示词得分
    core_indicators = [
        # 总结性词汇
        '总结', '结论', '总之', '简言之', '概括', '综上',
        # 重点强调词
        '关键', '核心', '主要', '重要', '基本',
        # 定义性词汇
        '是指', '是', '就是', '即',
        # 结果性词汇
        '实现', '完成', '达到', '获得',
        # 功能性词汇
        '功能', '特点', '优势', '作用', '效果'
    ]
    for indicator in core_indicators:
        if indicator in sentence:
            score += 5
            break  # 只计算一次

    # 4. 陈述性句子加分（包含"是""可以"等判断词）
    if any(word in sentence for word in ['是', '可以', '能够', '用于', '实现', '完成']):
        score += 4

    # 5. 数字和具体信息加分（但不是纯技术内容）
    if re.search(r'\d+[个项条人次篇]', sentence):
        score += 3

    # 6. 负面得分：技术配置、命令等内容降低得分
    tech_patterns = [
        r'^\s*\w+\s*=',  # 配置项
        r'https?://',  # URL
        r'\d{1,3}\.\d{1,3}\.',  # IP地址
        r'^\w+\.\w+',  # 文件名或域名
    ]
    for pattern in tech_patterns:
        if re.search(pattern, sentence):
            score -= 10
            break

    return score


def _truncate_cleanly(text, max_length):
    """
    干净地截断文本，确保在合适的边界截断

    Args:
        text: 原文本
        max_length: 最大长度

    Returns:
        str: 截断后的文本
    """
    if len(text) <= max_length:
        text = text.strip('，。、；：!!---""''《》')
        # 确保以句号结尾
        if text and text[-1] not in '。！？.!?.。':
            text += '。'
        return text

    # 先移除首尾标点
    text = text.strip('，。、；：!!---""''《》')

    # 尝试在最近的标点处截断
    for i in range(max_length - 1, max(0, max_length - 20), -1):
        if i < len(text) and text[i] in '。，、；':
            result = text[:i + 1].strip()
            if result and result[-1] not in '。！？':
                result += '。'
            return result

    # 如果找不到标点，直接截断并添加省略号
    result = text[:max_length - 1].strip()
    if len(result) > 5:
        result += '...'
    elif result and result[-1] not in '。！？':
        result += '。'

    return result


def _extract_keywords(content, max_keywords=10):
    """提取关键词用于句子评分"""
    # 分词
    words = re.findall(r'[\u4e00-\u9fff]{2,}|[a-zA-Z]{3,}', content)

    # 统计词频
    word_count = Counter(words)

    # 扩展停用词表
    stop_words = {
        '这个', '那个', '可以', '现在', '然后', '因为', '所以', '但是',
        '如果', '虽然', '或者', '而且', '比如', '就是', '什么', '怎么',
        '如何', '一个', '一些', '没有', '不是', '能够', '需要', '应该',
        '已经', '还是', '由于', '通过', '进行', '实现', '完成', '开始',
        '时候', '地方', '问题', '方法', '方式', '结果', '情况', '内容'
    }

    for word in list(word_count.keys()):
        if word.lower() in stop_words:
            del word_count[word]
        elif len(word) < 2:
            del word_count[word]

    # 返回最重要的关键词
    return [word for word, count in word_count.most_common(max_keywords)]


def _clean_content(content):
    """清理内容，移除 Markdown 标记和特殊符号"""
    # 移除代码块
    content = re.sub(r'```[\s\S]*?```', '', content)
    # 移除行内代码
    content = re.sub(r'`[^`]+`', '', content)
    # 移除标题标记
    content = re.sub(r'^#+\s+', '', content, flags=re.MULTILINE)
    # 移除链接（保留链接文本）
    content = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', content)
    # 移除图片
    content = re.sub(r'!\[([^\]]*)\]\([^)]+\)', '', content)
    # 移除加粗和斜体标记
    content = re.sub(r'[*_]{1,2}([^*_]+)[*_]{1,2}', r'\1', content)
    # 移除引用标记
    content = re.sub(r'^>\s+', '', content, flags=re.MULTILINE)
    # 移除列表标记
    content = re.sub(r'^[\s]*[-*+]\s+', '', content, flags=re.MULTILINE)
    content = re.sub(r'^\s*\d+\.\s+', '', content, flags=re.MULTILINE)
    # 移除水平线
    content = re.sub(r'^[-*_]{3,}\s*$', '', content, flags=re.MULTILINE)
    # 移除命令行符号和常见技术符号
    content = re.sub(r'[\$#>]\s*', '', content)
    # 移除换行符转义
    content = re.sub(r'\\[nrt]', '', content)
    # 移除括号内容（通常是非核心信息）
    content = re.sub(r'\([^)]*\)', '', content)
    content = re.sub(r'（[^）]*）', '', content)
    content = re.sub(r'\[[^\]]*\]', '', content)
    content = re.sub(r'[「『][^」』]*[」』]', '', content)
    # 移除URL残留
    content = re.sub(r'https?:[^\s]*', '', content)
    content = re.sub(r'www\.[^\s]*', '', content)
    # 移除IP地址
    content = re.sub(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', '', content)
    # 移除常见的命令/函数模式
    content = re.sub(r'\b[a-z_]+(?:_[a-z]+)+\b', ' ', content)  # snake_case
    content = re.sub(r'\b[A-Z][a-z]+(?:[A-Z][a-z]+)+\b', ' ', content)  # CamelCase
    # 移除文件扩展名
    content = re.sub(r'\b\w+\.(php|js|py|java|sql|sh|bash|yml|yaml|json|xml|html|css)\b', '', content)
    # 移除特殊符号（保留中文、英文、数字、基本标点）
    content = re.sub(r'[^\u4e00-\u9fff\w\s，。！？、；：""''《》.,!?\\-()·]', ' ', content)
    # 移除多余的空白字符
    content = re.sub(r'\s+', ' ', content)

    return content.strip()


def _split_sentences(content):
    """将内容分割成句子列表"""
    # 按句子分割（支持中英文标点）
    sentence_endings = r'[。！？\.!?]+'
    sentences = re.split(sentence_endings, content)

    # 过滤空句子和过短的句子，以及明显的技术性句子
    filtered_sentences = []
    tech_markers = [
        'sudo ', 'pip ', 'npm ', 'yum ', 'apt ', 'function(', 'class ',
        'import ', 'def ', '=>', '->', 'http://', 'https://', '127.0.',
        '192.168.', '0.0.0', 'localhost', 'SELECT ', 'INSERT ',
        'UPDATE ', 'DELETE ', 'CREATE ', 'ALTER ', 'DROP ',
        'GRANT ', 'REVOKE ', 'version(', 'database(', 'table(',
        'column(', 'index(', 'schema(', 'user(', 'password(',
        '安装 ', '配置 ', '部署 ', '服务器 ', '端口 ', '协议 ',
        '版本 ', '时间 ', '作者 ', '标签 ', '生成时间 ',
    ]

    for s in sentences:
        s = s.strip()
        if not s or len(s) < 8:
            continue
        # 跳过明显的代码/命令行内容
        if any(marker in s for marker in tech_markers):
            continue
        # 跳过纯技术配置的句子
        if re.match(r'^[\w\-./]+=[^\s]*$', s):
            continue
        # 跳过过长的数字序列（时间戳等）
        if re.search(r'\d{10,}', s):
            continue
        # 跳过纯英文字母加数字的组合（可能是变量名）
        if re.match(r'^[a-zA-Z0-9_\-\.]+$', s):
            continue
        filtered_sentences.append(s)

    return filtered_sentences


def strip_markdown(content):
    """
    移除 Markdown 格式标记，返回纯文本

    Args:
        content: Markdown 格式的内容

    Returns:
        str: 纯文本内容
    """
    if not content:
        return ''

    # 移除代码块
    content = re.sub(r'```[\s\S]*?```', '', content)
    # 移除行内代码
    content = re.sub(r'`[^`]+`', '', content)
    # 移除标题标记
    content = re.sub(r'^#+\s+', '', content, flags=re.MULTILINE)
    # 移除链接
    content = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', content)
    # 移除图片
    content = re.sub(r'!\[([^\]]*)\]\([^)]+\)', '', content)
    # 移除加粗和斜体标记
    content = re.sub(r'[*_]{1,2}([^*_]+)[*_]{1,2}', r'\1', content)
    # 移除引用标记
    content = re.sub(r'^>\s+', '', content, flags=re.MULTILINE)
    # 移除列表标记
    content = re.sub(r'^[\s]*[-*+]\s+', '', content, flags=re.MULTILINE)
    content = re.sub(r'^\s*\d+\.\s+', '', content, flags=re.MULTILINE)
    # 移除水平线
    content = re.sub(r'^[-*_]{3,}\s*$', '', content, flags=re.MULTILINE)

    return content.strip()


def truncate_text(text, max_length=200, suffix='...'):
    """
    截断文本到指定长度

    Args:
        text: 原文本
        max_length: 最大长度
        suffix: 截断后的后缀

    Returns:
        str: 截断后的文本
    """
    if not text:
        return ''

    text = text.strip()

    if len(text) <= max_length:
        return text

    # 在单词边界处截断（支持中文）
    if max_length > 3:
        truncated = text[:max_length - len(suffix)]
        # 尝试在最近的空格或标点处截断
        for i in range(len(truncated) - 1, max(0, len(truncated) - 20), -1):
            if truncated[i] in ' ,.!?，。！？':
                truncated = truncated[:i + 1]
                break
        return truncated + suffix

    return text[:max_length]
