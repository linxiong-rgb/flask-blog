"""
文本处理工具模块

该模块提供文本处理相关的工具函数：
- 自动生成文章摘要
- 文本截断和清理
"""

import re
from collections import Counter


def generate_summary(content, max_length=200):
    """
    从文章内容智能生成摘要

    使用基于关键词和句子位置的算法，智能提取最具代表性的句子

    Args:
        content: 文章内容（Markdown格式）
        max_length: 摘要最大长度（默认200字符）

    Returns:
        str: 生成的摘要（1-3句话，无特殊符号）
    """
    if not content:
        return ''

    # 步骤1: 清理 Markdown 和特殊符号
    cleaned_content = _clean_content(content)

    # 步骤2: 分割成句子
    sentences = _split_sentences(cleaned_content)

    if not sentences:
        return ''

    # 步骤3: 提取关键词用于评分
    keywords = _extract_keywords(cleaned_content)

    if not sentences:
        return ''

    # 步骤4: 智能选择句子
    selected_sentences = _select_best_sentences(sentences, keywords, max_length)

    if not selected_sentences:
        # 降级方案：使用首句
        selected_sentences = [sentences[0]] if sentences else []

    # 步骤5: 组合并优化摘要
    summary = ' '.join(selected_sentences)

    return _finalize_summary(summary, max_length)


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


def _select_best_sentences(sentences, keywords, max_length):
    """智能选择最佳句子"""
    if not sentences:
        return []

    # 为每个句子计算得分
    scored_sentences = []
    for i, sentence in enumerate(sentences):
        score = 0

        # 1. 位置得分：首句和尾句得分更高
        if i == 0:
            score += 10  # 首句最重要
        elif i == len(sentences) - 1:
            score += 8   # 尾句通常是总结
        elif i < len(sentences) * 0.2:
            score += 5   # 前20%的句子
        elif i > len(sentences) * 0.8:
            score += 5   # 后20%的句子

        # 2. 关键词密度得分
        keyword_count = sum(1 for kw in keywords if kw in sentence)
        score += keyword_count * 3

        # 3. 句子长度得分：适中长度的句子更好
        length = len(sentence)
        if 15 <= length <= 50:
            score += 5
        elif 10 <= length <= 80:
            score += 3

        # 4. 特征词加分（包含特定词汇的句子更重要）
        feature_words = ['总结', '结论', '因此', '总之', '简言之', '概括',
                        '首先', '其次', '最后', '关键', '核心', '主要',
                        '实现', '功能', '特点', '优势', '作用', '意义']
        if any(fw in sentence for fw in feature_words):
            score += 4

        scored_sentences.append((score, i, sentence))

    # 按得分排序
    scored_sentences.sort(key=lambda x: x[0], reverse=True)

    # 选择最佳句子
    selected = []
    total_length = 0

    # 优先选择得分最高的句子
    for score, idx, sentence in scored_sentences:
        if total_length + len(sentence) > max_length:
            # 如果加上这句会超出长度，尝试缩短
            remaining = max_length - total_length - 5
            if remaining > 15:  # 至少保留15个字符
                shortened = sentence[:remaining]
                if len(shortened) > 5:
                    selected.append(shortened)
                    break
            else:
                break

        selected.append(sentence)
        total_length += len(sentence)

        # 限制最多3句话
        if len(selected) >= 3:
            break

    # 按原文顺序排序
    selected_with_idx = [(s, next((i for i, _, sent in scored_sentences if sent == s), 999))
                         for s in selected]
    selected_with_idx.sort(key=lambda x: x[1])

    return [s for s, _ in selected_with_idx]


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


def _finalize_summary(summary, max_length):
    """最终处理摘要"""
    # 去除多余空格
    summary = re.sub(r'\s+', ' ', summary).strip()

    # 移除开头和结尾的特殊符号
    summary = summary.strip('，。、；：!!---""''《》')

    # 截断到最大长度
    if len(summary) > max_length:
        summary = summary[:max_length - 1].strip()
        # 确保不在词中间截断（对中文）
        if summary and summary[-1] not in '。，！？':
            # 尝试找到最近的标点
            for i in range(len(summary) - 1, max(0, len(summary) - 20), -1):
                if summary[i] in '。，、；':
                    summary = summary[:i + 1]
                    break
            else:
                summary += '...'

    # 添加结尾标点
    if summary and summary[-1] not in '。！？.!?.。':
        summary += '。'

    return summary


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
