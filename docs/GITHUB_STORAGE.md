# GitHub 图床配置指南

## 为什么使用 GitHub 作为图床？

- **完全免费**：GitHub 提供免费的仓库和流量
- **无需信用卡**：只需要 GitHub 账号即可
- **永久存储**：文件永久保存在仓库中
- **CDN 加速**：通过 `raw.githubusercontent.com` 访问，速度快
- **版本控制**：自动保留图片的历史版本

## 存储容量限制

- 单个文件：最大 100MB
- 仓库总大小：推荐不超过 1GB
- 流量：每月 100GB 带宽（对于小型博客足够）

对于博客图片，假设平均每张 500KB：
- 可以存储约 2000 张图片
- 每月可支持约 20 万次访问

## 设置步骤

### 1. 创建 GitHub 仓库

1. 登录 [GitHub](https://github.com)
2. 点击右上角 `+` → **New repository**
3. 设置仓库：
   - **Repository name**：`blog-images`（或其他名称）
   - **Description**：博客图片存储
   - **Public/Private**：选择 **Public**（公开访问）
   - **Initialize with README**：勾选
4. 点击 **Create repository**

> **注意**：仓库必须是 Public 的，否则图片无法公开访问

### 2. 创建 Personal Access Token

1. 点击右上角头像 → **Settings**
2. 左侧菜单最下方 → **Developer settings**
3. 选择 **Personal access tokens** → **Tokens (classic)**
4. 点击 **Generate new token** → **Generate new token (classic)**
5. 配置 Token：
   - **Note**：`Flask Blog Images`
   - **Expiration**：选择过期时间（或 No expiration）
   - **Scopes**：勾选 **repo**（Full control of private repositories）
6. 点击 **Generate token**
7. **重要**：复制并保存 Token（只显示一次！）

### 3. 获取仓库信息

在创建的仓库页面，记下以下信息：

- **Repository**：`你的用户名/blog-images`
- 例如：`linxiong-rgb/blog-images`

### 4. 配置环境变量

在 Render 中配置以下环境变量：

#### 方式 A：通过 Render Dashboard

1. 登录 [Render Dashboard](https://dashboard.render.com/)
2. 选择你的 Web Service
3. 点击 **Environment** 标签
4. 添加以下环境变量：

| 环境变量 | 值 | 说明 |
|---------|-----|------|
| `GITHUB_TOKEN` | 你的 Personal Access Token | 步骤 2 生成的 Token |
| `GITHUB_REPO` | `用户名/仓库名` | 例如：`linxiong-rgb/blog-images` |
| `GITHUB_BRANCH` | `main` | 分支名（默认 main）|
| `GITHUB_PATH` | `images` | 图片存储路径（可选）|

#### 方式 B：通过 render.yaml

在 `render.yaml` 中添加：

```yaml
envVars:
  - key: GITHUB_TOKEN
    sync: false  # 不在 YAML 中显示
  - key: GITHUB_REPO
    value: your-username/blog-images
  - key: GITHUB_BRANCH
    value: main
  - key: GITHUB_PATH
    value: images
```

> **安全提示**：不要在 render.yaml 中硬编码 Token，使用 Dashboard 单独配置

### 5. 创建图片存储目录（可选）

如果设置了 `GITHUB_PATH=images`，在仓库中创建 `images` 和 `images/covers` 目录：

```bash
# 在本地克隆仓库
git clone https://github.com/你的用户名/blog-images.git
cd blog-images

# 创建目录
mkdir -p images/covers

# 提交
git add .
git commit -m "Create image directories"
git push
```

### 6. 本地开发配置

创建 `.env` 文件（记得添加到 `.gitignore`）：

```bash
# GitHub 图床配置（可选，不配置则使用本地存储）
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx
GITHUB_REPO=your-username/blog-images
GITHUB_BRANCH=main
GITHUB_PATH=images
```

## 验证配置

部署后，检查日志确认 GitHub 存储已启用：

```
使用 GitHub 图床: your-username/blog-images/images
```

如果看到：
```
使用本地存储: /app/app/static/uploads/covers
```

说明环境变量未正确配置，仍在使用本地存储。

## 图片 URL 格式

使用 GitHub 图床后，图片 URL 格式为：

```
https://raw.githubusercontent.com/用户名/仓库名/分支/images/covers/20260228_054451.jpg
```

例如：
```
https://raw.githubusercontent.com/linxiong-rgb/blog-images/main/images/covers/20260228_054451.jpg
```

## 迁移现有图片

如果你之前已经上传了一些图片到 Render 的临时存储，可以使用以下脚本迁移到 GitHub：

```python
# migrate_to_github.py
import os
from app import create_app, db
from app.models.post import Post
from app.utils.storage import get_storage

app = create_app()

with app.app_context():
    storage = get_storage()

    # 检查是否使用 GitHub 存储
    if not hasattr(storage, 'token'):
        print("错误：未配置 GitHub 存储，请先设置环境变量")
        return

    # 获取所有有封面图的文章
    posts = Post.query.filter(Post.cover_image.isnot(None)).all()

    for post in posts:
        if post.cover_image.startswith('/static/uploads/'):
            # 这是本地存储的图片
            old_path = post.cover_image

            # 提取文件名
            filename = old_path.split('/')[-1]

            # 本地文件路径
            local_path = os.path.join('app/static/uploads/covers', filename)

            if os.path.exists(local_path):
                # 上传到 GitHub
                object_name = f'covers/{filename}'
                if storage.upload_file(local_path, object_name):
                    # 更新数据库
                    post.cover_image = storage.get_url(object_name)
                    print(f'已迁移: {filename}')
                else:
                    print(f'迁移失败: {filename}')

    db.session.commit()
    print('迁移完成！')
```

## 常见问题

### 1. 图片返回 404 错误

**原因**：仓库是 Private 的

**解决**：
1. 进入仓库 Settings
2. 滚动到底部 **Danger Zone**
3. 点击 **Change repository visibility**
4. 选择 **Public**

### 2. 上传失败

**可能原因**：
- Token 无效或过期
- Token 没有 repo 权限
- 仓库名称错误
- 单个文件超过 100MB

**解决方案**：
1. 重新生成 Token 并更新环境变量
2. 确认仓库名称格式：`用户名/仓庛名`
3. 压缩大图片或使用其他存储方式

### 3. 图片加载慢

**原因**：`raw.githubusercontent.com` 在国内访问可能较慢

**解决方案**：
- 使用 CDN 加速（如 jsDelivr）
- 将 URL 替换为：`https://cdn.jsdelivr.net/gh/用户名/仓庛@分支/路径`

### 4. Token 权限不足

**错误信息**：`401 Unauthorized` 或 `403 Forbidden`

**解决方案**：
1. 重新生成 Token，确保勾选 `repo` 权限
2. 更新 Render 环境变量中的 `GITHUB_TOKEN`
3. 触发重新部署

### 5. 环境变量配置后仍使用本地存储

**原因**：服务未重启或环境变量未正确加载

**解决方案**：
1. 在 Render 中触发手动部署
2. 检查环境变量名称是否正确（区分大小写）
3. 查看日志确认配置状态

## 高级配置

### 使用 jsDelivr CDN 加速

修改 `storage.py` 中的 `get_url` 方法：

```python
def get_url(self, object_name):
    """获取 GitHub 文件访问 URL（使用 CDN）"""
    # 使用 jsDelivr CDN
    return f'https://cdn.jsdelivr.net/gh/{self.repo}@{self.branch}/{self.path}/{object_name}'
```

jsDelivr CDN 优点：
- 全球 CDN 加速
- 国内访问速度更快
- 自动缓存优化

### 分仓存储

如果图片较多，可以按年份或月份分仓：

```python
# 环境变量
GITHUB_REPO=your-username/blog-images-2024  # 按年份
GITHUB_REPO=your-username/blog-images-feb  # 按月份
```

### 使用自托管加速

如果你有自己的服务器和域名，可以使用反向代理加速：

```nginx
# nginx 配置
location /images/ {
    proxy_pass https://raw.githubusercontent.com/username/repo/main/images/;
    proxy_cache_valid 200 7d;
}
```

## 监控和管理

### 查看仓库使用情况

在仓库页面可以查看：
- 文件数量和大小
- 最新提交记录
- 存储空间使用情况

### 清理无用图片

定期检查并删除不再使用的图片：

1. 在仓库中浏览 `images/covers` 目录
2. 对比数据库中的图片引用
3. 删除未使用的文件

### 备份建议

虽然 GitHub 本身就很可靠，但建议：
1. 定期克隆仓库到本地备份
2. 使用 GitHub 的 Release 功能存档重要图片

## 其他图床选择

如果 GitHub 图床不适合你，还可以考虑：

| 服务 | 免费额度 | 优点 | 缺点 |
|------|---------|------|------|
| **imgbb.com** | 32MB/张，无限 | 无需注册 | API 限速 |
| **imgur.com** | 无限 | 快速 | 需要登录 |
| **Postimage.org** | 无限 | 简单 | 有广告 |
| **Cloudinary** | 25GB/月 | 功能强大 | 需要注册 |

## 技术支持

如有问题，请查看：
- [GitHub API 文档](https://docs.github.com/en/rest)
- [GitHub Pages 文档](https://docs.github.com/en/pages)
