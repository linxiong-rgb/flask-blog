<div align="center">

# Flask Blog System

**现代化、功能完整的 Flask 博客系统**

[![Flask](https://img.shields.io/badge/Flask-3.0.0-blue?logo=flask)](https://flask.palletsprojects.com/)
[![Python](https://img.shields.io/badge/Python-3.8+-green?logo=python)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/linxiong-rgb/flask-blog?style=social)](https://github.com/linxiong-rgb/flask-blog/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/linxiong-rgb/flask-blog?style=social)](https://github.com/linxiong-rgb/flask-blog/network/members)

</div>

---

## 项目简介

一个基于 Flask 开发的现代化博客系统，专注于简洁、高效的用户体验。系统采用 Bootstrap 5 构建响应式前端界面，支持 Markdown 写作、夜间模式、智能搜索等功能。

### 核心特性

- **快速部署** - 支持多种部署方案（Vercel、Render、Docker、VPS）
- **Markdown 写作** - 支持标准 Markdown 语法和代码高亮
- **夜间模式** - 护眼的深色主题，偏好自动保存
- **智能搜索** - 实时搜索建议，支持文章/分类/标签
- **响应式设计** - 完美适配手机、平板和电脑
- **用户认证** - Flask-Login 用户认证系统
- **数据统计** - 文章浏览量统计

---

## 技术栈

| 类别 | 技术 | 版本 |
|------|------|------|
| 后端框架 | Flask | 3.0.0 |
| 数据库 | SQLite / PostgreSQL | 3 / 14+ |
| ORM | SQLAlchemy | 3.1.1 |
| 用户认证 | Flask-Login | 0.6.3 |
| CSRF 保护 | Flask-WTF | 1.2.1 |
| Markdown | Python-Markdown | 3.5.1 |
| 图片处理 | Pillow | 10.1.0+ |
| WSGI 服务器 | Gunicorn | 21.2.0 |
| 前端框架 | Bootstrap | 5.3.0 |
| 图标库 | Bootstrap Icons | 1.11.0 |

---

## 功能特性

### 核心功能

- 用户注册和登录 - Flask-Login 用户认证
- 文章管理 - 创建、编辑、删除文章
- Markdown 写作 - 支持标准 Markdown 语法
- 文章状态 - 发布/草稿管理
- 文章可见性 - 公开/私密/密码保护
- 浏览统计 - 文章浏览量统计
- 文章收藏 - 用户收藏喜欢的文章

### 高级功能

- **智能搜索** - 实时搜索建议，支持文章/分类/标签搜索
- **分类管理** - 将文章组织到不同分类
- **标签系统** - 多标签支持，标签云展示
- **文章归档** - 按日期浏览文章
- **友情链接** - 管理和展示友情链接
- **RSS 订阅** - 自动生成 RSS Feed
- **Sitemap** - 自动生成站点地图
- **文章分享** - 支持微博、QQ、微信分享

### 界面特色

- **夜间模式** - 护眼的深色主题，偏好自动保存
- **响应式设计** - 完美支持手机、平板和电脑
- **渐变配色** - 紫色渐变主题，时尚美观
- **卡片式布局** - Material Design 风格
- **流畅动画** - 过渡和悬停动画效果
- **Typora 风格** - 优雅的文章阅读体验
- **目录导航** - 自动生成文章目录
- **阅读进度条** - 顶部显示阅读进度
- **代码高亮** - 代码块语法高亮
- **字体调节** - 支持字体大小调节

### 管理功能

- **仪表板** - 数据统计和快速操作
- **文章管理** - 列表视图，删除确认
- **Markdown 导入** - 支持单个/批量导入 .md 文件
- **智能摘要** - 自动生成文章摘要
- **封面图生成** - 自动生成简约封面图
- **收藏管理** - 查看用户收藏列表
- **数据导出** - 导出 Markdown/HTML
- **友链管理** - 后台管理友情链接

### 图片功能

- **GitHub 图床** - 免费图床，jsDelivr CDN 加速，国内可直接访问
- **字体优化** - 支持楷体/宋体，跨平台中文字体自动检测
- **封面图生成** - 一键生成简约风格的封面图
- **重新生成封面** - 可重新生成文章封面图
- **快捷插入图片** - 编辑器内快捷插入本地图片
- **本地图片智能提示** - 自动检测并提示上传本地图片路径
- **图片查看功能** - 图片预览和查看
- **图片加载优化** - 图片懒加载，优化页面性能
- **图片上传** - 支持本地上传封面图和内容图片

---

## 快速开始

### 环境要求

- Python 3.8+
- pip 包管理器

### 安装步骤

```bash
# 1. 克隆项目
git clone https://github.com/linxiong-rgb/flask-blog.git
cd flask-blog

# 2. 创建并激活虚拟环境（推荐）
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

### 访问博客

打开浏览器访问: `http://localhost:5000`

**默认管理员账号：**
- 用户名: `admin01`
- 密码: `123456`

> **安全提醒**：首次使用后请立即修改默认密码！

---

## 项目结构

```
flask-blog/
├── app/
│   ├── __init__.py          # 应用工厂
│   ├── models/              # 数据模型
│   │   ├── __init__.py      # 模型初始化
│   │   ├── user.py          # 用户模型
│   │   ├── post.py          # 文章模型
│   │   ├── post_bookmark.py # 收藏模型
│   │   ├── category.py      # 分类模型
│   │   ├── tag.py           # 标签模型
│   │   └── friend_link.py   # 友链模型
│   ├── routes/              # 路由
│   │   ├── __init__.py      # 路由初始化
│   │   ├── main.py          # 主路由
│   │   ├── auth.py          # 认证路由
│   │   ├── admin.py         # 管理路由
│   │   └── export.py        # 导出路由（RSS、Sitemap）
│   ├── templates/           # 模板
│   │   ├── base.html        # 基础模板
│   │   ├── index.html       # 首页
│   │   ├── post.html        # 文章详情
│   │   ├── search.html      # 搜索页
│   │   ├── category.html    # 分类页
│   │   ├── tag.html         # 标签页
│   │   ├── archive.html     # 归档页
│   │   ├── categories.html  # 分类列表
│   │   ├── about.html       # 关于页面
│   │   ├── friend_links.html # 友链页
│   │   └── admin/           # 管理模板
│   │       ├── dashboard.html
│   │       ├── edit_post.html
│   │       ├── edit_category.html
│   │       ├── bookmarks.html
│   │       └── friend_links.html
│   ├── static/              # 静态文件
│   │   ├── css/             # 样式文件
│   │   ├── vendor/          # 第三方库
│   │   │   ├── bootstrap/   # Bootstrap 框架
│   │   │   └── icons/       # Bootstrap Icons
│   │   ├── fonts/           # 字体文件
│   │   ├── img/             # 默认图片
│   │   └── uploads/         # 上传文件（开发环境）
│   │       └── covers/     # 封面图片目录
│   ├── forms.py             # 表单类
│   ├── utils/               # 工具函数
│   │   ├── image_generator.py  # 封面图生成器
│   │   ├── scheduler.py     # 定时任务调度器
│   │   ├── text.py          # 文本处理工具
│   │   └── storage.py       # 存储后端（本地/GitHub）
│   └── security.py          # 安全配置
├── instance/                # 实例文件夹
├── requirements.txt         # 依赖列表
├── run.py                   # 启动脚本
├── reset_database.py        # 数据库重置脚本
├── LICENSE                  # MIT 许可证
├── README.md               # 项目文档
├── CONTRIBUTING.md         # 贡献指南
└── DEPLOY.md               # 部署文档
```

---

## 配置说明

### 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `SECRET_KEY` | Flask 密钥 | 自动生成 |
| `DATABASE_URL` | 数据库连接 | `sqlite:///blog.db` |
| `DEBUG` | 调试模式 | `True` |
| `FLASK_ENV` | 运行环境 | `development` |
| `GITHUB_TOKEN` | GitHub Personal Access Token | 无（可选）|
| `GITHUB_REPO` | GitHub 仓库（用户名/仓庛名） | 无（可选）|
| `GITHUB_BRANCH` | GitHub 分支名 | `main` |
| `GITHUB_PATH` | 图片存储路径 | `images` |

**配置 GitHub 图床**（推荐用于生产环境）：
- 免费图床，图片永久保存
- 无需信用卡
- 详见 [docs/GITHUB_STORAGE.md](docs/GITHUB_STORAGE.md)

### 主题定制

编辑 `app/static/css/style.css` 可自定义：

- `--primary-color` - 主色调
- `--gradient` - 渐变色
- `--text-color` - 文字颜色
- `--bg-color` - 背景色
- `--card-bg` - 卡片背景色

### 字体配置

项目支持跨平台中文字体，字体文件应放置在 `app/static/fonts/` 目录：

- `simkai.ttf` - 楷体
- `simsun.ttc` / `simsunb.ttf` - 宋体/粗宋体
- `msyh.ttc` / `msyhbd.ttc` - 微软雅黑
- `simhei.ttf` - 黑体

系统会自动检测并使用可用的字体。

---

## 常见问题

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

**本地开发环境：**
运行数据库重置脚本：
```bash
python reset_database.py
```

**生产环境（如 Render）：**
访问以下地址重新创建管理员：
```
https://你的域名/init-db
```

### 部署后无法登录

如果部署后出现登录失败，检查以下几点：
1. 确认已访问 `/init-db` 初始化数据库
2. 使用 `/check-db` 检查用户是否存在
3. 查看应用日志获取详细错误信息

### 图片上传失败

确保：
1. `app/static/uploads/covers/` 目录存在且有写入权限
2. 图片格式支持（PNG、JPG、GIF、WebP）
3. 图片大小不超过限制（默认 16MB）

### 封面图生成失败

确保：
1. 系统已安装 Pillow 库
2. 字体文件存在于 `app/static/fonts/` 目录
3. 查看日志获取详细错误信息

---

## 部署指南

### 快速部署到 Render

1. **Fork 本仓库** 到你的 GitHub

2. **访问 [Render](https://dashboard.render.com)** 并连接 GitHub

3. **创建 PostgreSQL 数据库**
   - 点击 New → PostgreSQL
   - 选择 Free 套餐
   - 复制 Internal Database URL

4. **创建 Web Service**
   - 点击 New → Web Service
   - 选择你 fork 的仓库
   - 配置如下：
     - Environment: Python 3
     - Build Command: `pip install -r requirements.txt`
     - Start Command: (留空，使用 Procfile)
   - 环境变量：
     ```
     DATABASE_URL=你的PostgreSQL URL
     SECRET_KEY=随机生成32位字符串
     DEBUG=False
     FLASK_ENV=production
     ```

5. **初始化数据库**
   - 部署完成后访问：`https://你的应用.onrender.com/init-db`
   - 使用 `/check-db` 验证数据库状态

6. **配置 GitHub 图床**（推荐）
   - 创建 GitHub 仓库和 Personal Access Token
   - 添加环境变量：`GITHUB_TOKEN`、`GITHUB_REPO`
   - 详见 [docs/GITHUB_STORAGE.md](docs/GITHUB_STORAGE.md)

7. **登录后台**
   - 访问：`https://你的应用.onrender.com/auth/login`
   - 用户名: `admin01`，密码: `123456`

详细部署文档请查看 [DEPLOY.md](DEPLOY.md)

---

## 贡献

欢迎贡献代码！请查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解详情。

### 开发流程

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

## 开源协议

本项目采用 [MIT License](LICENSE) 开源协议。

---

## 联系方式

- **作者**: linxiong-rgb
- **邮箱**: 3497875641@qq.com
- **GitHub**: [@linxiong-rgb](https://github.com/linxiong-rgb)

---

## 更新日志

### v1.5.0 (最新)

- **新增** 文章浏览权限 - 公开/私密/密码保护
- **新增** 数据库迁移功能 - 自动检测并添加新列
- **优化** 向后兼容 - 不影响现有数据
- **修复** 因缺少新列导致的 500 错误

### v1.4.0

- **修复** 图片上传嵌套语法问题
- **优化** 代码质量和安全性
- **移除** 批量上传功能

### v1.3.0

- **新增** GitHub 图床支持 - 免费图床，图片永久保存
- **新增** 存储后端抽象 - 支持本地和 GitHub 存储
- **优化** 图片上传流程 - 自动选择存储后端
- **修复** generate-summary API 400 错误
- **修复** 图片显示后消失的问题
- **新增** 默认 OG 图片 - 用于社交媒体分享

### v1.2.0

- **新增** 字体优化功能 - 支持楷体/宋体，跨平台字体检测
- **新增** 重新生成封面图功能
- **新增** 快捷插入图片功能
- **新增** 本地图片智能提示功能
- **新增** 图片查看功能
- **优化** 图片加载性能 - 懒加载支持
- **优化** 封面图生成器 - 支持更多字体和智能字体大小

### v1.1.0

- **新增** Markdown 文件批量导入
- **新增** 自动生成文章摘要
- **新增** 图片上传和优化
- **优化** 编辑器用户体验

### v1.0.0

- 初始版本发布
- 完整的博客功能
- 用户认证和权限管理

---

<div align="center">

**如果觉得项目对你有帮助，请给个 Star**

Made with ❤️ using Flask

</div>
