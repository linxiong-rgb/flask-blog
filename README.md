<div align="center">

# 🔐 Flask Blog System

**现代化、功能完整的 Flask 博客系统**

[![Flask](https://img.shields.io/badge/Flask-3.0.0-blue?logo=flask)](https://flask.palletsprojects.com/)
[![Python](https://img.shields.io/badge/Python-3.8+-green?logo=python)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/linxiong-rgb/flask-blog?style=social)](https://github.com/linxiong-rgb/flask-blog/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/linxiong-rgb/flask-blog?style=social)](https://github.com/linxiong-rgb/flask-blog/network/members)
[![GitHub issues](https://img.shields.io/github/issues/linxiong-rgb/flask-blog)](https://github.com/linxiong-rgb/flask-blog/issues)
[![GitHub pull requests](https://img.shields.io/github/issues-pr/linxiong-rgb/flask-blog)](https://github.com/linxiong-rgb/flask-blog/pulls)

</div>

---

## ✨ 项目简介

一个基于 Flask 开发的现代化博客系统，专注于简洁、高效的用户体验。系统采用 Bootstrap 5 构建响应式前端界面，支持 Markdown 写作、夜间模式、智能搜索等功能。

![Demo](https://img.shields.io/badge/Demo-Online-success?logo=data:image/svg%2Bxml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxNiIgaGVpZ2h0PSIxNiIgdmlld0JveD0iMCAwIDE2IDE2Ij48cGF0aCBkPSJNOCAwaC0ydjJoMnYyek0wIDBoMnYyaDJ2LTJoMnYtMnoiIGZpbGw9IiNmZmYiLz48L3N2Zz4=)

### 🎯 核心特性

- 🚀 **快速部署** - 支持多种部署方案（Vercel、Render、Docker、VPS）
- 📝 **Markdown 写作** - 支持标准 Markdown 语法和代码高亮
- 🌓 **夜间模式** - 护眼的深色主题，偏好自动保存
- 🔍 **智能搜索** - 实时搜索建议，支持文章/分类/标签
- 📱 **响应式设计** - 完美适配手机、平板和电脑
- 🔐 **用户认证** - Flask-Login 用户认证系统
- 📊 **数据统计** - 文章浏览量统计

---

## 🛠 技术栈

| 类别 | 技术 | 版本 |
|------|------|------|
| 后端框架 | Flask | 3.0.0 |
| 数据库 | SQLite | 3 |
| ORM | SQLAlchemy | 3.1.1 |
| 用户认证 | Flask-Login | 0.6.3 |
| CSRF 保护 | Flask-WTF | 1.2.1 |
| 前端框架 | Bootstrap | 5.3.0 |
| 图标库 | Bootstrap Icons | 1.11.0 |
| Markdown | Python-Markdown | 3.5.1 |

---

## 📸 功能截图

### 🏠 首页展示
- 卡片式文章列表
- 渐变色主题设计
- 响应式布局

### 📖 文章阅读
- Typora 风格阅读体验
- 自动生成目录导航
- 代码语法高亮
- 阅读进度条

### 🎛️ 管理后台
- 数据统计仪表板
- 文章 CRUD 管理
- 分类/标签管理
- 友情链接管理

---

## 🚀 快速开始

### 环境要求

- Python 3.8+
- pip 包管理器

### 安装步骤

```bash
# 1. 克隆项目
git clone https://github.com/linxiong-rgb/flask-blog.git
cd flask-blog

# 2. 安装依赖
pip install -r requirements.txt

# 3. 初始化数据库
python reset_database.py

# 4. 运行应用
python run.py
```

### 访问博客

打开浏览器访问: `http://localhost:5000`

**默认管理员账号：**
- 用户名: `admin01`
- 密码: `123456`

> ⚠️ **安全提醒**：首次使用后请立即修改默认密码！

---

## 📖 功能特点

### 📝 核心功能
- ✅ 用户注册和登录 - Flask-Login 用户认证
- ✅ 文章管理 - 创建、编辑、删除文章
- ✅ Markdown 写作 - 支持标准 Markdown 语法
- ✅ 文章状态 - 发布/草稿管理
- ✅ 浏览统计 - 文章浏览量统计
- ✅ 文章收藏 - 用户收藏喜欢的文章

### 🎯 高级功能
- ✅ **智能搜索** - 实时搜索建议，支持文章/分类/标签搜索
- ✅ **分类管理** - 将文章组织到不同分类
- ✅ **标签系统** - 多标签支持，标签云展示
- ✅ **文章归档** - 按日期浏览文章
- ✅ **友情链接** - 管理和展示友情链接
- ✅ **RSS 订阅** - 自动生成 RSS Feed
- ✅ **Sitemap** - 自动生成站点地图
- ✅ **文章分享** - 支持微博、QQ、微信分享

### 🎨 界面特色
- ✅ **夜间模式** - 护眼的深色主题，偏好自动保存
- ✅ **响应式设计** - 完美支持手机、平板和电脑
- ✅ **渐变配色** - 紫色渐变主题，时尚美观
- ✅ **卡片式布局** - Material Design 风格
- ✅ **流畅动画** - 过渡和悬停动画效果
- ✅ **Typora 风格** - 优雅的文章阅读体验
- ✅ **目录导航** - 自动生成文章目录
- ✅ **阅读进度条** - 顶部显示阅读进度
- ✅ **代码高亮** - 代码块语法高亮
- ✅ **字体调节** - 支持字体大小调节

### 🔧 管理功能
- ✅ **仪表板** - 数据统计和快速操作
- ✅ **文章管理** - 列表视图，删除确认
- ✅ **Markdown 导入** - 支持单个/批量导入 .md 文件
- ✅ **智能摘要** - 自动生成文章摘要
- ✅ **封面图生成** - 自动生成简约封面图
- ✅ **收藏管理** - 查看用户收藏列表
- ✅ **数据导出** - 导出 Markdown/HTML
- ✅ **友链管理** - 后台管理友情链接

---

## 📁 项目结构

```
flask-blog/
├── app/
│   ├── __init__.py          # 应用工厂
│   ├── models/              # 数据模型
│   │   ├── user.py          # 用户模型
│   │   ├── post.py          # 文章模型
│   │   ├── post_bookmark.py # 收藏模型
│   │   ├── category.py      # 分类模型
│   │   ├── tag.py           # 标签模型
│   │   └── friend_link.py   # 友链模型
│   ├── routes/              # 路由
│   │   ├── main.py          # 主路由
│   │   ├── auth.py          # 认证路由
│   │   ├── admin.py         # 管理路由
│   │   └── export.py        # 导出路由
│   ├── templates/           # 模板
│   │   ├── base.html        # 基础模板
│   │   ├── index.html       # 首页
│   │   ├── post.html        # 文章详情
│   │   ├── search.html      # 搜索页
│   │   ├── category.html    # 分类页
│   │   ├── tag.html         # 标签页
│   │   ├── archive.html     # 归档页
│   │   ├── categories.html  # 分类列表
│   │   └── admin/           # 管理模板
│   ├── static/              # 静态文件
│   │   ├── css/             # 样式文件
│   │   ├── js/              # JavaScript
│   │   ├── vendor/          # 第三方库
│   │   └── uploads/         # 上传文件
│   ├── forms.py             # 表单类
│   ├── utils/               # 工具函数
│   └── security.py          # 安全配置
├── instance/                # 实例文件夹
├── .github/                 # GitHub 配置
│   ├── ISSUE_TEMPLATE/      # Issue 模板
│   └── pull_request_template.md
├── requirements.txt         # 依赖列表
├── run.py                   # 启动脚本
├── reset_database.py        # 数据库重置脚本
├── LICENSE                  # MIT 许可证
├── README.md               # 项目文档
├── CONTRIBUTING.md         # 贡献指南
└── DEPLOY.md               # 部署文档
```

---

## 🎛 配置说明

### 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `SECRET_KEY` | Flask 密钥 | 自动生成 |
| `DATABASE_URL` | 数据库连接 | `sqlite:///blog.db` |
| `DEBUG` | 调试模式 | `True` |
| `FLASK_ENV` | 运行环境 | `development` |

### 主题定制

编辑 `app/static/css/style.css` 可自定义：

- `--primary-color` - 主色调
- `--gradient` - 渐变色
- `--text-color` - 文字颜色
- `--bg-color` - 背景色
- `--card-bg` - 卡片背景色

---

## 🐛 常见问题

### 端口被占用

修改 `run.py` 中的端口号：

```python
app.run(debug=True, host='0.0.0.0', port=5001)
```

### 搜索无结果

确保：
1. 文章已发布（非草稿状态）
2. 搜索关键词在标题/内容/摘要中

### 忘记管理员密码

运行数据库重置脚本：

```bash
python reset_database.py
```

---

## 🤝 贡献

欢迎贡献代码！请查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解详情。

### 开发流程

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

## 📄 开源协议

本项目采用 [MIT License](LICENSE) 开源协议。

---

## 📮 联系方式

- **作者**: linxiong-rgb
- **邮箱**: 3497875641@qq.com
- **GitHub**: [@linxiong-rgb](https://github.com/linxiong-rgb)

---

## ⭐ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=linxiong-rgb/flask-blog&type=Date)](https://star-history.com/#linxiong-rgb/flask-blog&Date)

---

<div align="center">

**如果觉得项目对你有帮助，请给个 Star ⭐**

Made with ❤️ using Flask

</div>
