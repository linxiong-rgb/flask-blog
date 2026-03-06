<div align="center">

# 🌟 Flask Blog System

# **现代化 Flask 博客 + 云相册系统**

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0.0-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![GitHub Stars](https://img.shields.io/github/stars/linxiong-rgb/flask-blog?style=social)](https://github.com/linxiong-rgb/flask-blog/stargazers)

**功能完整 · 界面美观 · 易于部署**

</div>

---

## ✨ 项目简介

一个基于 Flask 开发的**全功能博客系统 + 云相册**，专注于简洁、高效的用户体验。系统采用 Bootstrap 5 构建响应式前端界面，支持 Markdown 写作、夜间模式、智能搜索、云相册管理等丰富功能。

---

## 🎯 核心特性

### 📝 博客系统
- **Markdown 写作** - 支持标准 Markdown 语法和代码高亮
- **文章管理** - 发布/草稿/私密/密码保护
- **智能搜索** - 实时搜索建议，支持文章/分类/标签
- **分类标签** - 完善的分类和标签系统
- **夜间模式** - 护眼的深色主题
- **数据统计** - 文章浏览量统计
- **定时发布** - 设置文章发布时间，自动发布
- **收藏功能** - 收藏喜欢的文章
- **数据导出** - 支持 Markdown/HTML 格式导出

### 🖼️ 云相册系统
- **相册管理** - 创建和管理个人相册
- **图片上传** - 批量上传图片到 GitHub 存储
- **图片主题** - 为图片添加主题描述
- **权限设置** - 公开/私密相册切换
- **图片查看器** - 支持缩放、拖拽、全屏查看
- **图片下载** - 一键下载高清原图
- **GitHub 存储** - 免费 GitHub 图床，CDN 加速
- **响应式设计** - 完美适配移动端

### 🎨 界面特色
- **响应式设计** - 完美适配手机、平板和电脑
- **渐变配色** - 紫色渐变主题，时尚美观
- **卡片式布局** - Material Design 风格
- **流畅动画** - 过渡和悬停动画效果
- **阅读体验** - 目录导航，阅读进度条

### 🔒 安全特性
- **CSRF 保护** - 所有表单 CSRF 保护
- **XSS 防护** - HTML 内容清理
- **SQL 注入防护** - SQLAlchemy ORM
- **密码安全** - werkzeug 安全哈希
- **登录保护** - 速率限制和 IP 记录

---

## 🛠️ 技术栈

| 类别 | 技术 | 版本 |
|:---:|:---:|:---:|
| **后端框架** | Flask | 3.0.0 |
| **数据库** | SQLite / PostgreSQL | 3 / 14+ |
| **ORM** | SQLAlchemy | 3.1.1 |
| **用户认证** | Flask-Login | 0.6.3 |
| **CSRF 保护** | Flask-WTF | 1.2.1 |
| **Markdown** | Python-Markdown | 3.5.1 |
| **环境变量** | python-dotenv | 1.0.0+ |
| **缓存** | Flask-Caching | 2.1.0 |
| **WSGI 服务器** | Gunicorn | 21.2.0 |
| **前端框架** | Bootstrap | 5.3.0 |
| **图标库** | Bootstrap Icons | 1.11.0 |

---

## 📸 功能展示

### 云相册功能

| 功能 | 描述 |
|:---|:---|
| **相册管理** | 创建相册，设置名称、描述、可见性 |
| **图片上传** | 批量上传，支持多种图片格式 |
| **图片主题** | 为图片添加主题描述文字 |
| **权限设置** | 公开/私密相册切换 |
| **图片查看器** | 缩放(10%-500%)、拖拽平移、键盘快捷键 |
| **图片下载** | 支持跨域图片下载 |
| **GitHub 存储** | 免费 GitHub 图床，CDN 加速 |

### 博客功能

| 功能 | 描述 |
|:---|:---|
| **文章管理** | 创建、编辑、删除、发布/草稿 |
| **文章权限** | 公开、私密、密码保护 |
| **分类系统** | 多级分类，SEO 友好 |
| **标签系统** | 多标签，标签云展示 |
| **定时发布** | 设置未来时间自动发布 |
| **文章收藏** | 用户收藏喜欢的文章 |
| **数据导出** | Markdown/HTML 格式导出 |
| **友情链接** | 友链管理与展示 |
| **RSS 订阅** | 自动生成 RSS Feed |
| **Sitemap** | 自动生成站点地图 |

### 管理功能

| 功能 | 描述 |
|:---|:---|
| **仪表板** | 数据统计，快速操作 |
| **文章管理** | 列表视图，批量操作 |
| **Markdown 导入** | 单个/批量导入 .md 文件 |
| **封面图生成** | 一键生成简约封面 |
| **收藏管理** | 用户收藏列表 |
| **友链管理** | 后台管理友情链接 |
| **定时任务** | 查看和管理定时发布的文章 |

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

# 2. 创建并激活虚拟环境
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置环境变量（可选）
cp .env.example .env
# 编辑 .env 文件，设置 SECRET_KEY 等变量

# 5. 初始化数据库
python reset_database.py

# 6. 运行应用
python run.py
```

### 访问应用

打开浏览器访问: `http://localhost:5000`

**默认管理员账号：**
- 用户名: `admin01`
- 密码: `123456`

> ⚠️ **安全提醒**：首次使用后请立即修改默认密码！

---

## 📁 项目结构

```
flask-blog/
├── app/
│   ├── __init__.py              # 应用工厂
│   ├── models/                  # 数据模型
│   │   ├── __init__.py
│   │   ├── user.py              # 用户模型
│   │   ├── post.py              # 文章、分类、标签模型
│   │   ├── gallery.py           # 相册、图片模型
│   │   ├── friend_link.py       # 友链模型
│   │   └── post_bookmark.py     # 收藏模型
│   ├── routes/                  # 路由
│   │   ├── __init__.py
│   │   ├── main.py              # 主路由（首页、文章、搜索等）
│   │   ├── auth.py              # 认证路由（登录、注册）
│   │   ├── admin.py             # 管理后台路由
│   │   ├── gallery.py           # 云相册路由
│   │   └── export.py            # 导出路由
│   ├── templates/               # Jinja2 模板
│   │   ├── base.html            # 基础模板
│   │   ├── index.html           # 首页
│   │   ├── post.html            # 文章详情
│   │   ├── gallery/             # 云相册模板
│   │   │   ├── base.html        # 相册基础模板
│   │   │   ├── index.html       # 相册列表
│   │   │   ├── view_album.html  # 相册详情（含图片查看器）
│   │   │   ├── new_album.html   # 创建相册
│   │   │   └── edit_album.html  # 编辑相册
│   │   └── admin/               # 管理后台模板
│   ├── static/                  # 静态文件
│   │   ├── css/                 # 自定义样式
│   │   ├── js/                  # JavaScript 文件
│   │   ├── vendor/              # 第三方库
│   │   └── img/                 # 默认图片
│   ├── forms.py                 # WTForms 表单类
│   ├── utils/                   # 工具函数
│   │   ├── storage.py           # GitHub 存储后端
│   │   ├── image_generator.py   # 封面图生成器
│   │   ├── text.py              # 文本处理工具
│   │   └── scheduler.py         # 定时任务调度器
│   └── security.py              # 安全配置
├── instance/                    # 实例文件夹（数据库等）
├── logs/                        # 日志文件
├── docs/                        # 项目文档
│   ├── GITHUB_STORAGE.md        # GitHub 图床配置指南
│   └── GALLERY_DESIGN_REFERENCE.md  # 相册设计参考（已废弃）
├── requirements.txt             # Python 依赖
├── run.py                       # 启动脚本
├── reset_database.py            # 数据库重置脚本
├── update_database.py           # 数据库更新脚本
├── .env                         # 环境变量（需自行创建）
├── .env.example                 # 环境变量示例
├── .gitignore                   # Git 忽略文件
├── README.md                    # 项目文档
├── CHANGELOG.md                 # 更新日志
├── DEPLOY.md                    # 部署文档
├── CONTRIBUTING.md              # 贡献指南
├── Procfile                     # Render 部署配置
├── runtime.txt                  # Python 版本
└── LICENSE                      # MIT 开源协议
```

---

## ⚙️ 配置说明

### 环境变量

| 变量名 | 说明 | 默认值 | 必需 |
|:-------|:-----|-------|:----:|
| `SECRET_KEY` | Flask 密钥 | 自动生成 | ✅ |
| `DATABASE_URL` | 数据库连接 | `sqlite:///blog.db` | ❌ |
| `DEBUG` | 调试模式 | `False` | ❌ |
| `GITHUB_TOKEN` | GitHub Token | 无 | ❌ |
| `GITHUB_REPO` | GitHub 仓库 | 无 | ❌ |
| `GITHUB_BRANCH` | GitHub 分支 | `main` | ❌ |
| `GITHUB_PATH` | 图片存储路径 | `images` | ❌ |

### 配置 GitHub 图床（推荐）

使用 GitHub 作为免费图床，享受 jsDelivr CDN 加速：

1. 创建 GitHub 仓库存放图片（如：`username/blog-images`）
2. 生成 Personal Access Token（需要 `repo` 权限）
3. 配置环境变量：
   - `GITHUB_TOKEN`: `ghp_xxxxxxxxxxxx`
   - `GITHUB_REPO`: `username/blog-images`
   - `GITHUB_BRANCH`: `main`
   - `GITHUB_PATH`: `images`

详见：[docs/GITHUB_STORAGE.md](docs/GITHUB_STORAGE.md)

---

## 🌐 部署指南

### 快速部署到 Render

<div align="center">

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://dashboard.render.com/)

</div>

1. **Fork 本仓库**
2. **在 Render 创建 PostgreSQL 数据库**（免费套餐）
3. **创建 Web Service**，连接代码仓库
4. **配置环境变量**：
   - `SECRET_KEY`: 随机字符串
   - `DATABASE_URL`: Render 提供的 PostgreSQL URL
   - `GITHUB_TOKEN`: GitHub Token（可选）
   - `GITHUB_REPO`: GitHub 仓库（可选）
5. **部署完成后访问 `/init-db`** 初始化数据库
6. **使用 `/check-db`** 检查数据库状态

详细步骤请查看：[DEPLOY.md](DEPLOY.md)

### 其他部署方式

- **Vercel** - 零配置部署
- **Railway** - 一键部署
- **Docker** - 容器化部署
- **VPS** - 传统部署

---

## ❓ 常见问题

### 端口被占用

修改 `run.py` 中的端口号：
```python
app.run(debug=True, host='0.0.0.0', port=5001)
```

### 忘记管理员密码

**本地开发：**
```bash
python reset_database.py
```

**生产环境：**
访问 `https://你的域名/init-db` 重新创建管理员

### 图片上传失败

确保：
1. GitHub 仓库配置正确（Token、仓库名）
2. GitHub Token 有 `repo` 权限
3. 图片格式支持（PNG、JPG、GIF、WebP、BMP）
4. 图片大小不超过限制（默认 50MB）

### 部署后无法登录

1. 访问 `/init-db` 初始化数据库
2. 使用 `/check-db` 检查用户状态
3. 查看应用日志获取错误信息

### 数据库错误

如果遇到数据库表不存在或字段缺失：
```bash
python update_database.py
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

## 📝 更新日志

### v2.1.0 (2024-03)

**云相册系统重构**
- ✨ 简化相册系统，移除复杂功能
- ✨ 新增图片主题描述功能
- ✨ 新增高级图片查看器（缩放/拖拽/下载）
- ✨ 优化图片下载，支持跨域图片
- 🎨 重新设计相册 UI
- 🐛 修复灯箱按钮点击问题
- 🐛 修复图片加载问题

**博客系统优化**
- ✨ 新增定时发布功能
- ✨ 新增文章收藏功能
- 🎨 优化移动端体验

### v2.0.0

- ✨ 新增云相册系统
- ✨ 新增 GitHub 图床支持
- ✨ 新增文章密码保护
- ✨ 新增数据导出功能

---

## 📄 开源协议

本项目采用 [MIT License](LICENSE) 开源协议。

---

## 📮 联系方式

- **作者**: linxiong-rgb
- **邮箱**: 3497875641@qq.com
- **GitHub**: [@linxiong-rgb](https://github.com/linxiong-rgb)

---

<div align="center">

### 如果觉得项目对你有帮助，请给个 ⭐️ Star

**Made with ❤️ using Flask**

[⬆ 返回顶部](#-flask-blog-system)

</div>
