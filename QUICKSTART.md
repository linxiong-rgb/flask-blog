# 快速启动指南

## 问题已解决！

数据库已经成功重置，所有字段都已创建。

## 启动博客

```bash
cd ~/my-blog
python run.py
```

或

```bash
cd ~/my-blog
py run.py
```

## 访问地址

- 首页: http://localhost:5000
- 注册: http://localhost:5000/auth/register
- 登录: http://localhost:5000/auth/login
- 管理后台: http://localhost:5000/admin（需先登录）

## 首次使用流程

### 1. 注册账号
访问 http://localhost:5000/auth/register

### 2. 登录系统
使用注册的用户名和密码登录

### 3. 创建分类和标签
进入管理后台 → 创建分类和标签（可选）

### 4. 发布文章
- 方式一：手动创建
  1. 点击"新建文章"
  2. 填写标题、内容
  3. 选择分类、标签
  4. 点击"保存"

- 方式二：导入MD文件
  1. 点击"导入 MD"
  2. 选择MD文件
  3. 点击"导入"
  4. 编辑后发布

- 方式三：编辑时导入
  1. 新建文章
  2. 点击"导入 MD 文件"按钮
  3. 选择文件自动填充
  4. 补充信息后保存

## 功能测试

### 测试搜索
在顶部搜索框输入关键词搜索文章

### 测试夜间模式
点击导航栏的月亮图标切换深色主题

### 测试分类浏览
导航栏 → 分类 → 查看所有分类

### 测试标签过滤
点击文章标签查看相关文章

### 测试MD导入
1. 使用项目根目录的 `示例文章.md`
2. 或导入自己的MD文件

## 数据库已包含的字段

### Post 表（文章）
- ✅ category_id - 分类ID
- ✅ views - 浏览量
- ✅ cover_image - 封面图
- ✅ 所有其他必需字段

### Category 表（分类）
- ✅ id, name, description, created_at

### Tag 表（标签）
- ✅ id, name, created_at

### Post_Tags 表（关联）
- ✅ post_id, tag_id

## 项目完整功能

### 核心功能
- 用户注册/登录
- 文章CRUD
- Markdown支持
- 分类系统
- 标签系统
- 搜索功能

### 高级功能
- MD文件导入（单/批量）
- 多编码支持（UTF-8/GBK等）
- 浏览量统计
- 夜间模式
- 响应式设计
- 分页功能

### 界面特色
- 紫色渐变主题
- 卡片式布局
- 动画效果
- 侧边栏组件
- 面包屑导航

## 文件结构

```
my-blog/
├── app/
│   ├── __init__.py          ✅ Flask应用工厂
│   ├── models/
│   │   ├── user.py          ✅ 用户模型
│   │   └── post.py          ✅ 文章/分类/标签模型
│   ├── routes/
│   │   ├── auth.py          ✅ 认证路由
│   │   ├── main.py          ✅ 主要路由
│   │   └── admin.py         ✅ 管理路由（含导入）
│   ├── static/
│   │   └── css/
│   │       └── style.css    ✅ 自定义样式
│   └── templates/
│       ├── base.html        ✅ 基础模板
│       ├── index.html       ✅ 首页
│       ├── post.html        ✅ 文章详情
│       ├── about.html       ✅ 关于页
│       ├── search.html      ✅ 搜索页
│       ├── category.html    ✅ 分类页
│       ├── tag.html         ✅ 标签页
│       ├── categories.html  ✅ 分类列表
│       ├── auth/            ✅ 认证模板
│       └── admin/           ✅ 管理模板
├── instance/
│   └── blog.db             ✅ SQLite数据库（已重置）
├── requirements.txt        ✅ 依赖列表
├── run.py                 ✅ 启动脚本
├── reset_database.py      ✅ 数据库重置脚本
├── migrate_db.py          ✅ 数据库迁移脚本
├── README.md              ✅ 项目说明
├── PROJECT_GUIDE.md       ✅ 完整项目指南
└── 示例文章.md            ✅ 测试用MD文件
```

## 故障排除

### 如果启动失败

1. 确认依赖已安装：
```bash
pip install -r requirements.txt
```

2. 重置数据库：
```bash
python reset_database.py
```

3. 检查端口是否被占用：
```bash
# Windows
netstat -ano | findstr :5000

# 如果被占用，修改 run.py 中的端口
```

### 如果界面显示异常

1. 清除浏览器缓存
2. 硬刷新页面（Ctrl+F5）
3. 检查浏览器控制台是否有错误

### 如果导入MD失败

1. 确认文件是UTF-8编码（推荐）
2. 系统会自动尝试GBK等编码
3. 检查文件扩展名必须是.md

## 开发建议

### 修改主题色
编辑 `app/static/css/style.css`:
```css
:root {
    --primary-color: #667eea;  /* 修改这里 */
    --secondary-color: #764ba2; /* 和这里 */
}
```

### 修改密钥
编辑 `app/__init__.py`:
```python
app.config['SECRET_KEY'] = '改成随机字符串'
```

### 更换数据库
编辑 `app/__init__.py`:
```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://user:pass@localhost/blog'
```

## 后续优化建议

- 添加评论系统
- 图片上传功能
- 文章点赞/收藏
- RSS订阅
- 友情链接
- 文章归档
- 全文搜索优化
- 缓存优化
- 部署到生产环境

## 技术支持

如遇问题，检查以下文件：
- `PROJECT_GUIDE.md` - 完整项目文档
- `README.md` - 详细说明
- `reset_database.py` - 数据库重置
- `migrate_db.py` - 数据库迁移

---

**现在可以开始使用博客了！** 🎉
