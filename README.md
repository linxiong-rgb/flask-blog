# 我的博客

一个现代化、功能丰富的 Flask 博客系统，拥有美观的界面和丰富的功能。

## 功能特点

### 核心功能
- 用户注册和登录
- 文章的创建、编辑和删除
- 支持 Markdown 格式写作
- 文章发布/草稿状态管理
- 文章浏览量统计

### 高级功能
- 分类管理 - 将文章组织到不同分类
- 标签系统 - 为文章添加多个标签
- 全文搜索 - 搜索文章标题、内容和摘要
- 夜间模式 - 护眼的深色主题，自动保存偏好
- 文章封面图 - 支持为文章设置封面图片
- 分页功能 - 文章列表自动分页

### 界面特色
- 响应式设计 - 完美支持手机、平板和电脑
- 卡片式布局 - 现代化的 Material Design 风格
- 渐变配色 - 紫色渐变主题，时尚美观
- 动画效果 - 流畅的过渡和悬停动画
- 侧边栏组件 - 热门文章、标签云、站点统计
- 面包屑导航 - 清晰的页面层级

## 技术栈

- **后端**: Flask 3.0.0
- **数据库**: SQLite
- **ORM**: SQLAlchemy 3.1.1
- **用户认证**: Flask-Login 0.6.3
- **前端**: Bootstrap 5.3.0
- **图标**: Bootstrap Icons 1.11.0
- **Markdown**: Python-Markdown 3.5.1

## 安装步骤

### 1. 安装依赖

```bash
cd my-blog
pip install -r requirements.txt
```

### 2. 运行博客

```bash
python run.py
```

### 3. 访问博客

打开浏览器访问: `http://localhost:5000`

## 使用说明

### 首次使用

1. 访问 `http://localhost:5000/auth/register` 注册账号
2. 使用注册的账号登录
3. 点击导航栏的"管理"进入管理界面
4. 创建分类和标签（可选）
5. 创建你的第一篇文章

### Markdown 语法示例

```markdown
# 一级标题

## 二级标题

这是一段普通文本。

**粗体文本** 和 *斜体文本*

- 列表项 1
- 列表项 2
- 列表项 3

[链接文本](https://example.com)

`行内代码`

```
代码块
```

> 引用文本

![图片描述](图片URL)
```

### 文章管理

1. **创建文章**：管理后台 → 新建文章
2. **导入 Markdown**：管理后台 → 导入 MD（支持单个或批量导入）
3. **快捷导入**：在新建/编辑文章页面点击"导入 MD 文件"按钮
4. **设置分类**：选择已有分类或创建新分类
5. **添加标签**：勾选一个或多个标签
6. **设置封面**：输入图片 URL（可选）
7. **发布/草稿**：勾选"立即发布"或保存为草稿

### Markdown 文件导入

博客支持导入现有的 Markdown 文件，保持格式不变，不会出现乱码：

#### 支持的导入方式

1. **单文件导入**：管理后台 → 导入 MD → 选择单个 .md 文件
2. **批量导入**：管理后台 → 导入 MD → 选择多个 .md 文件
3. **编辑时导入**：新建/编辑文章 → 点击"导入 MD 文件"按钮

#### 支持的文件格式

- **标准 Markdown**：
  ```markdown
  # 文章标题

  这里是正文...
  ```

- **YAML Front Matter**（Jekyll/Hugo 格式）：
  ```markdown
  ---
  title: 文章标题
  date: 2025-01-17
  ---

  这里是正文...
  ```

#### 编码支持

自动识别并支持以下编码，防止乱码：
- UTF-8（推荐）
- UTF-8 with BOM
- GBK/GB2312（中文）
- ISO-8859-1

#### 导入说明

- 自动提取标题（从 # 标题、YAML front matter 或文件名）
- 自动生成摘要（文章前 200 字）
- 导入的文章默认为草稿状态
- 保持 Markdown 原始格式，不会出现乱码
- 可以在导入后编辑、添加分类和标签

### 分类和标签管理

在管理后台可以：
- 创建新分类
- 删除分类
- 添加新标签
- 删除标签

## 项目结构

```
my-blog/
├── app/
│   ├── __init__.py          # Flask 应用工厂
│   ├── models/              # 数据库模型
│   │   ├── user.py          # 用户模型
│   │   ├── post.py          # 文章、分类、标签模型
│   │   └── __init__.py
│   ├── routes/              # 路由
│   │   ├── auth.py          # 认证路由
│   │   ├── main.py          # 主要路由（含搜索、分类、标签）
│   │   ├── admin.py         # 管理路由
│   │   └── __init__.py
│   ├── templates/           # HTML 模板
│   │   ├── base.html        # 基础模板
│   │   ├── index.html       # 首页
│   │   ├── post.html        # 文章页
│   │   ├── about.html       # 关于页
│   │   ├── search.html      # 搜索页
│   │   ├── category.html    # 分类页
│   │   ├── tag.html         # 标签页
│   │   ├── categories.html  # 分类列表
│   │   ├── auth/            # 认证模板
│   │   └── admin/           # 管理模板
│   └── static/              # 静态文件
│       └── css/
│           └── style.css    # 自定义样式
├── instance/                # 实例文件夹（数据库）
├── requirements.txt         # 依赖列表
├── run.py                   # 启动脚本
└── README.md               # 说明文档
```

## 配置说明

在 `app/__init__.py` 中可以修改以下配置：

- `SECRET_KEY`: Flask 密钥，请修改为随机字符串
- `SQLALCHEMY_DATABASE_URI`: 数据库连接字符串

## 界面预览

### 特色功能

1. **夜间模式** - 点击导航栏的月亮图标切换
2. **搜索功能** - 顶部搜索框支持全文搜索
3. **分类浏览** - 导航栏 → 分类 → 查看所有分类
4. **标签过滤** - 点击文章标签查看相关文章
5. **热门文章** - 侧边栏显示浏览量最高的文章
6. **站点统计** - 实时显示文章、分类、标签数量

### 主题定制

编辑 `app/static/css/style.css` 可以自定义：

- 主色调（`--primary-color`）
- 次色调（`--secondary-color`）
- 背景色
- 字体和间距

## 常见问题

### 端口被占用

如果 5000 端口被占用，修改 `run.py` 中的端口号：

```python
app.run(debug=True, host='0.0.0.0', port=5001)  # 改为其他端口
```

### 重置数据库

删除 `instance/blog.db` 文件，重新运行应用即可创建新数据库。

### 分类/标签未显示

确保：
1. 已创建分类和标签
2. 文章已关联分类和标签
3. 文章状态为"已发布"

## 后续开发建议

- 添加评论系统
- 支持图片上传
- 文章点赞/收藏功能
- RSS 订阅
- 社交媒体分享
- 友情链接
- 文章归档页面
- 全文搜索优化（Elasticsearch）
- 缓存优化（Redis）
- 部署到生产环境

## 部署到生产环境

### 使用 Gunicorn

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 "app:create_app()"
```

### 使用 Nginx 反向代理

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static {
        alias /path/to/my-blog/app/static;
    }
}
```

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

## 联系方式

- Email: contact@myblog.com
- GitHub: github.com/myblog

---

**享受写作，分享知识！** ✨
