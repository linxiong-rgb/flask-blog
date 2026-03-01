# 技术栈徽章使用指南

本项目提供了本地 CSS 徽章组件，无需依赖外部服务（如 shields.io），可以在任何网络环境下正常显示。

## 为什么使用本地徽章？

1. **网络稳定** - 不依赖外部 CDN，国内网络环境友好
2. **加载快速** - 本地资源，无额外请求
3. **样式可控** - 完全自定义样式和动画
4. **主题适配** - 自动适配明暗主题

## 基础用法

### HTML 示例

```html
<!-- 单个徽章 -->
<div class="tech-badge tech-badge-flask">
    <i class="bi bi-server"></i>
    <span>Flask 3.0</span>
</div>

<!-- 徽章组 -->
<div class="tech-badge-group">
    <div class="tech-badge tech-badge-python">
        <i class="bi bi-braces"></i>
        <span>Python 3.10+</span>
    </div>
    <div class="tech-badge tech-badge-flask">
        <i class="bi bi-server"></i>
        <span>Flask 3.0</span>
    </div>
    <div class="tech-badge tech-badge-sqlalchemy">
        <i class="bi bi-database"></i>
        <span>SQLAlchemy</span>
    </div>
</div>
```

### 可用徽章类型

| 类型 | 类名 | 说明 |
|------|------|------|
| Flask | `tech-badge-flask` | Flask 框架（紫色渐变）|
| Python | `tech-badge-python` | Python 语言（蓝黄渐变）|
| SQLAlchemy | `tech-badge-sqlalchemy` | ORM（深蓝渐变）|
| Bootstrap | `tech-badge-bootstrap` | Bootstrap 框架（紫色）|
| PostgreSQL | `tech-badge-postgres` | PostgreSQL 数据库（深青）|
| SQLite | `tech-badge-sqlite` | SQLite 数据库（蓝色）|
| Markdown | `tech-badge-markdown` | Markdown 支持（蓝色）|
| MIT 许可证 | `tech-badge-mit` | MIT 开源协议（黄色）|
| GitHub Stars | `tech-badge-stars` | GitHub 星标数（金色）|
| GitHub Forks | `tech-badge-forks` | GitHub 分叉数（灰色）|

## 尺寸变体

```html
<!-- 小徽章 -->
<div class="tech-badge tech-badge-flask tech-badge-sm">
    <i class="bi bi-server"></i>
    <span>Flask 3.0</span>
</div>

<!-- 标准徽章 -->
<div class="tech-badge tech-badge-flask">
    <i class="bi bi-server"></i>
    <span>Flask 3.0</span>
</div>

<!-- 大徽章 -->
<div class="tech-badge tech-badge-flask tech-badge-lg">
    <i class="bi bi-server"></i>
    <span>Flask 3.0</span>
</div>
```

## 状态徽章

```html
<!-- 成功状态 -->
<span class="status-badge status-badge-success">运行中</span>

<!-- 警告状态 -->
<span class="status-badge status-badge-warning">需注意</span>

<!-- 错误状态 -->
<span class="status-badge status-badge-error">已停止</span>

<!-- 信息状态 -->
<span class="status-badge status-badge-info">处理中</span>
```

## 完整示例

```html
<div class="tech-badges-container">
    <div class="tech-badges-title">技术栈</div>
    <div class="tech-badge-group">
        <div class="tech-badge tech-badge-python">
            <i class="bi bi-braces"></i>
            <span>Python 3.10+</span>
        </div>
        <div class="tech-badge tech-badge-flask">
            <i class="bi bi-server"></i>
            <span>Flask 3.0</span>
        </div>
        <div class="tech-badge tech-badge-sqlalchemy">
            <i class="bi bi-database"></i>
            <span>SQLAlchemy</span>
        </div>
        <div class="tech-badge tech-badge-bootstrap">
            <i class="bi bi-bootstrap"></i>
            <span>Bootstrap 5</span>
        </div>
    </div>
</div>
```

## 在模板中使用

### Jinja2 宏示例

创建 `app/templates/components/badges.html`:

```jinja2
{% macro tech_badge(type, text, icon=None, size='') %}
<div class="tech-badge tech-badge-{{ type }} {{ size }}">
    {% if icon %}
    <i class="bi bi-{{ icon }}"></i>
    {% endif %}
    <span>{{ text }}</span>
</div>
{% endmacro %}

{% macro tech_badge_group(badges) %}
<div class="tech-badge-group">
    {% for badge in badges %}
        {{ tech_badge(badge.type, badge.text, badge.icon, badge.size|default('')) }}
    {% endfor %}
</div>
{% endmacro %}
```

使用示例：

```jinja2
{% from 'components/badges.html' import tech_badge, tech_badge_group %}

{{ tech_badge('flask', 'Flask 3.0', 'server') }}

{{ tech_badge_group([
    {'type': 'python', 'text': 'Python 3.10+', 'icon': 'braces'},
    {'type': 'flask', 'text': 'Flask 3.0', 'icon': 'server'},
    {'type': 'postgresql', 'text': 'PostgreSQL', 'icon': 'database'}
]) }}
```

## 自定义样式

如果需要自定义徽章样式，可以添加自己的 CSS 类：

```css
.tech-badge-myapp {
    background: linear-gradient(135deg, #your-color-1 0%, #your-color-2 100%);
    color: white;
}
```

## 主题适配

徽章样式已支持明暗主题自动切换，通过 CSS 变量实现：

```css
.tech-badges-container {
    background: var(--card-bg, #ffffff);
    border-color: var(--border-color, #e0e0e0);
}

[data-theme="dark"] .tech-badges-container {
    background: var(--card-bg, #1a1a2e);
    border-color: var(--border-color, #2d2d44);
}
```

## 常见问题

**Q: 为什么不用 shields.io？**

A: shields.io 在国内访问不稳定，可能被 CDN 拦截或加载缓慢。本地徽章完全可控，不受网络影响。

**Q: 如何添加新的徽章类型？**

A: 在 `badges.css` 中添加新的 `.tech-badge-xxx` 类，定义渐变色和样式即可。

**Q: 可以在 Markdown 中使用吗？**

A: Markdown 文件（如 README.md）仍使用 shields.io，因为 GitHub 支持。但在网页模板中应使用本地徽章。
