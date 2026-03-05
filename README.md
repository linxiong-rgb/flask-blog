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

### 🖼️ 云相册系统
- **多级相册** - 支持文件夹式相册管理
- **图片上传** - 批量上传，自动生成缩略图
- **图片管理** - 编辑标题、描述、权限设置
- **共享空间** - 社区图片分享与发现
- **密码保护** - 图片访问密码功能
- **图片查看器** - 缩放、旋转、全屏查看
- **GitHub 图床** - 免费图床，CDN 加速

### 🎨 界面特色
- **响应式设计** - 完美适配手机、平板和电脑
- **渐变配色** - 紫色渐变主题，时尚美观
- **卡片式布局** - Material Design 风格
- **流畅动画** - 过渡和悬停动画效果
- **阅读体验** - Typora 风格，目录导航，阅读进度条

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
| **图片处理** | Pillow | 10.1.0+ |
| **WSI 服务器** | Gunicorn | 21.2.0 |
| **前端框架** | Bootstrap | 5.3.0 |
| **图标库** | Bootstrap Icons | 1.11.0 |

---

## 📸 功能展示

### 云相册功能

| 功能 | 描述 |
|:---|:---|
| **相册管理** | 多级文件夹式相册，支持拖拽排序 |
| **图片上传** | 批量上传，支持 PNG/JPG/GIF/WebP/BMP |
| **缩略图生成** | 自动生成 200x200 缩略图 |
| **图片编辑** | 标题、描述、可见性、访问密码 |
| **共享空间** | 社区公开图片分享与浏览 |
| **密码保护** | 图片访问密码，session 验证 |
| **图片查看器** | 缩放、旋转、拖拽、全屏 |
| **图片分享** | 直接图片链接，一键复制 |

### 博客功能

| 功能 | 描述 |
|:---|:---|
| **文章管理** | 创建、编辑、删除、发布/草稿 |
| **文章权限** | 公开、私密、密码保护 |
| **分类系统** | 多级分类，SEO 友好 |
| **标签系统** | 多标签，标签云展示 |
| **文章归档** | 按日期浏览，时间线展示 |
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
| **数据导出** | Markdown/HTML 导出 |
| **友链管理** | 后台管理友情链接 |

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

# 4. 初始化数据库
python reset_database.py

# 5. 运行应用
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
│   │   ├── user.py              # 用户模型
│   │   ├── post.py              # 文章模型
│   │   ├── album.py             # 相册/图片模型
│   │   ├── category.py          # 分类模型
│   │   ├── tag.py               # 标签模型
│   │   └── friend_link.py       # 友链模型
│   ├── routes/                  # 路由
│   │   ├── main.py              # 主路由
│   │   ├── auth.py              # 认证路由
│   │   ├── admin.py             # 管理路由
│   │   ├── gallery.py           # 云相册路由
│   │   └── export.py            # 导出路由
│   ├── templates/               # 模板
│   │   ├── base.html            # 基础模板
│   │   ├── index.html           # 首页
│   │   ├── post.html            # 文章详情
│   │   ├── gallery/             # 云相册模板
│   │   │   ├── index.html       # 相册首页
│   │   │   ├── view_album.html  # 相册详情
│   │   │   ├── shared_space.html # 共享空间
│   │   │   └── shared_photo_detail.html # 图片详情
│   │   └── admin/               # 管理模板
│   ├── static/                  # 静态文件
│   │   ├── css/                 # 样式文件
│   │   ├── vendor/              # 第三方库
│   │   ├── fonts/               # 字体文件
│   │   ├── img/                 # 默认图片
│   │   └── uploads/             # 上传文件
│   ├── forms.py                 # 表单类
│   ├── utils/                   # 工具函数
│   │   ├── storage.py           # 存储后端
│   │   └── image_generator.py   # 封面图生成器
│   └── security.py              # 安全配置
├── instance/                    # 实例文件夹
├── requirements.txt             # 依赖列表
├── run.py                       # 启动脚本
├── reset_database.py            # 数据库重置脚本
├── README.md                    # 项目文档
├── CHANGELOG.md                 # 更新日志
├── DEPLOY.md                    # 部署文档
└── CONTRIBUTING.md              # 贡献指南
```

---

## ⚙️ 配置说明

### 环境变量

| 变量名 | 说明 | 默认值 |
|:-------|:-----|:-------|
| `SECRET_KEY` | Flask 密钥 | 自动生成 |
| `DATABASE_URL` | 数据库连接 | `sqlite:///blog.db` |
| `DEBUG` | 调试模式 | `True` |
| `GITHUB_TOKEN` | GitHub Token | 无（可选）|
| `GITHUB_REPO` | GitHub 仓库 | 无（可选）|
| `GITHUB_BRANCH` | GitHub 分支 | `main` |
| `GITHUB_PATH` | 图片存储路径 | `images` |

### 配置 GitHub 图床（推荐）

使用 GitHub 作为免费图床，享受 jsDelivr CDN 加速：

1. 创建 GitHub 仓库存放图片
2. 生成 Personal Access Token
3. 配置环境变量：`GITHUB_TOKEN`、`GITHUB_REPO`

详见：[docs/GITHUB_STORAGE.md](docs/GITHUB_STORAGE.md)

---

## 🌐 部署指南

### 快速部署到 Render

<div align="center">

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://dashboard.render.com/)

</div>

1. **Fork 本仓库**
2. **创建 PostgreSQL 数据库**（免费套餐）
3. **创建 Web Service**，配置环境变量
4. **初始化数据库** - 访问 `/init-db`
5. **配置 GitHub 图床**（可选）

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
1. `uploads/` 目录存在且有写入权限
2. 图片格式支持（PNG、JPG、GIF、WebP、BMP）
3. 图片大小不超过限制（默认 50MB）

### 部署后无法登录

1. 访问 `/init-db` 初始化数据库
2. 使用 `/check-db` 检查用户状态
3. 查看应用日志获取错误信息

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

### v2.0.0 (最新)

**云相册系统**
- ✨ 新增多级相册管理
- ✨ 新增图片批量上传
- ✨ 新增共享空间功能
- ✨ 新增图片密码保护
- ✨ 新增图片查看器（缩放/旋转/全屏）
- ✨ 新增 GitHub 图床支持
- 🎨 优化相册 UI 设计
- 🎨 优化共享空间布局

**博客系统**
- ✨ 新增文章密码保护
- ✨ 新增文章收藏功能
- 🐛 修复图片加载问题
- 🐛 修复 JavaScript 转义问题

### v1.5.0

- ✨ 新增文章浏览权限
- ✨ 新增数据库迁移功能
- 🐛 修复缺少新列导致的 500 错误

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
