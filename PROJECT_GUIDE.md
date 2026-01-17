# 博客项目完整文件列表

## 项目结构

```
my-blog/
├── app/                              # 应用主目录
│   ├── __init__.py                   # Flask 应用工厂
│   ├── models/                       # 数据库模型
│   │   ├── __init__.py
│   │   ├── user.py                   # 用户模型
│   │   └── post.py                   # 文章、分类、标签模型
│   ├── routes/                       # 路由
│   │   ├── __init__.py
│   │   ├── auth.py                   # 认证路由
│   │   ├── main.py                   # 主要路由
│   │   └── admin.py                  # 管理路由
│   ├── static/                       # 静态文件
│   │   └── css/
│   │       └── style.css             # 自定义样式
│   └── templates/                    # HTML 模板
│       ├── base.html                 # 基础模板
│       ├── index.html                # 首页
│       ├── post.html                 # 文章详情
│       ├── about.html                # 关于页
│       ├── search.html               # 搜索页
│       ├── category.html             # 分类页
│       ├── tag.html                  # 标签页
│       ├── categories.html           # 分类列表
│       ├── auth/                     # 认证模板
│       │   ├── login.html
│       │   └── register.html
│       └── admin/                    # 管理模板
│           ├── dashboard.html        # 管理后台
│           ├── edit_post.html        # 编辑文章
│           ├── edit_category.html    # 编辑分类
│           └── import.html           # 导入MD
├── instance/                         # 实例文件夹
│   └── blog.db                       # SQLite 数据库
├── requirements.txt                  # 依赖列表
├── run.py                            # 启动脚本
├── reset_database.py                 # 数据库重置脚本
├── migrate_db.py                     # 数据库迁移脚本
├── README.md                         # 项目说明
└── 示例文章.md                       # 示例 MD 文件
```

## 所有文件详细说明

### 核心文件

#### 1. run.py - 启动脚本
```python
from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
```

#### 2. requirements.txt - 依赖
```
Flask==3.0.0
Flask-SQLAlchemy==3.1.1
Flask-Login==0.6.3
Flask-WTF==1.2.1
email_validator==2.1.0.post1
markdown==3.5.1
Werkzeug==3.0.1
```

### 数据库模型

#### 3. app/models/user.py - 用户模型
- User 类（用户表）
- 密码加密
- 用户登录

#### 4. app/models/post.py - 文章模型
- Post 类（文章表）
- Category 类（分类表）
- Tag 类（标签表）
- post_tags 关联表

### 路由

#### 5. app/routes/auth.py - 认证路由
- /auth/register - 注册
- /auth/login - 登录
- /auth/logout - 退出

#### 6. app/routes/main.py - 主要路由
- / - 首页
- /post/<id> - 文章详情
- /about - 关于
- /category/<id> - 分类文章
- /tag/<id> - 标签文章
- /categories - 分类列表
- /search - 搜索

#### 7. app/routes/admin.py - 管理路由
- /admin/ - 管理后台
- /admin/post/new - 新建文章
- /admin/post/<id>/edit - 编辑文章
- /admin/post/<id>/delete - 删除文章
- /admin/category/new - 新建分类
- /admin/category/<id>/delete - 删除分类
- /admin/tag/new - 新建标签
- /admin/tag/<id>/delete - 删除标签
- /admin/import - 导入MD
- /admin/import/batch - 批量导入

### 模板文件

#### 8. app/templates/base.html - 基础模板
- 导航栏
- 搜索框
- 夜间模式切换
- 用户菜单
- 页脚

#### 9. app/templates/index.html - 首页
- Hero 区域
- 文章列表
- 侧边栏（热门文章、标签云、统计）

#### 10. app/templates/post.html - 文章详情
- 面包屑导航
- 文章内容
- 作者信息
- 分享功能

#### 11. app/templates/admin/dashboard.html - 管理后台
- 统计卡片
- 分类/标签管理
- 文章列表

#### 12. app/templates/admin/edit_post.html - 编辑文章
- 文章表单
- MD文件导入
- Markdown语法提示

#### 13. app/templates/admin/import.html - 导入页面
- 单文件导入
- 批量导入
- 导入结果

### 静态文件

#### 14. app/static/css/style.css - 样式文件
- CSS 变量（颜色、主题）
- 响应式布局
- 夜间模式
- 动画效果

### 工具脚本

#### 15. reset_database.py - 数据库重置
删除旧数据库并重新创建所有表

#### 16. migrate_db.py - 数据库迁移
更新现有数据库结构，保留数据

## 数据库表结构

### user 表
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| username | VARCHAR(80) | 用户名 |
| email | VARCHAR(120) | 邮箱 |
| password_hash | VARCHAR(128) | 密码哈希 |
| created_at | DATETIME | 创建时间 |

### post 表
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| title | VARCHAR(200) | 标题 |
| content | TEXT | 内容 |
| summary | VARCHAR(300) | 摘要 |
| user_id | INTEGER | 作者ID |
| category_id | INTEGER | 分类ID |
| views | INTEGER | 浏览量 |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |
| published | BOOLEAN | 是否发布 |
| cover_image | VARCHAR(500) | 封面图URL |

### category 表
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| name | VARCHAR(50) | 分类名 |
| description | VARCHAR(200) | 描述 |
| created_at | DATETIME | 创建时间 |

### tag 表
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| name | VARCHAR(50) | 标签名 |
| created_at | DATETIME | 创建时间 |

### post_tags 表（关联表）
| 字段 | 类型 | 说明 |
|------|------|------|
| post_id | INTEGER | 文章ID |
| tag_id | INTEGER | 标签ID |

## 功能清单

### 用户功能
- [x] 用户注册
- [x] 用户登录
- [x] 用户退出
- [x] 密码加密

### 文章功能
- [x] 创建文章
- [x] 编辑文章
- [x] 删除文章
- [x] Markdown支持
- [x] 浏览量统计
- [x] 封面图片
- [x] 发布/草稿

### 分类标签
- [x] 创建分类
- [x] 删除分类
- [x] 创建标签
- [x] 删除标签
- [x] 分类浏览
- [x] 标签过滤

### 导入功能
- [x] 导入MD文件
- [x] 批量导入
- [x] 编码识别
- [x] 格式解析

### 界面功能
- [x] 夜间模式
- [x] 响应式设计
- [x] 搜索功能
- [x] 分页功能
- [x] 热门文章
- [x] 站点统计

## 启动步骤

### 1. 安装依赖
```bash
cd my-blog
pip install -r requirements.txt
```

### 2. 重置数据库（如果需要）
```bash
python reset_database.py
```

### 3. 启动应用
```bash
python run.py
```

### 4. 访问博客
```
http://localhost:5000
```

## 首次使用

1. 注册账号：http://localhost:5000/auth/register
2. 登录系统
3. 进入管理后台创建分类和标签
4. 发布第一篇文章

## 常见问题

### 1. 数据库错误
运行 `python reset_database.py` 重置数据库

### 2. 端口占用
修改 `run.py` 中的端口号

### 3. 编码问题
导入MD文件时自动识别多种编码

## 技术栈

- **后端**: Flask 3.0
- **数据库**: SQLite
- **ORM**: SQLAlchemy
- **认证**: Flask-Login
- **前端**: Bootstrap 5
- **图标**: Bootstrap Icons
- **Markdown**: Python-Markdown
